"""Rollback physics — every invalid discharge is reversible.

    invalid_state -> rollback_condition -> restore_previous_valid_state

A discharge is tentative until verified; if it turns out invalid (schema/test/
claim failure, benchmark regression, forbidden claim, human rejection, artifact
instability) the controller restores the last valid state. A run cannot release
while a benchmark failed or a rollback is open.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

ROLLBACK_TYPES: frozenset[str] = frozenset(
    {
        "schema_failure",
        "test_failure",
        "claim_failure",
        "benchmark_regression",
        "forbidden_claim_detected",
        "human_rejection",
        "artifact_instability",
    }
)


class StateLossError(RuntimeError):
    """Raised when a rollback is requested but no prior valid state exists."""


@dataclass(frozen=True)
class StateSnapshot:
    state_id: str
    payload: dict[str, Any]
    valid: bool = True


@dataclass
class RollbackController:
    """A stack of state snapshots with reversible tentative discharges."""

    _stack: list[StateSnapshot] = field(default_factory=list)

    def checkpoint(self, state_id: str, payload: dict[str, Any]) -> None:
        """Record a known-good state."""
        self._stack.append(StateSnapshot(state_id, dict(payload), valid=True))

    def discharge(self, state_id: str, payload: dict[str, Any]) -> None:
        """Apply a tentative state that may later be rolled back."""
        self._stack.append(StateSnapshot(state_id, dict(payload), valid=True))

    @property
    def current(self) -> StateSnapshot | None:
        return self._stack[-1] if self._stack else None

    def _last_valid(self) -> StateSnapshot | None:
        for snap in reversed(self._stack):
            if snap.valid:
                return snap
        return None

    def trigger(self, rollback_type: str) -> StateSnapshot:
        """Reverse the tentative top state and restore the last valid one."""
        if rollback_type not in ROLLBACK_TYPES:
            raise ValueError(f"unknown rollback type: {rollback_type}")
        if not self._stack:
            raise StateLossError("nothing to roll back")
        self._stack.pop()  # drop the invalid discharge
        prior = self._last_valid()
        if prior is None:
            raise StateLossError("no prior valid state to restore")
        # discard anything above the restored point
        idx = self._stack.index(prior)
        self._stack = self._stack[: idx + 1]
        return prior


def can_release(*, benchmark_passed: bool, open_rollbacks: int) -> bool:
    """A run may release only with a passing benchmark and zero open rollbacks."""
    return benchmark_passed and open_rollbacks == 0


def rollback_metrics(events: list[dict[str, Any]]) -> dict[str, float]:
    """events: {rollback_type, was_invalid, recovered, state_lost}."""
    total = len(events)
    if total == 0:
        return {
            "rollback_defined_rate": 0.0,
            "rollback_success_rate": 0.0,
            "invalid_state_recovery_rate": 0.0,
            "state_loss_rate": 0.0,
        }
    triggered = [e for e in events if e.get("rollback_type") in ROLLBACK_TYPES]
    invalid = [e for e in events if e.get("was_invalid")]
    return {
        "rollback_defined_rate": round(len(triggered) / total, 4),
        "rollback_success_rate": round(
            sum(1 for e in triggered if e.get("recovered")) / len(triggered), 4
        )
        if triggered
        else 0.0,
        "invalid_state_recovery_rate": round(
            sum(1 for e in invalid if e.get("recovered")) / len(invalid), 4
        )
        if invalid
        else 1.0,
        "state_loss_rate": round(sum(1 for e in events if e.get("state_lost")) / total, 4),
    }
