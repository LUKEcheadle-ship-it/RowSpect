from io import BytesIO

import pandas as pd

from rowspect.io import get_excel_sheets, load_table


def test_load_csv_from_bytes():
    df = load_table(b"a,b\n1,x\n2,y\n", "sample.csv")
    assert df.shape == (2, 2)
    assert df["a"].tolist() == [1, 2]


def test_load_xlsx_sheet_from_bytes():
    buffer = BytesIO()
    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        pd.DataFrame({"a": [1]}).to_excel(writer, sheet_name="Summary", index=False)
        pd.DataFrame({"b": [2, 3]}).to_excel(writer, sheet_name="Details", index=False)

    data = buffer.getvalue()
    assert get_excel_sheets(data) == ["Summary", "Details"]
    df = load_table(data, "sample.xlsx", sheet_name="Details")
    assert df["b"].tolist() == [2, 3]
