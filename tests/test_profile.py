import pandas as pd

from rowspect.profile import profile_dataframe


def categories(profile):
    return {issue["category"] for issue in profile["issues"]}


def test_profile_detects_missing_blanks_and_outlier():
    df = pd.DataFrame({"name": ["A", "B", "", "B", None], "score": [10, 11, 12, 11, 1000]})
    profile = profile_dataframe(df)
    assert profile["rows"] == 5
    assert profile["missing_cells"] == 1
    assert {"missing_values", "blank_strings", "iqr_outliers"}.issubset(categories(profile))
    assert 0 <= profile["quality_score"] <= 100


def test_profile_detects_exact_duplicate_rows():
    df = pd.DataFrame({"a": [1, 2, 2], "b": ["x", "y", "y"]})
    profile = profile_dataframe(df)
    assert profile["duplicate_rows"] == 1
    assert "duplicate_rows" in categories(profile)


def test_profile_detects_numeric_text():
    profile = profile_dataframe(pd.DataFrame({"amount": ["10", "20", "30", "40"]}))
    assert "numeric_text" in categories(profile)


def test_profile_marks_empty_dataset_critical():
    profile = profile_dataframe(pd.DataFrame(columns=["a", "b"]))
    assert "empty_dataset" in categories(profile)
    assert profile["critical_count"] == 1
    assert profile["quality_score"] < 100


def test_profile_marks_all_missing_column_critical():
    profile = profile_dataframe(pd.DataFrame({"empty": [None, None], "ok": [1, 2]}))
    assert "all_missing_column" in categories(profile)
    assert profile["critical_count"] == 1


def test_profile_detects_duplicate_dataframe_columns():
    df = pd.DataFrame([[1, 2], [3, 4]])
    df.columns = ["same", "same"]
    profile = profile_dataframe(df)
    assert profile["duplicate_columns"] == 1
    assert "duplicate_columns" in categories(profile)


def test_score_label_thresholds_are_present():
    clean = profile_dataframe(pd.DataFrame({"a": [1, 2, 3], "b": ["x", "y", "z"]}))
    assert clean["quality_label"] == "Excellent"
    assert clean["quality_score"] >= 90
    assert set(clean["score_components"]) == {
        "missing_penalty",
        "duplicate_penalty",
        "blank_penalty",
        "constant_penalty",
        "outlier_penalty",
        "structural_penalty",
    }


def test_loaded_duplicate_headers_reach_profiler():
    from rowspect.io import load_table

    df = load_table(b"amount,amount\n1,2\n", "duplicate.csv")
    profile = profile_dataframe(df)
    assert profile["duplicate_columns"] == 1
    assert any(issue["category"] == "duplicate_columns" for issue in profile["issues"])


def test_comparison_reports_schema_missingness_median_and_new_categories():
    from rowspect.comparison import compare_dataframes, comparison_json

    baseline = pd.DataFrame({"amount": [10, 20], "state": ["AL", "GA"]})
    current = pd.DataFrame({"amount": [20, 40, None], "state": ["AL", "TX", "TX"], "new": [1, 2, 3]})
    result = compare_dataframes(baseline, current)
    assert result["row_count_change"] == 1
    assert result["columns_added"] == ["new"]
    assert result["quality_score_change"] < 0
    amount = next(item for item in result["column_changes"] if item["column"] == "amount")
    assert amount["numeric_median_change"] == 15.0
    state = next(item for item in result["column_changes"] if item["column"] == "state")
    assert state["new_category_examples"] == ["TX"]
    assert comparison_json(result).startswith("{")
