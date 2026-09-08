from __future__ import annotations

from typing import Any

import pandas as pd

SUPPORTED_TARGET_TYPES = {"text", "integer", "float", "boolean", "date", "datetime"}


class ConversionError(ValueError):
    """Raised when a conversion plan is malformed or cannot be applied safely."""


def normalize_conversion(plan: dict[str, Any], *, position: int = 0) -> dict[str, Any]:
    if not isinstance(plan, dict):
        raise ConversionError("Each conversion plan must be a JSON object.")
    column = plan.get("column")
    if not isinstance(column, str) or not column.strip():
        raise ConversionError("Each conversion requires a non-empty column name.")
    target_type = str(plan.get("target_type", "")).strip().lower()
    if target_type not in SUPPORTED_TARGET_TYPES:
        raise ConversionError(
            f"Unsupported target type '{target_type or 'missing'}'. Supported types: "
            + ", ".join(sorted(SUPPORTED_TARGET_TYPES))
        )
    return {
        "id": str(plan.get("id") or f"conversion-{position + 1}"),
        "column": column,
        "target_type": target_type,
    }


def normalize_conversions(plans: list[dict[str, Any]]) -> list[dict[str, Any]]:
    if not isinstance(plans, list):
        raise ConversionError("Conversions must be provided as a list.")
    if len(plans) > 100:
        raise ConversionError("A profile may contain at most 100 conversions.")
    normalized = [normalize_conversion(plan, position=index) for index, plan in enumerate(plans)]
    ids = [plan["id"] for plan in normalized]
    if len(ids) != len(set(ids)):
        raise ConversionError("Conversion ids must be unique within a profile.")
    return normalized


def _missing_mask(series: pd.Series) -> pd.Series:
    mask = series.isna().copy()
    if pd.api.types.is_object_dtype(series.dtype) or pd.api.types.is_string_dtype(series.dtype):
        mask = mask | series.map(lambda value: isinstance(value, str) and not value.strip())
    return mask.astype(bool)


def _convert_boolean(series: pd.Series) -> tuple[pd.Series, pd.Series]:
    truthy = {"true", "yes", "y", "1"}
    falsy = {"false", "no", "n", "0"}
    missing = _missing_mask(series)
    result = pd.Series(pd.NA, index=series.index, dtype="boolean")
    invalid = pd.Series(False, index=series.index)

    for index, value in series.items():
        if missing.loc[index]:
            continue
        if isinstance(value, bool):
            result.loc[index] = value
            continue
        token = str(value).strip().lower()
        if token in truthy:
            result.loc[index] = True
        elif token in falsy:
            result.loc[index] = False
        else:
            invalid.loc[index] = True
    return result, invalid


def _conversion_candidate(series: pd.Series, target_type: str) -> tuple[pd.Series, pd.Series]:
    missing = _missing_mask(series)
    non_missing = ~missing

    if target_type == "text":
        result = series.astype("string")
        result[missing] = pd.NA
        return result, pd.Series(False, index=series.index)

    if target_type in {"integer", "float"}:
        numeric = pd.to_numeric(series.where(non_missing), errors="coerce")
        invalid = non_missing & numeric.isna()
        if target_type == "integer":
            fractional = non_missing & numeric.notna() & ((numeric % 1).abs() > 1e-12)
            invalid = invalid | fractional
            result = numeric.round().astype("Int64")
        else:
            result = numeric.astype("Float64")
        return result, invalid.fillna(False)

    if target_type == "boolean":
        return _convert_boolean(series)

    if target_type in {"date", "datetime"}:
        parsed = pd.to_datetime(series.where(non_missing), errors="coerce")
        invalid = non_missing & parsed.isna()
        if target_type == "date":
            parsed = parsed.dt.normalize()
        return parsed, invalid.fillna(False)

    raise ConversionError(f"Unsupported target type: {target_type}")


def analyze_type_conversion(series: pd.Series, target_type: str, *, max_examples: int = 5) -> dict[str, Any]:
    target_type = str(target_type).strip().lower()
    if target_type not in SUPPORTED_TARGET_TYPES:
        raise ConversionError(f"Unsupported target type: {target_type}")

    converted, invalid = _conversion_candidate(series, target_type)
    missing = _missing_mask(series)
    non_missing_count = int((~missing).sum())
    failure_count = int(invalid.sum())
    convertible_count = max(non_missing_count - failure_count, 0)
    failure_examples = [str(value) for value in series[invalid].head(max_examples).tolist()]

    changed_count = 0
    for original, new in zip(series.tolist(), converted.tolist()):
        if pd.isna(original) and pd.isna(new):
            continue
        if str(original) != str(new):
            changed_count += 1

    return {
        "target_type": target_type,
        "source_dtype": str(series.dtype),
        "target_dtype": str(converted.dtype),
        "non_missing_count": non_missing_count,
        "convertible_count": convertible_count,
        "failure_count": failure_count,
        "failure_pct": round((failure_count / non_missing_count * 100) if non_missing_count else 0.0, 2),
        "changed_count": changed_count,
        "failure_examples": failure_examples,
        "safe_to_apply": failure_count == 0,
    }


def _column_positions(df: pd.DataFrame, name: str) -> list[int]:
    return [index for index, column in enumerate(df.columns) if str(column) == name]


def apply_type_conversions(
    df: pd.DataFrame,
    plans: list[dict[str, Any]],
    *,
    strict: bool = True,
) -> tuple[pd.DataFrame, list[dict[str, Any]]]:
    """Apply explicit conversion plans to a copy of a dataframe.

    With strict=True (the default), a conversion is not applied when any non-empty
    value cannot be converted. No invalid values are silently discarded.
    """
    normalized = normalize_conversions(plans)
    converted_df = df.copy(deep=True)
    results: list[dict[str, Any]] = []

    for plan in normalized:
        positions = _column_positions(converted_df, plan["column"])
        if not positions:
            results.append({**plan, "applied": False, "status": "missing_column", "failure_count": 0})
            continue
        if len(positions) > 1:
            results.append({**plan, "applied": False, "status": "ambiguous_column", "failure_count": 0})
            continue

        position = positions[0]
        source = converted_df.iloc[:, position]
        candidate, invalid = _conversion_candidate(source, plan["target_type"])
        analysis = analyze_type_conversion(source, plan["target_type"])

        if strict and analysis["failure_count"]:
            results.append({**plan, **analysis, "applied": False, "status": "blocked_invalid_values"})
            continue

        if not strict and invalid.any():
            candidate = candidate.copy()
            candidate[invalid] = pd.NA

        converted_df.iloc[:, position] = candidate
        results.append({**plan, **analysis, "applied": True, "status": "applied"})

    return converted_df, results
