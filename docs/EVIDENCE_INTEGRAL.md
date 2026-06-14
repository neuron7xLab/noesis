# Evidence Integral / Hash-Chain Bundle

`noesis/evidence_integral.py`. Stores the **integral of the process**, not just
the final result:

```
∫ process = ordered trace of state transitions + decisions + artifacts + hashes
```

Each transition is sha256-chained to its predecessor; the whole run is anchored
by `final_manifest_hash`, so it is replayable bit-for-bit.

## Bundle fields

`run_id`, `input_hash`, `state_transition_hashes` (chained), `artifact_hashes`,
`decision_hashes`, `verifier_outputs`, `rollback_points`, `final_manifest_hash`.
Artifacts carry a `transition_index` (link to a transition); transitions may
carry a `verifier_index` (link to a verifier output).

## A bundle is invalid if

- an artifact has no trace (`ARTIFACT_WITHOUT_TRACE`)
- a transition has no hash (`TRACE_WITHOUT_HASH`) / artifact has no hash (`ARTIFACT_WITHOUT_HASH`)
- a verifier result is not linked (`VERIFIER_NOT_LINKED`)
- the chain cannot be replayed (`BUNDLE_NOT_REPLAYABLE`)

`replay()` recomputes the chain + manifest hash; any tamper flips it to `False`.

## Metrics

`reproducibility_score`, `hash_coverage_rate`, `artifact_traceability_rate`,
`verifier_attachment_rate`.

> Path: flat `noesis/evidence_integral.py` (the `evidence` name is taken by
> `noesis/evidence.py`); equivalent to the spec's `cme/evidence/evidence_integral.py`.

```bash
python -m pytest tests/test_evidence_integral.py -q
```
