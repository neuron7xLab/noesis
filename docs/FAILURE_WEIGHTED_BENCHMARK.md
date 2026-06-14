# Failure-Weighted Benchmark + Release Verdict

`noesis/evaluation/failure_weighted_benchmark.py`. Makes failure signal stronger
than self-simulated success:

```
quality = verified_improvement − unsupported_claims − rollback_debt − human_gate_overload
```

## Dimensions (each `[0,1]`, weighted)

`artifact_quality` (.15) · `verification_strength` (.20) · `claim_safety` (.20) ·
`rollback_coverage` (.15) · `trace_completeness` (.10) · `gate_consistency` (.10) ·
`release_readiness` (.10).

`verified_improvement` = weighted sum. Penalties: unsupported (.10/claim),
forbidden (.25/claim), rollback debt (.05/item), human overload (.10×fraction).
`failure_weighted_score = verified_improvement − penalties`.

## Release verdict

`PASS` only if **none** of: forbidden claims, unsupported claims, open hard
failures, score < 0.55, release readiness < 0.50. Otherwise `FAIL` with explicit
`hard_blocks`.

`assemble_from_repo(root, dimensions)` pulls `hard_failures` and `UNSUPPORTED`
claims straight from `data/physics_boundary_contract.json` — so the open
trajectory hard failure (Role 2) propagates into a `FAIL` release verdict until
Role 3 closes it.

## Metrics

`failure_weighted_score`, `rollback_debt`, `unsupported_claim_count`,
`forbidden_claim_count`, `release_readiness_score`.

```bash
python -m pytest tests/test_failure_weighted_benchmark.py -q
python -m pytest -q
ruff check .
```
