"""RowSpect public API."""

from rowspect.clean import clean_dataframe, cleanup_summary
from rowspect.conversion import (
    ConversionError,
    analyze_type_conversion,
    apply_type_conversions,
)
from rowspect.comparison import compare_dataframes, compare_profiles, comparison_json
from rowspect.export import (
    dataframe_to_csv,
    dataframe_to_failing_rows_csv,
    dataframe_to_xlsx,
    export_safe_dataframe,
)
from rowspect.io import RowSpectIOError, get_excel_sheets, load_table
from rowspect.profile import profile_dataframe
from rowspect.report import build_html_report
from rowspect.rule_profiles import (
    RuleProfileError,
    build_rule_profile,
    dump_rule_profile,
    load_rule_profile,
)
from rowspect.validation import ValidationRuleError, build_failing_rows, failing_rows_dataframe, validate_dataframe

__all__ = [
    "ConversionError",
    "RowSpectIOError",
    "RuleProfileError",
    "ValidationRuleError",
    "build_failing_rows",
    "compare_dataframes",
    "compare_profiles",
    "comparison_json",
    "analyze_type_conversion",
    "apply_type_conversions",
    "build_html_report",
    "build_rule_profile",
    "clean_dataframe",
    "cleanup_summary",
    "dataframe_to_csv",
    "dataframe_to_failing_rows_csv",
    "dataframe_to_xlsx",
    "dump_rule_profile",
    "export_safe_dataframe",
    "failing_rows_dataframe",
    "get_excel_sheets",
    "load_rule_profile",
    "load_table",
    "profile_dataframe",
    "validate_dataframe",
]

__version__ = "1.3.0"
