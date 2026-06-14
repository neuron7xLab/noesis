# Source / Claim Status Hierarchy

Every claim and every source in Noesis carries exactly one status. The status
says *how strongly the software is entitled to assert the thing* — nothing more.

| status | name | meaning |
|---|---|---|
| **S0** | Repository fact | Directly present in code, schema, test, docs, or benchmark output. |
| **S1** | Deterministically validated | Verified by pytest, schema validation, a CLI run, a benchmark run, or a CI gate. |
| **S2** | Primary literature grounded | Supported by an original paper, book, or canonical formal source. |
| **S3** | Review literature grounded | Supported by a review, survey, synthesis, or meta-level scholarly source. |
| **S4** | Engineering analogy | A structurally useful analogy — not literal identity. |
| **S5** | Operational proxy | Implemented as a proxy metric, heuristic, or text-structural approximation. |
| **S6** | Speculative construct | A useful projection or research hypothesis — not validated. |
| **X**  | Forbidden claim | Must not be emitted as valid output. See [`OVERCLAIM_GUARDRAILS.md`](OVERCLAIM_GUARDRAILS.md). |

## Reading rules
- **S0–S1** are about the *software*: the thing is in the repo and/or machine-checked.
- **S2–S3** are about the *literature*: the framing is grounded in scholarship,
  but the software does not thereby *implement* the theory.
- **S4–S5** are honesty floors: an analogy is an analogy; a proxy is a proxy.
  Wording that upgrades S4/S5 to S0/S1/S2 is an overclaim.
- **S6** must always be labelled speculative; it may never be presented as validated.
- **X** is blocked at runtime by `noesis/forbidden.py` (`gate12_forbidden`).

## Promotion is forbidden by default
A claim does not move up the hierarchy because it sounds confident. Promotion
(S5→S2, S4→S1, …) requires new repo evidence or new sources recorded in
`data/sources.json` and `data/claim_source_ledger.json`. The bibliography
validator (`noesis bibliography validate`) enforces the floors.
