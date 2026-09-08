from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
import streamlit as st

from rowspect.clean import clean_dataframe
from rowspect.io import get_excel_sheets, load_table
from rowspect.profile import profile_dataframe
from rowspect.report import build_html_report

st.set_page_config(page_title="RowSpect", page_icon="🔎", layout="wide")

st.title("RowSpect")
st.caption("Local-first data quality profiling for CSV and Excel files.")
st.info("Your file is processed in this Streamlit session. RowSpect does not contain any upload or telemetry code.")

uploaded = st.file_uploader("Choose a CSV or Excel file", type=["csv", "xlsx"])

if uploaded is None:
    st.markdown(
        """
### What RowSpect checks
- missing and blank values
- duplicate rows
- column types and cardinality
- constant columns
- possible numbers stored as text
- IQR-based numeric outliers

Upload a file to generate a quality score, inspect issues, and export a standalone HTML report.
"""
    )
    st.stop()

file_bytes = uploaded.getvalue()
sheet_name = None
if Path(uploaded.name).suffix.lower() == ".xlsx":
    try:
        sheets = get_excel_sheets(file_bytes)
        sheet_name = st.selectbox("Excel sheet", sheets)
    except Exception as exc:
        st.error(f"Could not read workbook sheets: {exc}")
        st.stop()

try:
    dataframe = load_table(file_bytes, uploaded.name, sheet_name=sheet_name)
except Exception as exc:
    st.error(f"Could not read this file: {exc}")
    st.stop()

profile = profile_dataframe(dataframe)
report_html = build_html_report(profile, uploaded.name)

metric_columns = st.columns(5)
metric_columns[0].metric("Quality score", f"{profile['quality_score']}/100")
metric_columns[1].metric("Rows", f"{profile['rows']:,}")
metric_columns[2].metric("Columns", profile["columns_count"])
metric_columns[3].metric("Missing", f"{profile['missing_pct']}%")
metric_columns[4].metric("Duplicates", profile["duplicate_rows"])

overview_tab, issues_tab, columns_tab, clean_tab, export_tab = st.tabs(
    ["Overview", "Issues", "Columns", "Clean", "Export"]
)

with overview_tab:
    st.subheader("Preview")
    st.dataframe(dataframe.head(100), use_container_width=True)

    missing = pd.DataFrame(profile["columns"])[["column", "missing_pct"]].set_index("column")
    if not missing.empty and float(missing["missing_pct"].max()) > 0:
        st.subheader("Missing values by column")
        st.bar_chart(missing)

    numeric_columns = dataframe.select_dtypes(include="number").columns.tolist()
    if numeric_columns:
        st.subheader("Numeric summary")
        st.dataframe(dataframe[numeric_columns].describe().T, use_container_width=True)

with issues_tab:
    st.subheader(f"Detected issues ({profile['issue_count']})")
    if profile["issues"]:
        st.dataframe(pd.DataFrame(profile["issues"]), use_container_width=True, hide_index=True)
    else:
        st.success("No issues detected by the current checks.")
    st.caption("Outliers and type hints are review signals, not automatic errors.")

with columns_tab:
    column_profile = pd.DataFrame(profile["columns"])
    st.dataframe(column_profile, use_container_width=True, hide_index=True)

with clean_tab:
    st.subheader("Conservative cleanup")
    st.caption("RowSpect does not impute values or silently change column data types.")
    drop_duplicates = st.checkbox("Remove duplicate rows", value=True)
    trim_strings = st.checkbox("Trim leading/trailing spaces in text", value=True)
    normalize_blanks = st.checkbox("Convert blank strings to missing values", value=True)
    drop_empty_rows = st.checkbox("Remove completely empty rows", value=True)

    cleaned = clean_dataframe(
        dataframe,
        drop_duplicates=drop_duplicates,
        trim_strings=trim_strings,
        normalize_blank_strings=normalize_blanks,
        drop_empty_rows=drop_empty_rows,
    )
    st.write(f"Result: **{len(cleaned):,} rows × {cleaned.shape[1]} columns**")
    st.dataframe(cleaned.head(100), use_container_width=True)
    st.download_button(
        "Download cleaned CSV",
        data=cleaned.to_csv(index=False).encode("utf-8"),
        file_name=f"{Path(uploaded.name).stem}-rowspect-clean.csv",
        mime="text/csv",
    )

with export_tab:
    st.subheader("Export analysis")
    st.download_button(
        "Download HTML report",
        data=report_html.encode("utf-8"),
        file_name=f"{Path(uploaded.name).stem}-rowspect-report.html",
        mime="text/html",
    )
    st.download_button(
        "Download JSON profile",
        data=json.dumps(profile, indent=2, ensure_ascii=False).encode("utf-8"),
        file_name=f"{Path(uploaded.name).stem}-rowspect-profile.json",
        mime="application/json",
    )
