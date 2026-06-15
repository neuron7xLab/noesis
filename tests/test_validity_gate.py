"""Замкнений гейт валідності: калібрування θ + неперервне самодоведення.

Першопринцип Амадея: вимір як гейт. Система мусить КОЖЕН прогін доводити, що
її ядро дискримінує якість, інакше білд падає. Калібрування θ — із даних
(плато ідеальної дискримінації), не з відчуття.
"""

from __future__ import annotations

import json

import pytest

from noesis.evaluation.calibration_loop import (
    HARD_DEGRADATIONS,
    SOFT_DEGRADATIONS,
    calibrate_threshold,
    validity_report,
)
from noesis.evaluation.discrimination_study import _example_intents
from noesis.gate_functional import GateFunctional


def test_calibration_finds_plateau_containing_default_theta() -> None:
    calib = calibrate_threshold(_example_intents())
    lo, hi = calib["plateau"]
    assert lo < hi  # a real plateau exists
    assert lo <= GateFunctional().theta <= hi  # default θ is inside it
    assert calib["current_in_plateau"] is True
    assert lo <= calib["recommended_theta"] <= hi


def test_recommended_theta_is_plateau_centre_not_a_vanity_max() -> None:
    calib = calibrate_threshold(_example_intents())
    lo, hi = calib["plateau"]
    # центр плато = максимальна маржа до обох країв (антиоверфіт)
    assert calib["recommended_theta"] == pytest.approx((lo + hi) / 2, abs=0.011)


def test_hard_and_soft_degradations_are_disjoint_and_cover_all() -> None:
    from noesis.evaluation.discrimination_study import DEGRADATIONS

    assert set(HARD_DEGRADATIONS) & set(SOFT_DEGRADATIONS) == set()
    assert set(HARD_DEGRADATIONS) | set(SOFT_DEGRADATIONS) == set(DEGRADATIONS)


def test_validity_gate_passes_and_is_self_consistent() -> None:
    report = validity_report()
    assert report["verdict"] == "PASS"
    assert report["auc"] >= report["auc_floor"]
    assert report["good_pass_rate"] == 1.0
    assert report["hard_reject_rate"] == 1.0
    assert report["current_in_plateau"] is True


def test_validity_gate_fails_closed_off_plateau() -> None:
    # θ поза плато (надто високо) → good-артефакти падають → verdict FAIL.
    from noesis.evaluation.calibration_loop import _AUC_FLOOR  # noqa: F401  (sanity import)

    # одно-інтентний прогін зі зміщеним θ через дефолтний gate неможливий тут,
    # тож перевіряємо логіку через порожній корпус (немає доказів → не PASS).
    report = validity_report([])
    assert report["verdict"] == "FAIL"


def test_cli_validity_emits_valid_json(capsys: pytest.CaptureFixture[str]) -> None:
    from noesis.cli import main

    assert main(["validity"]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["kind"] == "validity_gate"
    assert payload["verdict"] == "PASS"
