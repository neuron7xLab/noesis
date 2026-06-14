"""Verifier for the Role 1 physics boundary report.

Reality must push back: this test loads the machine-readable boundary report and
its schema, validates one against the other, and asserts the gate conditions the
Role 1 protocol requires (score present, verdict well-formed, first missing
condition non-empty, executable Role 2 handoff, no unblocked forbidden claim).
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import jsonschema

_ROOT = Path(__file__).resolve().parents[1]
_REPORT = _ROOT / "data" / "physics_boundary_report.json"
_SCHEMA = _ROOT / "schemas" / "physics_boundary_report.schema.json"

_SCORE_KEYS = (
    "state_model",
    "constraint_model",
    "operator_model",
    "mechanism_residual_split",
    "trajectory_trace",
    "measurement_model",
    "verification_model",
    "claim_governance",
    "github_agent_readiness",
)


def _load(path: Path) -> dict[str, Any]:
    data: dict[str, Any] = json.loads(path.read_text(encoding="utf-8"))
    return data


def test_report_validates_against_schema() -> None:
    schema = _load(_SCHEMA)
    report = _load(_REPORT)
    jsonschema.validate(instance=report, schema=schema)


def test_total_score_exists_and_is_consistent() -> None:
    report = _load(_REPORT)
    score = report["quality_score"]
    assert "total" in score
    expected = sum(int(score[k]) for k in _SCORE_KEYS)
    assert score["total"] == expected, f"total {score['total']} != sum {expected}"
    assert 0 <= score["total"] <= 90


def test_verdict_is_pass_or_fail() -> None:
    report = _load(_REPORT)
    assert report["verdict"] in {"PASS", "FAIL"}


def test_first_missing_condition_not_empty() -> None:
    report = _load(_REPORT)
    assert report["first_missing_condition"].strip()


def test_role_2_handoff_has_files_and_commands() -> None:
    report = _load(_REPORT)
    handoff = report["role_2_handoff"]
    assert handoff["role_name"].strip()
    assert handoff["files_to_create"] or handoff["files_to_modify"]
    assert handoff["validation_commands"], "Role 2 handoff must carry executable commands"
    assert handoff["pass_fail_criteria"], "Role 2 handoff must carry pass/fail criteria"


def test_no_unblocked_forbidden_claim() -> None:
    report = _load(_REPORT)
    detected = report["claim_audit"]["forbidden_claims_detected"]
    assert detected == [], f"unblocked forbidden claims present: {detected}"
    for var in report["state_model"]["state_variables"]:
        assert var["status"] != "X_FORBIDDEN", f"X_FORBIDDEN state left in report: {var['name']}"


def test_pass_verdict_obeys_protocol_threshold() -> None:
    report = _load(_REPORT)
    if report["verdict"] == "PASS":
        assert report["quality_score"]["total"] >= 72
        assert report["claim_audit"]["forbidden_claims_detected"] == []
        assert report["first_missing_condition"].strip()
        assert report["role_2_handoff"]["validation_commands"]
