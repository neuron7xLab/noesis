"""Заборонені claims і евристика галюцинаційного ризику.

Жорстка межа продукту: ніколи не діагностувати, не лікувати, не замінювати
людське судження, не претендувати на AGI/свідомість.
"""

from __future__ import annotations

import re

# (підрядок у нижньому регістрі, мітка порушення)
_FORBIDDEN_CLAIMS: tuple[tuple[str, str], ...] = (
    ("agi", "claim of AGI"),
    ("загальний штучний інтелект", "claim of AGI"),
    ("artificial general intelligence", "claim of AGI"),
    ("діагноз", "medical diagnosis"),
    ("діагност", "medical diagnosis"),
    ("вилікує", "healing claim"),
    ("вилікуємо", "healing claim"),
    ("зцілює", "healing claim"),
    ("психотерап", "therapy claim"),
    ("замінює лікаря", "replaces clinician"),
    ("замінює психолога", "replaces clinician"),
    ("замінює людське судження", "replaces human judgment"),
    ("фізично розширюємо свідомість", "consciousness expansion claim"),
    ("доведена модель мозку", "validated brain model claim"),
    ("науково валідована когнітивна", "validated cognitive-science claim"),
    # v0.4 / EIIC — нейрокогнітивні та екстрапольовані overclaims
    ("детектує свідомість", "consciousness detection"),
    ("вимірює свідомість", "consciousness measurement"),
    ("система свідома", "consciousness claim"),
    ("вимірює досвід", "IIT-experience overclaim"),
    ("доводить досвід", "IIT-experience overclaim"),
    ("судилось", "destiny language"),
    ("призначено долею", "destiny language"),
    ("така доля", "destiny language"),
    ("містичн", "mysticism"),
    ("езотер", "mysticism"),
    ("карма", "mysticism"),
)

# Маркери непідкріпленої впевненості (галюцинаційний ризик).
_CERTAINTY_MARKERS: tuple[str, ...] = (
    "гарантовано", "стовідсотково", "100% точно", "доведено науково",
    "завжди працює", "ніколи не помиляється", "guaranteed", "always works",
)

_NUM = re.compile(r"\b\d{2,}\b")


def check_forbidden_claims(text: str) -> list[str]:
    """Повертає список порушень заборонених claims; порожній = чисто."""
    low = text.lower()
    return [label for needle, label in _FORBIDDEN_CLAIMS if needle in low]


def hallucination_risk(text: str, source: str = "") -> tuple[str, list[str]]:
    """Грубий ризик галюцинації: маркери надвпевненості + числа, відсутні у вході.

    Повертає (рівень, список_сигналів). Рівень ∈ {"low","medium","high"}.
    """
    low = text.lower()
    signals = [m for m in _CERTAINTY_MARKERS if m in low]
    # Числа у виході, яких немає у вхідному джерелі — потенційна фабрикація.
    src_nums = set(_NUM.findall(source))
    out_nums = [n for n in _NUM.findall(text) if n not in src_nums]
    if out_nums:
        signals.append(f"числа без джерела: {', '.join(sorted(set(out_nums)))}")
    if len(signals) >= 2:
        return "high", signals
    if signals:
        return "medium", signals
    return "low", signals
