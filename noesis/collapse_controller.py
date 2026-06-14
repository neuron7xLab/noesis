"""Module 7 — Collapse Controller: коли спинити розширення й видати артефакт/дію."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

from noesis.entropy_budget import EntropyBudget
from noesis.precision_scheduler import PrecisionSchedule


@dataclass(frozen=True)
class CollapseDecision:
    collapse_now: bool
    collapse_reason: str
    selected_candidate: str
    discarded_candidates: list[str]
    retained_uncertainties: list[str]
    final_artifact_target: str
    next_action: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def decide_collapse(budget: EntropyBudget, sched: PrecisionSchedule, next_action: str,
                    discarded: list[str]) -> CollapseDecision:
    if sched.decision == "human_review":
        return CollapseDecision(False, "human_review_required", sched.candidate_id, discarded,
                                ["фінальне рішення за людиною (високі ставки)"],
                                "рішення з людським гейтом", next_action)
    if sched.decision == "fail":
        return CollapseDecision(False, "further_expansion_needed", "", discarded,
                                ["артефакт невалідний — потрібен ще цикл"], "валідний артефакт", next_action)
    reason = "artifact_ready" if sched.decision == "pass" else "entropy_too_high" if sched.decision == "compress" else "enough_signal"
    return CollapseDecision(
        collapse_now=True,
        collapse_reason=reason,
        selected_candidate=sched.candidate_id,
        discarded_candidates=discarded,
        retained_uncertainties=["шумові осі відкинуто, але невизначеність наміру лишається у людини"],
        final_artifact_target="MethodArtifact (7 секцій)",
        next_action=next_action,
    )
