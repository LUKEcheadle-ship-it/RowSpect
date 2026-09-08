import json

import pytest

from rowspect.rule_profiles import (
    PROFILE_VERSION,
    RuleProfileError,
    build_rule_profile,
    dump_rule_profile,
    load_rule_profile,
)


def test_profile_round_trip_includes_rules_and_conversions():
    profile = build_rule_profile(
        "Customer import",
        description="Reusable monthly customer-data checks",
        rules=[
            {"id": "email-required", "type": "required", "column": "email"},
            {"id": "age-range", "type": "range", "column": "age", "min": 18, "max": 100},
        ],
        conversions=[
            {"id": "age-int", "column": "age", "target_type": "integer"},
        ],
    )
    loaded = load_rule_profile(dump_rule_profile(profile))
    assert loaded["version"] == PROFILE_VERSION
    assert loaded["name"] == "Customer import"
    assert len(loaded["rules"]) == 2
    assert loaded["conversions"][0]["target_type"] == "integer"


def test_profile_rejects_unknown_version_and_invalid_json():
    with pytest.raises(RuleProfileError, match="Unsupported rule profile version"):
        load_rule_profile(json.dumps({"version": 999, "name": "bad", "rules": []}))
    with pytest.raises(RuleProfileError, match="Invalid rule profile JSON"):
        load_rule_profile("{not-json")


def test_profile_rejects_duplicate_rule_ids():
    with pytest.raises(RuleProfileError, match="ids must be unique"):
        build_rule_profile(
            "bad",
            rules=[
                {"id": "same", "type": "required", "column": "a"},
                {"id": "same", "type": "required", "column": "b"},
            ],
        )
