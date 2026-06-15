"""Адверсаріальна батарея для forbidden-гейту.

Знайдено самозламом v0.8: наївний підрядковий матч ОДНОЧАСНО протікав на
тривіальній обфускації (``a g i``, гомогліф ``АGI``) і давав false-positive
(``magic`` ⟶ «claim of AGI»). Ці тести фіксують обидві межі назавжди.
"""

from __future__ import annotations

import pytest
from hypothesis import given
from hypothesis import strategies as st

from noesis.forbidden import check_forbidden_claims

# Слова, що містять підрядок "agi", але НІКОЛИ не є claim про AGI.
_BENIGN_AGI_SUBSTR = [
    "magic ground",
    "imagine a pipe",
    "imagination is the engine",
    "fragile state of the system",
    "це уявлення (imagination)",
    "pagination of results",
]

# Обфусковані варіанти claim про AGI — мають ловитись усі.
_EVASIONS = [
    "AGI achieved",
    "a g i achieved",
    "a.g.i. achieved",
    "a-g-i now",
    "система вже a_g_i",
    "ця система — АGI",  # кир. А
    "досягнуто AGI сьогодні",
]


@pytest.mark.parametrize("text", _EVASIONS)
def test_agi_evasions_are_blocked(text: str) -> None:
    assert "claim of AGI" in check_forbidden_claims(text)


@pytest.mark.parametrize("text", _BENIGN_AGI_SUBSTR)
def test_agi_substring_is_not_false_positive(text: str) -> None:
    assert "claim of AGI" not in check_forbidden_claims(text)


def test_known_real_claims_still_blocked() -> None:
    cases = {
        "це діагноз": "medical diagnosis",
        "ми вилікуємо все": "healing claim",
        "система детектує свідомість": "consciousness detection",
        "загальний штучний інтелект": "claim of AGI",
        "artificial general intelligence": "claim of AGI",
        "це карма": "mysticism",
    }
    for text, label in cases.items():
        assert label in check_forbidden_claims(text)


# PROPERTY: жодне англійське слово зі вшитим "agi", обрамлене не-AGI текстом,
# не повинно тригерити AGI-claim (поки навколо "agi" є літери).
@given(
    pre=st.text(alphabet="abcdefghijklmnopqrstuvwxyz", min_size=1, max_size=6),
    post=st.text(alphabet="abcdefghijklmnopqrstuvwxyz", min_size=1, max_size=6),
)
def test_agi_embedded_in_word_never_flags(pre: str, post: str) -> None:
    word = f"{pre}agi{post}"
    assert "claim of AGI" not in check_forbidden_claims(word)


# PROPERTY: довільні сепаратори між a, g, i завжди ловляться як AGI-claim.
@given(
    s1=st.sampled_from(["", " ", ".", "-", "_", "  ", " . "]),
    s2=st.sampled_from(["", " ", ".", "-", "_", "  ", " . "]),
)
def test_separated_agi_always_blocked(s1: str, s2: str) -> None:
    text = f"the a{s1}g{s2}i system"
    assert "claim of AGI" in check_forbidden_claims(text)
