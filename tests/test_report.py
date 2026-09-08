import pandas as pd

from rowspect.profile import profile_dataframe
from rowspect.report import build_html_report


def test_html_report_escapes_source_name_and_contains_summary():
    profile = profile_dataframe(pd.DataFrame({"a": [1, None]}))
    report = build_html_report(profile, "<private>.csv")
    assert "RowSpect data quality report" in report
    assert "&lt;private&gt;.csv" in report
    assert "Quality score / 100" in report
