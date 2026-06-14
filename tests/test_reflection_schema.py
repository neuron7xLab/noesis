"""Тести JSON-схем рефлексії, наміру та артефакту."""

from __future__ import annotations

from tools.artifact_checker import check_artifact
from tools.reflection_validator import validate_intent, validate_reflection


def test_valid_reflection_passes() -> None:
    obj = {
        "raw_intent": "хочу нарешті розібратися з репо",
        "crystallized_intent": "зібрати MVP cognitive-mirror-methods за контрактом",
        "blockers": ["розпорошеність файлів"],
        "next_action": "написати 7 методів",
    }
    assert validate_reflection(obj) == []


def test_missing_required_reflection_fails() -> None:
    errors = validate_reflection({"raw_intent": "щось хочу"})
    assert errors


def test_additional_property_rejected() -> None:
    obj = {
        "raw_intent": "a",
        "crystallized_intent": "b",
        "next_action": "c",
        "totally_extra": "ні",
    }
    assert validate_reflection(obj)


def test_valid_intent_passes() -> None:
    obj = {
        "surface": "збери репо",
        "process": "створ",
        "strategic": "інструмент мислення",
        "constraint": "без води",
        "next_action": "побудувати MVP",
        "assumptions": [],
    }
    assert validate_intent(obj) == []


def test_artifact_requires_seven_sections() -> None:
    partial = {"definition": "x", "input": "y"}
    problems = check_artifact(partial)
    assert any("method" in p for p in problems)
    assert any("failure_modes" in p for p in problems)
    assert len(problems) == 5
