# Metrics Inference Report

One consolidated report over the metrics this repo already computes, each value
carrying explicit provenance. No invented numbers: every value is read from a
real deterministic call into existing code. Two calls to `build_metrics_report()`
are deep-equal (no timestamps, no random fields).

## Tiers (operational)

- **MEASURED** — aggregate of a real deterministic run over the fixed benchmark
  corpus (N=100, proxy scorers, no human labels). Source: `run_benchmark()` and
  `run_benchmark_v6()`.
- **SIMULATED** — a metric from synthetically degraded inputs (mutation-testing
  style). Source: discharge-gate discriminant AUC over intact vs degraded
  artifacts (degradation families: drop_sections, off_topic, pad,
  strip_falsifier, inject_forbidden). Caveat: degradations are synthetic, not
  field data.
- **EXTRAPOLATED** — a projection read off a sampled curve. Source:
  `node_scaling_curve()` — `optimal_node_count` (argmax of cluster_quality over
  k in {1,2,3,5,8}) and `projected_cluster_quality_plateau` (the max sampled
  value). Caveat: values between/beyond sampled k are not measured.

## Provenance fields

Each metric carries: `name`, `value`, `tier`, `procedure`, `sample_n`, `caveat`.
Asserted prose (`name`, `procedure`, `caveat`) is run through the forbidden-claim
gate before emission; a hit raises (fail-closed).

## How to run

CLI:

```
noesis metrics
```

API:

```
POST /metrics    # or GET /metrics
```

Both return the report; the report validates against
`schemas/metrics_inference_report.schema.json`.

## not_claimed

The report carries an explicit negative declaration of what is **not** claimed:

- AGI
- artificial consciousness
- therapy
- medical validity
- scientific proof of consciousness expansion
- field-validated effect

This list is a disclaimer, so it is intentionally exempt from the forbidden-claim
gate (self-blocking a disclaimer would be incoherent).
