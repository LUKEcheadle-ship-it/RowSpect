import rowspect


def test_version_is_v1_3():
    assert rowspect.__version__ == "1.3.0"
    assert callable(rowspect.profile_dataframe)
    assert callable(rowspect.dataframe_to_xlsx)
