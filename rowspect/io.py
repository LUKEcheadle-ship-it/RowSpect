from __future__ import annotations

import csv
from io import BytesIO, StringIO
from pathlib import Path

import pandas as pd
from pandas.errors import EmptyDataError as PandasEmptyDataError
from pandas.errors import ParserError

SUPPORTED_EXTENSIONS = {".csv", ".xlsx"}
MAX_FILE_BYTES = 50 * 1024 * 1024


class RowSpectIOError(ValueError):
    """Raised when a user-provided table cannot be loaded safely."""


def validate_upload(data: bytes, filename: str, *, max_bytes: int = MAX_FILE_BYTES) -> str:
    extension = Path(filename).suffix.lower()
    if extension not in SUPPORTED_EXTENSIONS:
        raise RowSpectIOError("RowSpect supports CSV (.csv) and Excel (.xlsx) files.")
    if not data:
        raise RowSpectIOError("The uploaded file is empty.")
    if len(data) > max_bytes:
        raise RowSpectIOError(
            f"The uploaded file is larger than the {max_bytes // (1024 * 1024)} MB V1 limit."
        )
    return extension


def _decode_csv(data: bytes) -> str:
    for encoding in ("utf-8-sig", "utf-8", "latin-1"):
        try:
            return data.decode(encoding)
        except UnicodeDecodeError:
            continue
    raise RowSpectIOError("Could not decode this CSV file.")


def _detect_delimiter(text: str) -> str:
    sample = text[:8192]
    try:
        return csv.Sniffer().sniff(sample, delimiters=",;\t|").delimiter
    except csv.Error:
        return ","


def _validate_csv_structure(text: str, delimiter: str) -> None:
    reader = csv.reader(StringIO(text), delimiter=delimiter)
    expected_width: int | None = None
    for row_number, row in enumerate(reader, start=1):
        if not row or all(cell == "" for cell in row):
            continue
        if expected_width is None:
            expected_width = len(row)
            if expected_width == 0:
                raise RowSpectIOError("The CSV does not contain a readable header.")
            continue
        if len(row) != expected_width:
            raise RowSpectIOError(
                f"The CSV has an inconsistent number of fields on row {row_number} "
                f"(expected {expected_width}, found {len(row)})."
            )


def get_excel_sheets(data: bytes) -> list[str]:
    """Return sheet names from an XLSX workbook after basic upload validation."""
    validate_upload(data, "workbook.xlsx")
    try:
        workbook = pd.ExcelFile(BytesIO(data), engine="openpyxl")
    except Exception as exc:
        raise RowSpectIOError("Could not open this Excel workbook. It may be corrupt or invalid.") from exc
    if not workbook.sheet_names:
        raise RowSpectIOError("This Excel workbook does not contain any worksheets.")
    return workbook.sheet_names


def load_table(data: bytes, filename: str, sheet_name: str | None = None) -> pd.DataFrame:
    """Load a CSV or XLSX file from bytes without writing it to disk."""
    extension = validate_upload(data, filename)

    try:
        if extension == ".csv":
            text = _decode_csv(data)
            delimiter = _detect_delimiter(text)
            _validate_csv_structure(text, delimiter)
            df = pd.read_csv(StringIO(text), sep=delimiter)
        else:
            df = pd.read_excel(BytesIO(data), sheet_name=sheet_name or 0, engine="openpyxl")
    except PandasEmptyDataError as exc:
        raise RowSpectIOError("The file does not contain a readable header or data rows.") from exc
    except ParserError as exc:
        raise RowSpectIOError("The CSV structure is inconsistent and could not be parsed.") from exc
    except RowSpectIOError:
        raise
    except Exception as exc:
        label = "CSV" if extension == ".csv" else "Excel workbook"
        raise RowSpectIOError(f"Could not read this {label}. It may be corrupt or malformed.") from exc

    if df.shape[1] == 0:
        raise RowSpectIOError("No columns were found in this file.")
    return df
