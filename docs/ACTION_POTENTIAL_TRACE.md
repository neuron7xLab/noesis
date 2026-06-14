# Action Potential Trace

`noesis/runtime/action_potential_trace.py`. Every agent action is recorded as a
gated state transition, never as free-form output:

```
state_t → potential_delta → gate_score → decision → artifact_delta → state_t+1
```

## Record fields

`trace_id`, `cycle_id`, `state_t`, `intent_delta`, `unfinished_work_delta`,
`gate_score`, `threshold`, `decision`, `artifact_delta`, `rollback_condition`,
`state_t_plus_1`. Build one from a discharge-gate result with `record_from_gate`
(it copies `gate_score`/`threshold`/`decision` straight from the gate, so a
decision can never lack its score).

## A record is invalid (the trace fails) if

- it has no threshold (`validate_payload`: `ACTION_NO_THRESHOLD`)
- the decision has no score (`DECISION_NO_SCORE`)
- `artifact_delta` is empty (`ARTIFACT_DELTA_EMPTY`)
- `rollback_condition` is missing (`ROLLBACK_MISSING`)

`validate_record` checks a typed record; `validate_payload` checks a raw dict
(missing-key detection for external traces).

## Metrics

`trace_completeness_rate`, `rollback_defined_rate`, `decision_explainability_rate`.

## Example + run

[`data/action_potential_trace.example.json`](../data/action_potential_trace.example.json)
is a real, schema-valid trace (PASS / BELOW_THRESHOLD / HUMAN_REVIEW cycles).

```bash
python -m pytest tests/test_action_potential_trace.py -q
```
