# Next Actions — Owner Decision Required

## 1. Pipeline version collapse `v5→v8` (BREAKING — needs go/no-go)

**Finding.** The real bulk in this repo is not docs — it is a live **version chain**:

```
noesis/pipeline_v5  ◄─ benchmark.py
noesis/pipeline_v6  ◄─ app/api.py, cli.py, entropy_ledger, precision_gate, dimensionality, broadcast, pipeline_v7
noesis/pipeline_v7  ◄─ app/api.py, cli.py, cluster_quality, precision_scheduler, pipeline_v8, benchmark_v7/v8
noesis/pipeline_v8  ◄─ canon
+ benchmark_v6/v7/v8, evidence_bundle_v6/v7/v8 schemas, test_noesis_v6/v7/v8
```

`v8` transitively depends on `v7→v6→v5` and **`app/api.py` + `noesis/cli.py` expose
public v6/v7/v8 endpoints and commands.** Collapsing to a single canon (`v8`) means:

- inlining the still-used logic from v5/v6/v7 into v8 (or a clean `pipeline.py`),
- **removing public API endpoints** (`/pipeline/v6`, `/pipeline/v7`, ablation_v6 …) and CLI subcommands → **semver-major breaking change**,
- rewriting `test_noesis_v6/v7` against the unified surface,
- retiring `evidence_bundle_v6/v7` schemas + `VERDICT_V6/V7`, `VALIDATION_V6/V7` (docs already quarantined).

**This was deliberately NOT done in the doc-quarantine pass** — it would break the 537-green
baseline and drop public surface, which is your call, not an autonomous one.

**Decision needed:** OK to drop the v6/v7 public API/CLI surface? If yes → I do it as its own
test-covered PR (unify to v8, update 537 tests, keep coverage ≥90%, ship green).

## 2. Schema minimization (follow-on to #1)

56 schemas; the `_v6/_v7/_v8` evidence-bundle trio collapses with the pipeline collapse above.
The rest map 1:1 to live modules — no orphan schemas found this pass.
