"""Action-potential trace runtime.

Every agent action is recorded as a gated state transition, never free-form
output:

    state_t -> potential_delta -> gate_score -> decision -> artifact_delta -> state_t+1

A record is invalid (the trace fails) if it has no threshold, no gate score, an
empty artifact_delta, or no rollback_condition. The trace is the integral of the
process — the thing that makes a run replayable and reversible.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any


@dataclass(frozen=True)
class ActionPotentialRecord:
    trace_id: str
    cycle_id: int
    state_t: str
    intent_delta: str
    unfinished_work_delta: str
    gate_score: float
    threshold: float
    decision: str
    artifact_delta: str
    rollback_condition: str
    state_t_plus_1: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def record_from_gate(
    *,
    trace_id: str,
    cycle_id: int,
    state_t: str,
    intent_delta: str,
    unfinished_work_delta: str,
    gate_result: dict[str, Any],
    artifact_delta: str,
    rollback_condition: str,
    state_t_plus_1: str,
) -> ActionPotentialRecord:
    """Build a record from a discharge-gate result (carries score + threshold + decision)."""
    return ActionPotentialRecord(
        trace_id=trace_id,
        cycle_id=cycle_id,
        state_t=state_t,
        intent_delta=intent_delta,
        unfinished_work_delta=unfinished_work_delta,
        gate_score=float(gate_result["w"]),
        threshold=float(gate_result["threshold"]),
        decision=str(gate_result["decision"]),
        artifact_delta=artifact_delta,
        rollback_condition=rollback_condition,
        state_t_plus_1=state_t_plus_1,
    )


_REQUIRED_FIELDS = (
    "trace_id",
    "cycle_id",
    "state_t",
    "intent_delta",
    "unfinished_work_delta",
    "gate_score",
    "threshold",
    "decision",
    "artifact_delta",
    "rollback_condition",
    "state_t_plus_1",
)


def validate_payload(payload: dict[str, Any]) -> list[str]:
    """Validate a raw (external) trace record dict before it becomes a typed record."""
    problems: list[str] = []
    if payload.get("threshold") is None:
        problems.append("ACTION_NO_THRESHOLD: action has no threshold")
    if payload.get("gate_score") is None:
        problems.append("DECISION_NO_SCORE: decision has no gate_score")
    if not str(payload.get("artifact_delta", "")).strip():
        problems.append("ARTIFACT_DELTA_EMPTY: artifact_delta is empty")
    if not str(payload.get("rollback_condition", "")).strip():
        problems.append("ROLLBACK_MISSING: rollback_condition is missing")
    missing = [f for f in _REQUIRED_FIELDS if f not in payload]
    if missing:
        problems.append(f"FIELDS_MISSING: {', '.join(missing)}")
    return problems


def validate_record(record: ActionPotentialRecord) -> list[str]:
    """Return structured problems; empty list means the record is complete."""
    problems: list[str] = []
    if not record.artifact_delta.strip():
        problems.append("ARTIFACT_DELTA_EMPTY: artifact_delta is empty")
    if not record.rollback_condition.strip():
        problems.append("ROLLBACK_MISSING: rollback_condition is missing")
    if not record.state_t.strip() or not record.state_t_plus_1.strip():
        problems.append("STATE_INCOMPLETE: state_t / state_t_plus_1 missing")
    return problems


def _is_explainable(record: ActionPotentialRecord) -> bool:
    return (
        isinstance(record.gate_score, float)
        and isinstance(record.threshold, float)
        and record.decision.strip() != ""
        and record.intent_delta.strip() != ""
    )


def trace_metrics(records: list[ActionPotentialRecord]) -> dict[str, float]:
    total = len(records)
    if total == 0:
        return {
            "trace_completeness_rate": 0.0,
            "rollback_defined_rate": 0.0,
            "decision_explainability_rate": 0.0,
        }
    complete = sum(1 for r in records if not validate_record(r))
    rollback = sum(1 for r in records if r.rollback_condition.strip())
    explainable = sum(1 for r in records if _is_explainable(r))
    return {
        "trace_completeness_rate": round(complete / total, 4),
        "rollback_defined_rate": round(rollback / total, 4),
        "decision_explainability_rate": round(explainable / total, 4),
    }


def trace_to_dict(trace_id: str, records: list[ActionPotentialRecord]) -> dict[str, Any]:
    return {
        "trace_id": trace_id,
        "records": [r.to_dict() for r in records],
        "metrics": trace_metrics(records),
    }
