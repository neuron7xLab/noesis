"""Тести реверсивного інференсу та валідності його сліду за схемою."""

from __future__ import annotations

from tools.reflection_validator import validate_inference_trace
from tools.reverse_inference import plan_backwards


def test_missing_condition_drives_next_action() -> None:
    trace = plan_backwards(
        target_state="репо опубліковано",
        current_facts=["код є"],
        required_conditions=["код є", "тести зелені", "ліцензія"],
    )
    assert trace.missing_constraints == ["тести зелені", "ліцензія"]
    assert "тести зелені" in trace.next_action


def test_all_conditions_met() -> None:
    trace = plan_backwards("готово", ["a", "b"], ["a", "b"])
    assert trace.missing_constraints == []
    assert "досяжна" in trace.next_action


def test_trace_conforms_to_schema() -> None:
    trace = plan_backwards("ціль", ["a"], ["a", "b"])
    assert validate_inference_trace(trace.to_dict()) == []


def test_case_insensitive_matching() -> None:
    trace = plan_backwards("ціль", ["Код Є"], ["код є"])
    assert trace.missing_constraints == []
