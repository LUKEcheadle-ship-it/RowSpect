from rowspect.runtime import runtime_diagnostics


def test_runtime_diagnostics_do_not_include_host_identity():
    diagnostics = runtime_diagnostics()
    assert "python" in diagnostics
    assert "dependencies" in diagnostics
    assert "hostname" not in diagnostics
    assert "username" not in diagnostics
    assert set(diagnostics["dependencies"]) == {"pandas", "openpyxl", "streamlit"}
