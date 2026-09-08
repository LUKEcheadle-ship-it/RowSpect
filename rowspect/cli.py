from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from rowspect import __version__
from rowspect.conversion import apply_type_conversions
from rowspect.io import RowSpectIOError, get_excel_sheets, load_table
from rowspect.profile import profile_dataframe
from rowspect.report import build_html_report
from rowspect.rule_profiles import RuleProfileError, load_rule_profile
from rowspect.runtime import runtime_diagnostics
from rowspect.validation import validate_dataframe


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="rowspect",
        description="Profile and validate a local CSV or Excel file without uploading it anywhere.",
    )
    parser.add_argument("--version", action="version", version=f"RowSpect {__version__}")
    parser.add_argument(
        "--doctor",
        action="store_true",
        help="Check the local RowSpect runtime without reading a dataset",
    )
    parser.add_argument("path", nargs="?", type=Path, help="Path to a .csv or .xlsx file")
    parser.add_argument("--sheet", help="Excel worksheet name (defaults to the first sheet)")
    parser.add_argument("--json", dest="json_path", type=Path, help="Write the full generic JSON profile")
    parser.add_argument("--html", dest="html_path", type=Path, help="Write a standalone HTML report")
    parser.add_argument("--list-sheets", action="store_true", help="List Excel worksheet names and exit")
    parser.add_argument(
        "--rules-profile",
        type=Path,
        help="Apply validation rules from a reusable RowSpect JSON profile",
    )
    parser.add_argument(
        "--validation-json",
        type=Path,
        help="Write user-defined validation results to JSON (requires --rules-profile)",
    )
    parser.add_argument(
        "--apply-profile-conversions",
        action="store_true",
        help="Explicitly apply strict conversion plans stored in --rules-profile before validation",
    )
    parser.add_argument(
        "--fail-on-validation",
        action="store_true",
        help="Exit with status 1 when a configured validation rule fails",
    )
    return parser


def _run_doctor() -> int:
    diagnostics = runtime_diagnostics()
    print(f"RowSpect {__version__} runtime check")
    print(f"python={diagnostics['python']} supported={str(diagnostics['python_supported']).lower()}")
    for name, version in diagnostics["dependencies"].items():
        print(f"{name}={version or 'missing'}")
    print(f"healthy={str(diagnostics['healthy']).lower()}")
    return 0 if diagnostics["healthy"] else 2


def _load_rules_profile(path: Path) -> dict:
    try:
        data = path.read_bytes()
    except OSError as exc:
        raise RuleProfileError(f"Could not read rule profile {path}: {exc}") from exc
    return load_rule_profile(data)


def run(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.doctor:
        return _run_doctor()
    if args.path is None:
        print("RowSpect: a dataset path is required unless --doctor is used.", file=sys.stderr)
        return 2
    if args.validation_json and not args.rules_profile:
        print("RowSpect: --validation-json requires --rules-profile.", file=sys.stderr)
        return 2
    if args.apply_profile_conversions and not args.rules_profile:
        print("RowSpect: --apply-profile-conversions requires --rules-profile.", file=sys.stderr)
        return 2

    try:
        data = args.path.read_bytes()
    except OSError as exc:
        print(f"RowSpect: could not read {args.path}: {exc}", file=sys.stderr)
        return 2

    try:
        if args.list_sheets:
            if args.path.suffix.lower() != ".xlsx":
                print("RowSpect: --list-sheets is only valid for .xlsx files.", file=sys.stderr)
                return 2
            for sheet in get_excel_sheets(data):
                print(sheet)
            return 0

        df = load_table(data, args.path.name, sheet_name=args.sheet)
    except RowSpectIOError as exc:
        print(f"RowSpect: {exc}", file=sys.stderr)
        return 2

    rules_profile = None
    validation = None
    conversion_results: list[dict] = []
    if args.rules_profile:
        try:
            rules_profile = _load_rules_profile(args.rules_profile)
        except RuleProfileError as exc:
            print(f"RowSpect: {exc}", file=sys.stderr)
            return 2

        if args.apply_profile_conversions and rules_profile["conversions"]:
            df, conversion_results = apply_type_conversions(
                df,
                rules_profile["conversions"],
                strict=True,
            )
            blocked = [result for result in conversion_results if not result.get("applied")]
            if blocked:
                print("RowSpect: one or more profile conversions were blocked; dataset was not fully converted.", file=sys.stderr)
                for result in blocked:
                    print(
                        f"  {result['column']} -> {result['target_type']}: {result['status']}",
                        file=sys.stderr,
                    )
                return 2

        validation = validate_dataframe(df, rules_profile["rules"])

    profile = profile_dataframe(df)
    print(
        f"{args.path.name}: {profile['rows']} rows x {profile['columns_count']} columns | "
        f"quality {profile['quality_score']}/100 ({profile['quality_label']}) | "
        f"{profile['issue_count']} review signal(s)"
    )
    print(
        f"critical={profile['critical_count']} warning={profile['warning_count']} "
        f"info={profile['info_count']} missing={profile['missing_pct']}% duplicates={profile['duplicate_rows']}"
    )

    if rules_profile is not None and validation is not None:
        status = "PASS" if validation["validation_passed"] else "FAIL"
        print(
            f"rules-profile={rules_profile['name']} validation={status} "
            f"rules={validation['rule_count']} failing={validation['failing_rule_count']} "
            f"violations={validation['violation_count']}"
        )
        if rules_profile["conversions"] and not args.apply_profile_conversions:
            print(
                f"profile-conversions={len(rules_profile['conversions'])} not-applied "
                "(use --apply-profile-conversions to opt in)"
            )

    try:
        if args.json_path:
            args.json_path.write_text(json.dumps(profile, indent=2, ensure_ascii=False), encoding="utf-8")
        if args.html_path:
            args.html_path.write_text(build_html_report(profile, args.path.name), encoding="utf-8")
        if args.validation_json and validation is not None:
            args.validation_json.write_text(
                json.dumps(validation, indent=2, ensure_ascii=False),
                encoding="utf-8",
            )
    except OSError as exc:
        print(f"RowSpect: could not write an export file: {exc}", file=sys.stderr)
        return 2

    if args.fail_on_validation and validation is not None and not validation["validation_passed"]:
        return 1
    return 0


def main() -> None:
    raise SystemExit(run())


if __name__ == "__main__":
    main()
