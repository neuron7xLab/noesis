"""Intent parser — груба детермінована декомпозиція наміру на 5 шарів.

Це НЕ заміна LLM-дзеркала. Це швидкий офлайн-кістяк, що розкладає сире
повідомлення на surface/process/strategic/constraint/next_action, який далі
уточнює промпт prompts/finalizer_mirror.md. Невизначеність позначається явно.
"""

from __future__ import annotations

import re
from dataclasses import asdict, dataclass, field

_PROCESS_VERBS: tuple[str, ...] = (
    "створ", "побуд", "знайд", "витяг", "зроб", "напиш",
    "перевір", "проаналіз", "розшир", "стисн", "сформул", "оптиміз",
)
_CONSTRAINT_MARKERS: tuple[str, ...] = ("без ", "не ", "уник", "заборон", "лише", "тільки")


@dataclass(frozen=True)
class Intent:
    surface: str
    process: str
    strategic: str
    constraint: str
    next_action: str
    assumptions: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


def _sentences(text: str) -> list[str]:
    return [s.strip() for s in re.split(r"[.!?\n]+", text) if s.strip()]


def parse_intent(message: str) -> Intent:
    """Розкладає повідомлення на 5 шарів наміру (детерміновано, без мережі)."""
    msg = message.strip()
    sentences = _sentences(msg)
    low = msg.lower()

    surface = sentences[0] if sentences else msg
    verbs = [v for v in _PROCESS_VERBS if v in low]
    process = ", ".join(verbs) if verbs else "невизначено"
    strategic = sentences[-1] if len(sentences) > 1 else surface
    constraint = next(
        (s for s in sentences if any(m in s.lower() for m in _CONSTRAINT_MARKERS)),
        "не вказано явно",
    )
    next_action = surface
    assumptions: list[str] = []
    if not verbs:
        assumptions.append("операцію виведено евристично — потрібне підтвердження")
    if constraint == "не вказано явно":
        assumptions.append("обмеження не задано — діємо за безпечним замовчуванням")

    return Intent(
        surface=surface,
        process=process,
        strategic=strategic,
        constraint=constraint,
        next_action=next_action,
        assumptions=assumptions,
    )
