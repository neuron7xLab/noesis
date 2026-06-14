"""Tests for the per-operator trajectory trace (Role 3)."""

from __future__ import annotations

import json
from pathlib import Path

import jsonschema

from noesis.pipeline_v8 import run_and_save_v8
from noesis.trajectory import (
    V8_OPERATORS,
    OperatorStep,
    build_trajectory,
    trajectory_metrics,
    trajectory_to_dict,
    validate_trajectory,
)

_ROOT = Path(__file__).resolve().parents[1]
_SCHEMA = json.loads(
    (_ROOT / "schemas" / "trajectory_trace.schema.json").read_text(encoding="utf-8")
)
_RAW = "хочу запустити продукт але застряг між напрямками"


def _steps(n: int = 3) -> list[OperatorStep]:
    return [
        OperatorStep(f"op{i}", f"candidate {i}", 0.8, "PASS", f"art{i}.json")
        for i in range(n)
    ]


def test_build_is_replay_continuous() -> None:
    records = build_trajectory("t1", _steps(4))
    for i in range(len(records) - 1):
        assert records[i].state_t_plus_1 == records[i + 1].state_t


def test_all_required_fields_present() -> None:
    rec = build_trajectory("t1", _steps(1))[0]
    for f in ("trace_id", "state_t", "operation_t", "candidate_t", "score_t",
              "decision_t", "artifact_delta_t", "rollback_condition_t", "state_t_plus_1"):
        assert str(getattr(rec, f)).strip()
    assert rec.state_t == "s0:start"


def test_default_rollback_condition_filled() -> None:
    rec = build_trajectory("t1", [OperatorStep("op", "c", 0.5, "PASS", "a.json")])[0]
    assert rec.rollback_condition_t.strip()


def test_validate_passes_when_all_operators_traced() -> None:
    steps = [OperatorStep(op, "c", 0.7, "PASS", f"{op}.json") for op in ("a", "b", "c")]
    records = build_trajectory("t1", steps)
    assert validate_trajectory(records, ["a", "b", "c"]) == []


def test_missing_executed_operator_fails() -> None:
    records = build_trajectory("t1", _steps(2))  # op0, op1
    problems = validate_trajectory(records, ["op0", "op1", "op_never_traced"])
    assert any(p.startswith("OPERATOR_MISSING") for p in problems)


def test_broken_continuity_detected() -> None:
    records = build_trajectory("t1", _steps(3))
    tampered = [records[0], records[2]]  # skip step 1 -> continuity break + step gap
    problems = validate_trajectory(tampered, [])
    assert any(p.startswith("CONTINUITY_BROKEN") or p.startswith("STEP_NOT_CONTIGUOUS") for p in problems)


def test_empty_trajectory_fails() -> None:
    assert validate_trajectory([], ["a"]) == ["TRAJECTORY_EMPTY: no records"]


def test_metrics_full() -> None:
    m = trajectory_metrics(build_trajectory("t1", _steps(5)))
    assert m["trace_completeness_rate"] == 1.0
    assert m["rollback_defined_rate"] == 1.0
    assert m["replay_continuous"] == 1.0


def test_metrics_empty() -> None:
    assert trajectory_metrics([])["replay_continuous"] == 0.0


def test_to_dict_validates_against_schema() -> None:
    bundle = trajectory_to_dict("t1", build_trajectory("t1", _steps(3)), ["op0", "op1", "op2"])
    jsonschema.validate(instance=bundle, schema=_SCHEMA)
    assert bundle["valid"] is True


def test_pipeline_v8_emits_valid_trajectory(tmp_path: Path) -> None:
    run_and_save_v8(_RAW, tmp_path)
    bundle = json.loads((tmp_path / "trajectory_trace.json").read_text(encoding="utf-8"))
    jsonschema.validate(instance=bundle, schema=_SCHEMA)
    assert bundle["valid"] is True
    traced = {r["operation_t"] for r in bundle["records"]}
    assert set(V8_OPERATORS) <= traced
    assert bundle["metrics"]["replay_continuous"] == 1.0
