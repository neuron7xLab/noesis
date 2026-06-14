"""Cover formal/verify.py invariant verifiers."""

from __future__ import annotations

from formal.verify import (
    verify_extrapolated,
    verify_goal_regression,
    verify_introspection,
    verify_reflection,
)
from tools.reverse_inference import plan_backwards


def test_verify_reflection_valid() -> None:
    v = verify_reflection([(0.9, True), (0.2, False), (0.6, True), (0.3, False)])
    assert v.construct == "reflection"
    assert v.passed is True
    assert -1.0 <= v.score <= 1.0


def test_verify_reflection_invariant_violation() -> None:
    # all-tied confidence => no informative pairs => ValueError => failed verdict
    v = verify_reflection([(0.5, True), (0.5, False)])
    assert v.passed is False
    assert "інваріант" in v.detail


def test_verify_introspection_one_vs_zero() -> None:
    assert verify_introspection(["only-op"]).passed is True
    assert verify_introspection([]).passed is False


def test_verify_goal_regression_missing_constraint() -> None:
    trace = plan_backwards(
        target_state="продакшн з моніторингом",
        current_facts=["є прототип"],
        required_conditions=["CI зелений", "є алерти"],
    )
    v = verify_goal_regression(trace)
    assert v.construct == "goal_regression"
    assert isinstance(v.passed, bool)


def test_verify_goal_regression_all_present() -> None:
    trace = plan_backwards(
        target_state="ціль",
        current_facts=["усе є"],
        required_conditions=[],
    )
    v = verify_goal_regression(trace)
    assert v.construct == "goal_regression"


def test_verify_extrapolated_empty_is_blind_tail() -> None:
    v = verify_extrapolated({})
    assert v.construct == "extrapolated_thinking"
    assert v.passed is False
