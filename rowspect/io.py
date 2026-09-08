from __future__ import annotations

from io import BytesIO
from pathlib import Path

import pandas as pd

SUPPORTED_EXTENSIONS = {".csv", ".xlsx"}


def get_excel_sheets(data: bytes) -> list[str]:
    """Return sheet names from an XLSX workbook."""
    workbook = pd.ExcelFile(BytesIO(data), engine="openpyxl")
    return workbook.sheet_names


def load_table(data: bytes, filename: str, sheet_name: str | None = None) -> pd.DataFrame:
    """Load a CSV or XLSX file from bytes without writing it to disk."""
    extension = Path(filename).suffix.lower()
    if extension not in SUPPORTED_EXTENSIONS:
        raise ValueError("RowSpect currently supports .csv and .xlsx files.")

    buffer = BytesIO(data)
    if extension == ".csv":
        try:
            return pd.read_csv(buffer)
        except UnicodeDecodeError:
            buffer.seek(0)
            return pd.read_csv(buffer, encoding="latin-1")

    return pd.read_excel(buffer, sheet_name=sheet_name or 0, engine="openpyxl")
