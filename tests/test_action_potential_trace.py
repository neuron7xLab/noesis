"""Tests for the action-potential trace runtime."""

from __future__ import annotations

import json
from pathlib import Path

import jsonschema
import pytest

from noesis.gates.discharge_gate import DischargeGate
from noesis.runtime.action_potential_trace import (
    ActionPotentialRecord,
    record_from_gate,
    trace_metrics,
    validate_payload,
    validate_record,
)

_ROOT = Path(__file__).resolve().parents[1]
_SCHEMA = json.loads(
    (_ROOT / "schemas" / "action_potential_trace.schema.json").read_text(encoding="utf-8")
)
_EXAMPLE = _ROOT / "data" / "action_potential_trace.example.json"


def _record(**overrides: object) -> ActionPotentialRecord:
    gate = DischargeGate()
    res = gate.decide(relevance=0.9, verifier=0.9, progress=0.8, cost=0.05)
    base = dict(
        trace_id="t1",
        cycle_id=0,
        state_t="s0",
        intent_delta="do X",
        unfinished_work_delta="X not done",
        gate_result=res,
        artifact_delta="wrote file X",
        rollback_condition="test_failure -> git restore X",
        state_t_plus_1="s1",
    )
    base.update(overrides)  # type: ignore[arg-type]
    return record_from_gate(**base)  # type: ignore[arg-type]


def test_record_from_gate_carries_score_and_threshold() -> None:
    rec = _record()
    assert rec.gate_score >= rec.threshold
    assert rec.decision == "PASS"
    assert validate_record(rec) == []


def test_empty_artifact_delta_fails() -> None:
    rec = _record(artifact_delta="   ")
    problems = validate_record(rec)
    assert any(p.startswith("ARTIFACT_DELTA_EMPTY") for p in problems)


def test_missing_rollback_fails() -> None:
    rec = _record(rollback_condition="")
    problems = validate_record(rec)
    assert any(p.startswith("ROLLBACK_MISSING") for p in problems)


def test_incomplete_state_fails() -> None:
    rec = _record(state_t_plus_1="")
    assert any(p.startswith("STATE_INCOMPLETE") for p in validate_record(rec))


def test_validate_payload_detects_missing_threshold_and_score() -> None:
    problems = validate_payload({"artifact_delta": "x", "rollback_condition": "y"})
    assert any(p.startswith("ACTION_NO_THRESHOLD") for p in problems)
    assert any(p.startswith("DECISION_NO_SCORE") for p in problems)
    assert any(p.startswith("FIELDS_MISSING") for p in problems)


def test_metrics_all_complete() -> None:
    records = [_record(cycle_id=i) for i in range(3)]
    m = trace_metrics(records)
    assert m["trace_completeness_rate"] == 1.0
    assert m["rollback_defined_rate"] == 1.0
    assert m["decision_explainability_rate"] == 1.0


def test_metrics_penalize_incomplete() -> None:
    records = [_record(), _record(rollback_condition="")]
    m = trace_metrics(records)
    assert m["trace_completeness_rate"] == 0.5
    assert m["rollback_defined_rate"] == 0.5


def test_metrics_empty() -> None:
    assert trace_metrics([])["trace_completeness_rate"] == 0.0


def test_example_trace_validates_against_schema() -> None:
    bundle = json.loads(_EXAMPLE.read_text(encoding="utf-8"))
    jsonschema.validate(instance=bundle, schema=_SCHEMA)
    assert bundle["metrics"]["trace_completeness_rate"] == 1.0


def test_example_has_diverse_decisions() -> None:
    bundle = json.loads(_EXAMPLE.read_text(encoding="utf-8"))
    decisions = {r["decision"] for r in bundle["records"]}
    assert "PASS" in decisions
    assert len(decisions) >= 2


def test_invalid_unit_input_rejected_by_gate() -> None:
    with pytest.raises(ValueError):
        DischargeGate().decide(relevance=2.0, verifier=0.5, progress=0.5, cost=0.5)
