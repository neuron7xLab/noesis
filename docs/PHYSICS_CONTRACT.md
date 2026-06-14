# Physics Contract — Noesis (Role 2)

> Role 2 — Physics Contract Implementer. Converts the Role 1 boundary audit
> ([`data/physics_boundary_report.json`](../data/physics_boundary_report.json)) into an
> **executable** contract that fails automatically when the repository violates the
> physics boundary.

## What this layer is

A deterministic contract gate. It reads the Role 1 report, enforces ten contract
objects, and writes [`data/physics_boundary_contract.json`](../data/physics_boundary_contract.json).
It is **not** philosophy: if physics is only metaphor — no state, no constraint, no
invariant, no operator, no residual split, no measurement, no verifier, no
trajectory, no rollback — `contract_status` is `FAIL`.

## Run it

```bash
python -m noesis.contracts.physics_boundary_cli validate   # standalone module
python -m noesis.cli physics-boundary validate             # via the single CLI
```

Exit `0` only on `PASS`; exit `1` on any `FAIL` (unblocked forbidden claim, schema
failure, absent trajectory fields, missing Role 3 handoff, ...).

## Contract objects (typed, `noesis/contracts/physics_boundary.py`)

`StateVariable`, `BoundaryCondition`, `Invariant`, `OperatorContract`,
`MechanismResidualContract`, `TrajectoryContract`, `MeasurementMetric`,
`VerifierContract`, `ClaimStatusContract`, `ReleaseGate` — frozen dataclasses
(matching the repo idiom in `noesis/models.py`). JSON is validated with
`jsonschema`, consistent with the rest of the project. Every check returns
`PASS | FAIL | MISSING | UNKNOWN`; every violation is a structured `Failure`
(`failure_code`, `file_path`, `reason`, `required_fix`) — no silent failure.

## Schemas

| Schema | Validates |
|---|---|
| `schemas/physics_boundary_contract.schema.json` | the contract report |
| `schemas/operator_contract.schema.json` | one operator (`input→operation→output→validator`) |
| `schemas/claim_status_contract.schema.json` | one governed claim |
| `schemas/trajectory_contract.schema.json` | the per-operator trajectory fields |

## Hard-fail gates (FAIL regardless of score)

1. report schema invalid / missing
2. unblocked forbidden claim
3. a KEEP operator without a validator (or a KEEP operator without a repo location)
4. absent trajectory fields
5. missing Role 3 handoff
6. missing contract JSON
7. missing CLI command

## Scoring (0–100, PASS ≥ 80)

state 10 · boundary 10 · invariant 10 · operator 15 · mechanism/residual 10 ·
trajectory 10 · measurement 10 · verification 10 · claim-status 10 · role-3 5.
Score is informational; a hard-fail gate overrides it.

## Current verdict on this tree

`contract_status = FAIL`, `score = 95/100`, `hard_failures = ["trajectory"]`. This
is the **designed** behavior: Role 1 already named the missing per-operator
trajectory trace (`score_t`, `decision_t`, `rollback_condition_t`,
`state_t→state_t+1`) as the binding gap, and the contract gate now enforces it —
the build is not green until that trace exists. The contract LAYER itself is
complete and its tests pass; the FAIL is the gate correctly rejecting an
incomplete repository.

## Role 3 handoff

Derived from the first failing hard gate (`trajectory`):
**TRAJECTORY TRACE IMPLEMENTER** — create `schemas/trajectory_trace.schema.json`,
`noesis/trajectory.py`, `tests/test_trajectory_trace.py`; modify
`noesis/pipeline_v8.py`, `noesis/evidence.py`, `noesis/cli.py`. When implemented,
`python -m noesis.contracts.physics_boundary_cli validate` must exit `0`.

## Claim governance

Forbidden claims (AGI, consciousness detection/measurement, brain-bandwidth
measurement, biological GNWT proof, therapy, diagnosis, ungated "SpaceX/xAI
quality", LLM-judge-as-truth, proxy-as-measurement, "more agents = better
cognition") are blocked and mapped to safe research-software replacements in
`noesis/contracts/physics_boundary.py::FORBIDDEN_CLAIMS`.
