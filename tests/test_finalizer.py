"""Тести контракту Finalizer-100: довжина 90–110 слів + сенсові якорі."""

from __future__ import annotations

from tools.finalizer100 import (
    MAX_WORDS,
    MIN_WORDS,
    count_words,
    validate_finalizer,
)

ANCHORS = "намір мета блокер дія метрика ризик"


def test_count_words_cyrillic() -> None:
    assert count_words("слово слово слово") == 3
    assert count_words("намір — це сила") == 3  # тире не слово


def test_in_range_with_all_anchors_passes() -> None:
    text = " ".join(["слово"] * 100) + " " + ANCHORS
    result = validate_finalizer(text)
    assert MIN_WORDS <= result.word_count <= MAX_WORDS
    assert result.in_range
    assert result.missing_anchors == []
    assert result.ok


def test_too_short_fails() -> None:
    result = validate_finalizer(ANCHORS)
    assert not result.in_range
    assert not result.ok


def test_too_long_fails() -> None:
    text = " ".join(["слово"] * 200) + " " + ANCHORS
    result = validate_finalizer(text)
    assert not result.in_range
    assert not result.ok


def test_missing_anchor_fails_even_if_length_ok() -> None:
    text = " ".join(["слово"] * 100)
    result = validate_finalizer(text)
    assert result.in_range
    assert not result.ok
    assert "намір" in result.missing_anchors
