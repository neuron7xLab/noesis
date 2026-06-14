"""Human Eval Harness — формат для РЕАЛЬНОЇ людської оцінки без фейку.

Жодних автозаповнених людських рейтингів. Поки немає лейблів —
human_eval_status='pending'. Проксі-оцінки й людські лейбли — окремі поля.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any

PAIRWISE_QUESTIONS: tuple[str, ...] = (
    "Який вихід ясніший?",
    "Який вихід дає корисніший наступний крок?",
    "Який вихід краще уникає overclaim?",
    "Який вихід краще зберігає намір користувача?",
    "Який вихід менш шумний?",
    "Який вихід ти б реально використав?",
    "Який вихід відчувається over-engineered?",
    "Який вихід ховає невизначеність?",
)
RATING_SCHEMA: dict[str, str] = {
    "clarity": "1-5", "actionability": "1-5", "trustworthiness": "1-5",
    "overengineering": "1-5", "intent_preservation": "1-5", "claim_safety": "1-5",
    "preference": "A/B/tie",
}


def naive_baseline(raw: str) -> str:
    first = raw.strip().split(".")[0].strip()
    return f"[proxy_naive baseline] Розбий «{first[:80]}» на кроки і почни з найпростішого."


@dataclass(frozen=True)
class HumanEvalPacket:
    case_id: str
    domain: str
    raw_input: str
    baseline_output: str
    cme_full_output: str
    cme_without_category: str
    cme_without_theory: str
    cme_without_eiic: str
    cme_without_validator: str
    pairwise_questions: list[str]
    rating_schema: dict[str, str]
    blind_labels: dict[str, str]
    human_eval_status: str = "pending"
    human_labels: dict[str, Any] = field(default_factory=dict)
    baseline_source: str = "proxy_naive"

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def build_human_eval_packet(
    case_id: str, domain: str, raw: str, variants: dict[str, str]
) -> HumanEvalPacket:
    # сліпі мітки A/B детерміновано (без random): full=A, baseline=B
    blind = {"A": "cme_full", "B": "baseline"}
    return HumanEvalPacket(
        case_id=case_id,
        domain=domain,
        raw_input=raw,
        baseline_output=naive_baseline(raw),
        cme_full_output=variants.get("full", ""),
        cme_without_category=variants.get("without_category_layer", ""),
        cme_without_theory=variants.get("without_theory_layer", ""),
        cme_without_eiic=variants.get("without_eiic", ""),
        cme_without_validator=variants.get("without_validator", ""),
        pairwise_questions=list(PAIRWISE_QUESTIONS),
        rating_schema=RATING_SCHEMA,
        blind_labels=blind,
        human_eval_status="pending",
        human_labels={},
    )
