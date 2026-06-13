"""Верифікатори інваріантів: евіденція → Verdict.

Кожна функція реалізує предикат інваріанта одного конструкта поверх чистих
метрик. Пороги живуть ТУТ (точка політики), не в метриках (точка вимірювання).
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass

from formal.metrics import (
    falsifier_present,
    goodman_kruskal_gamma,
    information_sufficiency,
    problem_space_determinacy,
    semantic_disjointness,
    temporal_map_complete,
)
from tools.finalizer100 import MAX_WORDS, MIN_WORDS, REQUIRED_ANCHORS, count_words
from tools.reverse_inference import ReverseTrace

DISJOINTNESS_THRESHOLD = 0.5


@dataclass(frozen=True)
class Verdict:
    construct: str
    passed: bool
    score: float
    detail: str


def verify_reflection(judgments: Sequence[tuple[float, bool]]) -> Verdict:
    try:
        gamma = goodman_kruskal_gamma(judgments)
    except ValueError as exc:
        return Verdict("reflection", False, 0.0, f"інваріант порушено: {exc}")
    return Verdict("reflection", True, gamma, f"метакогнітивна роздільність γ={gamma:.3f}")


def verify_introspection(matching_operators: Sequence[object]) -> Verdict:
    ok = problem_space_determinacy(matching_operators)
    return Verdict(
        "introspection", ok, 1.0 if ok else 0.0,
        f"кандидатів першої дії: {len(matching_operators)} (потрібно рівно 1)",
    )


def verify_goal_regression(trace: ReverseTrace) -> Verdict:
    if not trace.missing_constraints:
        ok = "досяжна" in trace.next_action.lower()
        return Verdict("goal_regression", ok, 1.0 if ok else 0.0, "усі умови наявні → ціль досяжна")
    target = trace.missing_constraints[0]
    ok = target.lower() in trace.next_action.lower()
    return Verdict(
        "goal_regression", ok, 1.0 if ok else 0.0,
        f"soundness: next_action {'містить' if ok else 'НЕ містить'} missing[0]={target!r}",
    )


def verify_extrapolated(horizons: Mapping[str, object]) -> Verdict:
    ok = temporal_map_complete(horizons)
    return Verdict("extrapolated_thinking", ok, 1.0 if ok else 0.0,
                   "усі канонічні горизонти присутні й непорожні" if ok else "сліпий хвіст: порожній горизонт")


def verify_finalizer(text: str) -> Verdict:
    sufficiency = information_sufficiency(text, REQUIRED_ANCHORS)
    words = count_words(text)
    in_rate = MIN_WORDS <= words <= MAX_WORDS
    ok = sufficiency == 1.0 and in_rate
    return Verdict(
        "finalizer", ok, sufficiency,
        f"достатність={sufficiency:.2f}, швидкість={words} слів (межа {MIN_WORDS}-{MAX_WORDS})",
    )


def verify_insight_to_artifact(validation_section: str) -> Verdict:
    ok = falsifier_present(validation_section)
    return Verdict("insight_to_artifact", ok, 1.0 if ok else 0.0,
                   "виконуваний фальсифікатор присутній" if ok else "validation суто прозова — непроверно")


def verify_language_expansion(definition: str, anti_definition: str) -> Verdict:
    score = semantic_disjointness(definition, anti_definition)
    ok = score >= DISJOINTNESS_THRESHOLD
    return Verdict("language_expansion", ok, score,
                   f"семантична дизʼюнкція={score:.2f} (поріг {DISJOINTNESS_THRESHOLD})")
