"""Тести CME: forbidden, validators, registry, generators, evidence, pipeline."""

from __future__ import annotations

import json
from pathlib import Path

from noesis.evidence import write_evidence
from noesis.forbidden import check_forbidden_claims, hallucination_risk
from noesis.generators import (
    build_artifact_deterministic,
    build_introspection_deterministic,
    build_mirror_deterministic,
)
from noesis.pipeline import run_and_save, run_pipeline
from noesis.registry import REGISTRY, select_method
from noesis.validators import (
    validate_artifact,
    validate_introspection,
    validate_mirror,
)


def test_forbidden_claims_flagged() -> None:
    assert check_forbidden_claims("це AGI що ставить діагноз") == ["claim of AGI", "medical diagnosis"]
    assert check_forbidden_claims("структурований намір і дія") == []


def test_hallucination_levels() -> None:
    assert hallucination_risk("гарантовано доведено науково")[0] == "high"
    assert hallucination_risk("спокійний структурований опис")[0] == "low"


def test_deterministic_mirror_passes_validation() -> None:
    mirror = build_mirror_deterministic("хочу зібрати інструмент але боюсь що буде купа файлів")
    report = validate_mirror(mirror, "хочу зібрати інструмент")
    assert report.passed, report.to_dict()


def test_deterministic_introspection_passes() -> None:
    intro = build_introspection_deterministic("втомився і боюсь що не вийде")
    assert validate_introspection(intro).passed


def test_deterministic_artifact_passes() -> None:
    artifact = build_artifact_deterministic("межі мови задають межі мислення")
    report = validate_artifact(artifact)
    assert report.passed, report.to_dict()


def test_registry_specs_complete() -> None:
    assert set(REGISTRY) == {"mirror", "introspection", "reverse", "artifact"}
    for spec in REGISTRY.values():
        assert spec.trigger and spec.failure_modes and spec.input_schema and spec.output_schema


def test_select_method_routes_emotion_to_introspection() -> None:
    assert select_method("боюсь що не вийде") == "introspection"
    assert select_method("хочу зібрати інструмент") == "mirror"


def test_pipeline_passes_and_emits_one_action() -> None:
    run = run_pipeline("хочу зібрати всі методи в один інструмент")
    assert run.passed
    assert run.next_action.strip()


def test_evidence_bundle_writes_six_files(tmp_path: Path) -> None:
    run, manifest = run_and_save("хочу нарешті зробити щось своє", tmp_path)
    expected = {"raw_input.md", "mirror.md", "artifact.json", "validation.json", "decision.md", "manifest.json"}
    assert {p.name for p in tmp_path.iterdir()} == expected
    assert manifest["validations_passed"] is True
    loaded = json.loads((tmp_path / "manifest.json").read_text(encoding="utf-8"))
    assert loaded["id"] == manifest["id"]


def test_write_evidence_marks_failure(tmp_path: Path) -> None:
    manifest = write_evidence(
        tmp_path,
        raw_input="x",
        mirror_md="m",
        artifact={"definition": "d"},
        validations=[{"passed": False}],
        decision_md="d",
        method_selected="mirror",
    )
    assert manifest["validations_passed"] is False
