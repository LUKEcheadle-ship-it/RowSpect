from __future__ import annotations

import ast
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RUNTIME_FILES = [ROOT / "app.py", *sorted((ROOT / "rowspect").glob("*.py"))]
FORBIDDEN_NETWORK_IMPORTS = {"requests", "httpx", "boto3", "socket", "urllib.request"}
SECRET_PATTERNS = {
    "private key": re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----"),
    "github token": re.compile(r"\b(?:ghp|github_pat)_[A-Za-z0-9_]{20,}\b"),
    "aws access key": re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
    "openai-style secret": re.compile(r"\bsk-[A-Za-z0-9_-]{20,}\b"),
}
SKIP_PARTS = {".git", ".pytest_cache", "__pycache__", ".venv", "venv", "build", "dist"}


def _runtime_imports(path: Path) -> set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    imports: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imports.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imports.add(node.module)
    return imports


def main() -> int:
    failures: list[str] = []

    for path in RUNTIME_FILES:
        for imported in _runtime_imports(path):
            if imported in FORBIDDEN_NETWORK_IMPORTS:
                failures.append(f"runtime network import {imported!r} in {path.relative_to(ROOT)}")

    for path in ROOT.rglob("*"):
        if not path.is_file() or any(part in SKIP_PARTS for part in path.parts):
            continue
        if path.name == ".env" or path.suffix.lower() in {".pem", ".key", ".p12", ".pfx"}:
            failures.append(f"sensitive file type present: {path.relative_to(ROOT)}")
            continue
        if path.suffix.lower() in {".py", ".md", ".toml", ".txt", ".yml", ".yaml", ".json", ".csv"}:
            try:
                text = path.read_text(encoding="utf-8")
            except UnicodeDecodeError:
                continue
            for label, pattern in SECRET_PATTERNS.items():
                if pattern.search(text):
                    failures.append(f"possible {label} in {path.relative_to(ROOT)}")
            if re.search(r"(?i)(?:C:\\Users\\|/home/[A-Za-z0-9._-]+/)", text):
                failures.append(f"machine-specific absolute path in {path.relative_to(ROOT)}")

    user_data_files = [
        path.relative_to(ROOT)
        for path in ROOT.rglob("*")
        if path.is_file()
        and path.suffix.lower() in {".csv", ".xlsx", ".xls"}
        and "sample_data" not in path.parts
        and not any(part in SKIP_PARTS for part in path.parts)
    ]
    if user_data_files:
        failures.append(f"non-sample data files present: {', '.join(map(str, user_data_files))}")

    if failures:
        print("RowSpect public-release audit FAIL", file=sys.stderr)
        for failure in failures:
            print(f"- {failure}", file=sys.stderr)
        return 1

    print("RowSpect public-release audit PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
