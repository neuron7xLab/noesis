"""Tests for the Recovery Supervisor — the reversive recovery loop."""

from __future__ import annotations

import json
from pathlib import Path

import jsonschema
import pytest

from noesis.runtime.recovery_supervisor import (
    AttemptResult,
    FaultSignal,
    RecoverySupervisor,
    detect_fault,
    recovery_metrics,
    self_check,
)
from noesis.runtime.rollback import RollbackController

_SCHEMA = json.loads(
    (Path(__file__).resolve().parents[1] / "schemas" / "recovery_outcome.schema.json").read_text(
        encoding="utf-8"
    )
)


def _controller() -> RollbackController:
    c = RollbackController()
    c.checkpoint("good", {"v": 0})
    c.discharge("bad", {"v": 1})
    return c


def _reattempt(fail_until: int):  # type: ignore[no-untyped-def]
    calls = {"n": 0}

    def inner() -> AttemptResult:
        calls["n"] += 1
        return AttemptResult(ok=calls["n"] > fail_until, state_id="good", note=f"try {calls['n']}")

    return inner


def test_recovers_on_first_attempt_restores_prior_state() -> None:
    sup = RecoverySupervisor(_controller())
    outcome = sup.recover(FaultSignal("test_failure", "code_patch", "red"), _reattempt(0))
    assert outcome.status == "RECOVERED"
    assert outcome.restored_state == "good"
    assert outcome.escalated_to_human is False
    assert len(outcome.attempts) == 1


def test_recovers_after_retries() -> None:
    sup = RecoverySupervisor(_controller(), max_attempts=4)
    outcome = sup.recover(FaultSignal("schema_failure", "module_change", "red"), _reattempt(2))
    assert outcome.status == "RECOVERED"
    assert len(outcome.attempts) == 3


def test_escalates_to_human_when_budget_exhausted() -> None:
    sup = RecoverySupervisor(_controller(), max_attempts=2)
    outcome = sup.recover(FaultSignal("artifact_instability", "release_candidate", "red"), _reattempt(99))
    assert outcome.status == "ESCALATED"
    assert outcome.escalated_to_human is True
    assert len(outcome.attempts) == 2


def test_forbidden_claim_is_recoverable_fault() -> None:
    sup = RecoverySupervisor(_controller())
    outcome = sup.recover(
        FaultSignal("forbidden_claim_detected", "pull_request", "forbidden"), _reattempt(0)
    )
    assert outcome.status == "RECOVERED"


def test_state_loss_escalates() -> None:
    c = RollbackController()
    c.discharge("bad", {"v": 1})  # no checkpoint -> no prior valid
    sup = RecoverySupervisor(c)
    outcome = sup.recover(FaultSignal("test_failure", "code_patch", "red"), _reattempt(0))
    assert outcome.status == "UNRECOVERABLE"
    assert outcome.escalated_to_human is True


def test_unknown_fault_type_raises() -> None:
    sup = RecoverySupervisor(_controller())
    with pytest.raises(ValueError):
        sup.recover(FaultSignal("not_a_fault", "code_patch", "x"), _reattempt(0))


def test_zero_budget_rejected() -> None:
    with pytest.raises(ValueError):
        RecoverySupervisor(_controller(), max_attempts=0)


def test_detect_fault() -> None:
    assert detect_fault(gate_passed=True, process_alive=True, fault_type="test_failure", scale="x") is None
    fault = detect_fault(gate_passed=False, process_alive=True, fault_type="test_failure", scale="code_patch")
    assert fault is not None and fault.detail == "gate red"
    dead = detect_fault(gate_passed=True, process_alive=False, fault_type="test_failure", scale="x")
    assert dead is not None and dead.detail == "process silent"


def test_outcome_validates_against_schema() -> None:
    sup = RecoverySupervisor(_controller())
    outcome = sup.recover(FaultSignal("test_failure", "code_patch", "red"), _reattempt(0))
    jsonschema.validate(instance=outcome.to_dict(), schema=_SCHEMA)


def test_metrics_shape() -> None:
    outcomes = [
        RecoverySupervisor(_controller()).recover(FaultSignal("test_failure", "s", "r"), _reattempt(0)),
        RecoverySupervisor(_controller(), max_attempts=1).recover(
            FaultSignal("test_failure", "s", "r"), _reattempt(99)
        ),
    ]
    m = recovery_metrics(outcomes)
    assert m["recovery_success_rate"] == 0.5
    assert m["escalation_rate"] == 0.5
    assert m["mean_attempts_to_recover"] >= 1.0


def test_metrics_empty() -> None:
    assert recovery_metrics([])["recovery_success_rate"] == 0.0


def test_self_check_is_healthy() -> None:
    result = self_check()
    assert result["healthy"] is True
    assert result["statuses"] == ["RECOVERED", "RECOVERED", "ESCALATED"]
    assert result["metrics"]["recovery_success_rate"] == pytest.approx(2 / 3, abs=1e-3)
