"""Per-operator trajectory trace — the binding gap named by Role 1.

The Evidence Bundle persists final per-stage artifacts; this adds the *stepwise*
trace: one ordered record per executed operator carrying

    trace_id, state_t, operation_t, candidate_t, score_t, decision_t,
    artifact_delta_t, rollback_condition_t, state_t_plus_1

State labels are assigned so replay continuity holds by construction:
``state_t_plus_1[n] == state_t[n+1]``. A trace is invalid if any executed
operator is missing, any field is empty, the steps are not contiguous, or
continuity is broken.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

from noesis.ratios import rate

REQUIRED_FIELDS: tuple[str, ...] = (
    "trace_id",
    "state_t",
    "operation_t",
    "candidate_t",
    "score_t",
    "decision_t",
    "artifact_delta_t",
    "rollback_condition_t",
    "state_t_plus_1",
)


@dataclass(frozen=True)
class OperatorStep:
    """A single executed operator before it is placed in the trajectory."""

    operation: str
    candidate: str
    score: float
    decision: str
    artifact_delta: str
    rollback_condition: str = ""


@dataclass(frozen=True)
class TrajectoryRecord:
    trace_id: str
    step: int
    state_t: str
    operation_t: str
    candidate_t: str
    score_t: float
    decision_t: str
    artifact_delta_t: str
    rollback_condition_t: str
    state_t_plus_1: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _state_label(step: int, operation: str) -> str:
    return f"s{step}:{operation}"


def build_trajectory(trace_id: str, steps: list[OperatorStep]) -> list[TrajectoryRecord]:
    """Build a continuous trajectory; state_t_plus_1[n] == state_t[n+1] by construction."""
    records: list[TrajectoryRecord] = []
    state_t = "s0:start"
    for i, step in enumerate(steps):
        state_next = _state_label(i + 1, step.operation)
        rollback = step.rollback_condition or (
            f"schema_failure or test_failure -> restore {state_t}"
        )
        records.append(
            TrajectoryRecord(
                trace_id=trace_id,
                step=i,
                state_t=state_t,
                operation_t=step.operation,
                candidate_t=step.candidate,
                score_t=round(float(step.score), 4),
                decision_t=step.decision,
                artifact_delta_t=step.artifact_delta,
                rollback_condition_t=rollback,
                state_t_plus_1=state_next,
            )
        )
        state_t = state_next
    return records


def validate_trajectory(
    records: list[TrajectoryRecord], executed_operators: list[str]
) -> list[str]:
    """Return structured problems; empty list means the trace is complete + replayable."""
    problems: list[str] = []
    if not records:
        problems.append("TRAJECTORY_EMPTY: no records")
        return problems

    for r in records:
        for field_name in ("state_t", "operation_t", "candidate_t", "decision_t",
                           "artifact_delta_t", "rollback_condition_t", "state_t_plus_1",
                           "trace_id"):
            if not str(getattr(r, field_name)).strip():
                problems.append(f"FIELD_EMPTY: step {r.step} {field_name}")

    for i, r in enumerate(records):
        if r.step != i:
            problems.append(f"STEP_NOT_CONTIGUOUS: expected {i}, got {r.step}")
    for i in range(len(records) - 1):
        if records[i].state_t_plus_1 != records[i + 1].state_t:
            problems.append(f"CONTINUITY_BROKEN: step {i} -> {i + 1}")

    present = {r.operation_t for r in records}
    for op in executed_operators:
        if op not in present:
            problems.append(f"OPERATOR_MISSING: executed operator not traced: {op}")
    return problems


def trajectory_metrics(records: list[TrajectoryRecord]) -> dict[str, float]:
    total = len(records)
    if total == 0:
        return {"trace_completeness_rate": 0.0, "rollback_defined_rate": 0.0, "replay_continuous": 0.0}
    rollback = sum(1 for r in records if r.rollback_condition_t.strip())
    continuous = all(
        records[i].state_t_plus_1 == records[i + 1].state_t for i in range(total - 1)
    )
    complete = sum(
        1 for r in records if all(str(getattr(r, f)).strip() for f in REQUIRED_FIELDS)
    )
    return {
        "trace_completeness_rate": rate(complete, total),
        "rollback_defined_rate": rate(rollback, total),
        "replay_continuous": 1.0 if continuous else 0.0,
    }


def trajectory_to_dict(
    trace_id: str, records: list[TrajectoryRecord], executed_operators: list[str]
) -> dict[str, Any]:
    return {
        "trace_id": trace_id,
        "records": [r.to_dict() for r in records],
        "executed_operators": list(executed_operators),
        "metrics": trajectory_metrics(records),
        "valid": validate_trajectory(records, executed_operators) == [],
    }


# operator sequence the v0.8 pipeline executes, in order
V8_OPERATORS: tuple[str, ...] = (
    "intent_vector",
    "entropy_budget",
    "node_plan",
    "latency_profile",
    "iev_bandwidth",
    "precision_schedule",
    "collapse_decision",
    "cluster_quality",
    "bottleneck_plan",
    "artifact",
    "validation",
)
