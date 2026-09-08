from __future__ import annotations

from typing import Any

import pandas as pd


def clean_dataframe(
    df: pd.DataFrame,
    *,
    drop_duplicates: bool = True,
    trim_strings: bool = True,
    normalize_blank_strings: bool = True,
    drop_empty_rows: bool = True,
) -> pd.DataFrame:
    """Apply conservative, user-selected cleanup operations without mutating input."""
    cleaned = df.copy(deep=True)

    for position in range(cleaned.shape[1]):
        series = cleaned.iloc[:, position]
        if not (
            pd.api.types.is_object_dtype(series.dtype)
            or pd.api.types.is_string_dtype(series.dtype)
        ):
            continue
        transformed = series
        if trim_strings:
            transformed = transformed.map(lambda value: value.strip() if isinstance(value, str) else value)
        if normalize_blank_strings:
            transformed = transformed.map(
                lambda value: pd.NA if isinstance(value, str) and not value.strip() else value
            )
        cleaned.iloc[:, position] = transformed

    if drop_empty_rows:
        cleaned = cleaned.dropna(how="all")
    if drop_duplicates:
        cleaned = cleaned.drop_duplicates()
    return cleaned.reset_index(drop=True)


def cleanup_summary(before: pd.DataFrame, after: pd.DataFrame) -> dict[str, Any]:
    """Return a compact before/after summary for the UI and exports."""
    before_blanks = int(
        sum(
            before.iloc[:, idx]
            .dropna()
            .map(lambda value: isinstance(value, str) and not value.strip())
            .sum()
            for idx in range(before.shape[1])
        )
    )
    after_blanks = int(
        sum(
            after.iloc[:, idx]
            .dropna()
            .map(lambda value: isinstance(value, str) and not value.strip())
            .sum()
            for idx in range(after.shape[1])
        )
    )
    return {
        "rows_before": len(before),
        "rows_after": len(after),
        "rows_removed": len(before) - len(after),
        "duplicates_before": int(before.duplicated().sum()),
        "duplicates_after": int(after.duplicated().sum()),
        "blank_strings_before": before_blanks,
        "blank_strings_after": after_blanks,
        "missing_before": int(before.isna().sum().sum()),
        "missing_after": int(after.isna().sum().sum()),
    }
