"""Reverse inference — мислення назад: від бажаної цілі до наступної дії.

target_state → required_conditions → missing_constraints → next_action
"""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import asdict, dataclass


@dataclass(frozen=True)
class ReverseTrace:
    target_state: str
    required_conditions: list[str]
    missing_constraints: list[str]
    next_action: str

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


def _norm(s: str) -> str:
    return s.strip().lower()


def plan_backwards(
    target_state: str,
    current_facts: Iterable[str],
    required_conditions: Iterable[str],
) -> ReverseTrace:
    """Знаходить першу відсутню умову на шляху до цілі — це і є наступна дія."""
    have = {_norm(f) for f in current_facts}
    required = [c for c in required_conditions]
    missing = [c for c in required if _norm(c) not in have]
    next_action = (
        f"Забезпечити: {missing[0]}" if missing else f"Ціль досяжна: {target_state}"
    )
    return ReverseTrace(
        target_state=target_state,
        required_conditions=required,
        missing_constraints=missing,
        next_action=next_action,
    )
