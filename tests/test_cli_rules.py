import json

from rowspect.cli import run
from rowspect.rule_profiles import build_rule_profile, dump_rule_profile


def test_cli_validates_with_saved_profile_and_writes_results(tmp_path, capsys):
    source = tmp_path / "customers.csv"
    source.write_text("id,age\n1,20\n2,17\n", encoding="utf-8")
    profile_path = tmp_path / "rules.json"
    profile_path.write_bytes(
        dump_rule_profile(
            build_rule_profile(
                "customer rules",
                rules=[{"id": "adult", "type": "range", "column": "age", "min": 18}],
            )
        )
    )
    validation_path = tmp_path / "validation.json"

    code = run(
        [
            str(source),
            "--rules-profile",
            str(profile_path),
            "--validation-json",
            str(validation_path),
        ]
    )
    assert code == 0
    assert "validation=FAIL" in capsys.readouterr().out
    payload = json.loads(validation_path.read_text(encoding="utf-8"))
    assert payload["failing_rule_count"] == 1
    assert payload["violation_count"] == 1


def test_cli_can_fail_pipeline_on_validation(tmp_path):
    source = tmp_path / "customers.csv"
    source.write_text("id\n1\n1\n", encoding="utf-8")
    profile_path = tmp_path / "rules.json"
    profile_path.write_bytes(
        dump_rule_profile(
            build_rule_profile(
                "unique ids",
                rules=[{"type": "unique", "column": "id"}],
            )
        )
    )
    code = run(
        [
            str(source),
            "--rules-profile",
            str(profile_path),
            "--fail-on-validation",
        ]
    )
    assert code == 1


def test_cli_profile_conversions_are_opt_in_and_strict(tmp_path, capsys):
    source = tmp_path / "customers.csv"
    source.write_text("age\n10\nbad\n", encoding="utf-8")
    profile_path = tmp_path / "rules.json"
    profile_path.write_bytes(
        dump_rule_profile(
            build_rule_profile(
                "typed ages",
                conversions=[{"column": "age", "target_type": "integer"}],
            )
        )
    )

    code_without_apply = run([str(source), "--rules-profile", str(profile_path)])
    assert code_without_apply == 0
    assert "not-applied" in capsys.readouterr().out

    code_with_apply = run(
        [
            str(source),
            "--rules-profile",
            str(profile_path),
            "--apply-profile-conversions",
        ]
    )
    assert code_with_apply == 2
    assert "conversion" in capsys.readouterr().err.lower()


def test_cli_validation_json_requires_profile(tmp_path, capsys):
    source = tmp_path / "sample.csv"
    source.write_text("a\n1\n", encoding="utf-8")
    code = run([str(source), "--validation-json", str(tmp_path / "validation.json")])
    assert code == 2
    assert "requires --rules-profile" in capsys.readouterr().err
