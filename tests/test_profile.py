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
    assert clean["quality_score"] >= 95
    assert set(clean["score_components"]) == {
        "missing_penalty",
        "duplicate_penalty",
        "blank_penalty",
        "constant_penalty",
        "outlier_penalty",
        "structural_penalty",
    }
