"""Tests for fractal gate consistency across scales."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import jsonschema

from noesis.evaluation.fractal_gate_consistency import SCALES, check_fractal_consistency
from noesis.gates.discharge_gate import DischargeGate

_SCHEMA = json.loads(
    (
        Path(__file__).resolve().parents[1] / "schemas" / "fractal_gate_consistency.schema.json"
    ).read_text(encoding="utf-8")
)

_STRONG = {"relevance": 0.9, "verifier": 0.8, "progress": 0.8, "cost": 0.1}
_WEAK = {"relevance": 0.1, "verifier": 0.1, "progress": 0.1, "cost": 0.2}


def _all(inputs: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {scale: dict(inputs) for scale in SCALES}


def test_all_strong_passes_consistently() -> None:
    report = check_fractal_consistency(DischargeGate(), _all(_STRONG))
    assert report["status"] == "PASS"
    assert report["metrics"]["cross_scale_gate_consistency"] == 1.0
    assert report["metrics"]["false_pass_rate"] == 0.0
    assert set(report["scales"]) == set(SCALES)


def test_report_validates_against_schema() -> None:
    report = check_fractal_consistency(DischargeGate(), _all(_STRONG))
    jsonschema.validate(instance=report, schema=_SCHEMA)


def test_missing_scale_bypasses_gate() -> None:
    inputs = _all(_STRONG)
    del inputs["code_patch"]
    report = check_fractal_consistency(DischargeGate(), inputs)
    assert report["status"] == "FAIL"
    assert any(p.startswith("SCALE_BYPASSES_GATE") for p in report["problems"])


def test_scale_without_verifier_fails() -> None:
    inputs = _all(_STRONG)
    inputs["test_case"] = {"relevance": 0.9, "verifier": 0.0, "progress": 0.8, "cost": 0.1}
    report = check_fractal_consistency(DischargeGate(), inputs)
    assert report["status"] == "FAIL"
    assert any(p.startswith("SCALE_NO_VERIFIER") for p in report["problems"])


def test_release_cannot_pass_when_lower_scale_fails() -> None:
    inputs = _all(_STRONG)
    inputs["module_change"] = dict(_WEAK)  # a lower scale fails (BELOW_THRESHOLD)
    report = check_fractal_consistency(DischargeGate(), inputs)
    # release is strong -> PASS, but a lower scale failed -> false pass -> FAIL
    assert report["scales"]["release_candidate"] == "PASS"
    assert report["metrics"]["false_pass_rate"] == 1.0
    assert report["status"] == "FAIL"


def test_false_reject_detected() -> None:
    inputs = _all(_STRONG)
    inputs["release_candidate"] = dict(_WEAK)  # release rejected though all lower pass
    report = check_fractal_consistency(DischargeGate(), inputs)
    assert report["scales"]["release_candidate"] != "PASS"
    assert report["metrics"]["false_reject_rate"] == 1.0


def test_scale_failure_rate_tracks_weak_scales() -> None:
    inputs = _all(_STRONG)
    inputs["token_decision"] = dict(_WEAK)
    report = check_fractal_consistency(DischargeGate(), inputs)
    assert report["metrics"]["scale_specific_failure_rate"] > 0.0
