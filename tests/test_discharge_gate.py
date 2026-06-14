"""Tests for the gated discharge equation w = aR + bV + gP - dK."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import jsonschema
import pytest

from noesis.gates.discharge_gate import DECISIONS, DischargeGate, gate_metrics

_ROOT = Path(__file__).resolve().parents[1]
_SCHEMA = json.loads((_ROOT / "schemas" / "discharge_gate.schema.json").read_text(encoding="utf-8"))


def _gate() -> DischargeGate:
    return DischargeGate()


def test_pass_when_strong_and_cheap() -> None:
    r = _gate().decide(relevance=0.9, verifier=0.9, progress=0.8, cost=0.05)
    assert r["decision"] == "PASS"
    assert r["w"] >= r["threshold"]


def test_below_threshold_when_weak() -> None:
    r = _gate().decide(relevance=0.1, verifier=0.1, progress=0.1, cost=0.2)
    assert r["decision"] == "BELOW_THRESHOLD"
    assert r["w"] < r["threshold"]


def test_reroute_when_score_high_but_verifier_below_floor() -> None:
    r = _gate().decide(relevance=1.0, verifier=0.2, progress=1.0, cost=0.0)
    assert r["w"] >= r["threshold"]
    assert r["decision"] == "REROUTE"


def test_human_review_when_risk_exceeds_ceiling() -> None:
    r = _gate().decide(relevance=0.9, verifier=0.9, progress=0.9, cost=0.95)
    assert r["decision"] == "HUMAN_REVIEW"


def test_fail_when_verifier_failed() -> None:
    r = _gate().decide(relevance=0.9, verifier=0.9, progress=0.9, cost=0.0, verifier_failed=True)
    assert r["decision"] == "FAIL"


def test_pass_never_happens_below_threshold() -> None:
    gate = _gate()
    for rel in (0.0, 0.3, 0.6, 1.0):
        for ver in (0.0, 0.4, 1.0):
            for prog in (0.0, 0.5, 1.0):
                for cost in (0.0, 0.5, 0.8):
                    r = gate.decide(relevance=rel, verifier=ver, progress=prog, cost=cost)
                    assert r["decision"] in DECISIONS
                    if r["decision"] == "PASS":
                        assert r["w"] >= r["threshold"]


def test_risk_is_not_ignored() -> None:
    gate = _gate()
    cheap = gate.decide(relevance=0.9, verifier=0.9, progress=0.9, cost=0.0)
    pricey = gate.decide(relevance=0.9, verifier=0.9, progress=0.9, cost=0.8)
    assert pricey["w"] < cheap["w"]


def test_verifier_score_has_effect() -> None:
    gate = _gate()
    low = gate.decide(relevance=0.9, verifier=0.0, progress=0.9, cost=0.0)
    high = gate.decide(relevance=0.9, verifier=1.0, progress=0.9, cost=0.0)
    assert high["w"] > low["w"]


def test_inputs_out_of_range_raise() -> None:
    gate = _gate()
    with pytest.raises(ValueError):
        gate.decide(relevance=1.5, verifier=0.5, progress=0.5, cost=0.5)
    with pytest.raises(ValueError):
        gate.decide(relevance=0.5, verifier=0.5, progress=0.5, cost=-0.1)


def test_result_validates_against_schema() -> None:
    r = _gate().decide(relevance=0.9, verifier=0.9, progress=0.8, cost=0.05)
    jsonschema.validate(instance=r, schema=_SCHEMA)


def test_metrics_shape_and_rates() -> None:
    gate = _gate()
    results: list[dict[str, Any]] = [
        gate.decide(relevance=0.9, verifier=0.9, progress=0.9, cost=0.0),  # PASS
        gate.decide(relevance=0.1, verifier=0.1, progress=0.1, cost=0.1),  # BELOW
        gate.decide(relevance=0.9, verifier=0.9, progress=0.9, cost=0.95),  # HUMAN
    ]
    m = gate_metrics(gate, results)
    assert set(m) == {
        "gate_pass_rate",
        "noise_rejection_rate",
        "human_review_rate",
        "threshold_sensitivity",
    }
    assert m["gate_pass_rate"] == pytest.approx(1 / 3, abs=1e-3)
    assert m["human_review_rate"] == pytest.approx(1 / 3, abs=1e-3)
    assert 0.0 <= m["threshold_sensitivity"] <= 1.0


def test_metrics_empty() -> None:
    assert gate_metrics(_gate(), [])["gate_pass_rate"] == 0.0
