from io import BytesIO

import pandas as pd

from rowspect.export import dataframe_to_csv, dataframe_to_xlsx, export_safe_dataframe


def test_xlsx_export_round_trips():
    source = pd.DataFrame({"name": ["A", "B"], "value": [1, 2]})
    payload = dataframe_to_xlsx(source)
    assert payload[:2] == b"PK"
    loaded = pd.read_excel(BytesIO(payload), engine="openpyxl")
    pd.testing.assert_frame_equal(loaded, source)


def test_formula_like_text_is_neutralized_without_mutating_input():
    source = pd.DataFrame({"text": ["=1+1", "+SUM(A1:A2)", "safe"], "number": [1, 2, 3]})
    snapshot = source.copy(deep=True)
    safe = export_safe_dataframe(source)
    pd.testing.assert_frame_equal(source, snapshot)
    assert safe["text"].tolist() == ["'=1+1", "'+SUM(A1:A2)", "safe"]
    assert safe["number"].tolist() == [1, 2, 3]


def test_csv_export_can_preserve_formula_text_when_explicitly_requested():
    source = pd.DataFrame({"text": ["=1+1"]})
    safe = dataframe_to_csv(source).decode("utf-8")
    raw = dataframe_to_csv(source, neutralize_formulas=False).decode("utf-8")
    assert "'=1+1" in safe
    assert "=1+1" in raw and "'=1+1" not in raw
