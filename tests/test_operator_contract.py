"""Tests for the operator contract: input -> operation -> output -> validator."""

from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path
from typing import Any

import jsonschema

from noesis.contracts import physics_boundary_validator as v

_ROOT = v.repo_root()
_OP_SCHEMA = _ROOT / "schemas" / "operator_contract.schema.json"


def _load(path: Path) -> dict[str, Any]:
    data: dict[str, Any] = json.loads(path.read_text(encoding="utf-8"))
    return data


def _report() -> dict[str, Any]:
    return deepcopy(_load(_ROOT / "data" / "physics_boundary_report.json"))


def _operators() -> list[dict[str, Any]]:
    ops: list[dict[str, Any]] = _report()["operator_map"]
    return ops


def test_every_operator_has_io_and_operation() -> None:
    for op in _operators():
        assert op["input_state"].strip()
        assert op["operation"].strip()
        assert op["output_state"].strip()


def test_keep_and_modify_operators_validate_against_schema() -> None:
    schema = _load(_OP_SCHEMA)
    for op in _operators():
        if op["decision"] in {"KEEP", "MODIFY"}:
            jsonschema.validate(instance=op, schema=schema)


def test_operator_without_repo_location_cannot_be_keep() -> None:
    for op in _operators():
        location_absent = (not op["repo_location"].strip()) or "ABSENT" in op["repo_location"]
        if location_absent:
            assert op["decision"] != "KEEP"


def test_operator_without_validator_must_be_modify_or_create() -> None:
    for op in _operators():
        has_validator = bool(op["validator"].strip()) and "MISSING" not in op["validator"]
        if not has_validator:
            assert op["decision"] in {"MODIFY", "CREATE"}


def test_validator_flags_keep_without_validator() -> None:
    report = _report()
    report["operator_map"].append(
        {
            "operator_name": "BadOperator",
            "input_state": "x",
            "operation": "y",
            "output_state": "z",
            "repo_location": "noesis/bad.py",
            "validator": "",
            "failure_mode": "none",
            "decision": "KEEP",
        }
    )
    result = v.check_operators(_ROOT, report)
    assert result.status == "FAIL"
    assert any(f.failure_code == "OPERATOR_NO_VALIDATOR" for f in result.failures)


def test_validator_flags_keep_without_location() -> None:
    report = _report()
    report["operator_map"].append(
        {
            "operator_name": "NoLocOperator",
            "input_state": "x",
            "operation": "y",
            "output_state": "z",
            "repo_location": "ABSENT",
            "validator": "tests/x.py",
            "failure_mode": "none",
            "decision": "KEEP",
        }
    )
    result = v.check_operators(_ROOT, report)
    assert any(f.failure_code == "OPERATOR_KEEP_NO_LOCATION" for f in result.failures)


def test_validator_flags_missing_io_and_bad_decision() -> None:
    report = _report()
    report["operator_map"].append(
        {
            "operator_name": "Broken",
            "input_state": "",
            "operation": "",
            "output_state": "",
            "repo_location": "noesis/x.py",
            "validator": "tests/x.py",
            "failure_mode": "none",
            "decision": "NONSENSE",
        }
    )
    result = v.check_operators(_ROOT, report)
    codes = {f.failure_code for f in result.failures}
    assert "OPERATOR_FIELD_MISSING" in codes
    assert "OPERATOR_DECISION_INVALID" in codes
