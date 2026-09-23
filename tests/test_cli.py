import json

from rowspect.cli import run


def test_cli_profiles_csv_and_writes_exports(tmp_path, capsys):
    source = tmp_path / "sample.csv"
    source.write_text("a,b\n1,x\n2,y\n", encoding="utf-8")
    json_path = tmp_path / "profile.json"
    html_path = tmp_path / "report.html"
    code = run([str(source), "--json", str(json_path), "--html", str(html_path)])
    assert code == 0
    assert "quality" in capsys.readouterr().out
    payload = json.loads(json_path.read_text(encoding="utf-8"))
    assert payload["rows"] == 2
    assert "RowSpect data quality report" in html_path.read_text(encoding="utf-8")


def test_cli_missing_file_returns_2(tmp_path, capsys):
    code = run([str(tmp_path / "missing.csv")])
    assert code == 2
    assert "could not read" in capsys.readouterr().err


def test_cli_export_write_error_returns_2(tmp_path, capsys):
    source = tmp_path / "sample.csv"
    source.write_text("a\n1\n", encoding="utf-8")
    code = run([str(source), "--json", str(tmp_path / "missing-dir" / "out.json")])
    assert code == 2
    assert "could not write" in capsys.readouterr().err


def test_cli_doctor_healthy(monkeypatch, capsys):
    monkeypatch.setattr(
        "rowspect.cli.runtime_diagnostics",
        lambda: {
            "python": "3.12.0",
            "python_supported": True,
            "dependencies": {"pandas": "2.2.3", "openpyxl": "3.1.5", "streamlit": "1.63.0"},
            "dependencies_available": True,
            "healthy": True,
        },
    )
    code = run(["--doctor"])
    assert code == 0
    output = capsys.readouterr().out
    assert "runtime check" in output
    assert "healthy=true" in output


def test_cli_requires_path_without_doctor(capsys):
    code = run([])
    assert code == 2
    assert "dataset path is required" in capsys.readouterr().err


def test_cli_comparison_and_input_overwrite_protection(tmp_path, capsys):
    baseline = tmp_path / "baseline.csv"
    current = tmp_path / "current.csv"
    comparison_path = tmp_path / "comparison.json"
    baseline.write_text("id,state\n001,A\n002,B\n", encoding="utf-8")
    current.write_text("id,state\n001,A\n002,C\n003,C\n", encoding="utf-8")
    assert run([str(current), "--baseline", str(baseline), "--comparison-json", str(comparison_path)]) == 0
    assert "comparison=" in capsys.readouterr().out
    assert '"row_count_change": 1' in comparison_path.read_text(encoding="utf-8")

    assert run([str(current), "--json", str(current)]) == 2
    assert "must not overwrite" in capsys.readouterr().err
