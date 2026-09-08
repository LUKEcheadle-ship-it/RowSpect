from __future__ import annotations

import csv
import zipfile
from io import BytesIO, StringIO
from pathlib import Path

import pandas as pd
from pandas.errors import EmptyDataError as PandasEmptyDataError
from pandas.errors import ParserError

SUPPORTED_EXTENSIONS = {".csv", ".xlsx"}
MAX_FILE_BYTES = 50 * 1024 * 1024
MAX_XLSX_UNCOMPRESSED_BYTES = 250 * 1024 * 1024
MAX_XLSX_ARCHIVE_ENTRIES = 10_000


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


def _csv_header_and_width(text: str, delimiter: str) -> tuple[list[str], int]:
    reader = csv.reader(StringIO(text), delimiter=delimiter, strict=True)
    for row in reader:
        if row and any(cell != "" for cell in row):
            return row, len(row)
    raise RowSpectIOError("The CSV does not contain a readable header.")


def _validate_csv_structure(text: str, delimiter: str) -> list[str]:
    raw_header, expected_width = _csv_header_and_width(text, delimiter)
    reader = csv.reader(StringIO(text), delimiter=delimiter, strict=True)
    header_seen = False
    for row_number, row in enumerate(reader, start=1):
        if not row or all(cell == "" for cell in row):
            continue
        if not header_seen:
            header_seen = True
            continue
        if len(row) != expected_width:
            raise RowSpectIOError(
                f"The CSV has an inconsistent number of fields on row {row_number} "
                f"(expected {expected_width}, found {len(row)})."
            )
    return raw_header


def _validate_xlsx_archive(data: bytes) -> None:
    """Reject malformed or implausibly large XLSX ZIP containers before XML parsing."""
    try:
        with zipfile.ZipFile(BytesIO(data)) as archive:
            infos = archive.infolist()
            if len(infos) > MAX_XLSX_ARCHIVE_ENTRIES:
                raise RowSpectIOError(
                    f"This Excel workbook contains too many archive entries ({len(infos):,})."
                )
            if any(info.flag_bits & 0x1 for info in infos):
                raise RowSpectIOError("Encrypted Excel workbooks are not supported.")
            total_uncompressed = sum(info.file_size for info in infos)
            if total_uncompressed > MAX_XLSX_UNCOMPRESSED_BYTES:
                raise RowSpectIOError(
                    "This Excel workbook expands beyond RowSpect's 250 MB safety limit."
                )
            names = set(archive.namelist())
            if "[Content_Types].xml" not in names or "xl/workbook.xml" not in names:
                raise RowSpectIOError("The uploaded .xlsx file is not a valid Excel workbook.")
    except RowSpectIOError:
        raise
    except (zipfile.BadZipFile, OSError) as exc:
        raise RowSpectIOError("Could not open this Excel workbook. It may be corrupt or invalid.") from exc


def _xlsx_raw_headers(data: bytes, sheet_name: str | None) -> list[object] | None:
    """Read the original first-row headers so duplicate names are not hidden by pandas."""
    try:
        from openpyxl import load_workbook

        workbook = load_workbook(BytesIO(data), read_only=True, data_only=True)
        try:
            if sheet_name is not None:
                if sheet_name not in workbook.sheetnames:
                    raise RowSpectIOError(f"Worksheet '{sheet_name}' was not found.")
                worksheet = workbook[sheet_name]
            else:
                worksheet = workbook[workbook.sheetnames[0]]
            first_row = next(worksheet.iter_rows(min_row=1, max_row=1, values_only=True), None)
            if first_row is None:
                return None
            return ["" if value is None else value for value in first_row]
        finally:
            workbook.close()
    except RowSpectIOError:
        raise
    except Exception:
        return None


def get_excel_sheets(data: bytes) -> list[str]:
    """Return sheet names from an XLSX workbook after upload and archive validation."""
    validate_upload(data, "workbook.xlsx")
    _validate_xlsx_archive(data)
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
            raw_headers = _validate_csv_structure(text, delimiter)
            df = pd.read_csv(StringIO(text), sep=delimiter)
            if len(raw_headers) == df.shape[1]:
                df.columns = raw_headers
        else:
            _validate_xlsx_archive(data)
            raw_headers = _xlsx_raw_headers(data, sheet_name)
            df = pd.read_excel(BytesIO(data), sheet_name=sheet_name or 0, engine="openpyxl")
            if raw_headers is not None and len(raw_headers) == df.shape[1]:
                df.columns = raw_headers
    except csv.Error as exc:
        raise RowSpectIOError("The CSV contains malformed quoting and could not be parsed.") from exc
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
