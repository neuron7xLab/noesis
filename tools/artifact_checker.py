"""Artifact checker — кожен метод/артефакт зобов'язаний мати 7 секцій контракту.

definition · input · method · output · validation · example · failure_modes
Без усіх семи модуль не приймається в репозиторій.
"""

from __future__ import annotations

from typing import Any

REQUIRED_SECTIONS: tuple[str, ...] = (
    "definition",
    "input",
    "method",
    "output",
    "validation",
    "example",
    "failure_modes",
)


def check_artifact(obj: dict[str, Any]) -> list[str]:
    """Повертає список відсутніх/порожніх секцій; порожній список = валідно."""
    problems: list[str] = []
    for section in REQUIRED_SECTIONS:
        value = obj.get(section)
        if value is None or (isinstance(value, str) and not value.strip()):
            problems.append(f"відсутня секція: {section}")
    return problems


def is_valid_artifact(obj: dict[str, Any]) -> bool:
    return not check_artifact(obj)
