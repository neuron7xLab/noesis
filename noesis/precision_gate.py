"""IEV Precision Gate — Intentional-Evidential-Validation.

Вирішує, чи когнітивний стан проходить далі: pass | fail | compress | reroute |
human_review, з precision_weight ∈ [0,1] і поясненням, ЩО змінило вагу.
Жодного автоматичного pass за «гладкий» вихід. Людина — фінальний авторитет.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import TYPE_CHECKING, Any

from noesis.forbidden import check_forbidden_claims
from tools.artifact_checker import check_artifact
from formal.metrics import falsifier_present

if TYPE_CHECKING:
    from noesis.runs import V6Run

# Маркери високих ставок → обов'язковий human_review.
_HIGH_STAKES = (
    "стосунк", "партнер", "розлуч", "розрив", "здоров", "лікар", "діагноз", "суд",
    "юрид", "контракт", "інвест", "гроші", "кредит", "хто я", "сенс життя",
)


@dataclass(frozen=True)
class GateDecision:
    decision: str  # pass | fail | compress | reroute | human_review
    precision_weight: float
    reason: str
    intent_match: float
    evidence_strength: float
    claim_safety: float
    artifact_validity: float
    noise_risk: float
    next_route: str
    required_fix: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def iev_gate(run: V6Run, noise_axes: int, expanded_axes: int) -> GateDecision:
    low = run.raw_input.lower()
    action = run.action.selected_action

    intent_match = 1.0 if any(w in action.lower() for w in run.mirror.surface_intent.lower().split()[:4]) else 0.6
    evidence_strength = 1.0 if falsifier_present(run.artifact.get("validation", "")) else 0.4
    forbidden = check_forbidden_claims(" ".join([run.raw_input, action, *run.artifact.values()]))
    claim_safety = 0.0 if forbidden else 1.0
    artifact_validity = 1.0 if not check_artifact(run.artifact) else 0.3
    noise_risk = round(noise_axes / max(expanded_axes, 1), 3)
    high_stakes = any(m in low for m in _HIGH_STAKES)

    precision_weight = round(
        0.30 * intent_match + 0.20 * evidence_strength + 0.25 * claim_safety
        + 0.15 * artifact_validity + 0.10 * (1 - noise_risk), 3)

    # Правила рішення (порядок важливий).
    if forbidden:
        return _d("fail", precision_weight, f"forbidden claim: {', '.join(forbidden)}",
                  intent_match, evidence_strength, claim_safety, artifact_validity, noise_risk,
                  "reject", "прибрати заборонений claim")
    if check_artifact(run.artifact):
        return _d("fail", precision_weight, "немає валідного артефакту",
                  intent_match, evidence_strength, claim_safety, artifact_validity, noise_risk,
                  "artifact_builder", "добудувати 7 секцій")
    if high_stakes:
        return _d("human_review", precision_weight, "високі ставки (стосунки/медицина/право/фінанси/ідентичність)",
                  intent_match, evidence_strength, claim_safety, artifact_validity, noise_risk,
                  "human_intent_controller", "людське рішення обов'язкове")
    if noise_risk > 0.6:
        return _d("compress", precision_weight, f"корисний сигнал є, але ентропія зависока (noise_risk={noise_risk})",
                  intent_match, evidence_strength, claim_safety, artifact_validity, noise_risk,
                  "compressor", "стиснути, відкинути шумові осі")
    if intent_match < 0.7:
        return _d("reroute", precision_weight, f"намір недостатньо збігається (intent_match={intent_match})",
                  intent_match, evidence_strength, claim_safety, artifact_validity, noise_risk,
                  "critic", "повернути на critic/auditor")
    return _d("pass", precision_weight, "намір збігається, claim чистий, артефакт валідний, дія ясна",
              intent_match, evidence_strength, claim_safety, artifact_validity, noise_risk,
              "memory_store", "—")


def _d(decision: str, pw: float, reason: str, im: float, es: float, cs: float, av: float,
       nr: float, route: str, fix: str) -> GateDecision:
    return GateDecision(decision, pw, reason, im, es, cs, av, nr, route, fix)
