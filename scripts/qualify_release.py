from __future__ import annotations

import argparse
import json
import subprocess
import sys
import tempfile
from io import BytesIO
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def _run(label: str, command: list[str]) -> None:
    print(f"[gate] {label}: {' '.join(command)}")
    result = subprocess.run(command, cwd=ROOT, text=True)
    if result.returncode != 0:
        raise SystemExit(f"Release qualification failed at: {label}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Qualify the current RowSpect checkout for release.")
    parser.add_argument(
        "--require-ui",
        action="store_true",
        help="Require the live Streamlit HTTP smoke test to pass",
    )
    args = parser.parse_args()

    _run("compile", [sys.executable, "-m", "compileall", "-q", "app.py", "rowspect", "scripts"])
    # Keep pytest fixtures isolated from stale or inaccessible system temp
    # directories on developer and CI hosts.
    with tempfile.TemporaryDirectory(prefix="rowspect-pytest-", dir=ROOT) as pytest_temp:
        _run("tests", [sys.executable, "-m", "pytest", "-q", "--basetemp", pytest_temp])
    _run("public audit", [sys.executable, "scripts/audit_public_release.py"])

    with tempfile.TemporaryDirectory(prefix="rowspect-release-", dir=ROOT) as temp_dir:
        temp = Path(temp_dir)
        wheel_dir = temp / "wheel"
        wheel_dir.mkdir()
        _run(
            "wheel build",
            [sys.executable, "-m", "pip", "wheel", "--no-deps", ".", "-w", str(wheel_dir)],
        )
        wheels = list(wheel_dir.glob("rowspect-*.whl"))
        if len(wheels) != 1:
            raise SystemExit("Release qualification failed: expected exactly one RowSpect wheel.")

        json_path = temp / "profile.json"
        html_path = temp / "report.html"
        _run(
            "cli smoke",
            [
                sys.executable,
                "-m",
                "rowspect.cli",
                "sample_data/messy_customers.csv",
                "--json",
                str(json_path),
                "--html",
                str(html_path),
            ],
        )
        payload = json.loads(json_path.read_text(encoding="utf-8"))
        if payload.get("rows") != 10 or payload.get("columns_count") != 7:
            raise SystemExit("Release qualification failed: sample profile shape changed unexpectedly.")
        if "RowSpect data quality report" not in html_path.read_text(encoding="utf-8"):
            raise SystemExit("Release qualification failed: HTML report smoke check failed.")

        validation_path = temp / "validation.json"
        _run(
            "rules profile smoke",
            [
                sys.executable,
                "-m",
                "rowspect.cli",
                "sample_data/messy_customers.csv",
                "--rules-profile",
                "sample_data/customer_rules.json",
                "--validation-json",
                str(validation_path),
                "--apply-profile-conversions",
            ],
        )
        validation = json.loads(validation_path.read_text(encoding="utf-8"))
        if validation.get("rule_count") != 5:
            raise SystemExit("Release qualification failed: reusable rule profile did not load five rules.")
        if validation.get("failing_rule_count", 0) < 1:
            raise SystemExit("Release qualification failed: bundled messy sample unexpectedly passed all custom rules.")
        if validation.get("violation_count", 0) < 1:
            raise SystemExit("Release qualification failed: bundled messy sample produced no validation violations.")

        from rowspect.rule_profiles import build_rule_profile, dump_rule_profile, load_rule_profile

        round_trip_profile = build_rule_profile(
            "Qualification profile",
            description="Serialized and reloaded during release qualification",
            rules=[
                {"id": "email-required", "type": "required", "column": "email"},
                {"id": "age-range", "type": "range", "column": "age", "min": 18, "max": 100},
            ],
            conversions=[{"id": "age-int", "column": "age", "target_type": "integer"}],
        )
        reloaded_profile = load_rule_profile(dump_rule_profile(round_trip_profile))
        if reloaded_profile["rules"] != round_trip_profile["rules"] or reloaded_profile["conversions"] != round_trip_profile["conversions"]:
            raise SystemExit("Release qualification failed: reusable profile round-trip changed rules or conversions.")
        print("[gate] reusable profile round-trip: PASS")

        # 1.3 workflow gate: comparison, cross-column rules, preserved text,
        # and one-record-per-source-row failure export.
        baseline_path = temp / "baseline.csv"
        current_path = temp / "current.csv"
        baseline_path.write_text(
            "id,start,end,code\n001,2026-01-01,2026-01-02,NA\n002,2026-01-03,2026-01-04,NULL\n",
            encoding="utf-8",
        )
        current_path.write_text(
            "id,start,end,code\n001,2026-01-01,2026-01-02,NA\n002,2026-01-03,2026-01-02,NULL\n003,2026-01-05,2026-01-06,NEW\n",
            encoding="utf-8",
        )
        comparison_path = temp / "comparison.json"
        failing_rows_path = temp / "failing-rows.csv"
        cross_profile_path = temp / "cross-rules.json"
        cross_profile_path.write_text(
            json.dumps(
                {
                    "version": 1,
                    "name": "Cross-column release gate",
                    "rules": [
                        {
                            "id": "date-order",
                            "type": "compare_columns",
                            "left_column": "start",
                            "right_column": "end",
                            "operator": "le",
                            "mode": "date",
                        },
                        {"id": "code-required", "type": "required", "column": "code"},
                    ],
                }
            ),
            encoding="utf-8",
        )
        _run(
            "1.3 comparison and failing-row CLI smoke",
            [
                sys.executable,
                "-m",
                "rowspect.cli",
                str(current_path),
                "--baseline",
                str(baseline_path),
                "--comparison-json",
                str(comparison_path),
                "--rules-profile",
                str(cross_profile_path),
                "--failing-rows",
                str(failing_rows_path),
                "--preserve-text",
            ],
        )
        comparison = json.loads(comparison_path.read_text(encoding="utf-8"))
        if comparison.get("row_count_change") != 1 or comparison.get("columns_added") != []:
            raise SystemExit("Release qualification failed: comparison smoke result changed unexpectedly.")
        failing_lines = failing_rows_path.read_text(encoding="utf-8").splitlines()
        if len(failing_lines) != 2 or "_rowspect_source_row" not in failing_lines[0]:
            raise SystemExit("Release qualification failed: failing-row export shape changed unexpectedly.")

        from rowspect.clean import clean_dataframe
        from rowspect.conversion import apply_type_conversions
        from rowspect.export import dataframe_to_csv, dataframe_to_xlsx
        from rowspect.io import RowSpectIOError, load_table, validate_upload
        import pandas as pd

        preserved = load_table(current_path.read_bytes(), current_path.name, preserve_text=True)
        if preserved.iloc[0, 0] != "001" or preserved.iloc[0, 3] != "NA":
            raise SystemExit("Release qualification failed: preserve-text CSV semantics changed.")
        converted, conversion_results = apply_type_conversions(
            load_table(b"amount\n1\n2\n", "amount.csv"),
            [{"column": "amount", "target_type": "integer"}],
        )
        if not conversion_results[0].get("applied") or str(converted["amount"].dtype) != "Int64":
            raise SystemExit("Release qualification failed: public conversion API smoke failed.")
        cleaned = clean_dataframe(preserved, drop_duplicates=True, trim_strings=True, normalize_blank_strings=True, drop_empty_rows=True)
        if len(cleaned) != 3:
            raise SystemExit("Release qualification failed: cleanup smoke failed.")
        cleaned_csv = dataframe_to_csv(cleaned)
        if len(pd.read_csv(BytesIO(cleaned_csv), keep_default_na=False)) != len(cleaned):
            raise SystemExit("Release qualification failed: cleaned CSV could not be reloaded.")
        cleaned_xlsx = dataframe_to_xlsx(cleaned)
        if len(pd.read_excel(BytesIO(cleaned_xlsx), engine="openpyxl")) != len(cleaned):
            raise SystemExit("Release qualification failed: cleaned XLSX could not be reloaded.")
        print("[gate] cleaned CSV/XLSX archive reload: PASS")
        try:
            load_table(b"a,b\n1,2,3\n", "malformed.csv")
        except RowSpectIOError:
            pass
        else:
            raise SystemExit("Release qualification failed: malformed CSV was accepted.")
        try:
            validate_upload(b"12345", "oversized.csv", max_bytes=4)
        except RowSpectIOError:
            pass
        else:
            raise SystemExit("Release qualification failed: oversized input was accepted.")

        workbook_path = temp / "multi-sheet.xlsx"

        with pd.ExcelWriter(workbook_path, engine="openpyxl") as writer:
            pd.DataFrame({"id": [1]}).to_excel(writer, sheet_name="First", index=False)
            pd.DataFrame({"id": [2]}).to_excel(writer, sheet_name="Second", index=False)
        _run(
            "multi-sheet XLSX CLI smoke",
            [sys.executable, "-m", "rowspect.cli", str(workbook_path), "--sheet", "Second"],
        )

    try:
        import streamlit  # noqa: F401
    except ImportError:
        if args.require_ui:
            raise SystemExit("Release qualification failed: Streamlit is required for strict UI qualification.")
        print("[gate] ui smoke: SKIPPED (Streamlit not installed; use --require-ui for final release)")
    else:
        _run("ui smoke", [sys.executable, "scripts/smoke_streamlit.py"])

    _run("benchmark", [sys.executable, "scripts/benchmark_profile.py", "--rows", "100000", "--numeric", "12", "--text", "8"])

    print("RowSpect release qualification PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
