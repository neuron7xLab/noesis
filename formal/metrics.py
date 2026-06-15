"""Обчислювані метрики формального шару.

Кожна функція реалізує інваріант одного конструкта так, щоб його можна було
ПЕРЕВІРИТИ числом, а не словом. Жодних прихованих порогів усередині — пороги
живуть у формальних предикатах (formal/verify.py), метрики лишаються чистими.
"""

from __future__ import annotations

import re
from collections.abc import Mapping, Sequence
from math import isfinite

# Канонічні часові горизонти екстрапольованого мислення (Trope & Liberman, 2010).
CANONICAL_HORIZONS: tuple[str, ...] = ("now", "1d", "1w", "1m", "1y")

_WORD = re.compile(r"[\w’'-]+", re.UNICODE)
_DIGIT = re.compile(r"\d")

# Маркери виконуваного фальсифікатора (Popper, 1959): не проза, а перевірка.
_FALSIFIER_MARKERS: tuple[str, ...] = (
    "()", "==", "<=", ">=", "assert", "pytest", "python", "→", "->", "%",
)

# Мінімальний україномовний стоп-список для семантичної дизʼюнкції.
_STOP: frozenset[str] = frozenset(
    {"це", "що", "для", "над", "під", "або", "так", "там", "тут", "був",
     "усе", "все", "них", "як", "не", "на", "по", "до", "із", "зі"}
)


def goodman_kruskal_gamma(pairs: Sequence[tuple[float, bool]]) -> float:
    """Метакогнітивна роздільність як γ (Nelson, 1984; Goodman & Kruskal, 1954).

    pairs: послідовність (впевненість, коректність). Повертає γ ∈ [-1, 1] —
    рангову асоціацію між суб'єктивною впевненістю й об'єктивною коректністю.
    γ=1 — ідеальний моніторинг, γ=0 — сліпий, γ<0 — антикалібрований.
    Зв'язані пари (рівна впевненість або рівна коректність) виключаються.
    """
    # Fail-closed: не-скінченна впевненість (NaN/inf) не дорівнює нічому й не
    # більша за ніщо, тож тихо формувала б concordant/discordant і давала
    # хибний PASS у verify_reflection (знайдено хаос-стрес-тестом).
    if any(not isfinite(conf) for conf, _ in pairs):
        raise ValueError("впевненість має бути скінченною (без NaN/inf)")
    concordant = 0
    discordant = 0
    n = len(pairs)
    for i in range(n):
        conf_i, acc_i = pairs[i]
        for j in range(i + 1, n):
            conf_j, acc_j = pairs[j]
            if acc_i == acc_j or conf_i == conf_j:
                continue  # неінформативна (зв'язана) пара
            # Узгоджено, якщо впевненіший елемент і є коректним.
            if (conf_i > conf_j) == bool(acc_i):
                concordant += 1
            else:
                discordant += 1
    total = concordant + discordant
    if total == 0:
        raise ValueError("немає інформативних пар — γ невизначене")
    return (concordant - discordant) / total


def information_sufficiency(text: str, required_predicates: Sequence[str]) -> float:
    """Достатність стиснення (Tishby et al., 1999; Rissanen, 1978).

    Частка обов'язкових предикатів, збережених у стисненому представленні.
    1.0 = мінімальна достатня статистика повна.
    """
    if not required_predicates:
        raise ValueError("порожній набір обов'язкових предикатів")
    low = text.lower()
    present = sum(1 for p in required_predicates if p in low)
    return present / len(required_predicates)


def _content_tokens(text: str) -> set[str]:
    return {w for w in _WORD.findall(text.lower()) if w not in _STOP and len(w) > 2}


def semantic_disjointness(definition: str, anti_definition: str) -> float:
    """Семантична відстань дефініції від анти-дефініції (Katz & Fodor, 1963).

    1 − Jaccard над змістовними лексемами. 1.0 = повна дизʼюнкція (анти-дефініція
    реально відсікає), 0.0 = тавтологія (перефраз дефініції).
    """
    a = _content_tokens(definition)
    b = _content_tokens(anti_definition)
    if not a or not b:
        return 0.0
    intersection = len(a & b)
    union = len(a | b)
    return 1.0 - intersection / union


def falsifier_present(validation: str) -> bool:
    """Критерій демаркації (Popper, 1959): валідація — виконувана, не проза.

    True, якщо текст містить маркер виконуваної перевірки або числовий поріг.
    """
    low = validation.lower()
    has_marker = any(marker in low for marker in _FALSIFIER_MARKERS)
    has_threshold = bool(_DIGIT.search(validation))
    return has_marker or has_threshold


def temporal_map_complete(horizons: Mapping[str, object]) -> bool:
    """Повнота ментальної подорожі в часі (Suddendorf & Corballis, 2007).

    True, якщо всі канонічні горизонти присутні й непорожні (немає сліпого хвоста).
    """
    return all(
        key in horizons and str(horizons[key]).strip() for key in CANONICAL_HORIZONS
    )


def problem_space_determinacy(matching_operators: Sequence[object]) -> bool:
    """Детермінованість простору задачі (Newell & Simon, 1972).

    True, якщо рівно один оператор претендує на роль першої дії — інакше
    наступний крок неоднозначний (карта не зійшлася).
    """
    return len(matching_operators) == 1
