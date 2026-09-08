"""RowSpect: local-first data quality profiling for tabular data."""

from .clean import clean_dataframe
from .profile import profile_dataframe
from .report import build_html_report

__all__ = ["profile_dataframe", "clean_dataframe", "build_html_report"]
__version__ = "0.1.0"
