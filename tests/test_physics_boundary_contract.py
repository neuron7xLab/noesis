"""Tests for the Role 2 physics-boundary contract layer."""

from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path
from typing import Any

import jsonschema
import pytest

from noesis.contracts import physics_boundary_cli as cli
from noesis.contracts import physics_boundary_validator as v

_ROOT = v.repo_root()
_CONTRACT_SCHEMA = _ROOT / "schemas" / "physics_boundary_contract.schema.json"
_FAILURE_KEYS = {"failure_code", "file_path", "reason", "required_fix"}


def _load(path: Path) -> dict[str, Any]:
    data: dict[str, Any] = json.loads(path.read_text(encoding="utf-8"))
    return data


def _base_report() -> dict[str, Any]:
    return deepcopy(_load(_ROOT / "data" / "physics_boundary_report.json"))


def _write_repo(tmp_path: Path, report: dict[str, Any] | None) -> Path:
    (tmp_path / "data").mkdir(parents=True, exist_ok=True)
    (tmp_path / "schemas").mkdir(parents=True, exist_ok=True)
    # copy the real report schema so schema validation can run
    (tmp_path / "schemas" / "physics_boundary_report.schema.json").write_text(
        (_ROOT / "schemas" / "physics_boundary_report.schema.json").read_text(encoding="utf-8"),
        encoding="utf-8",
    )
    if report is not None:
        (tmp_path / "data" / "physics_boundary_report.json").write_text(
            json.dumps(report, ensure_ascii=False), encoding="utf-8"
        )
    return tmp_path


def test_contract_json_and_schema_exist_and_validate() -> None:
    contract = v.write_contract(_ROOT)
    assert v.contract_path(_ROOT).exists()
    assert _CONTRACT_SCHEMA.exists()
    jsonschema.validate(instance=contract, schema=_load(_CONTRACT_SCHEMA))


def test_contract_status_is_pass_or_fail() -> None:
    contract = v.build_contract(_ROOT)
    assert contract["contract_status"] in {"PASS", "FAIL"}


def test_failures_are_structured() -> None:
    contract = v.build_contract(_ROOT)
    for failure in contract["failures"]:
        assert _FAILURE_KEYS <= set(failure)
        for value in failure.values():
            assert isinstance(value, str) and value


def test_required_state_variables_are_checked() -> None:
    contract = v.build_contract(_ROOT)
    checked = {row["name"] for row in contract["state_variables_checked"]}
    for required in v.REQUIRED_STATE_VARIABLES:
        assert required in checked


def test_required_operators_are_checked() -> None:
    contract = v.build_contract(_ROOT)
    assert contract["operators_checked"], "no operators checked"
    for op in contract["operators_checked"]:
        assert "operator_name" in op and "decision" in op


def test_role_3_handoff_exists() -> None:
    contract = v.build_contract(_ROOT)
    handoff = contract["role_3_handoff"]
    assert handoff["role_name"]
    assert handoff["validation_commands"]
    assert handoff["pass_fail_criteria"]


def test_current_tree_passes_after_trajectory_closed() -> None:
    # Role 3 implemented the per-operator trajectory trace, so the contract passes
    # and the trajectory hard-failure is gone.
    contract = v.build_contract(_ROOT)
    assert contract["contract_status"] == "PASS"
    assert "trajectory" not in contract["hard_failures"]
    assert contract["trajectory_checked"]["status"] == "PASS"
    # with all hard gates clear, Role 3 advances to benchmark + ablation
    assert contract["role_3_handoff"]["role_name"] == "BENCHMARK + ABLATION AGENT"


def test_missing_report_is_fail(tmp_path: Path) -> None:
    root = _write_repo(tmp_path, None)
    contract = v.build_contract(root)
    assert contract["contract_status"] == "FAIL"
    assert "REPORT_MISSING" in contract["hard_failures"]


def test_full_trajectory_report_passes(tmp_path: Path) -> None:
    report = _base_report()
    report["trajectory_model"]["current_trace_support"] = "FULL"
    report["trajectory_model"]["missing_trace_fields"] = []
    root = _write_repo(tmp_path, report)
    contract = v.build_contract(root)
    assert contract["trajectory_checked"]["status"] == "PASS"
    assert contract["contract_status"] == "PASS"
    assert contract["score"] == 100


def test_unblocked_forbidden_claim_hard_fails(tmp_path: Path) -> None:
    report = _base_report()
    report["claim_audit"]["forbidden_claims_detected"] = ["CME is AGI"]
    root = _write_repo(tmp_path, report)
    contract = v.build_contract(root)
    assert contract["contract_status"] == "FAIL"
    assert "forbidden_claims" in contract["hard_failures"]


def test_invalid_report_status_fails_schema(tmp_path: Path) -> None:
    report = _base_report()
    report["state_model"]["state_variables"][0]["status"] = "BOGUS"
    root = _write_repo(tmp_path, report)
    contract = v.build_contract(root)
    assert "report_schema" in contract["hard_failures"]


def test_missing_report_schema_is_missing(tmp_path: Path) -> None:
    report = _base_report()
    (tmp_path / "data").mkdir(parents=True, exist_ok=True)
    (tmp_path / "data" / "physics_boundary_report.json").write_text(
        json.dumps(report, ensure_ascii=False), encoding="utf-8"
    )
    # no schemas/ dir -> schema check MISSING
    result = v.check_report_schema(tmp_path, report)
    assert result.status == "MISSING"


def test_cli_validate_passes_on_current_tree(capsys: pytest.CaptureFixture[str]) -> None:
    code = cli.run(["validate"])
    out = capsys.readouterr().out
    assert code == 0
    assert "PHYSICS CONTRACT: PASS" in out
