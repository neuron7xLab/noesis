"""Residual -> mechanism promotion gate.

An LLM guess (residual) may never become system truth (mechanism) without a
verifier:

    residual_candidate -> verifier -> promotion_decision -> mechanism_update

Fail-closed: no verifier attached means no promotion; a failed verifier rejects;
a forbidden claim is rejected; a proxy claiming to be a measurement is rejected;
an unsupported claim is escalated to human review. ``mechanism_update`` is True
only for a VERIFIED_MECHANISM.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

from noesis.ratios import rate

PROMOTION_STATES: frozenset[str] = frozenset(
    {
        "RESIDUAL",
        "CANDIDATE_MECHANISM",
        "VERIFIED_MECHANISM",
        "REJECTED",
        "HUMAN_REVIEW_REQUIRED",
    }
)


@dataclass(frozen=True)
class ResidualCandidate:
    candidate_id: str
    content: str
    kind: str  # e.g. llm_guess, proxy_metric, claim
    verifier_attached: bool
    verifier_passed: bool | None = None  # None = attached but not yet run
    is_forbidden: bool = False
    is_unsupported: bool = False
    claims_measurement_from_proxy: bool = False

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def promote(candidate: ResidualCandidate) -> dict[str, Any]:
    """Decide the promotion state for a residual candidate. Order is fail-closed."""
    if candidate.is_forbidden:
        state, reason = "REJECTED", "forbidden claim cannot become mechanism"
    elif candidate.claims_measurement_from_proxy:
        state, reason = "REJECTED", "a proxy may not be promoted to a measurement"
    elif not candidate.verifier_attached:
        state, reason = "RESIDUAL", "no verifier attached — cannot promote"
    elif candidate.is_unsupported:
        state, reason = "HUMAN_REVIEW_REQUIRED", "unsupported claim needs human review"
    elif candidate.verifier_passed is None:
        state, reason = "CANDIDATE_MECHANISM", "verifier attached but not yet run"
    elif candidate.verifier_passed is False:
        state, reason = "REJECTED", "verifier failed"
    else:
        state, reason = "VERIFIED_MECHANISM", "verifier passed"
    return {
        "candidate_id": candidate.candidate_id,
        "state": state,
        "reason": reason,
        "mechanism_update": state == "VERIFIED_MECHANISM",
    }


def promotion_metrics(decisions: list[dict[str, Any]]) -> dict[str, float]:
    total = len(decisions)
    if total == 0:
        return {
            "unverified_promotion_block_rate": 0.0,
            "verified_promotion_rate": 0.0,
            "rejected_residual_rate": 0.0,
            "mechanism_stability_rate": 0.0,
        }
    verified = [d for d in decisions if d["state"] == "VERIFIED_MECHANISM"]
    # every mechanism update must be a verified mechanism (stability invariant)
    stable = sum(1 for d in decisions if d["mechanism_update"] == (d["state"] == "VERIFIED_MECHANISM"))
    # candidates that did not pass verification must never carry a mechanism update
    non_verified = [d for d in decisions if d["state"] != "VERIFIED_MECHANISM"]
    blocked = sum(1 for d in non_verified if not d["mechanism_update"])
    return {
        "unverified_promotion_block_rate": rate(blocked, len(non_verified), default=1.0),
        "verified_promotion_rate": rate(len(verified), total),
        "rejected_residual_rate": rate(
            sum(1 for d in decisions if d["state"] == "REJECTED"), total
        ),
        "mechanism_stability_rate": rate(stable, total),
    }
