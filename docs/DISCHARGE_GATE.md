# Discharge Gate — when thought becomes action

`noesis/gates/discharge_gate.py`. The kernel equation:

```
w = αR + βV + γP − δK
```

R = relevance to intent, V = verifier strength, P = progress value,
K = cost/risk/latency (all in `[0, 1]`). Weights come from
`noesis.gate_functional.GateFunctional` (α .4 · β .3 · γ .2 · δ .3 · θ .5).

## Decision law (`DischargeGate.decide`)

Evaluated in order — risk and verification both bite:

1. `verifier_failed` → **FAIL**
2. `cost ≥ risk_ceiling` (0.85) → **HUMAN_REVIEW** (too risky to auto-discharge)
3. `w < θ` → **BELOW_THRESHOLD** (noise; no discharge)
4. `w ≥ θ` but `verifier < verifier_floor` (0.25) → **REROUTE** (needs evidence)
5. otherwise → **PASS** (discharge)

PASS can never occur below θ. Out-of-range inputs raise `ValueError`.

## Metrics (`gate_metrics`)

`gate_pass_rate`, `noise_rejection_rate` (BELOW_THRESHOLD share),
`human_review_rate`, `threshold_sensitivity` (share of decisions that flip when θ
is nudged ±0.05 — how close the batch sits to the cliff).

## Run

```bash
python -m pytest tests/test_discharge_gate.py -q
```
