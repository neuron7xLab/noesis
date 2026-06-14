"""Failure-weighted benchmark + release verdict.

Failure signal must outweigh self-simulated success:

    quality = verified_improvement − unsupported_claims − rollback_debt − human_gate_overload

A release is PASS only when there are no open hard failures, no forbidden or
unsupported claims, and both the failure-weighted score and release readiness
clear their thresholds. Calibrating to reality means a green light is earned by
surviving failure, not by reporting success.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

DIMENSIONS: tuple[str, ...] = (
    "artifact_quality",
    "verification_strength",
    "claim_safety",
    "rollback_coverage",
    "trace_completeness",
    "gate_consistency",
    "release_readiness",
)

_WEIGHTS: dict[str, float] = {
    "artifact_quality": 0.15,
    "verification_strength": 0.20,
    "claim_safety": 0.20,
    "rollback_coverage": 0.15,
    "trace_completeness": 0.10,
    "gate_consistency": 0.10,
    "release_readiness": 0.10,
}

_UNSUPPORTED_PENALTY = 0.10
_FORBIDDEN_PENALTY = 0.25
_ROLLBACK_PENALTY = 0.05
_HUMAN_PENALTY = 0.10
_SCORE_THRESHOLD = 0.55
_READINESS_THRESHOLD = 0.50


@dataclass(frozen=True)
class BenchmarkInput:
    dimensions: dict[str, float]
    unsupported_claim_count: int = 0
    forbidden_claim_count: int = 0
    rollback_debt: int = 0
    human_gate_overload: float = 0.0
    open_hard_failures: list[str] = field(default_factory=list)


def _validate(inp: BenchmarkInput) -> None:
    missing = [d for d in DIMENSIONS if d not in inp.dimensions]
    if missing:
        raise ValueError(f"missing benchmark dimensions: {missing}")
    for name, value in inp.dimensions.items():
        if not 0.0 <= value <= 1.0:
            raise ValueError(f"dimension {name} must be in [0, 1], got {value}")


def evaluate(inp: BenchmarkInput) -> dict[str, Any]:
    _validate(inp)
    verified_improvement = sum(_WEIGHTS[d] * inp.dimensions[d] for d in DIMENSIONS)
    penalties = (
        _UNSUPPORTED_PENALTY * inp.unsupported_claim_count
        + _FORBIDDEN_PENALTY * inp.forbidden_claim_count
        + _ROLLBACK_PENALTY * inp.rollback_debt
        + _HUMAN_PENALTY * inp.human_gate_overload
    )
    score = round(verified_improvement - penalties, 4)
    readiness = inp.dimensions["release_readiness"]

    hard_blocks: list[str] = []
    if inp.forbidden_claim_count > 0:
        hard_blocks.append("forbidden_claims_present")
    if inp.unsupported_claim_count > 0:
        hard_blocks.append("unsupported_claims_present")
    if inp.open_hard_failures:
        hard_blocks.append("open_hard_failures")
    if score < _SCORE_THRESHOLD:
        hard_blocks.append("score_below_threshold")
    if readiness < _READINESS_THRESHOLD:
        hard_blocks.append("release_readiness_below_threshold")

    verdict = "PASS" if not hard_blocks else "FAIL"
    return {
        "failure_weighted_score": score,
        "verified_improvement": round(verified_improvement, 4),
        "penalties": round(penalties, 4),
        "release_verdict": verdict,
        "hard_blocks": hard_blocks,
        "open_hard_failures": list(inp.open_hard_failures),
        "metrics": {
            "failure_weighted_score": score,
            "rollback_debt": inp.rollback_debt,
            "unsupported_claim_count": inp.unsupported_claim_count,
            "forbidden_claim_count": inp.forbidden_claim_count,
            "release_readiness_score": readiness,
        },
    }


def assemble_from_repo(root: Path, dimensions: dict[str, float]) -> BenchmarkInput:
    """Pull open hard failures from the physics-boundary contract, if present."""
    contract = root / "data" / "physics_boundary_contract.json"
    open_hard: list[str] = []
    unsupported = 0
    if contract.exists():
        data = json.loads(contract.read_text(encoding="utf-8"))
        open_hard = list(data.get("hard_failures", []))
        unsupported = sum(
            1
            for row in data.get("claim_status_checked", [])
            if row.get("claim_status") == "UNSUPPORTED"
        )
    return BenchmarkInput(
        dimensions=dimensions,
        unsupported_claim_count=unsupported,
        open_hard_failures=open_hard,
    )
