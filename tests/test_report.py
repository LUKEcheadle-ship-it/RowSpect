import pandas as pd

from rowspect.profile import profile_dataframe
from rowspect.report import build_html_report


def test_html_report_escapes_source_and_values():
    df = pd.DataFrame({"name": ["<script>alert(1)</script>", None]})
    profile = profile_dataframe(df)
    html = build_html_report(profile, "<bad>.csv")
    assert "<bad>.csv" not in html
    assert "&lt;bad&gt;.csv" in html
    assert "RowSpect data quality report" in html
    assert "Score deductions" in html


def test_html_report_contains_issue_severity_classes():
    profile = profile_dataframe(pd.DataFrame({"empty": [None, None]}))
    html = build_html_report(profile, "x.csv")
    assert "sev critical" in html
