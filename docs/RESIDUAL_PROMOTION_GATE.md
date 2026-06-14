# Residual → Mechanism Promotion Gate

`noesis/gates/residual_promotion.py`. Prevents an LLM guess (residual) from
becoming system truth (mechanism) without verification:

```
residual_candidate → verifier → promotion_decision → mechanism_update
```

## States

`RESIDUAL` · `CANDIDATE_MECHANISM` · `VERIFIED_MECHANISM` · `REJECTED` ·
`HUMAN_REVIEW_REQUIRED`. `mechanism_update` is `True` **only** for
`VERIFIED_MECHANISM`.

## Decision law (`promote`, fail-closed order)

1. forbidden claim → `REJECTED`
2. proxy claiming to be a measurement → `REJECTED`
3. no verifier attached → `RESIDUAL` (cannot promote)
4. unsupported claim → `HUMAN_REVIEW_REQUIRED`
5. verifier attached but not run → `CANDIDATE_MECHANISM`
6. verifier failed → `REJECTED`
7. verifier passed → `VERIFIED_MECHANISM`

## Metrics

`unverified_promotion_block_rate` (must be 1.0 — nothing unverified updates a
mechanism), `verified_promotion_rate`, `rejected_residual_rate`,
`mechanism_stability_rate` (every mechanism update is a verified mechanism).

## Run

```bash
python -m pytest tests/test_residual_promotion.py -q
```
