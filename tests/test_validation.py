import pandas as pd
import pytest

from rowspect.validation import ValidationRuleError, normalize_rule, validate_dataframe


def test_validation_rules_cover_required_unique_range_allowed_regex_and_date():
    df = pd.DataFrame(
        {
            "id": [1, 2, 2, 4],
            "email": ["a@example.com", "bad", "", None],
            "age": [20, 17, "unknown", 40],
            "state": ["AL", "GA", "XX", "AL"],
            "joined": ["2026-01-01", "2026-02-30", "2026-03-01", "not-a-date"],
        }
    )
    rules = [
        {"id": "required-email", "type": "required", "column": "email"},
        {"id": "unique-id", "type": "unique", "column": "id"},
        {"id": "adult-age", "type": "range", "column": "age", "min": 18, "max": 100},
        {"id": "states", "type": "allowed_values", "column": "state", "values": ["AL", "GA"]},
        {"id": "email-shape", "type": "regex", "column": "email", "pattern": r"[^@\s]+@[^@\s]+\.[^@\s]+"},
        {"id": "joined-date", "type": "date", "column": "joined", "format": "%Y-%m-%d"},
    ]

    result = validate_dataframe(df, rules)
    by_id = {item["id"]: item for item in result["results"]}

    assert result["rule_count"] == 6
    assert result["failing_rule_count"] == 6
    assert by_id["required-email"]["violation_count"] == 2
    assert by_id["unique-id"]["violation_count"] == 2
    assert by_id["adult-age"]["violation_count"] == 2
    assert by_id["states"]["violation_count"] == 1
    assert by_id["email-shape"]["violation_count"] == 1
    assert by_id["joined-date"]["violation_count"] == 2
    assert by_id["required-email"]["row_numbers"] == [4, 5]


def test_missing_and_duplicate_rule_columns_are_configuration_errors():
    df = pd.DataFrame([[1, 2]], columns=["dup", "dup"])
    result = validate_dataframe(
        df,
        [
            {"id": "missing", "type": "required", "column": "nope"},
            {"id": "ambiguous", "type": "required", "column": "dup"},
        ],
    )
    assert result["configuration_error_count"] == 2
    assert {item["status"] for item in result["results"]} == {"configuration_error"}


def test_range_rule_requires_a_bound_and_regex_must_compile():
    with pytest.raises(ValidationRuleError, match="requires min"):
        normalize_rule({"type": "range", "column": "age"})
    with pytest.raises(ValidationRuleError, match="Invalid regex"):
        normalize_rule({"type": "regex", "column": "email", "pattern": "["})


def test_numeric_values_do_not_pass_date_rule_as_unix_epoch_nanoseconds():
    df = pd.DataFrame({"joined": [20260101, 20260102]})
    result = validate_dataframe(df, [{"type": "date", "column": "joined"}])
    assert result["results"][0]["violation_count"] == 2
    assert result["validation_passed"] is False


def test_validation_passes_clean_dataset():
    df = pd.DataFrame({"id": [1, 2], "state": ["AL", "GA"]})
    result = validate_dataframe(
        df,
        [
            {"type": "unique", "column": "id"},
            {"type": "allowed_values", "column": "state", "values": ["AL", "GA"]},
        ],
    )
    assert result["validation_passed"] is True
    assert result["failing_rule_count"] == 0
