from __future__ import annotations

import argparse
import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


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
    with tempfile.TemporaryDirectory(prefix="rowspect-pytest-") as pytest_temp:
        _run("tests", [sys.executable, "-m", "pytest", "-q", "--basetemp", pytest_temp])
    _run("public audit", [sys.executable, "scripts/audit_public_release.py"])

    with tempfile.TemporaryDirectory(prefix="rowspect-release-") as temp_dir:
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

    try:
        import streamlit  # noqa: F401
    except ImportError:
        if args.require_ui:
            raise SystemExit("Release qualification failed: Streamlit is required for strict UI qualification.")
        print("[gate] ui smoke: SKIPPED (Streamlit not installed; use --require-ui for final release)")
    else:
        _run("ui smoke", [sys.executable, "scripts/smoke_streamlit.py"])

    print("RowSpect release qualification PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
