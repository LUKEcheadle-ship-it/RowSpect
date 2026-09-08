from __future__ import annotations

from typing import Any

import pandas as pd


def _safe_value(value: Any) -> Any:
    if value is None or pd.isna(value):
        return None
    if hasattr(value, "item"):
        try:
            value = value.item()
        except ValueError:
            pass
    if isinstance(value, pd.Timestamp):
        return value.isoformat()
    if isinstance(value, (str, int, float, bool)):
        return value
    return str(value)


def _blank_count(series: pd.Series) -> int:
    if not (
        pd.api.types.is_object_dtype(series.dtype)
        or pd.api.types.is_string_dtype(series.dtype)
    ):
        return 0
    non_null = series.dropna()
    if non_null.empty:
        return 0
    return int(non_null.map(lambda value: isinstance(value, str) and not value.strip()).sum())


def _numeric_text_ratio(series: pd.Series) -> float:
    if not (
        pd.api.types.is_object_dtype(series.dtype)
        or pd.api.types.is_string_dtype(series.dtype)
    ):
        return 0.0
    non_null = series.dropna().map(lambda value: value.strip() if isinstance(value, str) else value)
    non_blank = non_null[non_null.map(lambda value: value != "")]
    if len(non_blank) < 3:
        return 0.0
    parsed = pd.to_numeric(non_blank, errors="coerce")
    return float(parsed.notna().mean())


def _numeric_stats(series: pd.Series) -> dict[str, Any]:
    values = pd.to_numeric(series, errors="coerce").dropna()
    if values.empty:
        return {
            "min": None,
            "max": None,
            "mean": None,
            "median": None,
            "outlier_count": 0,
            "outlier_pct": 0.0,
        }

    q1 = values.quantile(0.25)
    q3 = values.quantile(0.75)
    iqr = q3 - q1
    if iqr == 0 or pd.isna(iqr):
        outliers = pd.Series(False, index=values.index)
    else:
        lower = q1 - (1.5 * iqr)
        upper = q3 + (1.5 * iqr)
        outliers = (values < lower) | (values > upper)

    outlier_count = int(outliers.sum())
    return {
        "min": _safe_value(values.min()),
        "max": _safe_value(values.max()),
        "mean": _safe_value(values.mean()),
        "median": _safe_value(values.median()),
        "outlier_count": outlier_count,
        "outlier_pct": round((outlier_count / len(values)) * 100, 2),
    }


def profile_dataframe(df: pd.DataFrame) -> dict[str, Any]:
    """Build a deterministic, JSON-serializable data-quality profile."""
    rows, column_count = df.shape
    total_cells = rows * column_count
    duplicate_rows = int(df.duplicated().sum()) if rows else 0
    duplicate_pct = (duplicate_rows / rows * 100) if rows else 0.0
    missing_cells = int(df.isna().sum().sum()) if total_cells else 0
    missing_pct = (missing_cells / total_cells * 100) if total_cells else 0.0

    issues: list[dict[str, Any]] = []
    columns: list[dict[str, Any]] = []
    total_outliers = 0
    total_blanks = 0
    constant_columns = 0

    if duplicate_rows:
        issues.append(
            {
                "severity": "warning",
                "category": "duplicates",
                "column": None,
                "count": duplicate_rows,
                "message": f"{duplicate_rows} duplicate row(s) detected.",
            }
        )

    for column in df.columns:
        series = df[column]
        missing_count = int(series.isna().sum())
        missing_column_pct = (missing_count / rows * 100) if rows else 0.0
        unique_count = int(series.nunique(dropna=True))
        unique_pct = (unique_count / max(rows - missing_count, 1) * 100) if rows else 0.0
        blank_count = _blank_count(series)
        total_blanks += blank_count
        numeric = pd.api.types.is_numeric_dtype(series.dtype) and not pd.api.types.is_bool_dtype(series.dtype)
        numeric_stats = _numeric_stats(series) if numeric else {
            "min": None,
            "max": None,
            "mean": None,
            "median": None,
            "outlier_count": 0,
            "outlier_pct": 0.0,
        }
        total_outliers += numeric_stats["outlier_count"]

        non_null = series.dropna()
        top_value = None
        top_frequency = 0
        if not non_null.empty:
            counts = non_null.value_counts(dropna=True)
            if not counts.empty:
                top_value = _safe_value(counts.index[0])
                top_frequency = int(counts.iloc[0])

        columns.append(
            {
                "column": str(column),
                "dtype": str(series.dtype),
                "missing_count": missing_count,
                "missing_pct": round(missing_column_pct, 2),
                "blank_count": blank_count,
                "unique_count": unique_count,
                "unique_pct": round(unique_pct, 2),
                "top_value": top_value,
                "top_frequency": top_frequency,
                **numeric_stats,
            }
        )

        if missing_count:
            severity = "warning" if missing_column_pct >= 20 else "info"
            issues.append(
                {
                    "severity": severity,
                    "category": "missing_values",
                    "column": str(column),
                    "count": missing_count,
                    "message": f"{missing_count} missing value(s) ({missing_column_pct:.1f}%).",
                }
            )
        if blank_count:
            issues.append(
                {
                    "severity": "warning",
                    "category": "blank_strings",
                    "column": str(column),
                    "count": blank_count,
                    "message": f"{blank_count} blank string value(s) detected.",
                }
            )
        if rows and unique_count <= 1:
            constant_columns += 1
            issues.append(
                {
                    "severity": "info",
                    "category": "constant_column",
                    "column": str(column),
                    "count": rows - missing_count,
                    "message": "Column has one or fewer non-null values.",
                }
            )
        if numeric_stats["outlier_count"]:
            issues.append(
                {
                    "severity": "info",
                    "category": "iqr_outliers",
                    "column": str(column),
                    "count": numeric_stats["outlier_count"],
                    "message": f"{numeric_stats['outlier_count']} potential IQR outlier(s) detected.",
                }
            )
        numeric_text_ratio = _numeric_text_ratio(series)
        if numeric_text_ratio >= 0.9:
            issues.append(
                {
                    "severity": "info",
                    "category": "numeric_text",
                    "column": str(column),
                    "count": int(round(numeric_text_ratio * max(len(series.dropna()), 1))),
                    "message": "Most non-empty values look numeric but the column is stored as text.",
                }
            )

    missing_penalty = min(missing_pct * 0.4, 40.0)
    duplicate_penalty = min(duplicate_pct * 0.2, 20.0)
    blank_pct = (total_blanks / total_cells * 100) if total_cells else 0.0
    blank_penalty = min(blank_pct * 0.3, 10.0)
    constant_penalty = min(constant_columns * 3.0, 15.0)
    numeric_cells = sum(
        int(df[column].notna().sum())
        for column in df.columns
        if pd.api.types.is_numeric_dtype(df[column])
    )
    outlier_pct = (total_outliers / numeric_cells * 100) if numeric_cells else 0.0
    outlier_penalty = min(outlier_pct * 0.15, 15.0)
    quality_score = max(
        0.0,
        100.0 - missing_penalty - duplicate_penalty - blank_penalty - constant_penalty - outlier_penalty,
    )

    severity_order = {"warning": 0, "info": 1}
    issues.sort(
        key=lambda item: (
            severity_order.get(item["severity"], 9),
            item["category"],
            item.get("column") or "",
        )
    )

    return {
        "rows": rows,
        "columns_count": column_count,
        "total_cells": total_cells,
        "missing_cells": missing_cells,
        "missing_pct": round(missing_pct, 2),
        "duplicate_rows": duplicate_rows,
        "duplicate_pct": round(duplicate_pct, 2),
        "quality_score": round(quality_score, 1),
        "issue_count": len(issues),
        "issues": issues,
        "columns": columns,
    }
