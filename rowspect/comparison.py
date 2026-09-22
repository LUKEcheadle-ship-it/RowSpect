from __future__ import annotations

from collections.abc import Iterable
from typing import Any

import pandas as pd

from rowspect.profile import profile_dataframe


def _ordered_unique(values: Iterable[Any]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for value in values:
        text = str(value)
        if text not in seen:
            seen.add(text)
            result.append(text)
    return result


def _json_value(value: Any) -> Any:
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
        except (AttributeError, ValueError):
            pass
    if isinstance(value, (str, int, float, bool)):
        return value
    return str(value)


def _non_missing_values(series: pd.Series) -> list[Any]:
    return [value for value in series.tolist() if not pd.isna(value)]


def _category_examples(current: pd.Series, baseline: pd.Series, limit: int = 5) -> list[str]:
    text_like = lambda series: (
        pd.api.types.is_object_dtype(series.dtype)
        or pd.api.types.is_string_dtype(series.dtype)
        or isinstance(series.dtype, pd.CategoricalDtype)
    )
    if not (text_like(current) or text_like(baseline)):
        return []
    old = {str(value) for value in _non_missing_values(baseline)}
    values = {str(value) for value in _non_missing_values(current) if str(value) not in old}
    return sorted(values)[:limit]


def compare_dataframes(current: pd.DataFrame, baseline: pd.DataFrame) -> dict[str, Any]:
    """Describe deterministic, review-oriented changes from baseline to current.

    This is descriptive change detection, not statistical significance testing.
    Column matching uses exact stringified header names; duplicate names are
    reported as a schema concern and are not guessed apart.
    """
    current_profile = profile_dataframe(current)
    baseline_profile = profile_dataframe(baseline)
    current_columns = _ordered_unique(current.columns)
    baseline_columns = _ordered_unique(baseline.columns)
    current_set = set(current_columns)
    baseline_set = set(baseline_columns)

    columns_added = [name for name in current_columns if name not in baseline_set]
    columns_removed = [name for name in baseline_columns if name not in current_set]
    common = [name for name in current_columns if name in baseline_set]
    changes: list[dict[str, Any]] = []
    for name in common:
        current_positions = [i for i, column in enumerate(current.columns) if str(column) == name]
        baseline_positions = [i for i, column in enumerate(baseline.columns) if str(column) == name]
        change: dict[str, Any] = {"column": name}
        if len(current_positions) != 1 or len(baseline_positions) != 1:
            change["status"] = "ambiguous_column"
            change["details"] = "The column name is duplicated in the current or baseline file."
            changes.append(change)
            continue

        current_series = current.iloc[:, current_positions[0]]
        baseline_series = baseline.iloc[:, baseline_positions[0]]
        current_profile_column = current_profile["columns"][current_positions[0]]
        baseline_profile_column = baseline_profile["columns"][baseline_positions[0]]
        current_dtype = str(current_series.dtype)
        baseline_dtype = str(baseline_series.dtype)
        change.update(
            {
                "status": "changed" if current_dtype != baseline_dtype else "unchanged",
                "type_changed": current_dtype != baseline_dtype,
                "baseline_dtype": baseline_dtype,
                "current_dtype": current_dtype,
                "missing_pct_change": round(
                    float(current_profile_column["missing_pct"])
                    - float(baseline_profile_column["missing_pct"]),
                    2,
                ),
                "baseline_missing_pct": baseline_profile_column["missing_pct"],
                "current_missing_pct": current_profile_column["missing_pct"],
                "new_category_examples": _category_examples(current_series, baseline_series),
            }
        )
        if current_profile_column["median"] is not None or baseline_profile_column["median"] is not None:
            baseline_median = baseline_profile_column["median"]
            current_median = current_profile_column["median"]
            change.update(
                {
                    "baseline_numeric_median": _json_value(baseline_median),
                    "current_numeric_median": _json_value(current_median),
                    "numeric_median_change": (
                        round(float(current_median) - float(baseline_median), 12)
                        if baseline_median is not None and current_median is not None
                        else None
                    ),
                }
            )
        changes.append(change)

    row_delta = int(len(current) - len(baseline))
    result = {
        "comparison_version": 1,
        "description": "Descriptive file-to-file changes; this is not statistical significance testing.",
        "baseline_rows": int(len(baseline)),
        "current_rows": int(len(current)),
        "row_count_change": row_delta,
        "rows_added": max(row_delta, 0),
        "rows_removed": max(-row_delta, 0),
        "baseline_columns": int(baseline.shape[1]),
        "current_columns": int(current.shape[1]),
        "columns_added": columns_added,
        "columns_removed": columns_removed,
        "column_changes": changes,
        "baseline_quality_score": baseline_profile["quality_score"],
        "current_quality_score": current_profile["quality_score"],
        "quality_score_change": round(
            float(current_profile["quality_score"]) - float(baseline_profile["quality_score"]), 1
        ),
    }
    return result


def compare_profiles(current_profile: dict[str, Any], baseline_profile: dict[str, Any]) -> dict[str, Any]:
    """Compare already-generated profiles when source data is unavailable."""
    result = {
        "comparison_version": 1,
        "description": "Descriptive profile changes; this is not statistical significance testing.",
        "baseline_rows": baseline_profile.get("rows", 0),
        "current_rows": current_profile.get("rows", 0),
        "row_count_change": int(current_profile.get("rows", 0) - baseline_profile.get("rows", 0)),
        "rows_added": max(int(current_profile.get("rows", 0) - baseline_profile.get("rows", 0)), 0),
        "rows_removed": max(int(baseline_profile.get("rows", 0) - current_profile.get("rows", 0)), 0),
        "baseline_columns": baseline_profile.get("columns_count", 0),
        "current_columns": current_profile.get("columns_count", 0),
        "columns_added": [],
        "columns_removed": [],
        "column_changes": [],
        "baseline_quality_score": baseline_profile.get("quality_score"),
        "current_quality_score": current_profile.get("quality_score"),
        "quality_score_change": round(
            float(current_profile.get("quality_score", 0)) - float(baseline_profile.get("quality_score", 0)), 1
        ),
    }
    return result


def comparison_json(comparison: dict[str, Any]) -> str:
    """Serialize comparison output with stable key ordering."""
    import json

    return json.dumps(comparison, indent=2, ensure_ascii=False, sort_keys=True, allow_nan=False)
