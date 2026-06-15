"""Калібрувальний реєстр: карта порогів + виміряна функція відгуку."""

from __future__ import annotations

import json

import pytest

from noesis.calibration import (
    Knob,
    calibration_report,
    gate_operating_curve,
    gate_weight_sensitivity,
    knobs,
)
from noesis.cli import main as cli_main


def test_knobs_pull_current_values_from_source() -> None:
    from formal.verify import DISJOINTNESS_THRESHOLD
    from noesis.feedback import MIN_PAIRS
    from noesis.gate_functional import GateFunctional

    by_name = {k.name: k for k in knobs()}
    assert by_name["theta"].current == GateFunctional().theta
    assert by_name["MIN_PAIRS"].current == MIN_PAIRS
    assert by_name["DISJOINTNESS_THRESHOLD"].current == DISJOINTNESS_THRESHOLD


def test_operating_curve_pass_rate_is_non_increasing_in_theta() -> None:
    curve = gate_operating_curve()
    passes = [row["pass_rate"] for row in curve]
    assert passes == sorted(passes, reverse=True)
    assert all(0.0 <= p <= 1.0 for p in passes)


def test_weight_sensitivity_signs_are_physically_sane() -> None:
    s = gate_weight_sensitivity()
    # Більша вага корисних осей → більше PASS; вартість/поріг/floor → менше.
    assert s["alpha"] > 0 and s["beta"] > 0 and s["gamma"] > 0
    assert s["delta"] < 0 and s["theta"] < 0
    assert s["verifier_floor"] < 0 and s["risk_ceiling"] > 0
    # θ — найчутливіший знобик.
    assert abs(s["theta"]) == max(abs(v) for v in s.values())


def test_data_dependent_knobs_carry_no_fake_sensitivity() -> None:
    report = calibration_report()
    dd = report["data_dependent_knobs"]
    assert "MIN_PAIRS" in dd and "_GAP_TOLERANCE" in dd
    by_name = {k.name: k for k in knobs()}
    for name in dd:
        assert by_name[name].sensitivity is None
        assert by_name[name].note  # has an honest «потрібні дані» note


def test_calibration_report_structure() -> None:
    report = calibration_report()
    assert report["kind"] == "calibration_map"
    assert report["grid_size"] == 625
    assert len(report["knobs"]) == 15
    assert len(report["gate_operating_curve"]) == 5


def test_knob_to_dict_round_trip() -> None:
    k = Knob("x", "mod", 0.5, 0.1, 0.9, "effect", sensitivity=-0.3, note="n")
    d = k.to_dict()
    assert d["recommended_range"] == [0.1, 0.9]
    assert d["sensitivity"] == -0.3 and d["note"] == "n"


def test_cli_calibrate_emits_valid_json(capsys: pytest.CaptureFixture[str]) -> None:
    assert cli_main(["calibrate"]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["kind"] == "calibration_map"
    assert payload["knobs"]
