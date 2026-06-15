"""Adversarial property-based battery — falsify the runtime's core invariants.

Not coverage: generated inputs hunt for an input where a gate's promise breaks.
Survival is information (the invariant holds across the fuzzed space); a failure is
a real bug. Each test attacks one foundational claim of the action-potential
runtime with Hypothesis.
"""

from __future__ import annotations

from hypothesis import given
from hypothesis import strategies as st

from noesis.evidence_integral import build_bundle, replay
from noesis.gates.discharge_gate import DECISIONS, DischargeGate
from noesis.gates.residual_promotion import ResidualCandidate, promote
from noesis.ratios import rate
from noesis.runtime.recovery_supervisor import (
    AttemptResult,
    FaultSignal,
    RecoverySupervisor,
)
from noesis.runtime.rollback import ROLLBACK_TYPES, RollbackController
from noesis.trajectory import OperatorStep, build_trajectory

_unit = st.floats(min_value=0.0, max_value=1.0, allow_nan=False, allow_infinity=False)
_GATE = DischargeGate()


# 1. FOUNDATIONAL: a PASS can never occur below threshold, and only with a
#    cleared verifier floor, sub-ceiling cost, and no verifier failure.
@given(r=_unit, v=_unit, p=_unit, k=_unit, vf=st.booleans())
def test_pass_implies_full_admissibility(r: float, v: float, p: float, k: float, vf: bool) -> None:
    res = _GATE.decide(relevance=r, verifier=v, progress=p, cost=k, verifier_failed=vf)
    assert res["decision"] in DECISIONS
    if res["decision"] == "PASS":
        assert res["w"] >= res["threshold"]
        assert v >= _GATE.verifier_floor
        assert k < _GATE.risk_ceiling
        assert vf is False


# 2. w is exactly the linear functional, rounded — no hidden adjustment.
@given(r=_unit, v=_unit, p=_unit, k=_unit)
def test_w_is_the_declared_functional(r: float, v: float, p: float, k: float) -> None:
    f = _GATE.functional
    expected = round(f.alpha * r + f.beta * v + f.gamma * p - f.delta * k, 4)
    assert _GATE.decide(relevance=r, verifier=v, progress=p, cost=k)["w"] == expected


# 3. MONOTONICITY: more cost never raises w; more verifier never lowers it.
@given(r=_unit, v=_unit, p=_unit, k1=_unit, k2=_unit)
def test_cost_is_monotone_non_increasing(r: float, v: float, p: float, k1: float, k2: float) -> None:
    lo, hi = sorted((k1, k2))
    w_lo = _GATE.decide(relevance=r, verifier=v, progress=p, cost=lo)["w"]
    w_hi = _GATE.decide(relevance=r, verifier=v, progress=p, cost=hi)["w"]
    assert w_hi <= w_lo + 1e-9


# 4. RISK VETO: cost at/above the ceiling can never auto-discharge.
@given(r=_unit, v=_unit, p=_unit, k=st.floats(min_value=0.85, max_value=1.0, allow_nan=False))
def test_high_risk_never_passes(r: float, v: float, p: float, k: float) -> None:
    assert _GATE.decide(relevance=r, verifier=v, progress=p, cost=k)["decision"] != "PASS"


# 5. rate() invariants: bounded, zero-safe, exact.
@given(n=st.integers(0, 10_000), d=st.integers(0, 10_000), dft=_unit)
def test_rate_is_zero_safe_and_exact(n: int, d: int, dft: float) -> None:
    out = rate(n, d, default=dft)
    if d == 0:
        assert out == dft
    else:
        assert out == round(n / d, 4)


# 6. SAFETY: no candidate becomes a mechanism without a passing, attached,
#    non-forbidden, non-proxy-overclaim, supported verifier.
@given(
    attached=st.booleans(),
    passed=st.sampled_from([True, False, None]),
    forbidden=st.booleans(),
    unsupported=st.booleans(),
    proxy=st.booleans(),
)
def test_no_unverified_promotion(
    attached: bool, passed: bool | None, forbidden: bool, unsupported: bool, proxy: bool
) -> None:
    c = ResidualCandidate(
        "c", "x", "claim", verifier_attached=attached, verifier_passed=passed,
        is_forbidden=forbidden, is_unsupported=unsupported, claims_measurement_from_proxy=proxy,
    )
    d = promote(c)
    if d["mechanism_update"]:
        assert d["state"] == "VERIFIED_MECHANISM"
        assert attached and passed is True
        assert not forbidden and not proxy and not unsupported


# 7. TAMPER-EVIDENCE: mutating any persisted transition field breaks replay.
@given(
    label=st.text(min_size=1, max_size=8),
    extra=st.integers(0, 5),
)
def test_single_tamper_breaks_replay(label: str, extra: int) -> None:
    transitions = [{"i": i, "state_t": f"s{i}", "state_t_plus_1": f"s{i + 1}"} for i in range(2)]
    bundle = build_bundle(
        run_id="r", input_text="in",
        transitions=transitions,
        artifacts=[{"name": "a", "transition_index": 0}],
        decisions=[{"d": "PASS"}],
        verifier_outputs=[{"v": True}],
        rollback_points=["cp"],
    )
    assert replay(bundle) is True
    bundle["transitions"][0]["state_t_plus_1"] = label + "_" + str(extra)
    assert replay(bundle) is False


# 8. TRAJECTORY: built traces are always replay-continuous and contiguous.
@given(
    steps=st.lists(
        st.tuples(st.text(min_size=1, max_size=6), _unit),
        min_size=1, max_size=12,
    )
)
def test_trajectory_is_replay_continuous(steps: list[tuple[str, float]]) -> None:
    ops = [OperatorStep(op, "cand", score, "PASS", f"{op}.json") for op, score in steps]
    records = build_trajectory("t", ops)
    for i in range(len(records) - 1):
        assert records[i].state_t_plus_1 == records[i + 1].state_t
        assert records[i + 1].step == records[i].step + 1


# 9. RECOVERY: always terminates in a valid state; budget exhaustion always
#    escalates to a human (never silent pass).
@given(
    fault=st.sampled_from(sorted(ROLLBACK_TYPES)),
    max_attempts=st.integers(1, 5),
)
def test_recovery_terminates_and_escalates(fault: str, max_attempts: int) -> None:
    c = RollbackController()
    c.checkpoint("good", {"v": 0})
    c.discharge("bad", {"v": 1})
    never = lambda: AttemptResult(ok=False, state_id="x")  # noqa: E731
    outcome = RecoverySupervisor(c, max_attempts=max_attempts).recover(
        FaultSignal(fault, "scale", "detail"), never
    )
    assert outcome.status in {"RECOVERED", "ESCALATED", "UNRECOVERABLE"}
    assert outcome.escalated_to_human is True  # it can never recover
