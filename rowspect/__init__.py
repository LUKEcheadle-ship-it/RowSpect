"""RowSpect public API."""

from rowspect.clean import clean_dataframe, cleanup_summary
from rowspect.export import dataframe_to_csv, dataframe_to_xlsx, export_safe_dataframe
from rowspect.io import RowSpectIOError, get_excel_sheets, load_table
from rowspect.profile import profile_dataframe
from rowspect.report import build_html_report

__all__ = [
    "RowSpectIOError",
    "build_html_report",
    "clean_dataframe",
    "cleanup_summary",
    "dataframe_to_csv",
    "dataframe_to_xlsx",
    "export_safe_dataframe",
    "get_excel_sheets",
    "load_table",
    "profile_dataframe",
]

__version__ = "1.1.0"
