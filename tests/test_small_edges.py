"""Cover small uncovered edges across pure functions."""

from __future__ import annotations

from noesis.adaptive import build_adaptive_mirror
from noesis.effective_dim import participation_ratio
from noesis.gates.discharge_gate import DischargeGate
from noesis.provenance import Claim, governance_summary, is_valid_provenance
from noesis.runtime.action_potential_trace import (
    record_from_gate,
    trace_to_dict,
    validate_payload,
)
from noesis.verdict import render_verdict_md


def test_discharge_threshold_sensitivity_hits_all_decision_branches() -> None:
    g = DischargeGate()
    results = [
        g.decide(relevance=0.9, verifier=0.9, progress=0.9, cost=0.0, verifier_failed=True),  # FAIL
        g.decide(relevance=0.9, verifier=0.9, progress=0.9, cost=0.95),  # HUMAN_REVIEW
        g.decide(relevance=1.0, verifier=0.5, progress=0.5, cost=0.5),  # w==theta -> flips at +eps
    ]
    sens = g.threshold_sensitivity(results)
    assert 0.0 < sens <= 1.0  # the borderline result flips


def test_action_potential_validate_payload_none_values() -> None:
    payload = {
        "trace_id": "t", "cycle_id": 0, "state_t": "s0", "intent_delta": "i",
        "unfinished_work_delta": "u", "gate_score": None, "threshold": None,
        "decision": "PASS", "artifact_delta": "a", "rollback_condition": "r",
        "state_t_plus_1": "s1",
    }
    probs = validate_payload(payload)
    assert any(p.startswith("ACTION_NO_THRESHOLD") for p in probs)
    assert any(p.startswith("DECISION_NO_SCORE") for p in probs)


def test_action_potential_record_and_trace_to_dict() -> None:
    res = DischargeGate().decide(relevance=0.9, verifier=0.9, progress=0.8, cost=0.05)
    rec = record_from_gate(
        trace_id="t", cycle_id=0, state_t="s0", intent_delta="i",
        unfinished_work_delta="u", gate_result=res, artifact_delta="a",
        rollback_condition="r", state_t_plus_1="s1",
    )
    assert rec.to_dict()["decision"] == "PASS"
    bundle = trace_to_dict("t", [rec])
    assert bundle["trace_id"] == "t" and bundle["records"]


def test_provenance_claim_and_summary() -> None:
    assert is_valid_provenance("observed") is True
    assert is_valid_provenance("bogus") is False
    c = Claim("field", "value", "inferred")
    assert c.to_dict() == {"field": "field", "value": "value", "provenance": "inferred"}
    summary = governance_summary([c, Claim("f2", "v2", "observed")])
    assert summary["inferred"] == 1 and summary["observed"] == 1


def test_render_verdict_md() -> None:
    md = render_verdict_md(
        {
            "run_id": "r1", "pipeline_version": "0.5", "overall_status": "PASS",
            "gates_passed": 10, "gates_total": 10, "gates_failed": [],
            "claim_governance": {}, "baseline": {}, "deterministic_modules": ["a"],
            "llm_modules": [],
        }
    )
    assert "VERDICT" in md and "r1" in md


def test_participation_ratio_edges() -> None:
    assert participation_ratio([]) == 0.0
    identical = participation_ratio([[1.0, 0.0], [1.0, 0.0], [1.0, 0.0]])
    assert identical >= 1.0


def test_adaptive_compression_status_branches() -> None:
    long_input = "слово " * 60
    long_out = build_adaptive_mirror(long_input)
    short_out = build_adaptive_mirror("старт")
    assert long_out.compression_status in {
        "compressed", "structured_not_compressed", "expanded_by_request", "failed_compression",
    }
    assert short_out.compression_status == "structured_not_compressed"
