from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from rowspect.io import RowSpectIOError, get_excel_sheets, load_table
from rowspect.profile import profile_dataframe
from rowspect.report import build_html_report


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="rowspect",
        description="Profile a local CSV or Excel file without uploading it anywhere.",
    )
    parser.add_argument("--version", action="version", version="RowSpect 1.0.0")
    parser.add_argument("path", type=Path, help="Path to a .csv or .xlsx file")
    parser.add_argument("--sheet", help="Excel worksheet name (defaults to the first sheet)")
    parser.add_argument("--json", dest="json_path", type=Path, help="Write the full JSON profile")
    parser.add_argument("--html", dest="html_path", type=Path, help="Write a standalone HTML report")
    parser.add_argument("--list-sheets", action="store_true", help="List Excel worksheet names and exit")
    return parser


def run(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
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
        profile = profile_dataframe(df)
    except RowSpectIOError as exc:
        print(f"RowSpect: {exc}", file=sys.stderr)
        return 2

    print(
        f"{args.path.name}: {profile['rows']} rows x {profile['columns_count']} columns | "
        f"quality {profile['quality_score']}/100 ({profile['quality_label']}) | "
        f"{profile['issue_count']} review signal(s)"
    )
    print(
        f"critical={profile['critical_count']} warning={profile['warning_count']} "
        f"info={profile['info_count']} missing={profile['missing_pct']}% duplicates={profile['duplicate_rows']}"
    )

    try:
        if args.json_path:
            args.json_path.write_text(json.dumps(profile, indent=2, ensure_ascii=False), encoding="utf-8")
        if args.html_path:
            args.html_path.write_text(build_html_report(profile, args.path.name), encoding="utf-8")
    except OSError as exc:
        print(f"RowSpect: could not write an export file: {exc}", file=sys.stderr)
        return 2
    return 0


def main() -> None:
    raise SystemExit(run())


if __name__ == "__main__":
    main()
