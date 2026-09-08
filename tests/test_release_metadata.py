from pathlib import Path
import tomllib

import rowspect

ROOT = Path(__file__).resolve().parents[1]


def test_release_versions_are_consistent():
    pyproject = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    version = pyproject["project"]["version"]
    assert version == rowspect.__version__ == "1.2.0"


def test_production_files_exist():
    expected = [
        "Dockerfile",
        ".dockerignore",
        ".streamlit/config.toml",
        "docs/DEPLOYMENT.md",
        "docs/RELEASE_CHECKLIST.md",
        "scripts/qualify_release.py",
        "scripts/smoke_streamlit.py",
        "scripts/audit_public_release.py",
        "rowspect/validation.py",
        "rowspect/conversion.py",
        "rowspect/rule_profiles.py",
    ]
    for relative in expected:
        assert (ROOT / relative).is_file(), relative


def test_runtime_requirements_are_pinned():
    requirements = (ROOT / "requirements.txt").read_text(encoding="utf-8").splitlines()
    assert requirements == [
        "pandas==2.2.3",
        "streamlit==1.63.0",
        "openpyxl==3.1.5",
    ]


def test_streamlit_config_keeps_security_controls_enabled():
    config = tomllib.loads((ROOT / ".streamlit" / "config.toml").read_text(encoding="utf-8"))
    assert config["server"]["maxUploadSize"] == 50
    assert config["server"]["enableXsrfProtection"] is True
    assert config["server"]["enableCORS"] is True
    assert config["browser"]["gatherUsageStats"] is False


def test_dockerfile_runs_as_non_root_and_has_healthcheck():
    dockerfile = (ROOT / "Dockerfile").read_text(encoding="utf-8")
    assert "USER rowspect" in dockerfile
    assert "HEALTHCHECK" in dockerfile
    assert "_stcore/health" in dockerfile


def test_ui_display_copy_disambiguates_headers_without_mutating_source():
    import pandas as pd

    from rowspect.ui import display_dataframe

    source = pd.DataFrame([[1, 2, 3], ["text", 4, 5]], columns=["dup", "dup", ""])
    displayed = display_dataframe(source)

    assert list(source.columns) == ["dup", "dup", ""]
    assert list(displayed.columns) == ["dup", "dup [2]", "Unnamed column 3"]
    assert displayed.iloc[:, 0].tolist() == ["1", "text"]
