# First Principles — the bibliography is the constitution

Noesis is a thinking instrument. A thinking instrument has no right to assert
anything it cannot trace. The bibliographic evidence graph is therefore not
documentation *about* the system — it is the **first principle** the system is
built on. Every other layer is downstream of it.

## The five invariants

1. **No claim without status.** Every important assertion carries exactly one
   status from the hierarchy S0..S6/X ([`SOURCE_STATUS_HIERARCHY.md`](SOURCE_STATUS_HIERARCHY.md)).
   A claim with no status does not exist.

2. **No status without solidity.** Every claim is anchored to ≥1 source
   (Gate 11). Nothing floats. There is no silent "trust me" — speculative
   constructs (S6) are still source-framed and quarantined in the open
   ([`UNSUPPORTED_CLAIMS.md`](UNSUPPORTED_CLAIMS.md)).

3. **No solidity without hierarchy.** A claim's *type* fixes the band of
   statuses it may hold (Gate 12): an implementation claim is S0/S1, a proxy is
   S5, an analogy is S4, a literature claim (S2/S3) must actually cite primary or
   review literature. Promotion across the hierarchy is forbidden by default —
   it requires new repo evidence or new sources, not more confidence.

4. **No hierarchy without verification.** The graph is machine-checked, not
   asserted. 13 gates run in CI ([`tests/test_bibliography_coverage.py`](../tests/test_bibliography_coverage.py)):
   coverage, status, limitation, forbidden mapping, source quality (≥70%
   primary/review), repo linkage, no decorative sources, proxy honesty, human
   responsibility, term mapping, solidity, hierarchy, and a **runtime guard**
   that proves the forbidden data is actually caught by `noesis/forbidden.py`.

5. **No verification without consequence.** A claim that cannot be sourced,
   validated, or bounded is marked unsupported or removed. A theory term that
   loses its source mapping fails the build (Gate 10). A forbidden overclaim has
   a safe replacement and a blocking gate ([`OVERCLAIM_GUARDRAILS.md`](OVERCLAIM_GUARDRAILS.md)).

## Why this comes first
Most "AI thinking tools" inflate: an analogy becomes a mechanism, a proxy
becomes a measurement, a hypothesis becomes a fact. Noesis inverts the default.
The burden of proof sits on the claim, the hierarchy is enforced in code, and
the honest backlog is visible rather than hidden. The bibliography is what makes
the instrument trustworthy enough to think *with*.

## Operate it
```bash
noesis bibliography verdict     # full evidence verdict (non-zero on failure)
noesis bibliography validate    # 13 gates
noesis bibliography missing     # the honest backlog
```
Canonical data: `data/sources.json`, `data/claim_source_ledger.json`,
`data/forbidden_claims.json`, `data/theory_vocabulary.json`. Everything else in
the bibliography is generated from these — never hand-edited.
