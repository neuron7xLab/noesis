"""Adaptive Intent Mirror — Finalizer-Adaptive замість фіксованого 90–110.

Виправляє padding: довжина виходу відповідає режиму складності. compression_status
тегується чесно (compressed / structured_not_compressed / expanded_by_request /
failed_compression) — «структуровано» більше не видається за «стиснуто».
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

from noesis.complexity import ComplexityProfile, estimate_complexity
from noesis.generators import build_mirror_deterministic
from tools.finalizer100 import count_words

_SHORT_REQ = ("коротко", "стисло", "tldr", "без води", "одним реченням")


@dataclass(frozen=True)
class IntentMirrorAdaptive:
    surface_intent: str
    hidden_goal: str
    constraint: str
    blocker: str
    next_action: str
    success_metric: str
    risk: str
    risk_reduction: str
    output_mode: str
    word_budget: int
    finalizer: str
    input_words: int
    output_words: int
    compression_status: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _clip(text: str, n: int) -> str:
    parts = text.split()
    return " ".join(parts[:n]) if len(parts) > n else text


def render_adaptive(raw: str, mode: str, budget: int) -> str:
    m = build_mirror_deterministic(raw)
    if mode == "micro":
        text = f"Хочеш: {_clip(m.hidden_goal, 8)}. Дія: {_clip(m.next_action, 10)}."
    elif mode == "brief":
        text = (f"Намір: {_clip(m.surface_intent, 10)}. Мета: {_clip(m.hidden_goal, 8)}. "
                f"Блокер: {_clip(m.blocker, 6)}. Дія: {_clip(m.next_action, 10)}. "
                f"Ризик: {_clip(m.critical_risk, 5)}.")
    else:
        base = (f"Явний запит — {_clip(m.surface_intent, 12)}; прихована мета — {_clip(m.hidden_goal, 10)}; "
                f"обмеження — {_clip(m.constraint, 8)}; блокер — {_clip(m.blocker, 8)}; "
                f"дія — {_clip(m.next_action, 12)}; метрика — {_clip(m.success_metric, 8)}; "
                f"ризик — {_clip(m.critical_risk, 6)}; зниження — {_clip(m.risk_reduction, 8)}.")
        if mode in ("deep", "protocol"):
            base += (f" Розгорнуто: домінантний блокер — {_clip(m.blocker, 10)}; критичний ризик — "
                     f"{_clip(m.critical_risk, 10)}; перший крок мінімізує саме його, а метрика "
                     f"{_clip(m.success_metric, 10)} робить результат перевірним за горизонт {m.time_horizon}.")
        # стеля без підлоги: тримаємо ≤ budget, але НЕ доповнюємо
        text = " ".join(base.split()[: max(budget, 1)])
    return text


def _compression_status(raw: str, output_words: int, input_words: int, mode: str) -> str:
    if output_words < input_words:
        return "compressed"
    if mode in ("deep", "protocol"):
        return "expanded_by_request"
    # Спека: при input<40 розширення виправдане структурою (не провал — вхід уже малий).
    if input_words >= 40:
        return "failed_compression"  # суттєвий вхід став довшим без виправдання
    return "structured_not_compressed"


def build_adaptive_mirror(raw: str, profile: ComplexityProfile | None = None) -> IntentMirrorAdaptive:
    profile = profile or estimate_complexity(raw)
    mode = profile.recommended_output_mode
    m = build_mirror_deterministic(raw)
    finalizer = render_adaptive(raw, mode, profile.word_budget)
    out_words = count_words(finalizer)
    status = _compression_status(raw, out_words, profile.input_words, mode)
    return IntentMirrorAdaptive(
        surface_intent=m.surface_intent,
        hidden_goal=m.hidden_goal,
        constraint=m.constraint,
        blocker=m.blocker,
        next_action=m.next_action,
        success_metric=m.success_metric,
        risk=m.critical_risk,
        risk_reduction=m.risk_reduction,
        output_mode=mode,
        word_budget=profile.word_budget,
        finalizer=finalizer,
        input_words=profile.input_words,
        output_words=out_words,
        compression_status=status,
    )
