from __future__ import annotations

import json
from typing import Any

from rowspect.conversion import ConversionError, normalize_conversions
from rowspect.validation import ValidationRuleError, normalize_rules

PROFILE_VERSION = 1
MAX_PROFILE_BYTES = 256 * 1024


class RuleProfileError(ValueError):
    """Raised when a reusable RowSpect validation profile is invalid."""


def normalize_rule_profile(profile: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(profile, dict):
        raise RuleProfileError("A RowSpect rule profile must be a JSON object.")

    version = profile.get("version", PROFILE_VERSION)
    if version != PROFILE_VERSION:
        raise RuleProfileError(
            f"Unsupported rule profile version {version!r}; expected {PROFILE_VERSION}."
        )

    name = profile.get("name", "RowSpect validation profile")
    if not isinstance(name, str) or not name.strip():
        raise RuleProfileError("A rule profile requires a non-empty name.")
    if len(name) > 120:
        raise RuleProfileError("Rule profile names are limited to 120 characters.")

    description = profile.get("description", "")
    if not isinstance(description, str) or len(description) > 1000:
        raise RuleProfileError("Rule profile description must be text no longer than 1000 characters.")

    try:
        rules = normalize_rules(profile.get("rules", []))
        conversions = normalize_conversions(profile.get("conversions", []))
    except (ValidationRuleError, ConversionError) as exc:
        raise RuleProfileError(str(exc)) from exc

    return {
        "version": PROFILE_VERSION,
        "name": name.strip(),
        "description": description.strip(),
        "rules": rules,
        "conversions": conversions,
    }


def load_rule_profile(data: bytes | str) -> dict[str, Any]:
    if isinstance(data, bytes):
        if len(data) > MAX_PROFILE_BYTES:
            raise RuleProfileError(
                f"Rule profiles are limited to {MAX_PROFILE_BYTES // 1024} KB."
            )
        try:
            text = data.decode("utf-8")
        except UnicodeDecodeError as exc:
            raise RuleProfileError("Rule profile JSON must use UTF-8 encoding.") from exc
    else:
        text = data
        if len(text.encode("utf-8")) > MAX_PROFILE_BYTES:
            raise RuleProfileError(
                f"Rule profiles are limited to {MAX_PROFILE_BYTES // 1024} KB."
            )

    try:
        payload = json.loads(text)
    except json.JSONDecodeError as exc:
        raise RuleProfileError(f"Invalid rule profile JSON: {exc.msg}") from exc
    return normalize_rule_profile(payload)


def dump_rule_profile(profile: dict[str, Any], *, indent: int = 2) -> bytes:
    normalized = normalize_rule_profile(profile)
    return json.dumps(normalized, indent=indent, ensure_ascii=False).encode("utf-8")


def build_rule_profile(
    name: str,
    *,
    rules: list[dict[str, Any]] | None = None,
    conversions: list[dict[str, Any]] | None = None,
    description: str = "",
) -> dict[str, Any]:
    return normalize_rule_profile(
        {
            "version": PROFILE_VERSION,
            "name": name,
            "description": description,
            "rules": rules or [],
            "conversions": conversions or [],
        }
    )
