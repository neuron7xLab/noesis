"""Bibliography coverage gate.

Fails if the claim-to-source evidence graph is inconsistent, if a theory term
appears in the repo without a source mapping (Gate 10), or if the committed
generated docs have drifted from the canonical data.
"""

from __future__ import annotations

import dataclasses
import json

import pytest
from fastapi.testclient import TestClient

from app.api import app
from noesis import bibliography as bib


@pytest.fixture(scope="module")
def lib() -> bib.Library:
    return bib.load_library()


@pytest.fixture(scope="module")
def scan(lib: bib.Library) -> bib.ScanResult:
    return bib.scan_repo(lib)


# --- gates -------------------------------------------------------------------

def test_all_gates_pass(lib: bib.Library, scan: bib.ScanResult) -> None:
    results = bib.validate(lib, scan)
    failed = [r.gate for r in results if not r.passed]
    assert not failed, f"failing gates: {failed}"
    assert len(results) == 13


def test_no_unsupported_or_orphan(lib: bib.Library, scan: bib.ScanResult) -> None:
    """First principle: only solid, anchored data — no claim without a source,
    no source without a claim."""
    m = bib.missing(lib, scan)
    assert m["claims_without_sources"] == []
    assert m["sources_without_claims"] == []


def test_hierarchy_type_status_coherent(lib: bib.Library) -> None:
    for c in lib.claims:
        allowed = bib.CLAIM_TYPE_STATUS.get(c.claim_type)
        if allowed is not None:
            assert c.status in allowed, f"{c.claim_id}: {c.claim_type} cannot be {c.status}"


def test_runtime_guard_probes_are_caught(lib: bib.Library) -> None:
    from noesis.forbidden import check_forbidden_claims

    for f in lib.forbidden:
        if f.gate_that_blocks_it == "gate12_forbidden":
            assert f.probe.strip(), f.id
            assert check_forbidden_claims(f.probe), f"runtime guard misses {f.id}"


def test_every_claim_has_valid_status(lib: bib.Library) -> None:
    for c in lib.claims:
        assert c.status in bib.VALID_STATUSES, c.claim_id


def test_no_broken_source_refs(lib: bib.Library) -> None:
    by_id = lib.source_by_id
    for c in lib.claims:
        for sid in c.source_ids:
            assert sid in by_id, f"{c.claim_id} -> unknown source {sid}"


def test_proxy_claims_say_proxy(lib: bib.Library) -> None:
    for c in lib.claims:
        if c.claim_type == "proxy_claim":
            blob = (c.claim_text + " " + c.allowed_wording).lower()
            assert "proxy" in blob and c.forbidden_wording.strip(), c.claim_id


def test_forbidden_claims_have_replacement_and_gate(lib: bib.Library) -> None:
    assert lib.forbidden
    for f in lib.forbidden:
        assert f.safe_replacement.strip() and f.gate_that_blocks_it.strip(), f.id


def test_theory_anchor_quality_at_least_70_percent(lib: bib.Library, scan: bib.ScanResult) -> None:
    gate5 = next(r for r in bib.validate(lib, scan) if r.gate.startswith("Gate 5"))
    assert gate5.passed, gate5.detail


# --- Gate 10: the core invariant --------------------------------------------

def test_unmapped_theory_term_fails_gate10(lib: bib.Library, scan: bib.ScanResult) -> None:
    """Simulate a new theory term added without a citation mapping."""
    present = next(iter(scan.present_terms))  # a term that really occurs in the repo
    broken_vocab = [
        dataclasses.replace(t, source_ids=[]) if t.term == present else t
        for t in lib.vocabulary
    ]
    broken = dataclasses.replace(lib, vocabulary=broken_vocab)
    broken_scan = bib.scan_repo(broken)
    gate10 = next(r for r in bib.validate(broken, broken_scan) if r.gate.startswith("Gate 10"))
    assert not gate10.passed
    assert any(present in o for o in gate10.offenders)


def test_unknown_source_ref_fails_gate10(lib: bib.Library) -> None:
    present = next(iter(bib.scan_repo(lib).present_terms))
    broken_vocab = [
        dataclasses.replace(t, source_ids=["does_not_exist"]) if t.term == present else t
        for t in lib.vocabulary
    ]
    broken = dataclasses.replace(lib, vocabulary=broken_vocab)
    gate10 = next(r for r in bib.validate(broken, bib.scan_repo(broken)) if r.gate.startswith("Gate 10"))
    assert not gate10.passed


# --- generated-doc drift guard ----------------------------------------------

def test_generated_docs_in_sync(lib: bib.Library, scan: bib.ScanResult) -> None:
    checks = {
        "docs/BIBLIOGRAPHY.md": bib.render_bibliography_md(lib),
        "docs/CLAIM_SOURCE_LEDGER.md": bib.render_claim_ledger_md(lib),
        "docs/OVERCLAIM_GUARDRAILS.md": bib.render_overclaim_md(lib),
        "docs/BIBLIOGRAPHIC_EVIDENCE_GRAPH.md": bib.render_evidence_graph_md(lib, scan),
        "docs/UNSUPPORTED_CLAIMS.md": bib.render_unsupported_md(lib, scan),
    }
    stale = [
        rel for rel, rendered in checks.items()
        if (lib.root / rel).read_text(encoding="utf-8") != rendered
    ]
    assert not stale, f"stale generated docs (run `noesis bibliography verdict --write`): {stale}"


def test_bibtex_and_graph_shapes(lib: bib.Library) -> None:
    bibtex = bib.export_bibtex(lib)
    assert bibtex.count("@") >= len(lib.sources)
    graph = bib.build_source_graph(lib)
    assert graph["nodes"] and graph["edges"]


# --- CLI + API surface -------------------------------------------------------

def test_cli_validate_exit_zero() -> None:
    from noesis.cli import main

    assert main(["bibliography", "validate"]) == 0
    assert main(["bibliography", "verdict"]) == 0


def test_api_bibliography_endpoints() -> None:
    c = TestClient(app)
    assert c.get("/bibliography").status_code == 200
    assert c.post("/bibliography/scan").status_code == 200
    v = c.get("/bibliography/verdict").json()
    assert v["overall_status"] == "PASS"
    assert c.post("/bibliography/validate").json()["passed"] is True
    assert c.get("/bibliography/graph").json()["nodes"]


def test_audit_shape(lib: bib.Library, scan: bib.ScanResult) -> None:
    a = bib.audit(lib, scan)
    for key in (
        "total_files_scanned", "total_claims_extracted", "claims_by_status",
        "claims_without_sources", "sources_without_claims", "forbidden_claims_guarded",
        "proxy_claims", "speculative_claims", "coverage_percent", "bibliography_gate_status",
    ):
        assert key in a
    assert a["bibliography_gate_status"] == "PASS"
    json.dumps(a)  # serializable
