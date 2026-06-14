# Physics Boundary Audit — Noesis / Noemic Gate

> Role 1 — First-Principles Physics Auditor.
> Repository treated as a controlled state-transformation loop `x_t → O_i(x_t) → x_{t+1}`.
> Machine-readable companion: [`data/physics_boundary_report.json`](../data/physics_boundary_report.json)
> validated by [`tests/test_physics_boundary_report_schema.py`](../tests/test_physics_boundary_report_schema.py).

## 1. System identity

- **Type:** deterministic + LLM-assisted externalized-metacognition pipeline over text,
  shipped as the `noesis` CLI (44 subcommands incl. `bibliography`) and a FastAPI
  service (`app.api:app`). Explicitly **not** AGI, therapy, diagnosis, or
  consciousness detection.
- **Core transformation:** `raw_text → complexity → adaptive mirror → causal categories
  → reality-map delta → theory contribution → EIIC → action selection → artifact →
  12 gates → Evidence Bundle → verdict`, with a claim-to-source bibliographic evidence
  graph as a cross-cutting governance layer.
- **Input state:** intent-bearing natural-language text.
- **Output state:** Evidence Bundle (15 files in v0.8) with `overall_status` PASS/FAIL,
  sha256 `input_hash`, deterministic-vs-LLM module split.
- **Validation boundary:** 12 deterministic gates + jsonschema (38 schemas) +
  forbidden-claim detector + hallucination-risk heuristic + provenance tagging +
  bibliographic evidence-graph gate. LLM output is advisory prose only and cannot
  pass a gate by itself.

## 2. State model

Nine of ten candidate state variables are repo-backed and test-covered
(`S1_TESTED`): intent, context, candidate, claim, evidence, gate, artifact,
verification, release. The tenth — an explicit per-operator **trajectory_state** —
exists only as single-shot schemas (`inference_trace`, `broadcast_trace`) and is
rated `S5_PROXY`. Evidence paths in `state_model.state_variables` of the JSON.

## 3. Boundary conditions

- Every artifact MUST validate against its jsonschema.
- Every high-level claim MUST carry exactly one provenance tag
  `{observed, inferred, speculative, forbidden}` (`noesis/provenance.py`).
- Every literature-grounded claim MUST resolve to a source in the bibliographic
  evidence graph (`noesis/bibliography.py`, `tests/test_bibliography_coverage.py`).
- An artifact MUST pass all 12 gates for `overall_status = PASS`.
- Extrapolated EIIC cores are force-tagged `speculative` (Gate 8).
- `ruff` + `mypy --strict` + `pytest` with a ≥90% coverage gate MUST be green in CI.

Forbidden claims (blocked by `noesis/forbidden.py`): AGI, consciousness
detection/measurement, IIT-proves-experience, medical diagnosis/healing/therapy,
destiny/karma/mysticism, validated-brain-model-without-data, overconfidence markers.

## 4. Invariants

| Invariant | Conserves | Verified by |
|---|---|---|
| intent_coherence | artifact stays aligned to extracted intent | `intent_coherence_score` + signal/noise check |
| claim_status_traceability | one provenance tag per claim | `noesis/provenance.py`, `tests/test_noesis_v4.py` |
| source_traceability | literature claim maps to a real source | `noesis/bibliography.py`, `tests/test_bibliography_coverage.py`, Gate 13 |
| proxy_honesty | proxies labelled, never promoted | `docs/THEORIES.md`, ablation, VERDICT.md |
| artifact_reproducibility | same input → same run_id offline | `noesis/evidence.py` sha256 |
| human_responsibility | human keeps decision authority | `human_bottleneck_score`, forbidden detector |
| validation_evidence | no PASS without populated validation + gates | `noesis/verdict.py` |
| entropy_gating | admit only intent-preserving, precision-raising content (w ≥ θ) | `noesis/gate_functional.py`, `tests/test_gate_math.py` |

## 5. Operator map

Ten operators mapped `input → operation → output → validator` (full table in JSON
`operator_map`). Decisions:

- **KEEP (7):** Complexity, IntentVector, GateFunctional, CollapseController,
  ForbiddenClaim, **Bibliography** (claim-to-source evidence graph), Evidence.
- **MODIFY (2):** AdaptiveMirror (pads short inputs — compression metric honestly
  fails), Verdict (raises `FileNotFoundError` on an absent bundle instead of a
  graceful `BLOCKED`).
- **CREATE (1):** TrajectoryTrace (absent — only single-shot trace schemas exist).

## 6. Mechanism vs residual

- **Mechanism (deterministic):** 12 gates, IEV gate functional, 38 schemas,
  provenance + forbidden detectors, bibliographic evidence graph, Evidence Bundle +
  sha256, 100-input benchmark + ablation, verdict gate.
- **Residual (LLM):** finalizer prose quality only; LLM off the critical path.
- **Promotion rule:** residual cannot become mechanism truth without a gate + schema
  + provenance tag (+ a source edge for literature claims). Enforced architecturally
  and by the bibliography gate, but **not yet a single coded promotion-gate test**.

## 7. Trajectory trace

`current_trace_support = PARTIAL`. The Evidence Bundle persists final per-stage
artifacts (15 files, `input_hash`, manifest metrics) but **no stepwise trace
record** with `score_t`, `decision_t`, `rollback_condition_t`, or explicit
`state_t → state_t+1`. A run is auditable by artifact, not replayable by step.
This is the binding gap (see §12).

## 8. Measurement model

Computed + thresholded: `intent_coherence_score`, `noise_rejection_score`,
`iev_bandwidth_score`, `latency_drag_score`, `human_bottleneck_score`,
`source_coverage_rate`, `test_coverage` (≥90% gate, 92.61% observed), plus benchmark
`claim_safety_rate`/`artifact_validity_rate` (=1.0, structural consistency only).
PROXY/MISSING: `operator_coverage_rate`, `rollback_rate` (no stepwise trace),
`human_preference_quality` (deferred to Phase 3 human eval).

## 9. Verification model

`pytest` (215 PASS + ≥90% coverage gate), `ruff` (clean), `mypy --strict` (64 files),
jsonschema validation, forbidden-claim verifier, claim-status verifier,
**bibliography verifier (`noesis bibliography validate` → exit 0, Gate 13)**, verdict
gate, 100-input benchmark, and this audit's schema test (7 PASS).

## 10. Claim audit

- **Repo facts:** 215 pytest @92.61% coverage, mypy strict (64 files), ruff clean,
  38 schemas, 44 CLI subcommands, 15-file v0.8 bundle, bibliographic evidence graph.
- **Tested:** forbidden detection, IEV gate functional, schema validation,
  bibliography coverage.
- **Literature:** WM/cognitive-control/metacognition/GWT/active-inference/distributed-
  cognition sources carried in the evidence graph as S2/S3, not implementations.
- **Proxy:** 12 "theories" are text proxies; benchmark rates measure structure;
  IEV gate/bandwidth/dimensionality are labelled heuristics.
- **Speculative:** EIIC extrapolated cores (force-tagged).
- **Unsupported (self-flagged):** "compression" on short inputs; category layer
  decorative for validation.
- **Forbidden detected and unblocked:** none.

## 11. Quality score

| Category | Score |
|---|---|
| state_model | 8 |
| constraint_model | 9 |
| operator_model | 8 |
| mechanism_residual_split | 8 |
| trajectory_trace | 7 |
| measurement_model | 8 |
| verification_model | 9 |
| claim_governance | 10 |
| github_agent_readiness | 8 |
| **TOTAL** | **75 / 90** |

PASS threshold is 72 with no unblocked forbidden claim, a non-empty first missing
condition, and an executable Role 2 handoff — all satisfied.

## 12. First missing condition

> There is no unified machine-readable per-operator trajectory trace: the Evidence
> Bundle persists final per-stage artifacts but no stepwise record carrying
> `score_t`, `decision_t`, `rollback_condition_t`, and explicit
> `state_t → state_t+1`, so a run cannot be replayed or rolled back step by step.

## 13. Role 2 handoff — TRAJECTORY TRACE IMPLEMENTER

- **Create:** `schemas/trajectory_trace.schema.json`, `noesis/trajectory.py`,
  `tests/test_trajectory_trace.py`.
- **Modify:** `noesis/pipeline_v8.py`, `noesis/evidence.py`, `noesis/cli.py`.
- **Validate:**
  ```bash
  python -m noesis.cli pipeline-v8 examples/problems/08_ai_system_design.txt --evidence out/
  test -f out/trajectory_trace.json
  python -m pytest tests/test_trajectory_trace.py -q
  python -m pytest -q && ruff check . && mypy
  ```
- **Pass/fail:** `out/trajectory_trace.json` validates against its schema; one
  ordered record per executed operator with all nine trace fields; replay
  continuity `state_t_plus_1[n] == state_t[n+1]`; test fails if any executed
  operator is missing from the trace; pytest + ruff + mypy green and ≥90% coverage
  holds.

## 14. Verdict

**PASS — 75/90.** Noesis is a genuinely honest, gate-governed cognitive pipeline:
deterministic mechanism cleanly separated from LLM residual (LLM off the critical
path), every claim provenance-tagged AND, where it cites literature, edge-bound to a
real source in the bibliographic evidence graph, forbidden claims blocked and tested.
It clears the boundary bar. Its next required build is the stepwise trajectory trace
(Role 2), without which the loop is auditable by artifact but not replayable by step.

> Protocol command note: the Role 1 spec used `cme.cli`; the canonical package is
> `noesis` (`python -m noesis.cli ...`). `noesis bibliography validate` exists and
> passes (exit 0). `noesis verdict` requires a bundle dir argument
> (`noesis verdict out/` after a pipeline run), not `.`.
