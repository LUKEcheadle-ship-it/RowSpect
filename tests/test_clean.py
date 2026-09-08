import pandas as pd

from rowspect.clean import clean_dataframe


def test_clean_dataframe_is_conservative_and_non_mutating():
    original = pd.DataFrame(
        {
            "name": [" Alice ", " Alice ", "   ", None],
            "value": [1, 1, 2, 3],
        }
    )
    cleaned = clean_dataframe(original)

    assert original.loc[0, "name"] == " Alice "
    assert len(cleaned) == 3
    assert cleaned.loc[0, "name"] == "Alice"
    assert pd.isna(cleaned.loc[1, "name"])
