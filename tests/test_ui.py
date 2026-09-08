import pandas as pd

from rowspect.ui import column_display_label, display_dataframe


def test_column_display_label_preserves_numeric_zero_header():
    assert column_display_label(0, 1) == "0"
    assert column_display_label("", 2) == "Unnamed column 2"


def test_display_dataframe_handles_lists_and_dicts_for_rule_tables():
    source = pd.DataFrame(
        {
            "parameter": [["AL", "GA"], {"min": 18, "max": 100}, None],
            "status": ["pass", "fail", "pass"],
        }
    )
    displayed = display_dataframe(source)
    assert displayed.loc[0, "parameter"] == "['AL', 'GA']"
    assert displayed.loc[1, "parameter"] == "{'min': 18, 'max': 100}"
    assert displayed.loc[2, "parameter"] is None
