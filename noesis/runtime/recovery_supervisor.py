"""Recovery Supervisor — the reversive cognitive loop that lifts fallen models.

A fall is a silenced gradient: a gate goes red or a process goes quiet. The
supervisor sits *outside* the failed layer (a layer cannot lift itself once its
gradient collapses, INV-YV1) and runs a reversive loop:

    fault -> rollback (reverse to last valid) -> re-attempt (forward) -> repeat
          -> RECOVERED  | ESCALATED (human) | UNRECOVERABLE (state loss)

It never silently passes: budget exhausted or prior valid state lost both escalate
to a human. Recovery memory comes from the rollback stack; the loop re-derives the
state rather than fabricating a new one.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from noesis.ratios import rate
from noesis.runtime.rollback import ROLLBACK_TYPES, RollbackController, StateLossError

RECOVERY_STATES: frozenset[str] = frozenset({"RECOVERED", "ESCALATED", "UNRECOVERABLE"})


@dataclass(frozen=True)
class FaultSignal:
    """A detected fall: a rollback-typed fault at a fractal scale."""

    fault_type: str
    scale: str
    detail: str


@dataclass(frozen=True)
class AttemptResult:
    """Outcome of one forward re-attempt after a reverse."""

    ok: bool
    state_id: str
    note: str = ""


@dataclass(frozen=True)
class RecoveryAttempt:
    index: int
    rolled_back_to: str
    reattempt_ok: bool
    note: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "index": self.index,
            "rolled_back_to": self.rolled_back_to,
            "reattempt_ok": self.reattempt_ok,
            "note": self.note,
        }


@dataclass(frozen=True)
class RecoveryOutcome:
    status: str
    fault_type: str
    scale: str
    attempts: list[RecoveryAttempt]
    restored_state: str
    escalated_to_human: bool
    reason: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "status": self.status,
            "fault_type": self.fault_type,
            "scale": self.scale,
            "attempts": [a.to_dict() for a in self.attempts],
            "restored_state": self.restored_state,
            "escalated_to_human": self.escalated_to_human,
            "reason": self.reason,
        }


@dataclass
class RecoverySupervisor:
    """Detects falls and runs the reversive recovery loop with a bounded budget."""

    controller: RollbackController
    max_attempts: int = 3

    def __post_init__(self) -> None:
        if self.max_attempts < 1:
            raise ValueError("max_attempts must be >= 1")

    def recover(
        self, fault: FaultSignal, reattempt: Callable[[], AttemptResult]
    ) -> RecoveryOutcome:
        """Reverse to the last valid state, re-attempt forward, repeat until budget."""
        if fault.fault_type not in ROLLBACK_TYPES:
            raise ValueError(f"unknown fault type: {fault.fault_type}")

        attempts: list[RecoveryAttempt] = []
        for i in range(1, self.max_attempts + 1):
            try:
                restored = self.controller.trigger(fault.fault_type)
            except StateLossError as exc:
                return RecoveryOutcome(
                    status="UNRECOVERABLE",
                    fault_type=fault.fault_type,
                    scale=fault.scale,
                    attempts=attempts,
                    restored_state="",
                    escalated_to_human=True,
                    reason=f"state loss, escalate to human: {exc}",
                )
            # A re-attempt that throws IS a failed attempt — the supervisor sits
            # outside the failed layer and must survive it (INV-YV1), not die with
            # it. Crashing here violated "always terminates / escalates to human"
            # (знайдено хаос-стрес-тестом). Record the failure and keep the loop.
            try:
                result = reattempt()
            except Exception as exc:
                result = AttemptResult(
                    ok=False,
                    state_id=restored.state_id,
                    note=f"attempt raised: {type(exc).__name__}: {exc}",
                )
            attempts.append(
                RecoveryAttempt(i, restored.state_id, result.ok, result.note)
            )
            if result.ok:
                return RecoveryOutcome(
                    status="RECOVERED",
                    fault_type=fault.fault_type,
                    scale=fault.scale,
                    attempts=attempts,
                    restored_state=restored.state_id,
                    escalated_to_human=False,
                    reason=f"recovered on attempt {i}",
                )
            # leave a fresh tentative state so the next reverse has something to undo
            self.controller.discharge(f"retry-{i}", {"attempt": i, "fault": fault.fault_type})

        return RecoveryOutcome(
            status="ESCALATED",
            fault_type=fault.fault_type,
            scale=fault.scale,
            attempts=attempts,
            restored_state="",
            escalated_to_human=True,
            reason=f"exhausted {self.max_attempts} attempts, escalate to human",
        )


def detect_fault(
    *, gate_passed: bool, process_alive: bool, fault_type: str, scale: str
) -> FaultSignal | None:
    """A fall is the *absence* of a healthy pulse: red gate or dead process."""
    if gate_passed and process_alive:
        return None
    detail = "gate red" if not gate_passed else "process silent"
    return FaultSignal(fault_type=fault_type, scale=scale, detail=detail)


def recovery_metrics(outcomes: list[RecoveryOutcome]) -> dict[str, float]:
    total = len(outcomes)
    recovered = [o for o in outcomes if o.status == "RECOVERED"]
    escalated = sum(1 for o in outcomes if o.escalated_to_human)
    lost = sum(1 for o in outcomes if o.status == "UNRECOVERABLE")
    return {
        "recovery_success_rate": rate(len(recovered), total),
        "escalation_rate": rate(escalated, total),
        "mean_attempts_to_recover": rate(sum(len(o.attempts) for o in recovered), len(recovered)),
        "state_loss_rate": rate(lost, total),
    }


def _make_reattempt(fail_until: int) -> Callable[[], AttemptResult]:
    """A reattempt that fails the first ``fail_until`` calls, then succeeds."""
    calls = {"n": 0}

    def reattempt() -> AttemptResult:
        calls["n"] += 1
        ok = calls["n"] > fail_until
        return AttemptResult(ok=ok, state_id="restored", note=f"attempt {calls['n']}")

    return reattempt


def self_check() -> dict[str, Any]:
    """Deterministic reflex self-test: recover-first-try, recover-after-retry, escalate."""
    outcomes: list[RecoveryOutcome] = []

    # 1. recovers on the first re-attempt
    c1 = RollbackController()
    c1.checkpoint("good", {"v": 0})
    c1.discharge("bad", {"v": 1})
    outcomes.append(
        RecoverySupervisor(c1).recover(
            FaultSignal("test_failure", "code_patch", "tests red"), _make_reattempt(0)
        )
    )

    # 2. recovers on the second re-attempt
    c2 = RollbackController()
    c2.checkpoint("good", {"v": 0})
    c2.discharge("bad", {"v": 1})
    outcomes.append(
        RecoverySupervisor(c2).recover(
            FaultSignal("schema_failure", "module_change", "schema red"), _make_reattempt(1)
        )
    )

    # 3. never recovers within budget -> escalates to human
    c3 = RollbackController()
    c3.checkpoint("good", {"v": 0})
    c3.discharge("bad", {"v": 1})
    outcomes.append(
        RecoverySupervisor(c3, max_attempts=2).recover(
            FaultSignal("forbidden_claim_detected", "pull_request", "forbidden claim"),
            _make_reattempt(99),
        )
    )

    statuses = [o.status for o in outcomes]
    healthy = (
        statuses == ["RECOVERED", "RECOVERED", "ESCALATED"]
        and outcomes[2].escalated_to_human
        and all(o.restored_state == "good" for o in outcomes[:2])
    )
    return {
        "healthy": healthy,
        "statuses": statuses,
        "metrics": recovery_metrics(outcomes),
        "outcomes": [o.to_dict() for o in outcomes],
    }
