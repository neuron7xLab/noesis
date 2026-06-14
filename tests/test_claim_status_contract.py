"""Tests for the claim-status contract and forbidden-claim governance."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import jsonschema

from noesis.contracts import physics_boundary_validator as v
from noesis.contracts.physics_boundary import ALLOWED_REPLACEMENTS, FORBIDDEN_CLAIMS

_ROOT = v.repo_root()
_CLAIM_SCHEMA = _ROOT / "schemas" / "claim_status_contract.schema.json"


def _load(path: Path) -> dict[str, Any]:
    data: dict[str, Any] = json.loads(path.read_text(encoding="utf-8"))
    return data


def _claims() -> list[dict[str, Any]]:
    contract = v.build_contract(_ROOT)
    rows: list[dict[str, Any]] = contract["claim_status_checked"]
    return rows


def test_every_claim_has_status_and_validates() -> None:
    schema = _load(_CLAIM_SCHEMA)
    rows = _claims()
    assert rows, "no claims checked"
    for row in rows:
        assert row["claim_status"]
        jsonschema.validate(instance=row, schema=schema)


def test_forbidden_claims_have_safe_replacement() -> None:
    for row in _claims():
        if row["claim_status"] == "X_FORBIDDEN":
            assert row["allowed_wording"].strip(), f"{row['claim_text']} lacks a safe replacement"


def test_proxy_claims_contain_proxy_wording() -> None:
    for row in _claims():
        if row["claim_status"] == "S5_PROXY":
            blob = (row["claim_text"] + " " + row["allowed_wording"]).lower()
            assert "proxy" in blob


def test_unsupported_claims_cannot_pass_release_gate() -> None:
    for row in _claims():
        if row["claim_status"] == "UNSUPPORTED":
            assert row["gate"] == "release_blocked"


def test_no_forbidden_wording_appears_in_allowed_wording() -> None:
    for row in _claims():
        forbidden = row["forbidden_wording"].lower().strip()
        allowed = row["allowed_wording"].lower()
        if forbidden:
            assert forbidden not in allowed


def test_forbidden_constants_map_to_distinct_replacements() -> None:
    for needle, replacement in FORBIDDEN_CLAIMS:
        assert needle.strip()
        assert replacement.strip()
        assert needle.lower() not in replacement.lower()
    assert ALLOWED_REPLACEMENTS
