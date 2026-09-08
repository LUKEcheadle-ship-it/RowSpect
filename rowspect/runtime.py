from __future__ import annotations

import importlib.metadata
import sys
from typing import Any

REQUIRED_PACKAGES = ("pandas", "openpyxl", "streamlit")


def _version(package: str) -> str | None:
    try:
        return importlib.metadata.version(package)
    except importlib.metadata.PackageNotFoundError:
        return None


def runtime_diagnostics() -> dict[str, Any]:
    """Return non-identifying runtime diagnostics suitable for support output."""
    dependencies = {name: _version(name) for name in REQUIRED_PACKAGES}
    python_ok = sys.version_info >= (3, 11)
    deps_ok = all(version is not None for version in dependencies.values())
    return {
        "python": ".".join(str(part) for part in sys.version_info[:3]),
        "python_supported": python_ok,
        "dependencies": dependencies,
        "dependencies_available": deps_ok,
        "healthy": python_ok and deps_ok,
    }
