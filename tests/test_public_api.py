import rowspect


def test_version_is_v1():
    assert rowspect.__version__ == "1.0.0"
    assert callable(rowspect.profile_dataframe)
    assert callable(rowspect.dataframe_to_xlsx)
