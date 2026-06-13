"""Complexity Estimator — скільки виходу заслуговує вхід (фікс padding-проблеми).

Короткий вхід НЕ доповнюється до 90–110 слів. Режим виходу обирається за довжиною
й явним запитом користувача (коротко/протокол).
"""

from __future__ import annotations

import re
from dataclasses import asdict, dataclass
from typing import Any

from tools.finalizer100 import count_words

_WORD = re.compile(r"[\w’'-]+", re.UNICODE)
_AMBIGUITY = ("чи ", " або ", "між ", "не знаю", "не впевнен", "не розумію")
_NOISE = ("блін", "просто", "якось", "ну ", "взагалі", "типу", "знову", "постійно")
_PRESSURE = ("треба", "дедлайн", "зараз", "мушу", "горить", "терміново")
_DEEP_REQ = ("протокол", "детально", "розгорнуто", "глибоко", "повний розбір")
_SHORT_REQ = ("коротко", "стисло", "tldr", "одним реченням", "без води")

# режим → (lo, hi) бюджет слів
OUTPUT_MODES: dict[str, tuple[int, int]] = {
    "micro": (7, 20),
    "brief": (40, 80),
    "standard": (90, 140),
    "deep": (250, 600),
    "protocol": (1000, 4000),
}
_BUDGET = {"micro": 14, "brief": 60, "standard": 110, "deep": 350, "protocol": 1200}


@dataclass(frozen=True)
class ComplexityProfile:
    input_words: int
    signal_density: float
    ambiguity_level: str
    emotional_noise_level: str
    domain: str
    decision_pressure: str
    requires_theory_layer: bool
    requires_category_layer: bool
    requires_eiic: bool
    recommended_output_mode: str
    word_budget: int

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _level(n: int) -> str:
    return "high" if n >= 3 else "medium" if n >= 1 else "low"


def _mode(words: int, low: str) -> str:
    if any(r in low for r in _DEEP_REQ):
        return "protocol" if "протокол" in low else "deep"
    if any(r in low for r in _SHORT_REQ):
        return "micro"
    if words < 8:
        return "micro"
    if words < 30:
        return "brief"
    if words <= 80:
        return "standard"
    return "deep"


def estimate_complexity(raw: str) -> ComplexityProfile:
    low = raw.lower()
    words = count_words(raw)
    tokens = _WORD.findall(low)
    uniq = len({t for t in tokens if len(t) > 3})
    density = round(uniq / max(len(tokens), 1), 3)
    amb = _level(sum(1 for m in _AMBIGUITY if m in low))
    noise = _level(sum(1 for m in _NOISE if m in low))
    pressure = _level(sum(1 for m in _PRESSURE if m in low))
    mode = _mode(words, low)
    return ComplexityProfile(
        input_words=words,
        signal_density=density,
        ambiguity_level=amb,
        emotional_noise_level=noise,
        domain="general",
        decision_pressure=pressure,
        requires_theory_layer=noise != "low" or amb != "low",
        requires_category_layer=words >= 8,
        requires_eiic=mode in ("deep", "protocol") or pressure != "low",
        recommended_output_mode=mode,
        word_budget=_BUDGET[mode],
    )
