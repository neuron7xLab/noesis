"""Tests for the failure-weighted benchmark + release verdict."""

from __future__ import annotations

import json
from pathlib import Path

import jsonschema
import pytest

from noesis.evaluation.failure_weighted_benchmark import (
    DIMENSIONS,
    BenchmarkInput,
    assemble_from_repo,
    evaluate,
)

_ROOT = Path(__file__).resolve().parents[1]
_SCHEMA = json.loads(
    (_ROOT / "schemas" / "failure_weighted_benchmark.schema.json").read_text(encoding="utf-8")
)


def _dims(value: float = 0.9) -> dict[str, float]:
    return {d: value for d in DIMENSIONS}


def test_clean_run_passes_and_validates() -> None:
    report = evaluate(BenchmarkInput(dimensions=_dims(0.9)))
    assert report["release_verdict"] == "PASS"
    jsonschema.validate(instance=report, schema=_SCHEMA)


def test_failures_lower_the_score() -> None:
    clean = evaluate(BenchmarkInput(dimensions=_dims(0.9)))["failure_weighted_score"]
    with_fail = evaluate(
        BenchmarkInput(dimensions=_dims(0.9), unsupported_claim_count=2, rollback_debt=3)
    )["failure_weighted_score"]
    assert with_fail < clean


def test_unsupported_claims_are_not_ignored() -> None:
    report = evaluate(BenchmarkInput(dimensions=_dims(0.9), unsupported_claim_count=1))
    assert report["release_verdict"] == "FAIL"
    assert "unsupported_claims_present" in report["hard_blocks"]


def test_forbidden_claim_blocks_release() -> None:
    report = evaluate(BenchmarkInput(dimensions=_dims(0.9), forbidden_claim_count=1))
    assert report["release_verdict"] == "FAIL"
    assert "forbidden_claims_present" in report["hard_blocks"]


def test_open_hard_failures_block_release() -> None:
    report = evaluate(BenchmarkInput(dimensions=_dims(0.9), open_hard_failures=["trajectory"]))
    assert report["release_verdict"] == "FAIL"
    assert "open_hard_failures" in report["hard_blocks"]


def test_low_readiness_blocks_release() -> None:
    dims = _dims(0.9)
    dims["release_readiness"] = 0.1
    report = evaluate(BenchmarkInput(dimensions=dims))
    assert report["release_verdict"] == "FAIL"
    assert "release_readiness_below_threshold" in report["hard_blocks"]


def test_benchmark_does_not_only_reward_success() -> None:
    # a high-success run with open failures must still FAIL
    report = evaluate(
        BenchmarkInput(dimensions=_dims(1.0), forbidden_claim_count=1, open_hard_failures=["x"])
    )
    assert report["release_verdict"] == "FAIL"


def test_missing_dimension_raises() -> None:
    with pytest.raises(ValueError):
        evaluate(BenchmarkInput(dimensions={"artifact_quality": 0.9}))


def test_dimension_out_of_range_raises() -> None:
    dims = _dims(0.9)
    dims["claim_safety"] = 1.5
    with pytest.raises(ValueError):
        evaluate(BenchmarkInput(dimensions=dims))


def test_assemble_from_repo_pulls_open_hard_failures() -> None:
    # the live contract on this repo carries the trajectory hard failure
    inp = assemble_from_repo(_ROOT, _dims(0.9))
    report = evaluate(inp)
    assert "trajectory" in inp.open_hard_failures
    assert report["release_verdict"] == "FAIL"
