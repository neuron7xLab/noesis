"""Канонічна математика гейта: participation-ratio D_eff + gating-функціонал."""

from __future__ import annotations

import math

from noesis.effective_dim import effective_dimensionality, participation_ratio
from noesis.gate_functional import GateFunctional


# ── D_eff = tr(Σ)²/tr(Σ²) — стандартні тотожності ─────────────────────────────


def test_participation_ratio_identical_is_one() -> None:
    # N однакових векторів → нуль-варіація → 1.0
    assert participation_ratio([[1.0, 0.0, 0.0]] * 3) == 1.0


def test_participation_ratio_orthogonal_basis() -> None:
    # 3 ортонормальні e1,e2,e3: центрування знімає 1 ступінь → PR = 2.0 (точно)
    pr = participation_ratio([[1.0, 0, 0], [0, 1.0, 0], [0, 0, 1.0]])
    assert math.isclose(pr, 2.0, abs_tol=1e-9)


def test_participation_ratio_near_duplicate_collapses() -> None:
    pr = participation_ratio([[1.0, 0.0], [1.0, 1e-9]])
    assert pr < 1.1  # майже колапс до 1 осі


def test_effective_dimensionality_text() -> None:
    assert effective_dimensionality(["альфа бета", "альфа бета", "альфа бета"]) == 1.0
    # три тексти з неперетинним словником → 3 ортогональні вектори → D_eff=2.0
    deff = effective_dimensionality(["альфа бета", "гама дельта", "епсілон дзета"])
    assert math.isclose(deff, 2.0, abs_tol=1e-3)


def test_effective_dim_monotone_with_diversity() -> None:
    low = effective_dimensionality(["план продукт", "план продукт", "план запуск"])
    high = effective_dimensionality(["альфа бета", "гама дельта", "епсілон дзета"])
    assert high > low  # більше різноманіття → вища ефективна розмірність


# ── Gating-функціонал w(h) = αR + βV + γP − δK ───────────────────────────────


def test_gate_functional_linear_score() -> None:
    g = GateFunctional(alpha=0.4, beta=0.3, gamma=0.2, delta=0.3, theta=0.5)
    # R=1,V=1,P=1,K=0 → 0.4+0.3+0.2 = 0.9
    assert math.isclose(g.score(1, 1, 1, 0), 0.9, abs_tol=1e-9)
    assert g.accept(1, 1, 1, 0)


def test_gate_functional_cost_subtracts() -> None:
    g = GateFunctional()
    # високий K тягне нижче порога
    assert not g.accept(relevance=1, verifier=0, progress=0, cost=1)


def test_gate_functional_explain_components() -> None:
    g = GateFunctional()
    e = g.explain(1, 1, 1, 0)
    assert math.isclose(e["w"], e["alpha_R"] + e["beta_V"] + e["gamma_P"] + e["minus_delta_K"], abs_tol=1e-9)
    assert e["accept"] == 1.0
