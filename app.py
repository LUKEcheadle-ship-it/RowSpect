from __future__ import annotations

import json
from pathlib import Path
from uuid import uuid4

import pandas as pd
import streamlit as st

from rowspect.clean import clean_dataframe, cleanup_summary
from rowspect.conversion import (
    ConversionError,
    SUPPORTED_TARGET_TYPES,
    analyze_type_conversion,
    apply_type_conversions,
)
from rowspect.export import dataframe_to_csv, dataframe_to_xlsx
from rowspect.insights import correlation_matrix, missingness_table, numeric_histogram, top_values
from rowspect.io import MAX_FILE_BYTES, RowSpectIOError, get_excel_sheets, load_table
from rowspect.profile import profile_dataframe
from rowspect.report import build_html_report
from rowspect.rule_profiles import (
    RuleProfileError,
    build_rule_profile,
    dump_rule_profile,
    load_rule_profile,
)
from rowspect.ui import column_display_label, display_dataframe
from rowspect.validation import ValidationRuleError, normalize_rule, validate_dataframe

st.set_page_config(page_title="RowSpect", page_icon="🔎", layout="wide")

st.markdown(
    """
<style>
.block-container { max-width: 1220px; padding-top: 2.1rem; padding-bottom: 4rem; }
[data-testid="stMetricValue"] { font-size: 1.7rem; }
.rowspect-hero { padding: 0.2rem 0 0.7rem; }
.rowspect-kicker { color: #667085; font-size: 0.92rem; margin-bottom: 0.2rem; }
.rowspect-title { font-size: 2.35rem; line-height: 1.08; font-weight: 750; letter-spacing: -0.035em; margin: 0; }
.rowspect-subtitle { color: #667085; font-size: 1.05rem; max-width: 820px; margin-top: 0.55rem; }
</style>
<div class="rowspect-hero">
  <div class="rowspect-kicker">LOCAL-FIRST DATA QUALITY</div>
  <div class="rowspect-title">RowSpect</div>
  <div class="rowspect-subtitle">Inspect, validate, and safely clean CSV and Excel files with explainable quality checks, reusable rules, and explicit type conversions—without sending the dataset to a RowSpect backend.</div>
</div>
""",
    unsafe_allow_html=True,
)

with st.sidebar:
    st.header("Analyze a dataset")
    uploaded = st.file_uploader(
        "CSV or Excel",
        type=["csv", "xlsx"],
        help=f"RowSpect accepts .csv and .xlsx files up to {MAX_FILE_BYTES // (1024 * 1024)} MB.",
    )
    use_sample = st.checkbox("Use the built-in sample", value=False, disabled=uploaded is not None)
    st.caption("Files are processed in the current Streamlit process. RowSpect contains no telemetry or upload backend.")

if uploaded is not None:
    file_bytes = uploaded.getvalue()
    source_name = uploaded.name
elif use_sample:
    sample_path = Path(__file__).parent / "sample_data" / "messy_customers.csv"
    file_bytes = sample_path.read_bytes()
    source_name = sample_path.name
else:
    left, right = st.columns([1.2, 0.8])
    with left:
        st.subheader("What RowSpect checks")
        st.markdown(
            """
- missing cells and blank strings
- exact duplicate rows
- duplicate and all-missing columns
- constant columns
- numbers stored as text
- IQR-based potential numeric outliers
- reusable required/unique/range/allowed-value/regex/date rules
"""
        )
    with right:
        st.subheader("What RowSpect can produce")
        st.markdown(
            """
- cleaned CSV and Excel files
- standalone HTML quality report
- machine-readable JSON profile
- reusable validation/conversion profile JSON
"""
        )
    st.info("Upload a dataset from the sidebar or enable the built-in sample to try RowSpect immediately.")
    st.stop()

sheet_name = None
if Path(source_name).suffix.lower() == ".xlsx":
    try:
        sheets = get_excel_sheets(file_bytes)
        sheet_name = st.sidebar.selectbox("Worksheet", sheets)
    except RowSpectIOError as exc:
        st.error(str(exc))
        st.stop()

try:
    dataframe = load_table(file_bytes, source_name, sheet_name=sheet_name)
except RowSpectIOError as exc:
    st.error(str(exc))
    st.stop()

profile = profile_dataframe(dataframe)
report_html = build_html_report(profile, source_name)

st.session_state.setdefault("rowspect_rules", [])
st.session_state.setdefault("rowspect_conversions", [])
st.session_state.setdefault("rowspect_profile_name", "My RowSpect profile")
st.session_state.setdefault("rowspect_profile_description", "")

st.caption(
    f"Source: **{source_name}**"
    + (f" · sheet: **{sheet_name}**" if sheet_name else "")
    + f" · {len(file_bytes) / 1024:.1f} KB"
)

metric_columns = st.columns(6)
metric_columns[0].metric(f"Quality · {profile['quality_label']}", f"{profile['quality_score']}/100")
metric_columns[1].metric("Rows", f"{profile['rows']:,}")
metric_columns[2].metric("Columns", f"{profile['columns_count']:,}")
metric_columns[3].metric("Missing", f"{profile['missing_pct']}%")
metric_columns[4].metric("Duplicates", f"{profile['duplicate_rows']:,}")
metric_columns[5].metric("Review signals", f"{profile['issue_count']:,}")

if profile["critical_count"]:
    st.error(f"{profile['critical_count']} critical structural issue(s) should be reviewed before using this dataset downstream.")
elif profile["warning_count"]:
    st.warning(f"{profile['warning_count']} warning(s) found. The dataset is usable for review, but cleanup may be needed.")
else:
    st.success("No critical or warning-level issues were detected by the generic quality checks.")

(
    overview_tab,
    issues_tab,
    columns_tab,
    explore_tab,
    validate_tab,
    convert_tab,
    clean_tab,
    export_tab,
) = st.tabs(["Overview", "Issues", "Columns", "Explore", "Validate", "Convert", "Clean", "Export"])

with overview_tab:
    left, right = st.columns([1.45, 0.55])
    with left:
        st.subheader("Data preview")
        st.dataframe(display_dataframe(dataframe.head(100)), width="stretch", height=390)
        st.caption("Showing up to the first 100 rows. RowSpect analyzes the complete loaded sheet.")
    with right:
        st.subheader("Issue mix")
        st.metric("Critical", profile["critical_count"])
        st.metric("Warnings", profile["warning_count"])
        st.metric("Informational", profile["info_count"])

    missing = missingness_table(profile)
    if not missing.empty:
        st.subheader("Missing values by column")
        chart = missing.set_index("column")[["missing_pct"]]
        st.bar_chart(chart)
    else:
        st.info("No missing values were detected.")

    with st.expander("How the quality score is calculated"):
        st.write(
            "The score starts at 100 and applies bounded deductions for missing cells, duplicate rows, blank strings, "
            "constant columns, potential IQR outliers, and structural problems. It is a review aid—not a guarantee that data is correct."
        )
        component_df = pd.DataFrame(
            [
                {"component": key.replace("_", " ").title(), "penalty": value}
                for key, value in profile["score_components"].items()
            ]
        )
        st.dataframe(display_dataframe(component_df), hide_index=True, width="stretch")

with issues_tab:
    st.subheader("Detected review signals")
    severities = ["critical", "warning", "info"]
    selected = st.multiselect("Show severities", severities, default=severities)
    visible = [issue for issue in profile["issues"] if issue["severity"] in selected]
    if visible:
        st.dataframe(display_dataframe(pd.DataFrame(visible)), width="stretch", hide_index=True)
    else:
        st.success("No issues match the selected severity filters.")
    st.caption("Potential outliers and inferred type hints are review signals, not automatic errors.")

with columns_tab:
    st.subheader("Column profile")
    column_profile = pd.DataFrame(profile["columns"])
    st.dataframe(display_dataframe(column_profile), width="stretch", hide_index=True, height=460)

    if profile["columns"]:
        column_positions = list(range(len(profile["columns"])))
        selected_position = st.selectbox(
            "Inspect one column",
            column_positions,
            format_func=lambda idx: f"{idx + 1} · {profile['columns'][idx]['column']}",
        )
        detail = profile["columns"][selected_position]
        details = st.columns(5)
        details[0].metric("Type", detail["dtype"])
        details[1].metric("Missing", f"{detail['missing_pct']}%")
        details[2].metric("Unique", f"{detail['unique_count']:,}")
        details[3].metric("Top frequency", f"{detail['top_frequency']:,}")
        details[4].metric("Outliers", f"{detail['outlier_count']:,}")

with explore_tab:
    numeric_positions = [
        idx
        for idx in range(dataframe.shape[1])
        if pd.api.types.is_numeric_dtype(dataframe.iloc[:, idx].dtype)
        and not pd.api.types.is_bool_dtype(dataframe.iloc[:, idx].dtype)
    ]
    text_positions = [
        idx
        for idx in range(dataframe.shape[1])
        if pd.api.types.is_object_dtype(dataframe.iloc[:, idx].dtype)
        or pd.api.types.is_string_dtype(dataframe.iloc[:, idx].dtype)
        or isinstance(dataframe.iloc[:, idx].dtype, pd.CategoricalDtype)
    ]

    if numeric_positions:
        st.subheader("Numeric distribution")
        numeric_position = st.selectbox(
            "Numeric column",
            numeric_positions,
            key="numeric_explore",
            format_func=lambda idx: f"{idx + 1} · {dataframe.columns[idx]}",
        )
        numeric_series = dataframe.iloc[:, numeric_position]
        histogram = numeric_histogram(numeric_series)
        if not histogram.empty:
            st.bar_chart(histogram.set_index("range"))
        selected_detail = profile["columns"][numeric_position]
        stats = st.columns(5)
        stats[0].metric("Min", selected_detail["min"] if selected_detail["min"] is not None else "—")
        stats[1].metric("Median", selected_detail["median"] if selected_detail["median"] is not None else "—")
        stats[2].metric("Mean", round(selected_detail["mean"], 3) if isinstance(selected_detail["mean"], float) else selected_detail["mean"] or "—")
        stats[3].metric("Max", selected_detail["max"] if selected_detail["max"] is not None else "—")
        stats[4].metric("IQR outliers", selected_detail["outlier_count"])

        corr = correlation_matrix(dataframe)
        if not corr.empty:
            st.subheader("Numeric correlation")
            st.dataframe(display_dataframe(corr), width="stretch")
            st.caption("Pearson correlation for up to the first 20 numeric columns.")
    else:
        st.info("No numeric columns are available for distribution or correlation analysis.")

    if text_positions:
        st.subheader("Top text values")
        text_position = st.selectbox(
            "Text column",
            text_positions,
            key="text_explore",
            format_func=lambda idx: f"{idx + 1} · {dataframe.columns[idx]}",
        )
        values = top_values(dataframe.iloc[:, text_position])
        if not values.empty:
            st.bar_chart(values.set_index("value"))

with validate_tab:
    st.subheader("Custom validation")
    st.caption("Define what good data means for this file, then save the checks as a reusable JSON profile.")

    uploaded_profile = st.file_uploader(
        "Load a RowSpect rule profile",
        type=["json"],
        key="rules_profile_upload",
        help="Profiles contain validation rules and optional explicit type-conversion plans, but never source data.",
    )
    if uploaded_profile is not None:
        try:
            loaded_profile = load_rule_profile(uploaded_profile.getvalue())
            st.success(
                f"Loaded '{loaded_profile['name']}' · {len(loaded_profile['rules'])} rule(s) · "
                f"{len(loaded_profile['conversions'])} conversion(s)."
            )
            if st.button("Use loaded profile in this session"):
                st.session_state["rowspect_rules"] = loaded_profile["rules"]
                st.session_state["rowspect_conversions"] = loaded_profile["conversions"]
                st.session_state["rowspect_profile_name"] = loaded_profile["name"]
                st.session_state["rowspect_profile_description"] = loaded_profile["description"]
                st.rerun()
        except RuleProfileError as exc:
            st.error(str(exc))

    profile_name = st.text_input("Profile name", key="rowspect_profile_name")
    st.text_input("Profile description (optional)", key="rowspect_profile_description")

    st.markdown("#### Add a validation rule")
    rule_columns = st.columns([1.1, 1.2, 0.75])
    with rule_columns[0]:
        rule_type = st.selectbox(
            "Rule",
            ["required", "unique", "range", "allowed_values", "regex", "date"],
            format_func=lambda value: value.replace("_", " ").title(),
        )
    with rule_columns[1]:
        rule_position = st.selectbox(
            "Column",
            list(range(dataframe.shape[1])),
            key="rule_column_position",
            format_func=lambda idx: f"{idx + 1} · {column_display_label(dataframe.columns[idx], idx + 1)}",
        )
    with rule_columns[2]:
        rule_severity = st.selectbox("Severity", ["warning", "critical", "info"])

    rule_column = str(dataframe.columns[rule_position])
    rule_column_count = sum(str(column) == rule_column for column in dataframe.columns)
    rule_column_valid = bool(rule_column.strip()) and rule_column_count == 1
    if not rule_column_valid:
        st.warning("Rules require a unique, non-blank column name. Rename this column before attaching a reusable rule to it.")

    rule_payload: dict = {
        "id": f"{rule_type}-{uuid4().hex[:8]}",
        "type": rule_type,
        "column": rule_column,
        "severity": rule_severity,
    }

    if rule_type == "range":
        bounds = st.columns(2)
        with bounds[0]:
            use_min = st.checkbox("Set minimum", value=True, key="rule_use_min")
            minimum = st.number_input("Minimum", value=0.0, disabled=not use_min, key="rule_min")
        with bounds[1]:
            use_max = st.checkbox("Set maximum", value=True, key="rule_use_max")
            maximum = st.number_input("Maximum", value=100.0, disabled=not use_max, key="rule_max")
        if use_min:
            rule_payload["min"] = minimum
        if use_max:
            rule_payload["max"] = maximum
    elif rule_type == "allowed_values":
        allowed_text = st.text_area(
            "Allowed values (one per line)",
            key="rule_allowed_values",
            placeholder="AL\nGA\nFL",
        )
        raw_values = [value.strip() for value in allowed_text.splitlines() if value.strip()]
        selected_series = dataframe.iloc[:, rule_position]
        if pd.api.types.is_numeric_dtype(selected_series.dtype):
            parsed_values = []
            for value in raw_values:
                try:
                    number = float(value)
                    parsed_values.append(int(number) if number.is_integer() else number)
                except ValueError:
                    parsed_values.append(value)
            rule_payload["values"] = parsed_values
        else:
            rule_payload["values"] = raw_values
    elif rule_type == "regex":
        rule_payload["pattern"] = st.text_input(
            "Full-match regular expression",
            key="rule_regex",
            placeholder=r"[^@\s]+@[^@\s]+\.[^@\s]+",
        )
    elif rule_type == "date":
        date_format = st.text_input(
            "Date format (optional)",
            key="rule_date_format",
            placeholder="%Y-%m-%d",
        )
        if date_format.strip():
            rule_payload["format"] = date_format.strip()

    if st.button("Add validation rule", disabled=not rule_column_valid):
        try:
            normalized = normalize_rule(rule_payload, position=len(st.session_state["rowspect_rules"]))
            st.session_state["rowspect_rules"] = [*st.session_state["rowspect_rules"], normalized]
            st.success("Rule added.")
            st.rerun()
        except ValidationRuleError as exc:
            st.error(str(exc))

    current_rules = st.session_state["rowspect_rules"]
    if current_rules:
        st.markdown("#### Current rules")
        rules_table = pd.DataFrame(current_rules)
        st.dataframe(display_dataframe(rules_table), hide_index=True, width="stretch")
        controls = st.columns(2)
        if controls[0].button("Remove last rule"):
            st.session_state["rowspect_rules"] = current_rules[:-1]
            st.rerun()
        if controls[1].button("Clear rules"):
            st.session_state["rowspect_rules"] = []
            st.rerun()

        validation = validate_dataframe(dataframe, current_rules)
        metrics = st.columns(4)
        metrics[0].metric("Rules", validation["rule_count"])
        metrics[1].metric("Passing", validation["passed_rule_count"])
        metrics[2].metric("Failing", validation["failing_rule_count"])
        metrics[3].metric("Violating rows", validation["violating_row_count"])

        if validation["validation_passed"]:
            st.success("This dataset passes every configured validation rule.")
        else:
            st.warning(
                f"{validation['failing_rule_count']} configured rule(s) need attention; "
                f"{validation['violation_count']} total rule violation(s) were found."
            )

        result_rows = []
        for result in validation["results"]:
            row = dict(result)
            row["row_numbers"] = ", ".join(str(value) for value in row.get("row_numbers", []))
            result_rows.append(row)
        st.dataframe(display_dataframe(pd.DataFrame(result_rows)), hide_index=True, width="stretch")
        st.caption("Reported row numbers use spreadsheet/CSV-style numbering: header is row 1, first data row is row 2.")
        st.download_button(
            "Download validation results JSON",
            data=json.dumps(validation, indent=2, ensure_ascii=False).encode("utf-8"),
            file_name=f"{Path(source_name).stem}-rowspect-validation.json",
            mime="application/json",
        )
    else:
        st.info("Add a rule or load a saved profile to validate this dataset against business-specific expectations.")

    try:
        reusable_profile = build_rule_profile(
            profile_name,
            description=st.session_state["rowspect_profile_description"],
            rules=st.session_state["rowspect_rules"],
            conversions=st.session_state["rowspect_conversions"],
        )
        st.download_button(
            "Download reusable rule profile",
            data=dump_rule_profile(reusable_profile),
            file_name="rowspect-rules.json",
            mime="application/json",
            help="Save this file and load it the next time you receive the same kind of dataset.",
        )
    except RuleProfileError as exc:
        st.error(str(exc))

with convert_tab:
    st.subheader("Safe type conversion")
    st.caption("RowSpect previews conversions and blocks them when any non-empty value cannot be converted. Nothing is changed silently.")

    conversion_columns = st.columns([1.2, 1.0])
    with conversion_columns[0]:
        conversion_position = st.selectbox(
            "Column to convert",
            list(range(dataframe.shape[1])),
            key="conversion_column_position",
            format_func=lambda idx: f"{idx + 1} · {column_display_label(dataframe.columns[idx], idx + 1)}",
        )
    with conversion_columns[1]:
        target_type = st.selectbox(
            "Target type",
            sorted(SUPPORTED_TARGET_TYPES),
            format_func=str.title,
        )

    conversion_column = str(dataframe.columns[conversion_position])
    conversion_column_count = sum(str(column) == conversion_column for column in dataframe.columns)
    conversion_column_valid = bool(conversion_column.strip()) and conversion_column_count == 1
    if not conversion_column_valid:
        st.warning("Safe conversion requires a unique, non-blank column name.")

    try:
        conversion_analysis = analyze_type_conversion(dataframe.iloc[:, conversion_position], target_type)
        conversion_metrics = st.columns(4)
        conversion_metrics[0].metric("Source type", conversion_analysis["source_dtype"])
        conversion_metrics[1].metric("Convertible", conversion_analysis["convertible_count"])
        conversion_metrics[2].metric("Blocked values", conversion_analysis["failure_count"])
        conversion_metrics[3].metric("Would change", conversion_analysis["changed_count"])
        if conversion_analysis["failure_examples"]:
            st.warning("Examples that cannot be safely converted: " + ", ".join(conversion_analysis["failure_examples"]))
        elif conversion_column_valid:
            st.success(f"All non-empty values can be converted to {target_type} safely.")
    except ConversionError as exc:
        st.error(str(exc))
        conversion_analysis = None

    if st.button("Add conversion to plan", disabled=not conversion_column_valid):
        plan = {
            "id": f"conversion-{uuid4().hex[:8]}",
            "column": conversion_column,
            "target_type": target_type,
        }
        existing = [item for item in st.session_state["rowspect_conversions"] if item["column"] != conversion_column]
        st.session_state["rowspect_conversions"] = [*existing, plan]
        st.success("Conversion added to the working plan.")
        st.rerun()

    conversion_plans = st.session_state["rowspect_conversions"]
    converted_dataframe = dataframe
    conversion_results: list[dict] = []
    conversions_safe = False
    if conversion_plans:
        st.markdown("#### Planned conversions")
        st.dataframe(display_dataframe(pd.DataFrame(conversion_plans)), hide_index=True, width="stretch")
        if st.button("Clear conversion plan"):
            st.session_state["rowspect_conversions"] = []
            st.rerun()

        converted_dataframe, conversion_results = apply_type_conversions(
            dataframe,
            conversion_plans,
            strict=True,
        )
        conversions_safe = all(result.get("applied") for result in conversion_results)
        st.dataframe(display_dataframe(pd.DataFrame(conversion_results)), hide_index=True, width="stretch")
        if conversions_safe:
            st.success("Every planned conversion is safe to apply to a downloadable working copy.")
            st.dataframe(display_dataframe(converted_dataframe.head(100)), width="stretch", height=330)
            convert_dl = st.columns(2)
            with convert_dl[0]:
                st.download_button(
                    "Download converted CSV",
                    data=dataframe_to_csv(converted_dataframe),
                    file_name=f"{Path(source_name).stem}-rowspect-converted.csv",
                    mime="text/csv",
                    width="stretch",
                )
            with convert_dl[1]:
                st.download_button(
                    "Download converted Excel",
                    data=dataframe_to_xlsx(converted_dataframe),
                    file_name=f"{Path(source_name).stem}-rowspect-converted.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    width="stretch",
                )
        else:
            st.warning("At least one planned conversion is blocked. RowSpect will not export a partially converted dataset from this tab.")
    else:
        st.info("Add one or more explicit conversions to create a typed working copy. The original upload is never modified.")

with clean_tab:
    st.subheader("Conservative cleanup")
    st.caption("RowSpect never imputes values or silently changes data types.")

    cleanup_source = dataframe
    if st.session_state["rowspect_conversions"]:
        conversion_candidate, cleanup_conversion_results = apply_type_conversions(
            dataframe,
            st.session_state["rowspect_conversions"],
            strict=True,
        )
        all_cleanup_conversions_safe = all(result.get("applied") for result in cleanup_conversion_results)
        use_converted_source = st.checkbox(
            "Apply the safe conversion plan before cleanup",
            value=all_cleanup_conversions_safe,
            disabled=not all_cleanup_conversions_safe,
        )
        if not all_cleanup_conversions_safe:
            st.warning("The current conversion plan contains blocked changes, so cleanup will use the original data.")
        elif use_converted_source:
            cleanup_source = conversion_candidate

    neutralize_formulas = st.checkbox(
        "Neutralize formula-like text in downloaded spreadsheets",
        value=True,
        help="Prefixes text beginning with =, +, -, or @ so spreadsheet apps treat it as literal text.",
    )
    option_cols = st.columns(2)
    with option_cols[0]:
        drop_duplicates = st.checkbox("Remove exact duplicate rows", value=True)
        trim_strings = st.checkbox("Trim leading/trailing text spaces", value=True)
    with option_cols[1]:
        normalize_blanks = st.checkbox("Convert blank strings to missing values", value=True)
        drop_empty_rows = st.checkbox("Remove completely empty rows", value=True)

    cleaned = clean_dataframe(
        cleanup_source,
        drop_duplicates=drop_duplicates,
        trim_strings=trim_strings,
        normalize_blank_strings=normalize_blanks,
        drop_empty_rows=drop_empty_rows,
    )
    summary = cleanup_summary(cleanup_source, cleaned)
    summary_cols = st.columns(4)
    summary_cols[0].metric("Rows removed", summary["rows_removed"])
    summary_cols[1].metric("Duplicates remaining", summary["duplicates_after"])
    summary_cols[2].metric("Blank strings before", summary["blank_strings_before"])
    summary_cols[3].metric("Blank strings after", summary["blank_strings_after"])
    st.dataframe(display_dataframe(cleaned.head(100)), width="stretch", height=390)

    dl1, dl2 = st.columns(2)
    with dl1:
        st.download_button(
            "Download cleaned CSV",
            data=dataframe_to_csv(cleaned, neutralize_formulas=neutralize_formulas),
            file_name=f"{Path(source_name).stem}-rowspect-clean.csv",
            mime="text/csv",
            width="stretch",
        )
    with dl2:
        st.download_button(
            "Download cleaned Excel",
            data=dataframe_to_xlsx(cleaned, neutralize_formulas=neutralize_formulas),
            file_name=f"{Path(source_name).stem}-rowspect-clean.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            width="stretch",
        )

with export_tab:
    st.subheader("Export the analysis")
    st.write("Share the standalone HTML report, archive the JSON profile, or inspect both without exposing the original dataset.")
    ex1, ex2 = st.columns(2)
    with ex1:
        st.download_button(
            "Download HTML report",
            data=report_html.encode("utf-8"),
            file_name=f"{Path(source_name).stem}-rowspect-report.html",
            mime="text/html",
            width="stretch",
        )
    with ex2:
        st.download_button(
            "Download JSON profile",
            data=json.dumps(profile, indent=2, ensure_ascii=False).encode("utf-8"),
            file_name=f"{Path(source_name).stem}-rowspect-profile.json",
            mime="application/json",
            width="stretch",
        )
    st.caption("The generic exported profile contains aggregate quality results and column statistics, not the full source dataset.")
