from io import BytesIO

import pandas as pd
import pytest

from rowspect.io import RowSpectIOError, get_excel_sheets, load_table, validate_upload


def test_load_comma_csv_from_bytes():
    df = load_table(b"a,b\n1,x\n2,y\n", "sample.csv")
    assert df.shape == (2, 2)
    assert df["a"].tolist() == [1, 2]


def test_load_semicolon_csv():
    df = load_table(b"a;b\n1;x\n2;y\n", "sample.csv")
    assert list(df.columns) == ["a", "b"]
    assert df.iloc[1, 1] == "y"


def test_load_latin1_csv():
    data = "name\nJos\xe9\n".encode("latin-1")
    df = load_table(data, "people.csv")
    assert df.iloc[0, 0] == "José"


def test_rejects_empty_upload():
    with pytest.raises(RowSpectIOError, match="empty"):
        load_table(b"", "sample.csv")


def test_rejects_unsupported_extension():
    with pytest.raises(RowSpectIOError, match="supports CSV"):
        validate_upload(b"x", "sample.txt")


def test_rejects_file_over_limit():
    with pytest.raises(RowSpectIOError, match="larger"):
        validate_upload(b"12345", "sample.csv", max_bytes=4)


def test_excel_sheet_discovery_and_loading():
    buffer = BytesIO()
    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        pd.DataFrame({"a": [1]}).to_excel(writer, sheet_name="First", index=False)
        pd.DataFrame({"b": [2]}).to_excel(writer, sheet_name="Second", index=False)
    data = buffer.getvalue()
    assert get_excel_sheets(data) == ["First", "Second"]
    df = load_table(data, "sample.xlsx", sheet_name="Second")
    assert list(df.columns) == ["b"]
    assert df.iloc[0, 0] == 2


def test_corrupt_excel_has_clean_error():
    with pytest.raises(RowSpectIOError, match="corrupt|malformed"):
        load_table(b"not-a-workbook", "sample.xlsx")


def test_header_only_csv_loads_and_profiles_later():
    df = load_table(b"a,b\n", "header.csv")
    assert df.shape == (0, 2)


def test_malformed_csv_has_clean_error():
    with pytest.raises(RowSpectIOError, match="inconsistent|malformed"):
        load_table(b"a,b\n1,2,3\n", "bad.csv")


def test_invalid_excel_sheet_has_specific_error():
    buffer = BytesIO()
    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        pd.DataFrame({"a": [1]}).to_excel(writer, sheet_name="Only", index=False)
    with pytest.raises(RowSpectIOError, match="Worksheet 'Missing' was not found"):
        load_table(buffer.getvalue(), "sample.xlsx", sheet_name="Missing")


def test_csv_duplicate_headers_are_preserved():
    df = load_table(b"a,a\n1,2\n", "duplicate.csv")
    assert list(df.columns) == ["a", "a"]


def test_xlsx_duplicate_headers_are_preserved():
    buffer = BytesIO()
    pd.DataFrame([[1, 2]], columns=["a", "a"]).to_excel(buffer, index=False, engine="openpyxl")
    df = load_table(buffer.getvalue(), "duplicate.xlsx")
    assert list(df.columns) == ["a", "a"]


def test_xlsx_archive_expansion_limit(monkeypatch):
    import rowspect.io as io_module

    buffer = BytesIO()
    pd.DataFrame({"a": [1, 2]}).to_excel(buffer, index=False, engine="openpyxl")
    monkeypatch.setattr(io_module, "MAX_XLSX_UNCOMPRESSED_BYTES", 10)
    with pytest.raises(RowSpectIOError, match="expands beyond"):
        load_table(buffer.getvalue(), "large.xlsx")


def test_malformed_csv_quoting_has_clean_error():
    with pytest.raises(RowSpectIOError, match="malformed quoting"):
        load_table(b'a,b\n"1,2\n', "bad-quotes.csv")
