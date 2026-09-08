import pandas as pd

from rowspect.clean import clean_dataframe, cleanup_summary


def test_cleaning_is_conservative_and_does_not_mutate_input():
    original = pd.DataFrame({"name": ["  A ", "", "  A "], "value": [1, 2, 1]})
    snapshot = original.copy(deep=True)
    cleaned = clean_dataframe(original)
    pd.testing.assert_frame_equal(original, snapshot)
    assert cleaned["name"].tolist()[0] == "A"
    assert pd.isna(cleaned["name"].iloc[1])
    assert len(cleaned) == 2


def test_cleaning_removes_exact_duplicates_after_trimming():
    df = pd.DataFrame({"name": ["A", " A "]})
    cleaned = clean_dataframe(df)
    assert cleaned["name"].tolist() == ["A"]


def test_cleanup_summary_reports_changes():
    before = pd.DataFrame({"a": [" ", "x", "x"], "b": [None, 1, 1]})
    after = clean_dataframe(before)
    summary = cleanup_summary(before, after)
    assert summary["rows_removed"] == 2
    assert summary["blank_strings_before"] == 1
    assert summary["blank_strings_after"] == 0
