# Rollback Physics

`noesis/runtime/rollback.py`. Every invalid discharge is reversible:

```
invalid_state → rollback_condition → restore_previous_valid_state
```

A digital discharge — unlike a biological action potential — carries a
`rollback_condition`. That is what lets the action-potential runtime treat a
tentative state as *not yet an action* until it survives verification.

## Rollback types

`schema_failure` · `test_failure` · `claim_failure` · `benchmark_regression` ·
`forbidden_claim_detected` · `human_rejection` · `artifact_instability`.

## Controller

`RollbackController.checkpoint()` records a known-good state; `discharge()`
applies a tentative state; `trigger(rollback_type)` drops the tentative top and
restores the last valid state. No prior valid state → `StateLossError`. An
unknown rollback type → `ValueError`.

`can_release(benchmark_passed, open_rollbacks)` — a run may release **only** with
a passing benchmark and zero open rollbacks (a failed benchmark never releases).

## Metrics

`rollback_defined_rate`, `rollback_success_rate`, `invalid_state_recovery_rate`,
`state_loss_rate`.

```bash
python -m pytest tests/test_rollback.py -q
```
