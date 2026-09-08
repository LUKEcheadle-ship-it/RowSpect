from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
import streamlit as st

from rowspect.clean import clean_dataframe, cleanup_summary
from rowspect.export import dataframe_to_csv, dataframe_to_xlsx
from rowspect.insights import correlation_matrix, missingness_table, numeric_histogram, top_values
from rowspect.io import MAX_FILE_BYTES, RowSpectIOError, get_excel_sheets, load_table
from rowspect.profile import profile_dataframe
from rowspect.report import build_html_report
from rowspect.ui import display_dataframe

st.set_page_config(page_title="RowSpect", page_icon="🔎", layout="wide")

st.markdown(
    """
<style>
.block-container { max-width: 1220px; padding-top: 2.1rem; padding-bottom: 4rem; }
[data-testid="stMetricValue"] { font-size: 1.7rem; }
.rowspect-hero { padding: 0.2rem 0 0.7rem; }
.rowspect-kicker { color: #667085; font-size: 0.92rem; margin-bottom: 0.2rem; }
.rowspect-title { font-size: 2.35rem; line-height: 1.08; font-weight: 750; letter-spacing: -0.035em; margin: 0; }
.rowspect-subtitle { color: #667085; font-size: 1.05rem; max-width: 760px; margin-top: 0.55rem; }
</style>
<div class="rowspect-hero">
  <div class="rowspect-kicker">LOCAL-FIRST DATA QUALITY</div>
  <div class="rowspect-title">RowSpect</div>
  <div class="rowspect-subtitle">Inspect CSV and Excel files for missing values, duplicates, suspicious types, constants, and numeric outliers—without sending the dataset to a RowSpect backend.</div>
</div>
""",
    unsafe_allow_html=True,
)

with st.sidebar:
    st.header("Analyze a dataset")
    uploaded = st.file_uploader(
        "CSV or Excel",
        type=["csv", "xlsx"],
        help=f"V1 accepts .csv and .xlsx files up to {MAX_FILE_BYTES // (1024 * 1024)} MB.",
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
        st.subheader("What V1 checks")
        st.markdown(
            """
- missing cells and blank strings
- exact duplicate rows
- duplicate and all-missing columns
- constant columns
- numbers stored as text
- IQR-based potential numeric outliers
- per-column cardinality and summary statistics
"""
        )
    with right:
        st.subheader("What V1 exports")
        st.markdown(
            """
- standalone HTML quality report
- machine-readable JSON profile
- cleaned CSV
- cleaned Excel workbook
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
    st.success("No critical or warning-level issues were detected by the current V1 checks.")

(
    overview_tab,
    issues_tab,
    columns_tab,
    explore_tab,
    clean_tab,
    export_tab,
) = st.tabs(["Overview", "Issues", "Columns", "Explore", "Clean", "Export"])

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

with clean_tab:
    st.subheader("Conservative cleanup")
    st.caption("RowSpect never imputes values or silently changes data types in V1.")
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
        dataframe,
        drop_duplicates=drop_duplicates,
        trim_strings=trim_strings,
        normalize_blank_strings=normalize_blanks,
        drop_empty_rows=drop_empty_rows,
    )
    summary = cleanup_summary(dataframe, cleaned)
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
    st.caption("The exported profile contains aggregate quality results and column statistics, not the full source dataset.")
