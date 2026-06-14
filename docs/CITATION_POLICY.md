# Citation Policy

When to cite, when to mark proxy, and when to refuse a claim outright.

## 1. When to cite
Cite a primary or review source whenever the software borrows a **concept,
vocabulary, or framing** from cognitive science, neuroscience, AI, philosophy,
or software engineering. The citation grounds the *framing*, not an
implementation. Record it in `data/sources.json` with `used_in` pointing at the
exact files that use it.

## 2. When to mark proxy (S5)
If a construct is implemented as a heuristic, text-structural approximation, or
composite score — say **proxy**. The word "proxy" must appear in the claim text
or allowed wording, and a `forbidden_wording` must name the overclaim it must
not become (enforced by Gate 8). Examples: IEV bandwidth, cognitive
dimensionality, cluster quality, Φ-proxy, theory lenses.

## 3. When to mark analogy (S4)
If the software borrows *structure* from a theory but does not instantiate it,
say **analogy**: GNWT broadcast, externalized active inference, the
low-bandwidth controller, the conceptual-engineering category layer. Analogy is
never identity.

## 4. When to mark speculative (S6)
A construct with no validation and no adequate source is **speculative** and
must be listed in [`UNSUPPORTED_CLAIMS.md`](UNSUPPORTED_CLAIMS.md) (e.g. EIIC).

## 5. When to refuse a claim (X)
If a statement asserts AGI, consciousness detection, experience measurement,
therapy, diagnosis, destiny, physical entropy, or measured neural quantities —
**refuse it**. Replace with the safe wording in
[`OVERCLAIM_GUARDRAILS.md`](OVERCLAIM_GUARDRAILS.md).

## 6. Source quality bar
At least **70%** of theory anchors must be primary or review literature
(Gate 5). Engineering analogies and background sources are allowed but cannot
dominate the theory base.

## 7. No decorative citations
A source that anchors no claim and is used in no file is removed (Gate 6/7). A
source cited in docs but not yet central to a ledger claim is marked
**background**, not deleted.

## 8. Adding a new theory term
Add the term to `data/theory_vocabulary.json` **with** its `source_ids` in the
same change. `tests/test_bibliography_coverage.py` (Gate 10) fails otherwise.
