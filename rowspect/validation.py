from __future__ import annotations

import re
from decimal import Decimal, InvalidOperation
from typing import Any

import pandas as pd

SUPPORTED_RULE_TYPES = {
    "required",
    "unique",
    "range",
    "allowed_values",
    "regex",
    "date",
    "compare_columns",
}
SUPPORTED_COMPARISON_OPERATORS = {"eq", "ne", "lt", "le", "gt", "ge"}
SUPPORTED_COMPARISON_MODES = {"numeric", "date", "text"}
SUPPORTED_SEVERITIES = {"critical", "warning", "info"}
MAX_RULES = 100
MAX_REGEX_LENGTH = 512
MAX_ALLOWED_VALUES = 5000
MAX_REPORTED_ROWS = 100


class ValidationRuleError(ValueError):
    """Raised when a validation rule is malformed."""


def _missing_mask(series: pd.Series) -> pd.Series:
    mask = series.isna().copy()
    if pd.api.types.is_object_dtype(series.dtype) or pd.api.types.is_string_dtype(series.dtype):
        mask = mask | series.map(lambda value: isinstance(value, str) and not value.strip())
    return mask.astype(bool)


def normalize_rule(rule: dict[str, Any], *, position: int = 0) -> dict[str, Any]:
    if not isinstance(rule, dict):
        raise ValidationRuleError("Each validation rule must be a JSON object.")

    rule_type = str(rule.get("type", "")).strip().lower()
    if rule_type not in SUPPORTED_RULE_TYPES:
        raise ValidationRuleError(
            f"Unsupported rule type '{rule_type or 'missing'}'. Supported types: "
            + ", ".join(sorted(SUPPORTED_RULE_TYPES))
        )

    column = rule.get("column", rule.get("left_column"))
    if not isinstance(column, str) or not column.strip():
        raise ValidationRuleError("Each validation rule requires a non-empty column name.")

    severity = str(rule.get("severity", "warning")).strip().lower()
    if severity not in SUPPORTED_SEVERITIES:
        raise ValidationRuleError("Rule severity must be critical, warning, or info.")

    normalized: dict[str, Any] = {
        "id": str(rule.get("id") or f"rule-{position + 1}"),
        "type": rule_type,
        "column": column,
        "severity": severity,
    }

    custom_message = rule.get("message")
    if custom_message is not None:
        if not isinstance(custom_message, str) or len(custom_message) > 500:
            raise ValidationRuleError("Rule message must be text no longer than 500 characters.")
        normalized["message"] = custom_message

    if rule_type == "range":
        minimum = rule.get("min")
        maximum = rule.get("max")
        if minimum is None and maximum is None:
            raise ValidationRuleError("A range rule requires min, max, or both.")
        for label, value in (("min", minimum), ("max", maximum)):
            if value is not None:
                try:
                    normalized[label] = float(value)
                except (TypeError, ValueError) as exc:
                    raise ValidationRuleError(f"Range {label} must be numeric.") from exc
        if minimum is not None and maximum is not None and float(minimum) > float(maximum):
            raise ValidationRuleError("Range min cannot be greater than max.")

    elif rule_type == "allowed_values":
        values = rule.get("values")
        if not isinstance(values, list) or not values:
            raise ValidationRuleError("An allowed_values rule requires a non-empty values list.")
        if len(values) > MAX_ALLOWED_VALUES:
            raise ValidationRuleError(f"allowed_values supports at most {MAX_ALLOWED_VALUES} values.")
        normalized["values"] = values

    elif rule_type == "regex":
        pattern = rule.get("pattern")
        if not isinstance(pattern, str) or not pattern:
            raise ValidationRuleError("A regex rule requires a non-empty pattern.")
        if len(pattern) > MAX_REGEX_LENGTH:
            raise ValidationRuleError(f"Regex patterns are limited to {MAX_REGEX_LENGTH} characters.")
        try:
            re.compile(pattern)
        except re.error as exc:
            raise ValidationRuleError(f"Invalid regex pattern: {exc}") from exc
        normalized["pattern"] = pattern

    elif rule_type == "date":
        date_format = rule.get("format")
        if date_format is not None:
            if not isinstance(date_format, str) or len(date_format) > 128:
                raise ValidationRuleError("Date format must be text no longer than 128 characters.")
            normalized["format"] = date_format

    elif rule_type == "compare_columns":
        left_column = rule.get("left_column", rule.get("column"))
        right_column = rule.get("right_column", rule.get("other_column"))
        if not isinstance(left_column, str) or not left_column.strip():
            raise ValidationRuleError("A compare_columns rule requires a non-empty left_column.")
        if not isinstance(right_column, str) or not right_column.strip():
            raise ValidationRuleError("A compare_columns rule requires a non-empty right_column.")
        operator = str(rule.get("operator", "")).strip().lower()
        if operator not in SUPPORTED_COMPARISON_OPERATORS:
            raise ValidationRuleError(
                "compare_columns operator must be one of: "
                + ", ".join(sorted(SUPPORTED_COMPARISON_OPERATORS))
            )
        mode = str(rule.get("mode", "numeric")).strip().lower()
        if mode not in SUPPORTED_COMPARISON_MODES:
            raise ValidationRuleError(
                "compare_columns mode must be one of: "
                + ", ".join(sorted(SUPPORTED_COMPARISON_MODES))
            )
        normalized.update(
            {
                "left_column": left_column,
                "right_column": right_column,
                "operator": operator,
                "mode": mode,
            }
        )

    return normalized


def normalize_rules(rules: list[dict[str, Any]]) -> list[dict[str, Any]]:
    if not isinstance(rules, list):
        raise ValidationRuleError("Validation rules must be provided as a list.")
    if len(rules) > MAX_RULES:
        raise ValidationRuleError(f"A profile may contain at most {MAX_RULES} validation rules.")

    normalized = [normalize_rule(rule, position=index) for index, rule in enumerate(rules)]
    ids = [rule["id"] for rule in normalized]
    if len(ids) != len(set(ids)):
        raise ValidationRuleError("Validation rule ids must be unique within a profile.")
    return normalized


def _rule_message(rule: dict[str, Any]) -> str:
    if rule.get("message"):
        return str(rule["message"])

    column = rule["column"]
    rule_type = rule["type"]
    if rule_type == "required":
        return f"{column} must contain a value."
    if rule_type == "unique":
        return f"{column} must be unique when present."
    if rule_type == "range":
        lower = rule.get("min")
        upper = rule.get("max")
        if lower is not None and upper is not None:
            return f"{column} must be between {lower:g} and {upper:g}."
        if lower is not None:
            return f"{column} must be at least {lower:g}."
        return f"{column} must be no greater than {upper:g}."
    if rule_type == "allowed_values":
        return f"{column} must contain one of the configured allowed values."
    if rule_type == "regex":
        return f"{column} must match the configured text pattern."
    if rule_type == "date":
        return f"{column} must contain a valid date."
    if rule_type == "compare_columns":
        return (
            f"{rule['left_column']} must be {rule['operator']} {rule['right_column']} "
            f"using {rule['mode']} comparison."
        )
    return f"{column} failed validation."


def _column_positions(df: pd.DataFrame, name: str) -> list[int]:
    return [index for index, column in enumerate(df.columns) if str(column) == name]


def _decimal_value(value: Any) -> Decimal | None:
    if isinstance(value, bool):
        return None
    try:
        parsed = Decimal(str(value).strip())
    except (InvalidOperation, TypeError, ValueError):
        return None
    return parsed if parsed.is_finite() else None


def _comparison_mask(left: pd.Series, right: pd.Series, rule: dict[str, Any]) -> pd.Series:
    missing = _missing_mask(left) | _missing_mask(right)
    invalid = pd.Series(False, index=left.index)
    outcomes = pd.Series(False, index=left.index)
    mode = rule["mode"]
    for index in left.index:
        if bool(missing.loc[index]):
            continue
        left_value: Any = left.loc[index]
        right_value: Any = right.loc[index]
        if mode == "numeric":
            parsed_left = _decimal_value(left_value)
            parsed_right = _decimal_value(right_value)
            if parsed_left is None or parsed_right is None:
                invalid.loc[index] = True
                continue
            comparable_left, comparable_right = parsed_left, parsed_right
        elif mode == "date":
            if pd.api.types.is_numeric_dtype(left.dtype) or pd.api.types.is_numeric_dtype(right.dtype):
                invalid.loc[index] = True
                continue
            comparable_left = pd.to_datetime(left_value, errors="coerce")
            comparable_right = pd.to_datetime(right_value, errors="coerce")
            if pd.isna(comparable_left) or pd.isna(comparable_right):
                invalid.loc[index] = True
                continue
        else:
            comparable_left, comparable_right = str(left_value), str(right_value)

        operator = rule["operator"]
        outcomes.loc[index] = {
            "eq": comparable_left == comparable_right,
            "ne": comparable_left != comparable_right,
            "lt": comparable_left < comparable_right,
            "le": comparable_left <= comparable_right,
            "gt": comparable_left > comparable_right,
            "ge": comparable_left >= comparable_right,
        }[operator]
    return ((~missing & ~outcomes) | invalid).astype(bool)


def _evaluate_rule(series: pd.Series, rule: dict[str, Any]) -> pd.Series:
    missing = _missing_mask(series)
    rule_type = rule["type"]

    if rule_type == "required":
        return missing

    if rule_type == "unique":
        return (~missing) & series.duplicated(keep=False)

    if rule_type == "range":
        non_missing = ~missing
        numeric = pd.to_numeric(series.where(non_missing), errors="coerce")
        invalid = non_missing & numeric.isna()
        if rule.get("min") is not None:
            invalid = invalid | (non_missing & numeric.lt(rule["min"]))
        if rule.get("max") is not None:
            invalid = invalid | (non_missing & numeric.gt(rule["max"]))
        return invalid.fillna(False)

    if rule_type == "allowed_values":
        return ((~missing) & ~series.isin(rule["values"])).fillna(False)

    if rule_type == "regex":
        text = series.astype("string")
        matches = text.str.fullmatch(rule["pattern"], na=True)
        return ((~missing) & ~matches).fillna(False)

    if rule_type == "date":
        non_missing = ~missing
        if pd.api.types.is_numeric_dtype(series.dtype) and not pd.api.types.is_datetime64_any_dtype(series.dtype):
            return non_missing
        date_format = rule.get("format")
        parsed = pd.to_datetime(series.where(non_missing), format=date_format, errors="coerce")
        return (non_missing & parsed.isna()).fillna(False)

    if rule_type == "compare_columns":
        raise ValidationRuleError("compare_columns requires both referenced columns.")

    raise ValidationRuleError(f"Unsupported validation rule type: {rule_type}")


def validate_dataframe(df: pd.DataFrame, rules: list[dict[str, Any]]) -> dict[str, Any]:
    """Validate a dataframe using deterministic, user-defined rules.

    Rule references use exact column names. A rule is reported as a configuration
    error when its column is missing or ambiguous because duplicate headers exist.
    """
    normalized_rules = normalize_rules(rules)
    results: list[dict[str, Any]] = []
    all_violating_positions: set[int] = set()
    total_violations = 0
    failing_rules = 0
    configuration_errors = 0

    for rule in normalized_rules:
        positions = _column_positions(df, rule["column"])
        base = {
            "id": rule["id"],
            "type": rule["type"],
            "column": rule["column"],
            "severity": rule["severity"],
            "message": _rule_message(rule),
        }

        if not positions:
            configuration_errors += 1
            failing_rules += 1
            results.append(
                {
                    **base,
                    "status": "configuration_error",
                    "violation_count": 0,
                        "violation_pct": 0.0,
                        "row_numbers": [],
                        "all_row_numbers": [],
                        "details": "The configured column does not exist in this dataset.",
                }
            )
            continue
        if len(positions) > 1:
            configuration_errors += 1
            failing_rules += 1
            results.append(
                {
                    **base,
                    "status": "configuration_error",
                    "violation_count": 0,
                    "violation_pct": 0.0,
                    "row_numbers": [],
                    "all_row_numbers": [],
                    "details": "The configured column name is ambiguous because it appears more than once.",
                }
            )
            continue

        if rule["type"] == "compare_columns":
            left_positions = _column_positions(df, rule["left_column"])
            right_positions = _column_positions(df, rule["right_column"])
            if len(left_positions) != 1 or len(right_positions) != 1:
                configuration_errors += 1
                failing_rules += 1
                missing_names = []
                if not left_positions:
                    missing_names.append(f"left column '{rule['left_column']}' is missing")
                elif len(left_positions) > 1:
                    missing_names.append(f"left column '{rule['left_column']}' is ambiguous")
                if not right_positions:
                    missing_names.append(f"right column '{rule['right_column']}' is missing")
                elif len(right_positions) > 1:
                    missing_names.append(f"right column '{rule['right_column']}' is ambiguous")
                results.append(
                    {
                        **base,
                        "left_column": rule["left_column"],
                        "right_column": rule["right_column"],
                        "operator": rule["operator"],
                        "mode": rule["mode"],
                        "status": "configuration_error",
                        "violation_count": 0,
                        "violation_pct": 0.0,
                        "row_numbers": [],
                        "all_row_numbers": [],
                        "rows_truncated": False,
                        "details": "; ".join(missing_names),
                    }
                )
                continue
            left = df.iloc[:, left_positions[0]]
            right = df.iloc[:, right_positions[0]]
            mask = _comparison_mask(left, right, rule)
            violating_positions = [index for index, failed in enumerate(mask.tolist()) if failed]
            violation_count = len(violating_positions)
            if violation_count:
                failing_rules += 1
                total_violations += violation_count
                all_violating_positions.update(violating_positions)
            results.append(
                {
                    **base,
                    "left_column": rule["left_column"],
                    "right_column": rule["right_column"],
                    "operator": rule["operator"],
                    "mode": rule["mode"],
                    "status": "fail" if violation_count else "pass",
                    "violation_count": violation_count,
                    "violation_pct": round((violation_count / len(df) * 100) if len(df) else 0.0, 2),
                    "row_numbers": [position + 2 for position in violating_positions[:MAX_REPORTED_ROWS]],
                    "all_row_numbers": [position + 2 for position in violating_positions],
                    "rows_truncated": violation_count > MAX_REPORTED_ROWS,
                    "details": None,
                }
            )
            continue

        series = df.iloc[:, positions[0]]
        mask = _evaluate_rule(series, rule).astype(bool)
        violating_positions = [index for index, failed in enumerate(mask.tolist()) if failed]
        violation_count = len(violating_positions)
        if violation_count:
            failing_rules += 1
            total_violations += violation_count
            all_violating_positions.update(violating_positions)

        reported_rows = [position + 2 for position in violating_positions[:MAX_REPORTED_ROWS]]
        results.append(
            {
                **base,
                "status": "fail" if violation_count else "pass",
                "violation_count": violation_count,
                "violation_pct": round((violation_count / len(df) * 100) if len(df) else 0.0, 2),
                "row_numbers": reported_rows,
                "all_row_numbers": [position + 2 for position in violating_positions],
                "rows_truncated": violation_count > MAX_REPORTED_ROWS,
                "details": None,
            }
        )

    return {
        "rule_count": len(normalized_rules),
        "passed_rule_count": len(normalized_rules) - failing_rules,
        "failing_rule_count": failing_rules,
        "configuration_error_count": configuration_errors,
        "violation_count": total_violations,
        "violating_row_count": len(all_violating_positions),
        "validation_passed": failing_rules == 0,
        "results": results,
    }


def failing_rows_dataframe(df: pd.DataFrame, validation: dict[str, Any]) -> pd.DataFrame:
    """Return each failing source row once with rule IDs and human reasons."""
    failures: dict[int, dict[str, list[str]]] = {}
    for result in validation.get("results", []):
        rule_id = str(result.get("id", ""))
        reason = str(result.get("message") or result.get("details") or "Validation failed.")
        for row_number in result.get("all_row_numbers", result.get("row_numbers", [])):
            position = int(row_number) - 2
            if position < 0 or position >= len(df):
                continue
            entry = failures.setdefault(position, {"ids": [], "reasons": []})
            if rule_id not in entry["ids"]:
                entry["ids"].append(rule_id)
            if reason not in entry["reasons"]:
                entry["reasons"].append(reason)

    positions = sorted(failures)
    if not positions:
        return pd.DataFrame(
            columns=[
                *map(str, df.columns),
                "_rowspect_source_row",
                "_rowspect_failed_rule_ids",
                "_rowspect_failure_reasons",
            ]
        )

    source_rows = df.iloc[positions].copy(deep=True).reset_index(drop=True)
    source_rows.columns = [str(column) for column in source_rows.columns]
    metadata = pd.DataFrame(
        [
            {
                "_rowspect_source_row": position + 2,
                "_rowspect_failed_rule_ids": ", ".join(failures[position]["ids"]),
                "_rowspect_failure_reasons": " | ".join(failures[position]["reasons"]),
            }
            for position in positions
        ]
    )
    return pd.concat([source_rows, metadata], axis=1)

build_failing_rows = failing_rows_dataframe
