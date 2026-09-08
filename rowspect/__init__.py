"""RowSpect public API."""

from rowspect.clean import clean_dataframe, cleanup_summary
from rowspect.conversion import (
    ConversionError,
    analyze_type_conversion,
    apply_type_conversions,
)
from rowspect.export import dataframe_to_csv, dataframe_to_xlsx, export_safe_dataframe
from rowspect.io import RowSpectIOError, get_excel_sheets, load_table
from rowspect.profile import profile_dataframe
from rowspect.report import build_html_report
from rowspect.rule_profiles import (
    RuleProfileError,
    build_rule_profile,
    dump_rule_profile,
    load_rule_profile,
)
from rowspect.validation import ValidationRuleError, validate_dataframe

__all__ = [
    "ConversionError",
    "RowSpectIOError",
    "RuleProfileError",
    "ValidationRuleError",
    "analyze_type_conversion",
    "apply_type_conversions",
    "build_html_report",
    "build_rule_profile",
    "clean_dataframe",
    "cleanup_summary",
    "dataframe_to_csv",
    "dataframe_to_xlsx",
    "dump_rule_profile",
    "export_safe_dataframe",
    "get_excel_sheets",
    "load_rule_profile",
    "load_table",
    "profile_dataframe",
    "validate_dataframe",
]

__version__ = "1.2.0"
