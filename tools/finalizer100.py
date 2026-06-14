"""Finalizer100 — стиснення хаосу до дії: рівно 90–110 слів українською.

Детермінований валідатор фінального артефакту. Сам текст пише людина або LLM
за промптом prompts/finalizer_mirror.md — інструмент лише перевіряє контракт.
"""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass

MIN_WORDS = 90
MAX_WORDS = 110

# Кореневі якорі обов'язкових сенсових полів (перевіряємо як підрядки,
# щоб ловити всі словоформи: намір/наміру, метрика/метрики, ризик/ризики).
REQUIRED_ANCHORS: tuple[str, ...] = ("намір", "мет", "блокер", "дія", "метрик", "ризик")

_WORD_RE = re.compile(r"[\w’'-]+", re.UNICODE)


def count_words(text: str) -> int:
    """Підрахунок слів з підтримкою кирилиці й апострофів."""
    return len(_WORD_RE.findall(text))


@dataclass(frozen=True)
class FinalizerResult:
    word_count: int
    in_range: bool
    missing_anchors: list[str]
    ok: bool


def validate_finalizer(text: str) -> FinalizerResult:
    """Перевіряє довжину 90–110 слів і наявність обов'язкових сенсових якорів."""
    wc = count_words(text)
    in_range = MIN_WORDS <= wc <= MAX_WORDS
    low = text.lower()
    missing = [a for a in REQUIRED_ANCHORS if a not in low]
    return FinalizerResult(wc, in_range, missing, in_range and not missing)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="finalizer100",
        description="Перевірити Finalizer-100 артефакт (90–110 слів, обов'язкові якорі).",
    )
    parser.add_argument("path", nargs="?", help="файл для перевірки; stdin якщо не вказано")
    args = parser.parse_args(argv)

    text = (
        open(args.path, encoding="utf-8").read()  # noqa: SIM115 — короткоживучий CLI
        if args.path
        else sys.stdin.read()
    )
    result = validate_finalizer(text)
    status = "OK" if result.ok else "FAIL"
    print(f"[{status}] words={result.word_count} target={MIN_WORDS}-{MAX_WORDS} in_range={result.in_range}")
    if result.missing_anchors:
        print("відсутні якорі: " + ", ".join(result.missing_anchors))
    return 0 if result.ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
