"""Tests for the evidence integral / hash-chain bundle."""

from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path
from typing import Any

import jsonschema

from noesis.evidence_integral import build_bundle, bundle_metrics, replay, validate_bundle

_SCHEMA = json.loads(
    (Path(__file__).resolve().parents[1] / "schemas" / "evidence_integral.schema.json").read_text(
        encoding="utf-8"
    )
)


def _bundle() -> dict[str, Any]:
    transitions = [
        {"cycle": 0, "state_t": "s0", "state_t_plus_1": "s1", "verifier_index": 0},
        {"cycle": 1, "state_t": "s1", "state_t_plus_1": "s2", "verifier_index": 1},
    ]
    artifacts = [
        {"name": "file_a", "transition_index": 0},
        {"name": "file_b", "transition_index": 1},
    ]
    decisions = [{"decision": "PASS"}, {"decision": "PASS"}]
    verifiers = [{"name": "pytest", "passed": True}, {"name": "ruff", "passed": True}]
    return build_bundle(
        run_id="run-1",
        input_text="hello",
        transitions=transitions,
        artifacts=artifacts,
        decisions=decisions,
        verifier_outputs=verifiers,
        rollback_points=["checkpoint:s0"],
    )


def test_bundle_validates_against_schema() -> None:
    jsonschema.validate(instance=_bundle(), schema=_SCHEMA)


def test_bundle_is_sound_and_replayable() -> None:
    b = _bundle()
    assert validate_bundle(b) == []
    assert replay(b) is True


def test_tamper_breaks_replay() -> None:
    b = _bundle()
    b["transitions"][0]["state_t_plus_1"] = "TAMPERED"
    assert replay(b) is False
    assert any(p.startswith("BUNDLE_NOT_REPLAYABLE") for p in validate_bundle(b))


def test_artifact_without_trace_flagged() -> None:
    b = _bundle()
    b["artifacts"].append({"name": "orphan"})  # no transition_index
    problems = validate_bundle(b)
    assert any(p.startswith("ARTIFACT_WITHOUT_TRACE") for p in problems)


def test_artifact_without_hash_flagged() -> None:
    b = _bundle()
    b["artifact_hashes"] = b["artifact_hashes"][:-1]  # drop one hash
    assert any(p.startswith("ARTIFACT_WITHOUT_HASH") for p in validate_bundle(b))


def test_verifier_not_linked_flagged() -> None:
    b = _bundle()
    b["transitions"][0]["verifier_index"] = 99  # out of range
    assert any(p.startswith("VERIFIER_NOT_LINKED") for p in validate_bundle(b))


def test_metrics_full_coverage() -> None:
    m = bundle_metrics(_bundle())
    assert m["reproducibility_score"] == 1.0
    assert m["hash_coverage_rate"] == 1.0
    assert m["artifact_traceability_rate"] == 1.0
    assert m["verifier_attachment_rate"] == 1.0


def test_metrics_penalize_orphan_artifact() -> None:
    b = _bundle()
    b["artifacts"].append({"name": "orphan"})
    m = bundle_metrics(b)
    assert m["artifact_traceability_rate"] < 1.0


def test_input_hash_is_deterministic() -> None:
    a = deepcopy(_bundle())
    b = deepcopy(_bundle())
    assert a["input_hash"] == b["input_hash"]
    assert a["final_manifest_hash"] == b["final_manifest_hash"]
