"""Дискримінантна валідність IEV-гейта проти контрольованої деградації.

Ground truth = об'єктивні деградації, не людські оцінки. Перевіряємо, що гейт
ранжує цілий артефакт вище деградованого (AUC) і вето на категоріальних провалах
(no falsifier / forbidden claim).
"""

from __future__ import annotations

import json

import pytest

from noesis.evaluation.artifact_scorer import gate_decision, score_artifact, verifier_failed
from noesis.evaluation.discrimination_study import DEGRADATIONS, _auc, run_study, study_report
from noesis.gates.discharge_gate import DischargeGate
from noesis.generators import build_artifact_deterministic

_INTENT = "оптимізувати водопостачання міста через мережу сенсорів і прогноз попиту"


def test_scorer_gives_good_artifact_high_signal_low_cost() -> None:
    s = score_artifact(_INTENT, build_artifact_deterministic(_INTENT))
    assert all(0.0 <= v <= 1.0 for v in s.values())
    assert s["relevance"] > 0.5 and s["verifier"] > 0.5 and s["progress"] > 0.5
    assert s["cost"] == 0.0
    # порожній намір → нульова релевантність (без ділення на нуль)
    assert score_artifact("", build_artifact_deterministic(_INTENT))["relevance"] == 0.0


def test_verifier_failed_flags_categorical_failures() -> None:
    good = build_artifact_deterministic(_INTENT)
    assert verifier_failed(good) is False
    assert verifier_failed(DEGRADATIONS["strip_falsifier"](good)) is True
    assert verifier_failed(DEGRADATIONS["inject_forbidden"](good)) is True


def test_gate_vetoes_forbidden_and_unfalsifiable_artifacts() -> None:
    gate = DischargeGate()
    good = build_artifact_deterministic(_INTENT)
    assert gate_decision(_INTENT, good, gate)["decision"] == "PASS"
    assert gate_decision(_INTENT, DEGRADATIONS["inject_forbidden"](good), gate)["decision"] == "FAIL"
    assert gate_decision(_INTENT, DEGRADATIONS["strip_falsifier"](good), gate)["decision"] == "FAIL"


def test_auc_edges() -> None:
    assert _auc([], [1.0]) == 0.0
    assert _auc([1.0, 1.0], [0.0, 0.0]) == 1.0  # perfect separation
    assert _auc([0.5], [0.5]) == 0.5  # tie → chance


def test_study_validates_discrimination_and_closes_leaks() -> None:
    report = study_report()
    assert report["overall_auc"] >= 0.9  # gate strongly discriminates quality
    assert report["good_pass_rate"] == 1.0
    per = report["per_degradation"]
    # категоріальні провали мають бути зарубані (pass_rate 0)
    assert per["inject_forbidden"]["pass_rate"] == 0.0
    assert per["strip_falsifier"]["pass_rate"] == 0.0
    assert per["drop_sections"]["pass_rate"] == 0.0
    assert per["off_topic"]["pass_rate"] == 0.0
    # кожна деградація ранжується нижче цілого артефакту
    assert all(d["auc"] >= 0.7 for d in per.values())


def test_run_study_empty_is_safe() -> None:
    report = run_study([])
    assert report["n_intents"] == 0
    assert report["overall_auc"] == 0.0


def test_cli_discriminate_emits_valid_json(capsys: pytest.CaptureFixture[str]) -> None:
    from noesis.cli import main

    assert main(["discriminate"]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["kind"] == "discriminant_validity"
    assert payload["overall_auc"] >= 0.9
