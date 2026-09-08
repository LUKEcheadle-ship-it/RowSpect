from __future__ import annotations

from io import BytesIO

import pandas as pd

FORMULA_PREFIXES = ("=", "+", "-", "@")


def neutralize_formula_text(value):
    """Prefix formula-like text so spreadsheet apps treat it as literal text."""
    if not isinstance(value, str):
        return value
    stripped = value.lstrip()
    if stripped.startswith(FORMULA_PREFIXES):
        return "'" + value
    return value


def export_safe_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """Return a copy with formula-like text neutralized for spreadsheet export."""
    safe = df.copy(deep=True)
    for idx in range(safe.shape[1]):
        series = safe.iloc[:, idx]
        if pd.api.types.is_object_dtype(series.dtype) or pd.api.types.is_string_dtype(series.dtype):
            safe.iloc[:, idx] = series.map(neutralize_formula_text)
    return safe


def dataframe_to_csv(df: pd.DataFrame, *, neutralize_formulas: bool = True) -> bytes:
    export_df = export_safe_dataframe(df) if neutralize_formulas else df
    return export_df.to_csv(index=False).encode("utf-8")


def dataframe_to_xlsx(
    df: pd.DataFrame,
    *,
    sheet_name: str = "Cleaned Data",
    neutralize_formulas: bool = True,
) -> bytes:
    """Serialize a dataframe to an in-memory XLSX workbook."""
    buffer = BytesIO()
    safe_sheet = (sheet_name or "Cleaned Data")[:31]
    export_df = export_safe_dataframe(df) if neutralize_formulas else df
    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        export_df.to_excel(writer, index=False, sheet_name=safe_sheet)
        worksheet = writer.book[safe_sheet]
        worksheet.freeze_panes = "A2"
        worksheet.auto_filter.ref = worksheet.dimensions
        for column_cells in worksheet.columns:
            letter = column_cells[0].column_letter
            width = min(
                40,
                max(10, max(len(str(cell.value)) if cell.value is not None else 0 for cell in column_cells) + 2),
            )
            worksheet.column_dimensions[letter].width = width
    return buffer.getvalue()
