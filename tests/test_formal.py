"""Верифікація формального шару: метрики, інваріанти, реєстр конструктів."""

from __future__ import annotations

import pytest

from formal.constructs import MEANING_CLOSURE_AXIOM, REGISTRY
from formal.metrics import (
    CANONICAL_HORIZONS,
    falsifier_present,
    goodman_kruskal_gamma,
    information_sufficiency,
    problem_space_determinacy,
    semantic_disjointness,
    temporal_map_complete,
)
from formal.verify import (
    verify_finalizer,
    verify_goal_regression,
    verify_insight_to_artifact,
    verify_language_expansion,
    verify_reflection,
)
from tools.reverse_inference import plan_backwards

# ── γ: метакогнітивна роздільність (Nelson 1984) ──────────────────────────────


def test_gamma_perfect_calibration() -> None:
    assert goodman_kruskal_gamma([(0.9, True), (0.8, True), (0.3, False)]) == 1.0


def test_gamma_anticalibration() -> None:
    assert goodman_kruskal_gamma([(0.2, True), (0.9, False)]) == -1.0


def test_gamma_undefined_raises_on_tied_pairs() -> None:
    with pytest.raises(ValueError):
        goodman_kruskal_gamma([(0.5, True), (0.5, True)])


# ── Інформаційна достатність (Tishby et al. 1999) ─────────────────────────────


def test_information_sufficiency_full() -> None:
    assert information_sufficiency("намір мета блокер дія метрика ризик", ("намір", "ризик")) == 1.0


def test_information_sufficiency_partial() -> None:
    assert information_sufficiency("лише намір", ("намір", "ризик")) == 0.5


# ── Семантична дизʼюнкція (Katz & Fodor 1963) ─────────────────────────────────


def test_disjointness_tautology_is_zero() -> None:
    assert semantic_disjointness("вектор бажаного результату", "вектор бажаного результату") == 0.0


def test_disjointness_disjoint_is_one() -> None:
    assert semantic_disjointness("намір бажання ціль", "емоція почуття настрій") == 1.0


# ── Фальсифікованість (Popper 1959) ───────────────────────────────────────────


def test_falsifier_present_executable() -> None:
    assert falsifier_present("artifact_checker() повертає []")
    assert falsifier_present("частка зростає на 20%")


def test_falsifier_absent_prose() -> None:
    assert not falsifier_present("користувач відчуває ясність і натхнення")


# ── Часова повнота й детермінованість ─────────────────────────────────────────


def test_temporal_complete() -> None:
    assert temporal_map_complete(dict.fromkeys(CANONICAL_HORIZONS, "наслідок"))


def test_temporal_incomplete_blind_tail() -> None:
    horizons = dict.fromkeys(CANONICAL_HORIZONS, "x")
    horizons["1y"] = ""
    assert not temporal_map_complete(horizons)


def test_determinacy() -> None:
    assert problem_space_determinacy(["one_action"])
    assert not problem_space_determinacy([])
    assert not problem_space_determinacy(["a", "b"])


# ── Верифікатори (Verdict) ────────────────────────────────────────────────────


def test_verify_reflection_passes() -> None:
    v = verify_reflection([(0.9, True), (0.3, False)])
    assert v.passed and v.score == 1.0


def test_verify_goal_regression_soundness() -> None:
    trace = plan_backwards("ціль", ["a"], ["a", "b", "c"])
    v = verify_goal_regression(trace)
    assert v.passed  # next_action посилається на missing[0]


def test_verify_finalizer_round_trip() -> None:
    good = " ".join(["слово"] * 100) + " намір мета блокер дія метрика ризик"
    assert verify_finalizer(good).passed
    assert not verify_finalizer("намір мета блокер дія метрика ризик").passed  # замало слів


def test_verify_insight_to_artifact() -> None:
    assert verify_insight_to_artifact("python -m pytest повертає 0").passed
    assert not verify_insight_to_artifact("виглядає добре").passed


def test_verify_language_expansion() -> None:
    assert verify_language_expansion("намір бажання ціль", "емоція настрій").passed
    assert not verify_language_expansion("вектор результату", "вектор результату").passed


# ── Реєстр конструктів ────────────────────────────────────────────────────────


def test_registry_covers_seven_methods() -> None:
    assert len(REGISTRY) == 7
    for construct in REGISTRY.values():
        assert construct.citations  # кожен конструкт має цитування
        assert construct.invariant
        assert construct.falsifier


def test_meaning_closure_axiom_present() -> None:
    assert "⟨I, A, V⟩" in MEANING_CLOSURE_AXIOM
