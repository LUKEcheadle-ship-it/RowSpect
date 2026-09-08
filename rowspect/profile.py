from __future__ import annotations

from collections import Counter
from typing import Any

import pandas as pd

SEVERITY_ORDER = {"critical": 0, "warning": 1, "info": 2}


def _safe_value(value: Any) -> Any:
    if value is None:
        return None
    try:
        if pd.isna(value):
            return None
    except (TypeError, ValueError):
        pass
    if hasattr(value, "item"):
        try:
            value = value.item()
        except (ValueError, AttributeError):
            pass
    if isinstance(value, pd.Timestamp):
        return value.isoformat()
    if isinstance(value, (str, int, float, bool)):
        return value
    return str(value)


def _is_text(series: pd.Series) -> bool:
    return pd.api.types.is_object_dtype(series.dtype) or pd.api.types.is_string_dtype(series.dtype)


def _blank_count(series: pd.Series) -> int:
    if not _is_text(series):
        return 0
    non_null = series.dropna()
    return int(non_null.map(lambda value: isinstance(value, str) and not value.strip()).sum())


def _numeric_text_ratio(series: pd.Series) -> float:
    if not _is_text(series):
        return 0.0
    values = series.dropna().map(lambda value: value.strip() if isinstance(value, str) else value)
    values = values[values.map(lambda value: value != "")]
    if len(values) < 3:
        return 0.0
    parsed = pd.to_numeric(values, errors="coerce")
    return float(parsed.notna().mean())


def _numeric_stats(series: pd.Series) -> dict[str, Any]:
    values = pd.to_numeric(series, errors="coerce").dropna()
    base = {
        "min": None,
        "max": None,
        "mean": None,
        "median": None,
        "std": None,
        "outlier_count": 0,
        "outlier_pct": 0.0,
        "iqr_lower": None,
        "iqr_upper": None,
    }
    if values.empty:
        return base

    q1 = values.quantile(0.25)
    q3 = values.quantile(0.75)
    iqr = q3 - q1
    lower = q1 - 1.5 * iqr if pd.notna(iqr) else None
    upper = q3 + 1.5 * iqr if pd.notna(iqr) else None
    if iqr == 0 or pd.isna(iqr):
        outliers = pd.Series(False, index=values.index)
    else:
        outliers = (values < lower) | (values > upper)

    count = int(outliers.sum())
    return {
        "min": _safe_value(values.min()),
        "max": _safe_value(values.max()),
        "mean": _safe_value(values.mean()),
        "median": _safe_value(values.median()),
        "std": _safe_value(values.std()) if len(values) > 1 else 0.0,
        "outlier_count": count,
        "outlier_pct": round(count / len(values) * 100, 2),
        "iqr_lower": _safe_value(lower),
        "iqr_upper": _safe_value(upper),
    }


def _score_label(score: float) -> str:
    if score >= 95:
        return "Excellent"
    if score >= 80:
        return "Good"
    if score >= 65:
        return "Needs review"
    return "Poor"


def profile_dataframe(df: pd.DataFrame) -> dict[str, Any]:
    """Build a deterministic, JSON-serializable data-quality profile."""
    rows, column_count = df.shape
    total_cells = rows * column_count
    duplicate_rows = int(df.duplicated().sum()) if rows else 0
    duplicate_pct = duplicate_rows / rows * 100 if rows else 0.0
    missing_cells = int(df.isna().sum().sum()) if total_cells else 0
    missing_pct = missing_cells / total_cells * 100 if total_cells else 0.0
    duplicate_columns = int(pd.Index(df.columns).duplicated().sum())

    issues: list[dict[str, Any]] = []
    columns: list[dict[str, Any]] = []
    total_outliers = 0
    total_blanks = 0
    constant_columns = 0

    if rows == 0:
        issues.append(
            {
                "severity": "critical",
                "category": "empty_dataset",
                "column": None,
                "count": 0,
                "message": "The dataset has columns but no data rows.",
            }
        )
    if duplicate_rows:
        issues.append(
            {
                "severity": "warning",
                "category": "duplicate_rows",
                "column": None,
                "count": duplicate_rows,
                "message": f"{duplicate_rows} exact duplicate row(s) detected.",
            }
        )
    if duplicate_columns:
        issues.append(
            {
                "severity": "critical",
                "category": "duplicate_columns",
                "column": None,
                "count": duplicate_columns,
                "message": "Duplicate column names can make downstream analysis ambiguous.",
            }
        )

    for position, column in enumerate(df.columns):
        series = df.iloc[:, position]
        missing_count = int(series.isna().sum())
        missing_column_pct = missing_count / rows * 100 if rows else 0.0
        non_missing_count = max(rows - missing_count, 0)
        unique_count = int(series.nunique(dropna=True))
        unique_pct = unique_count / max(non_missing_count, 1) * 100 if rows else 0.0
        blank_count = _blank_count(series)
        total_blanks += blank_count
        numeric = pd.api.types.is_numeric_dtype(series.dtype) and not pd.api.types.is_bool_dtype(series.dtype)
        numeric_stats = _numeric_stats(series) if numeric else _numeric_stats(pd.Series(dtype="float64"))
        total_outliers += int(numeric_stats["outlier_count"])

        non_null = series.dropna()
        top_value = None
        top_frequency = 0
        if not non_null.empty:
            counts = non_null.value_counts(dropna=True)
            if not counts.empty:
                top_value = _safe_value(counts.index[0])
                top_frequency = int(counts.iloc[0])

        column_name = str(column)
        numeric_text_ratio = _numeric_text_ratio(series)
        columns.append(
            {
                "column": column_name,
                "position": position + 1,
                "dtype": str(series.dtype),
                "missing_count": missing_count,
                "missing_pct": round(missing_column_pct, 2),
                "blank_count": blank_count,
                "unique_count": unique_count,
                "unique_pct": round(unique_pct, 2),
                "top_value": top_value,
                "top_frequency": top_frequency,
                "numeric_text_pct": round(numeric_text_ratio * 100, 2),
                **numeric_stats,
            }
        )

        if rows and missing_count == rows:
            issues.append(
                {
                    "severity": "critical",
                    "category": "all_missing_column",
                    "column": column_name,
                    "count": missing_count,
                    "message": "Every value in this column is missing.",
                }
            )
        elif missing_count:
            severity = "warning" if missing_column_pct >= 20 else "info"
            issues.append(
                {
                    "severity": severity,
                    "category": "missing_values",
                    "column": column_name,
                    "count": missing_count,
                    "message": f"{missing_count} missing value(s) ({missing_column_pct:.1f}%).",
                }
            )
        if blank_count:
            issues.append(
                {
                    "severity": "warning",
                    "category": "blank_strings",
                    "column": column_name,
                    "count": blank_count,
                    "message": f"{blank_count} blank string value(s) detected.",
                }
            )
        if rows and unique_count <= 1 and missing_count < rows:
            constant_columns += 1
            issues.append(
                {
                    "severity": "info",
                    "category": "constant_column",
                    "column": column_name,
                    "count": non_missing_count,
                    "message": "Column has only one distinct non-missing value.",
                }
            )
        if numeric_stats["outlier_count"]:
            issues.append(
                {
                    "severity": "info",
                    "category": "iqr_outliers",
                    "column": column_name,
                    "count": int(numeric_stats["outlier_count"]),
                    "message": f"{numeric_stats['outlier_count']} potential IQR outlier(s) detected.",
                }
            )
        if numeric_text_ratio >= 0.9:
            issues.append(
                {
                    "severity": "info",
                    "category": "numeric_text",
                    "column": column_name,
                    "count": int(round(numeric_text_ratio * max(len(non_null), 1))),
                    "message": "Most non-empty values look numeric but the column is stored as text.",
                }
            )

    missing_penalty = min(missing_pct * 0.45, 40.0)
    duplicate_penalty = min(duplicate_pct * 0.25, 20.0)
    blank_pct = total_blanks / total_cells * 100 if total_cells else 0.0
    blank_penalty = min(blank_pct * 0.35, 10.0)
    constant_penalty = min(constant_columns * 2.5, 12.5)
    numeric_cells = sum(
        int(df.iloc[:, idx].notna().sum())
        for idx in range(column_count)
        if pd.api.types.is_numeric_dtype(df.iloc[:, idx].dtype)
        and not pd.api.types.is_bool_dtype(df.iloc[:, idx].dtype)
    )
    outlier_pct = total_outliers / numeric_cells * 100 if numeric_cells else 0.0
    outlier_penalty = min(outlier_pct * 0.1, 10.0)
    structural_penalty = 50.0 if rows == 0 else 0.0
    structural_penalty += min(duplicate_columns * 15.0, 30.0)

    quality_score = max(
        0.0,
        100.0
        - missing_penalty
        - duplicate_penalty
        - blank_penalty
        - constant_penalty
        - outlier_penalty
        - structural_penalty,
    )
    quality_score = round(quality_score, 1)

    issues.sort(
        key=lambda item: (
            SEVERITY_ORDER.get(item["severity"], 9),
            item["category"],
            item.get("column") or "",
        )
    )
    severity_counts = Counter(issue["severity"] for issue in issues)

    return {
        "rows": rows,
        "columns_count": column_count,
        "total_cells": total_cells,
        "missing_cells": missing_cells,
        "missing_pct": round(missing_pct, 2),
        "blank_cells": total_blanks,
        "blank_pct": round(blank_pct, 2),
        "duplicate_rows": duplicate_rows,
        "duplicate_pct": round(duplicate_pct, 2),
        "duplicate_columns": duplicate_columns,
        "quality_score": quality_score,
        "quality_label": _score_label(quality_score),
        "issue_count": len(issues),
        "critical_count": severity_counts.get("critical", 0),
        "warning_count": severity_counts.get("warning", 0),
        "info_count": severity_counts.get("info", 0),
        "issues": issues,
        "columns": columns,
        "score_components": {
            "missing_penalty": round(missing_penalty, 2),
            "duplicate_penalty": round(duplicate_penalty, 2),
            "blank_penalty": round(blank_penalty, 2),
            "constant_penalty": round(constant_penalty, 2),
            "outlier_penalty": round(outlier_penalty, 2),
            "structural_penalty": round(structural_penalty, 2),
        },
    }
