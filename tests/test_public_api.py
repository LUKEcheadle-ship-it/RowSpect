import rowspect


def test_version_is_v1_2():
    assert rowspect.__version__ == "1.2.0"
    assert callable(rowspect.profile_dataframe)
    assert callable(rowspect.dataframe_to_xlsx)
