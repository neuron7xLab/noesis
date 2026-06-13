"""Тести CME v0.4 (нейрокогнітивні лінзи) та EIIC v0.1."""

from __future__ import annotations

from pathlib import Path

import pytest

from cme.eiic import run_eiic
from cme.forbidden import check_forbidden_claims
from cme.neuro import PROVENANCE, run_v4
from cme.theories import classify_regime, locate_prediction_error, run_theories
from cme.generators import build_mirror_deterministic
from cme.ontology import build_reality_maps, extract_categories

_PROBLEMS = sorted((Path(__file__).resolve().parent.parent / "examples" / "problems").glob("*.txt"))


def test_regime_and_error_classifiers() -> None:
    assert classify_regime("боюсь що не вийде небезпечно")[0] == "defense"
    assert classify_regime("немає сил усе валиться вигорів")[0] == "collapse"
    assert locate_prediction_error("не розумію не можу сформулювати")[0] == "semantic"


def test_run_theories_twelve_lenses() -> None:
    raw = "хочу запустити продукт але боюсь і немає сил розпорошуюсь"
    mirror = build_mirror_deterministic(raw)
    maps = build_reality_maps(extract_categories(raw))
    readouts = run_theories(raw, mirror, maps)
    assert len(readouts) == 12
    assert all(r.status == "deterministic-proxy" for r in readouts.values())
    # IIT-лінза явно НЕ претендує на свідомість
    assert "НЕ свідомість" in readouts["iit"].operator_output


def test_neuro_forbidden_claims_clean() -> None:
    run = run_v4("хочу зрозуміти суть свободи і змінити підхід")
    blob = " ".join(str(v) for v in run.sections().values())
    assert check_forbidden_claims(blob) == []


def test_forbidden_detects_consciousness_and_destiny() -> None:
    assert "consciousness detection" in check_forbidden_claims("система детектує свідомість")
    assert "destiny language" in check_forbidden_claims("тобі судилось це")


@pytest.mark.parametrize("path", _PROBLEMS, ids=lambda p: p.name)
def test_neuro_end_to_end_dod(path: Path) -> None:
    run = run_v4(path.read_text(encoding="utf-8").strip())
    assert run.passed, [v.to_dict() for v in run.validations if not v.passed]
    sections = run.sections()
    # DoD: режим, помилка передбачення, workspace-сигнал, дія, концепт, failure mode
    assert sections["state_space_map"]["current_state"]
    assert run.prediction_error_stack.value
    assert run.workspace_broadcast.value
    assert run.active_inference_policy.value
    assert run.conceptual_refactor.value
    assert run.next_action.value
    for tagged in (run.prediction_error_stack, run.workspace_broadcast, run.next_action):
        assert tagged.provenance in PROVENANCE


@pytest.mark.parametrize("path", _PROBLEMS, ids=lambda p: p.name)
def test_eiic_terminal_vector(path: Path) -> None:
    core = run_eiic(path.read_text(encoding="utf-8").strip())
    assert core.passed, core.validation.to_dict()
    # екстрапольоване ядро НЕ видається за спостережене
    assert core.extrapolated_core.provenance == "speculative"
    assert core.peak_architecture.provenance == "speculative"
    assert any(t.provenance == "observed" for t in (core.current_state, core.next_action))
    assert core.first_missing_condition.value.strip()
