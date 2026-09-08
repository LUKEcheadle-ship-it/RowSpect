import pandas as pd

from rowspect.profile import profile_dataframe


def test_profile_detects_missing_duplicates_blanks_and_outlier():
    df = pd.DataFrame(
        {
            "name": ["A", "B", "", "B", None],
            "score": [10, 11, 12, 11, 1000],
        }
    )
    profile = profile_dataframe(df)

    assert profile["rows"] == 5
    assert profile["columns_count"] == 2
    assert profile["missing_cells"] == 1
    categories = {issue["category"] for issue in profile["issues"]}
    assert "missing_values" in categories
    assert "blank_strings" in categories
    assert "iqr_outliers" in categories
    assert 0 <= profile["quality_score"] <= 100


def test_profile_detects_exact_duplicate_rows():
    df = pd.DataFrame({"a": [1, 2, 2], "b": ["x", "y", "y"]})
    profile = profile_dataframe(df)
    assert profile["duplicate_rows"] == 1
    assert any(issue["category"] == "duplicates" for issue in profile["issues"])


def test_profile_detects_numeric_text():
    df = pd.DataFrame({"amount": ["10", "20", "30", "40"]})
    profile = profile_dataframe(df)
    assert any(issue["category"] == "numeric_text" for issue in profile["issues"])
