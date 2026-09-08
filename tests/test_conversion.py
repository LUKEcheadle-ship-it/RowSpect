import pandas as pd
import pytest

from rowspect.conversion import (
    ConversionError,
    analyze_type_conversion,
    apply_type_conversions,
    normalize_conversions,
)


def test_integer_conversion_applies_only_when_all_values_are_safe():
    df = pd.DataFrame({"age": ["10", "20", None, "30"]})
    converted, results = apply_type_conversions(
        df,
        [{"id": "age-int", "column": "age", "target_type": "integer"}],
    )
    assert results[0]["applied"] is True
    assert str(converted["age"].dtype) == "Int64"
    assert converted["age"].tolist()[:2] == [10, 20]
    assert results[0]["changed_count"] == 3


def test_strict_integer_conversion_blocks_invalid_and_fractional_values():
    df = pd.DataFrame({"age": ["10", "2.5", "bad"]})
    converted, results = apply_type_conversions(
        df,
        [{"column": "age", "target_type": "integer"}],
    )
    assert results[0]["applied"] is False
    assert results[0]["status"] == "blocked_invalid_values"
    assert results[0]["failure_count"] == 2
    assert converted["age"].tolist() == df["age"].tolist()


def test_boolean_and_date_conversion():
    df = pd.DataFrame(
        {
            "active": ["yes", "no", "TRUE", None],
            "joined": ["2026-01-01", "2026-02-02", None, "2026-03-03"],
        }
    )
    converted, results = apply_type_conversions(
        df,
        [
            {"column": "active", "target_type": "boolean"},
            {"column": "joined", "target_type": "date"},
        ],
    )
    assert all(result["applied"] for result in results)
    assert str(converted["active"].dtype) == "boolean"
    assert str(converted["joined"].dtype).startswith("datetime64")


def test_numeric_source_is_not_silently_interpreted_as_epoch_date():
    df = pd.DataFrame({"when": [20260101, 20260102]})
    converted, results = apply_type_conversions(
        df,
        [{"column": "when", "target_type": "date"}],
    )
    assert results[0]["applied"] is False
    assert results[0]["failure_count"] == 2
    assert converted["when"].tolist() == [20260101, 20260102]


def test_analysis_reports_bad_examples_without_applying():
    series = pd.Series(["1", "two", "3"])
    analysis = analyze_type_conversion(series, "float")
    assert analysis["failure_count"] == 1
    assert analysis["failure_examples"] == ["two"]
    assert analysis["safe_to_apply"] is False


def test_duplicate_column_name_blocks_conversion():
    df = pd.DataFrame([["1", "2"]], columns=["amount", "amount"])
    converted, results = apply_type_conversions(
        df,
        [{"column": "amount", "target_type": "integer"}],
    )
    assert results[0]["status"] == "ambiguous_column"
    assert results[0]["applied"] is False
    assert list(converted.columns) == ["amount", "amount"]


def test_profile_allows_only_one_conversion_per_column():
    with pytest.raises(ConversionError, match="only one conversion per column"):
        normalize_conversions(
            [
                {"column": "amount", "target_type": "float"},
                {"column": "amount", "target_type": "integer"},
            ]
        )


def test_non_strict_conversion_requires_explicit_opt_in_and_uses_missing_for_failures():
    df = pd.DataFrame({"amount": ["1.5", "bad", "2.5"]})
    converted, results = apply_type_conversions(
        df,
        [{"column": "amount", "target_type": "float"}],
        strict=False,
    )
    assert results[0]["applied"] is True
    assert pd.isna(converted.loc[1, "amount"])
