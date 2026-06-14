"""Офлайн-тести труби: парсер секцій + завантаження промптів (без мережі)."""

from __future__ import annotations

from tools.llm_adapter import load_prompt
from tools.pipeline import parse_sections


def test_parse_sections_extracts_seven() -> None:
    text = (
        "definition: щось\n"
        "input: вхід\n"
        "method: метод\n"
        "output: вихід\n"
        "validation: тест\n"
        "example: приклад\n"
        "failure_modes: режими\n"
    )
    parsed = parse_sections(text)
    assert set(parsed) == {
        "definition", "input", "method", "output", "validation", "example", "failure_modes",
    }
    assert parsed["definition"] == "щось"


def test_parse_sections_ignores_noise() -> None:
    parsed = parse_sections("# заголовок\ndefinition: x\nбла бла\noutput: y")
    assert parsed == {"definition": "x", "output": "y"}


def test_load_prompt_extracts_fenced_block() -> None:
    prompt = load_prompt("finalizer_mirror.md")
    assert "FINALIZER_MIRROR_ENGINE" in prompt
    assert "Ти хочеш від мене" in prompt
    # fenced-блок, а не markdown-обгортка
    assert not prompt.lstrip().startswith("#")
