"""Closed-loop calibration + continuous validity gate for the IEV discharge gate.

First-principles automation (measure → calibrate → self-enforce), not assertion:

1. CALIBRATE — sweep θ over the discrimination study and find the *plateau* where
   every intact artifact still PASSes and every HARD degradation is rejected. The
   robust operating point is the plateau centre, not a vanity maximum.
2. SELF-ENFORCE — `validity_report` is a single fail-closed verdict (AUC, good-pass,
   hard-reject, θ-in-plateau) meant to run in CI: the system must continuously
   *prove* its core mechanism discriminates, or the build breaks.

Severity split is principled: HARD degradations (missing sections, off-topic,
stripped falsifier, injected forbidden claim) MUST be rejected; ``pad`` is SOFT
(a complete, falsifiable, on-topic artifact that is merely inflated) and is not
held against the gate — chasing it would overfit θ and erode good-artifact margin.

Mechanistic note the loop surfaces: the categorical *veto* (no falsifier / forbidden
claim) does the hard-rejection work; θ only governs the soft/margin tradeoff.
"""

from __future__ import annotations

from collections.abc import Sequence
from typing import Any

from noesis.evaluation.discrimination_study import (
    _example_intents,
    run_study,
)
from noesis.gate_functional import GateFunctional
from noesis.gates.discharge_gate import DischargeGate
from noesis.ratios import rate

# must-reject vs acceptable-to-pass
HARD_DEGRADATIONS: tuple[str, ...] = (
    "drop_sections",
    "off_topic",
    "strip_falsifier",
    "inject_forbidden",
)
SOFT_DEGRADATIONS: tuple[str, ...] = ("pad",)

_DEFAULT_THETAS: tuple[float, ...] = tuple(round(0.30 + 0.02 * i, 2) for i in range(23))  # .30..0.74
_AUC_FLOOR = 0.9


def _hard_reject_rate(per_degradation: dict[str, dict[str, float]]) -> float:
    passed = sum(per_degradation[k]["pass_rate"] for k in HARD_DEGRADATIONS)
    return round(1.0 - rate(passed, len(HARD_DEGRADATIONS)), 4)


def calibrate_threshold(
    intents: Sequence[str], thetas: Sequence[float] = _DEFAULT_THETAS
) -> dict[str, Any]:
    """Sweep θ; find the plateau where good-pass=1 ∧ hard-reject=1; recommend its centre."""
    curve: list[dict[str, float]] = []
    plateau: list[float] = []
    for theta in thetas:
        report = run_study(intents, DischargeGate(functional=GateFunctional(theta=theta)))
        good_pass = report["good_pass_rate"]
        hard_reject = _hard_reject_rate(report["per_degradation"])
        soft_pass = round(
            rate(sum(report["per_degradation"][k]["pass_rate"] for k in SOFT_DEGRADATIONS),
                 len(SOFT_DEGRADATIONS)),
            4,
        )
        curve.append(
            {
                "theta": theta,
                "good_pass_rate": good_pass,
                "hard_reject_rate": hard_reject,
                "soft_pass_rate": soft_pass,
                "good_margin": round(report["good_mean_w"] - theta, 4),
            }
        )
        if good_pass == 1.0 and hard_reject == 1.0:
            plateau.append(theta)

    if plateau:
        lo, hi = min(plateau), max(plateau)
        recommended = round((lo + hi) / 2, 4)
    else:
        lo = hi = recommended = 0.0
    return {
        "plateau": [lo, hi],
        "recommended_theta": recommended,
        "current_theta": GateFunctional().theta,
        "current_in_plateau": bool(plateau) and lo <= GateFunctional().theta <= hi,
        "curve": curve,
    }


def validity_report(intents: Sequence[str] | None = None) -> dict[str, Any]:
    """Closed-loop self-proof: discrimination AUC + calibrated θ, as a fail-closed verdict."""
    intents = list(intents) if intents is not None else _example_intents()
    study = run_study(intents)
    calib = calibrate_threshold(intents)
    hard_reject = _hard_reject_rate(study["per_degradation"])
    verdict_pass = (
        study["overall_auc"] >= _AUC_FLOOR
        and study["good_pass_rate"] == 1.0
        and hard_reject == 1.0
        and calib["current_in_plateau"]
    )
    return {
        "kind": "validity_gate",
        "verdict": "PASS" if verdict_pass else "FAIL",
        "auc": study["overall_auc"],
        "auc_floor": _AUC_FLOOR,
        "good_pass_rate": study["good_pass_rate"],
        "hard_reject_rate": hard_reject,
        "current_theta": calib["current_theta"],
        "recommended_theta": calib["recommended_theta"],
        "robust_plateau": calib["plateau"],
        "current_in_plateau": calib["current_in_plateau"],
        "n_intents": study["n_intents"],
        "soft_degradations": list(SOFT_DEGRADATIONS),
        "mechanism": "категоріальне вето (no-falsifier/forbidden) робить hard-rejection; θ керує soft/margin",
        "boundary": study["boundary"],
    }
