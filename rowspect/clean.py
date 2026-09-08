from __future__ import annotations

import pandas as pd


def clean_dataframe(
    df: pd.DataFrame,
    *,
    drop_duplicates: bool = True,
    trim_strings: bool = True,
    normalize_blank_strings: bool = True,
    drop_empty_rows: bool = True,
) -> pd.DataFrame:
    """Apply conservative, user-selected cleanup operations.

    RowSpect deliberately avoids imputing values or changing inferred data types.
    """
    cleaned = df.copy(deep=True)

    string_columns = [
        column
        for column in cleaned.columns
        if pd.api.types.is_object_dtype(cleaned[column].dtype)
        or pd.api.types.is_string_dtype(cleaned[column].dtype)
    ]

    for column in string_columns:
        series = cleaned[column]
        if trim_strings:
            cleaned[column] = series.map(lambda value: value.strip() if isinstance(value, str) else value)
        if normalize_blank_strings:
            cleaned[column] = cleaned[column].map(
                lambda value: pd.NA if isinstance(value, str) and not value.strip() else value
            )

    if drop_empty_rows:
        cleaned = cleaned.dropna(how="all")
    if drop_duplicates:
        cleaned = cleaned.drop_duplicates()

    return cleaned.reset_index(drop=True)
