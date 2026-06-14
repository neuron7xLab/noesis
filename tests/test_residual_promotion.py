"""Tests for the residual -> mechanism promotion gate."""

from __future__ import annotations

import json
from pathlib import Path

import jsonschema

from noesis.gates.residual_promotion import (
    ResidualCandidate,
    promote,
    promotion_metrics,
)

_SCHEMA = json.loads(
    (Path(__file__).resolve().parents[1] / "schemas" / "residual_promotion.schema.json").read_text(
        encoding="utf-8"
    )
)


def test_llm_output_cannot_become_mechanism_directly() -> None:
    c = ResidualCandidate("c1", "llm idea", "llm_guess", verifier_attached=False)
    d = promote(c)
    assert d["state"] == "RESIDUAL"
    assert d["mechanism_update"] is False


def test_no_verifier_means_no_promotion() -> None:
    c = ResidualCandidate("c2", "x", "llm_guess", verifier_attached=False, verifier_passed=True)
    # even with a (spurious) passed flag, no attached verifier blocks promotion
    assert promote(c)["mechanism_update"] is False


def test_verified_candidate_becomes_mechanism() -> None:
    c = ResidualCandidate("c3", "x", "claim", verifier_attached=True, verifier_passed=True)
    d = promote(c)
    assert d["state"] == "VERIFIED_MECHANISM"
    assert d["mechanism_update"] is True


def test_failed_verifier_rejects() -> None:
    c = ResidualCandidate("c4", "x", "claim", verifier_attached=True, verifier_passed=False)
    assert promote(c)["state"] == "REJECTED"


def test_attached_but_unrun_is_candidate() -> None:
    c = ResidualCandidate("c5", "x", "claim", verifier_attached=True, verifier_passed=None)
    d = promote(c)
    assert d["state"] == "CANDIDATE_MECHANISM"
    assert d["mechanism_update"] is False


def test_forbidden_claim_is_rejected() -> None:
    c = ResidualCandidate(
        "c6", "AGI achieved", "claim", verifier_attached=True, verifier_passed=True,
        is_forbidden=True,
    )
    assert promote(c)["state"] == "REJECTED"


def test_unsupported_claim_escalates_to_human() -> None:
    c = ResidualCandidate(
        "c7", "x", "claim", verifier_attached=True, verifier_passed=True, is_unsupported=True
    )
    d = promote(c)
    assert d["state"] == "HUMAN_REVIEW_REQUIRED"
    assert d["mechanism_update"] is False


def test_proxy_cannot_become_measurement() -> None:
    c = ResidualCandidate(
        "c8", "proxy", "proxy_metric", verifier_attached=True, verifier_passed=True,
        claims_measurement_from_proxy=True,
    )
    assert promote(c)["state"] == "REJECTED"


def test_decision_validates_against_schema() -> None:
    c = ResidualCandidate("c9", "x", "claim", verifier_attached=True, verifier_passed=True)
    jsonschema.validate(instance=promote(c), schema=_SCHEMA)


def test_metrics_block_unverified_and_count_verified() -> None:
    decisions = [
        promote(ResidualCandidate("a", "x", "llm_guess", verifier_attached=False)),
        promote(ResidualCandidate("b", "x", "claim", verifier_attached=True, verifier_passed=True)),
        promote(ResidualCandidate("c", "x", "claim", verifier_attached=True, verifier_passed=False)),
    ]
    m = promotion_metrics(decisions)
    assert m["unverified_promotion_block_rate"] == 1.0
    assert m["verified_promotion_rate"] > 0.0
    assert m["rejected_residual_rate"] > 0.0
    assert m["mechanism_stability_rate"] == 1.0


def test_metrics_empty() -> None:
    assert promotion_metrics([])["verified_promotion_rate"] == 0.0
