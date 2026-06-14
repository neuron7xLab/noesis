# Recovery Supervisor — the reversive recovery loop (Layer −1)

`noesis/runtime/recovery_supervisor.py`. Answers "who lifts the models when they
fall": a supervisor **outside** the failed layer that runs a reversive loop.

```
fault → rollback (reverse to last valid) → re-attempt (forward) → repeat
      → RECOVERED | ESCALATED (human) | UNRECOVERABLE (state loss)
```

A layer cannot lift itself once its gradient collapses (INV-YV1), so the lifter
must be a still-living layer above it. Recovery memory is the rollback stack — the
loop **re-derives** the state, it does not fabricate a new one.

## Reflex arc

1. **detect** (`detect_fault`) — a fall is the *absence* of a healthy pulse: a red
   gate or a silent process, not a message.
2. **reverse** (`RollbackController.trigger`) — undo the bad discharge, restore the
   last valid state.
3. **forward** (`reattempt` callable) — re-run the gated operation.
4. **repeat** up to `max_attempts`.
5. **escalate** — budget exhausted or no prior valid state → `escalated_to_human`.

It never silently passes: `RECOVERED` requires a real successful re-attempt.

## Outcome + metrics

`RecoveryOutcome{status, fault_type, scale, attempts, restored_state,
escalated_to_human, reason}` (schema `schemas/recovery_outcome.schema.json`).
Metrics: `recovery_success_rate`, `escalation_rate`, `mean_attempts_to_recover`,
`state_loss_rate`.

## Run

```bash
python -m noesis.cli recovery self-check        # deterministic reflex self-test
python -m pytest tests/test_recovery_supervisor.py -q
```

`self-check` runs three synthetic faults (recover-first-try, recover-after-retry,
escalate-on-budget) and exits 0 only if the reflex behaves: two recoveries
restoring the prior valid state, one honest escalation to human.

> The supervisor itself is under the gate: it has a bounded budget and escalates
> rather than looping forever. The last irreducible lifter is the human operator —
> autonomy has a floor (INV-YV1).
