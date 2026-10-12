"""Exercise the real Streamlit app with independent workbook inputs."""
from io import BytesIO
from pathlib import Path
from unittest.mock import patch

import pandas as pd
from streamlit.testing.v1 import AppTest


ROOT = Path(__file__).resolve().parents[1]


class Upload(BytesIO):
    def __init__(self, name, contents):
        super().__init__(contents)
        self.name = name


def workbook(sheets):
    contents = BytesIO()
    with pd.ExcelWriter(contents, engine="openpyxl") as writer:
        for name, values in sheets.items():
            pd.DataFrame({"id": values}).to_excel(writer, sheet_name=name, index=False)
    return contents.getvalue()


def run_app(primary, baseline):
    def upload(label, *args, **kwargs):
        return {"CSV or Excel": primary, "Previous baseline (optional)": baseline}.get(label)
    with patch("streamlit.file_uploader", side_effect=upload):
        app = AppTest.from_file(str(ROOT / "app.py"), default_timeout=20).run()
    assert not app.exception, [e.message for e in app.exception]
    return app


def test_different_workbook_sheet_names_compare_without_error():
    app = run_app(Upload("current.xlsx", workbook({"October": [1, 2, 3]})),
                  Upload("previous.xlsx", workbook({"September": [1, 2]})))
    assert not any("Baseline could not be compared" in e.value for e in app.error)
    assert any(m.label == "Rows changed" and m.value == "+1" for m in app.metric)
    assert next(s for s in app.selectbox if s.label == "Baseline worksheet").value == "September"


def test_baseline_has_its_own_selectable_worksheet():
    primary = Upload("current.xlsx", workbook({"Current": [1, 2, 3]}))
    baseline = Upload("previous.xlsx", workbook({"Old": [1], "Archive": [1, 2]}))
    app = run_app(primary, baseline)
    select = next(s for s in app.selectbox if s.label == "Baseline worksheet")
    assert select.options == ["Old", "Archive"]
    with patch("streamlit.file_uploader", side_effect=lambda label, *a, **kw: {
        "CSV or Excel": primary, "Previous baseline (optional)": baseline}.get(label)):
        select.select("Archive").run()
    assert not app.exception
    assert any(m.label == "Rows changed" and m.value == "+1" for m in app.metric)


def test_csv_baseline_does_not_inherit_xlsx_sheet():
    app = run_app(Upload("current.xlsx", workbook({"Named": [1, 2]})),
                  Upload("previous.csv", b"id\n1\n"))
    assert not any(s.label == "Baseline worksheet" for s in app.selectbox)
    assert any(m.label == "Rows changed" and m.value == "+1" for m in app.metric)


def test_csv_primary_can_select_a_baseline_xlsx_sheet():
    app = run_app(Upload("current.csv", b"id\n1\n2\n"),
                  Upload("previous.xlsx", workbook({"Historical": [1]})))
    assert next(s for s in app.selectbox if s.label == "Baseline worksheet").value == "Historical"
    assert any(m.label == "Rows changed" and m.value == "+1" for m in app.metric)


def test_numeric_sheet_name_is_a_name_not_an_index():
    app = run_app(Upload("current.xlsx", workbook({"Current": [1, 2, 3]})),
                  Upload("previous.xlsx", workbook({"0": [1, 2]})))
    assert next(s for s in app.selectbox if s.label == "Baseline worksheet").value == "0"
    assert any(m.label == "Rows changed" and m.value == "+1" for m in app.metric)


def test_corrupt_baseline_does_not_crash_current_analysis():
    app = run_app(Upload("current.csv", b"id\n1\n2\n"),
                  Upload("previous.xlsx", b"not a workbook"))
    assert any("Baseline could not be compared" in e.value for e in app.error)
    assert any(m.label == "Rows" and m.value == "2" for m in app.metric)
