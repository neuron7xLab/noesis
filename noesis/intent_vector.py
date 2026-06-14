"""Module 1 — Intent Vector Estimator (CME v0.8).

Стабільний напрям, що мусить лишатись когерентним крізь усі проходи моделей.
Коротший за вхід; містить forbidden_drift; не мотиваційна мова.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

from noesis.generators import build_mirror_deterministic
from tools.finalizer100 import count_words

_IDENTITY = ("хто я", "сенс життя", "ким бути", "справжн")


@dataclass(frozen=True)
class IntentVector:
    core_direction: str
    non_negotiable_constraint: str
    desired_artifact: str
    forbidden_drift: str
    validation_standard: str
    time_horizon: str
    identity_relevance: str
    risk_if_distorted: str
    input_words: int
    vector_words: int

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _clip(t: str, n: int) -> str:
    p = t.split()
    return " ".join(p[:n]) if len(p) > n else t


def estimate_intent_vector(raw: str) -> IntentVector:
    m = build_mirror_deterministic(raw)
    core = _clip(m.hidden_goal, 9)
    # Вектор = СТИСНУТИЙ напрям (core_direction), не конкатенація метаполів.
    vec_text = core
    return IntentVector(
        core_direction=core,
        non_negotiable_constraint=_clip(m.constraint, 8),
        desired_artifact="перевірний MethodArtifact (7 секцій) + одна наступна дія",
        forbidden_drift="розпорошення; абстракція без дії; зміщення наміру в шум",
        validation_standard="проходить noesis validate (0 порушень), артефакт із фальсифікатором",
        time_horizon=m.time_horizon,
        identity_relevance="high" if any(k in raw.lower() for k in _IDENTITY) else "low",
        risk_if_distorted=_clip(m.critical_risk, 8),
        input_words=count_words(raw),
        vector_words=count_words(vec_text),
    )
