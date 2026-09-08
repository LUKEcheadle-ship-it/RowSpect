from rowspect.io import load_table


def test_load_csv_from_bytes():
    df = load_table(b"a,b\n1,x\n2,y\n", "sample.csv")
    assert df.shape == (2, 2)
    assert df["a"].tolist() == [1, 2]
