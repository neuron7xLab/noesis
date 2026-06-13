"""10 messy real-world прикладів проходять трубу end-to-end і проходять валідацію."""

from __future__ import annotations

from pathlib import Path

import pytest

from cme.pipeline import run_pipeline
from tools.finalizer100 import MAX_WORDS, MIN_WORDS, count_words

_EXAMPLES = sorted((Path(__file__).resolve().parent.parent / "examples" / "messy").glob("*.txt"))


def test_ten_examples_present() -> None:
    assert len(_EXAMPLES) >= 10


@pytest.mark.parametrize("path", _EXAMPLES, ids=lambda p: p.name)
def test_messy_example_end_to_end(path: Path) -> None:
    raw = path.read_text(encoding="utf-8").strip()
    run = run_pipeline(raw)
    # 1. кожна валідація проходить
    assert run.passed, [v.to_dict() for v in run.validations if not v.passed]
    # 2. рівно одна конкретна наступна дія
    assert run.next_action.strip()
    # 3. фіналайзер коротший за вхід і в межах швидкості (clearer/shorter/verifiable)
    words = count_words(run.mirror.finalizer)
    assert MIN_WORDS <= words <= MAX_WORDS
