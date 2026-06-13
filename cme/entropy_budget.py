"""Module 2 — Entropy Budget Estimator: скільки дослідження заслуговує задача."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

from cme.complexity import estimate_complexity

_HIGH_STAKES = ("стосунк", "партнер", "здоров", "лікар", "суд", "юрид", "контракт",
                "інвест", "гроші", "хто я", "сенс життя", "розлуч")


@dataclass(frozen=True)
class EntropyBudget:
    initial_state_space_size: str
    required_expansion: str
    allowed_iterations: int
    collapse_urgency: str
    risk_of_overexpansion: str
    recommended_node_count: int
    human_review_bias: bool

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def estimate_entropy_budget(raw: str) -> EntropyBudget:
    p = estimate_complexity(raw)
    mode = p.recommended_output_mode
    high_stakes = any(m in raw.lower() for m in _HIGH_STAKES)
    size = {"micro": "low", "brief": "low", "standard": "medium", "deep": "high", "protocol": "extreme"}[mode]
    expansion = {"micro": "none", "brief": "small", "standard": "moderate", "deep": "broad", "protocol": "adversarial"}[mode]
    iters = {"micro": 1, "brief": 2, "standard": 3, "deep": 5, "protocol": 8}[mode]
    nodes = {"micro": 1, "brief": 2, "standard": 3, "deep": 5, "protocol": 8}[mode]
    urgency = "after_review" if high_stakes else ("research_mode" if mode == "protocol"
              else "immediate" if mode in ("micro", "brief") else "soon")
    over_risk = "high" if mode in ("deep", "protocol") else "medium" if mode == "standard" else "low"
    return EntropyBudget(size, expansion, iters, urgency, over_risk, nodes, high_stakes)
