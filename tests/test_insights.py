import pandas as pd

from rowspect.insights import correlation_matrix, missingness_table, numeric_histogram, top_values
from rowspect.profile import profile_dataframe


def test_missingness_table_only_returns_missing_columns():
    df = pd.DataFrame({"a": [1, None], "b": [1, 2]})
    table = missingness_table(profile_dataframe(df))
    assert table["column"].tolist() == ["a"]


def test_correlation_requires_two_numeric_columns():
    assert correlation_matrix(pd.DataFrame({"a": [1, 2]})).empty
    matrix = correlation_matrix(pd.DataFrame({"a": [1, 2, 3], "b": [2, 4, 6]}))
    assert matrix.loc["a", "b"] == 1.0


def test_numeric_histogram_counts_all_numeric_values():
    hist = numeric_histogram(pd.Series([1, 2, 3, 4, None]), bins=2)
    assert int(hist["count"].sum()) == 4


def test_top_values_limits_results():
    table = top_values(pd.Series(["a", "a", "b", "c"]), limit=2)
    assert table["value"].tolist() == ["a", "b"]
