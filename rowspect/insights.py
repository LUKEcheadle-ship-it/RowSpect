from __future__ import annotations

import pandas as pd


def missingness_table(profile: dict) -> pd.DataFrame:
    rows = [
        {"column": col["column"], "missing_pct": col["missing_pct"], "missing_count": col["missing_count"]}
        for col in profile.get("columns", [])
        if col.get("missing_count", 0) > 0
    ]
    if not rows:
        return pd.DataFrame(columns=["column", "missing_pct", "missing_count"])
    return pd.DataFrame(rows).sort_values(["missing_pct", "missing_count"], ascending=False).reset_index(drop=True)


def correlation_matrix(df: pd.DataFrame, *, max_columns: int = 20) -> pd.DataFrame:
    numeric = df.select_dtypes(include="number")
    if numeric.shape[1] < 2:
        return pd.DataFrame()
    numeric = numeric.iloc[:, :max_columns]
    return numeric.corr(numeric_only=True).round(3)


def numeric_histogram(series: pd.Series, *, bins: int = 20) -> pd.DataFrame:
    values = pd.to_numeric(series, errors="coerce").dropna()
    if values.empty:
        return pd.DataFrame(columns=["range", "count"])
    unique = values.nunique()
    bin_count = max(1, min(bins, int(unique)))
    if bin_count == 1:
        return pd.DataFrame({"range": [str(values.iloc[0])], "count": [len(values)]})
    buckets = pd.cut(values, bins=bin_count, duplicates="drop")
    counts = buckets.value_counts(sort=False)
    return pd.DataFrame({"range": counts.index.astype(str), "count": counts.values})


def top_values(series: pd.Series, *, limit: int = 15) -> pd.DataFrame:
    values = series.dropna()
    if values.empty:
        return pd.DataFrame(columns=["value", "count"])
    counts = values.astype(str).value_counts().head(limit)
    return pd.DataFrame({"value": counts.index, "count": counts.values})
