"""Module 6 — Precision-Weight Scheduler: коли довіряти/стискати/відхиляти/перенаправляти."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from noesis.runs import V7Run


@dataclass(frozen=True)
class PrecisionSchedule:
    candidate_id: str
    intent_match_score: float
    evidence_score: float
    novelty_score: float
    risk_score: float
    artifact_validity_score: float
    failure_mode_score: float
    precision_weight: float
    decision: str
    next_route: str
    reason: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def schedule_precision(v7: V7Run) -> PrecisionSchedule:
    g = v7.gate
    risk = round(1 - g.claim_safety, 3)
    novelty = round(min(1.0, v7.dimensionality.useful_dimensionality_gain / 5), 3)
    fm = 1.0 if v7.v6.artifact.get("failure_modes", "").strip() else 0.0
    decision_map = {"pass": "pass", "compress": "compress", "human_review": "human_review",
                    "fail": "fail", "reroute": "reroute_critic"}
    decision = decision_map.get(g.decision, g.decision)
    return PrecisionSchedule(
        candidate_id=v7.v6.action.selected_action[:32],
        intent_match_score=g.intent_match,
        evidence_score=g.evidence_strength,
        novelty_score=novelty,
        risk_score=risk,
        artifact_validity_score=g.artifact_validity,
        failure_mode_score=fm,
        precision_weight=g.precision_weight,
        decision=decision,
        next_route=g.next_route,
        reason=g.reason + " | novelty≠validity",
    )
