# Quarantine Ledger — Tight-Toolkit Pass

**Date:** 2026-06-15
**Scope decision:** "Тугий практичний тулкіт" — keep only docs backed by a live, tested
module or required by the practical/honesty spine; quarantine pure theory/metaphysics
and superseded version snapshots. **Nothing deleted — moved here, fully reversible via `git mv`.**

## Objective criterion applied

A doc was quarantined **only** if it met one of:
1. **No live module** implements it (pure theory / metaphysics / analogy overlay), or
2. **Superseded version snapshot** — a `_V6`/`_V7`/`_V2`/`_V06` doc whose canonical
   replacement (`VALIDATION.md`, `ROADMAP.md`, current `VERDICT`/architecture) already exists.

All 63 docs were checked against `noesis/`, `noesis/gates/`, `noesis/runtime/`, `formal/`,
`tools/` and `tests/`. **52 docs were KEPT** because each maps to live, tested code
(e.g. `adaptive.py`, `causal.py`, `collapse_controller.py`, `dimensionality.py`,
`cluster_quality.py`, `broadcast.py`, `precision_gate.py`, `residual_promotion.py`,
`bottleneck_plan.py`). Loud titles ≠ decoration — most "neuro" docs document real modules.

## Quarantined (11)

| Doc | Reason | Live module? |
|-----|--------|--------------|
| CIVILIZATIONAL_METAPHYSICS.md | Pure metaphysics, decorative | NONE |
| EXTERNALIZED_ACTIVE_INFERENCE.md | Theory overlay, no implementation | NONE |
| GNWT_OPERATIONAL_ANALOGY.md | Analogy overlay on `broadcast.py`; the doc is decoration, the code stays | code kept |
| philosophy.md | Non-operational manifesto-adjacent prose | NONE |
| VERDICT_V6.md | Superseded version snapshot | canon = current VERDICT |
| VERDICT_V7.md | Superseded version snapshot | canon = current VERDICT |
| VALIDATION_V6.md | Superseded | canon = VALIDATION.md |
| VALIDATION_V7.md | Superseded | canon = VALIDATION.md |
| ROADMAP_V6.md | Superseded | canon = ROADMAP.md |
| NOESIS_V06_ARCHITECTURE.md | Superseded version snapshot | canon = ARCHITECTURE.md |
| ABLATION_V2.md | Superseded version snapshot | current ablation in benchmark docs |

## Not touched in this pass (flagged, requires owner decision)

The real bulk is **code version-churn**, not docs: `noesis/pipeline_v5→v6→v7→v8` form a
live **dependency chain** wired into `app/api.py` and `noesis/cli.py` public surface
(v6/v7/v8 endpoints + commands). Collapsing to a single canon is a **breaking refactor**
(drops public API surface, semver-major), not a quarantine. See `artifacts/NEXT_ACTIONS.md`.

## Reversal

```bash
git mv docs/quarantine/<NAME>.md docs/<NAME>.md   # and revert link repointing
```
