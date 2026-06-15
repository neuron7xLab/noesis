"""Entropy Delegation Ledger — що делеговано LLM, що втримано людиною.

Розрізнення з розмови: автоматизація делегує ДІЮ; кластер делегує обчислювальну
ЕНТРОПІЮ (мислення). Фінальну відповідальність делегувати НЕ можна. Вузьке місце —
людська IEV-bandwidth + Semi-Automated Precision Layer (auditor/verifier).
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from noesis.runs import V6Run

DELEGATED_TO_LLM = (
    "variation_generation", "drafting", "counterargument", "failure_mode_search",
    "compression", "schema_filling",
)
RETAINED_BY_HUMAN = (
    "intent_vector", "contextual_judgment", "moral_responsibility",
    "final_acceptance", "life_risk_decisions",
)


@dataclass(frozen=True)
class EntropyLedger:
    delegated_to_llm: list[str]
    retained_by_human: list[str]
    delegated_entropy_score: float
    human_bottleneck_score: float
    automation_readiness: str
    danger_if_automated: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class PrecisionWeightReport:
    auditor_score: float
    verifier_score: float
    human_override_required: bool
    acceptance_threshold: float
    rejection_reason: str
    recommended_next_node: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def build_entropy_ledger(run: V6Run, gate_decision: str, high_stakes: bool) -> EntropyLedger:
    # делегована ентропія: частка контуру, винесена на LLM-вузли
    delegated_entropy_score = round(len(DELEGATED_TO_LLM) / (len(DELEGATED_TO_LLM) + len(RETAINED_BY_HUMAN)), 3)
    # людське вузьке місце: чим більше ручних рішень/перевірок, тим вище
    human_bottleneck_score = round(0.7 if gate_decision == "human_review" else 0.5, 3)
    readiness = "low" if high_stakes else "medium"
    danger = ("людина абдикує судження; LLM перевиробляє правдоподібне сміття; "
              "auditor стає церемоніальним; verifier лише штампує")
    return EntropyLedger(
        delegated_to_llm=list(DELEGATED_TO_LLM),
        retained_by_human=list(RETAINED_BY_HUMAN),
        delegated_entropy_score=delegated_entropy_score,
        human_bottleneck_score=human_bottleneck_score,
        automation_readiness=readiness,
        danger_if_automated=danger,
    )


def semi_automated_precision(run: V6Run, high_stakes: bool) -> PrecisionWeightReport:
    """Auditor/Verifier рахують precision-weights; людина — фінальний авторитет.

    ЧЕСНО (з розмови): це масштабує ПРОПУСКНУ судження, не його РОЗМІРНІСТЬ —
    поки auditor/verifier не ортогональні людині, вони клонують її prior.
    """
    contributing = sum(1 for c in run.contributions if c.contribution_score > 0)
    auditor_score = round(min(1.0, 0.4 + 0.2 * contributing), 3)  # покриття failure-mode/альтернатив
    gates = {c.name: c.passed for c in run.validation.checks}
    verifier_score = round(sum(gates.values()) / max(len(gates), 1), 3) if gates else 0.0
    human_override = high_stakes or run.flags.get("pipeline_overbuilt", False)
    return PrecisionWeightReport(
        auditor_score=auditor_score,
        verifier_score=verifier_score,
        human_override_required=human_override,
        acceptance_threshold=0.7,
        rejection_reason="високі ставки або overbuilt" if human_override else "—",
        recommended_next_node="human_intent_controller" if human_override else "memory_store",
    )
