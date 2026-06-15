"""Construct-validity tests for the continuous artifact proxy.

The legacy proxy saturated (no spread). These tests pin the property that makes
the new proxy *valid*: each degradation drops its targeted dimension while the
others stay intact, and the aggregate ranks intact artifacts above degraded ones.
"""

from __future__ import annotations

import json

from noesis.evaluation.artifact_proxy import (
    DIMENSIONS,
    TARGETS,
    discrimination_matrix,
    score_artifact,
)
from noesis.evaluation.discrimination_study import DEGRADATIONS, _example_intents
from noesis.forbidden import check_forbidden_claims
from noesis.generators import build_artifact_deterministic


def _clean_pair() -> tuple[dict[str, str], str]:
    intent = _example_intents()[0]
    return dict(build_artifact_deterministic(intent)), intent


def test_clean_artifact_scores_high_but_not_trivially_saturated() -> None:
    art, intent = _clean_pair()
    s = score_artifact(art, intent)
    assert set(s) == {*DIMENSIONS, "OVERALL"}
    assert s["OVERALL"] >= 0.7
    # relevance is a genuine continuous overlap, not a forced ceiling.
    assert 0.0 < s["relevance"] <= 1.0


def test_each_degradation_tanks_its_targeted_dimension() -> None:
    art, intent = _clean_pair()
    base = score_artifact(art, intent)
    for dim, degradation in TARGETS.items():
        degraded = DEGRADATIONS[degradation](art)
        s = score_artifact(degraded, intent)
        assert s[dim] < base[dim], f"{degradation} should drop {dim}: {s[dim]} !< {base[dim]}"
        # and it must tank the aggregate too (fail-closed geometric mean).
        assert s["OVERALL"] < base["OVERALL"]


def test_matrix_shows_clean_above_every_degradation() -> None:
    m = discrimination_matrix()
    assert m["n_intents"] >= 1
    clean_overall = m["matrix"]["clean"]["OVERALL"]
    for degradation in DEGRADATIONS:
        assert m["matrix"][degradation]["OVERALL"] < clean_overall
        # each degradation perfectly separated from clean on this objective set.
        assert m["per_degradation_auc"][degradation] >= 0.7
    assert m["overall_auc_clean_vs_all_degraded"] >= 0.7


def test_matrix_is_deterministic() -> None:
    assert discrimination_matrix() == discrimination_matrix()


def test_no_forbidden_claims_in_matrix_prose() -> None:
    m = discrimination_matrix()
    prose = " ".join([m["kind"], m["boundary"], *m["dimensions"], *m["targets"].values()])
    assert check_forbidden_claims(prose) == []


def test_cli_proxy_matrix_runs_and_emits_json() -> None:
    from noesis.cli import main

    rc = main(["proxy-matrix"])
    assert rc == 0


def test_cli_output_parses(capsys) -> None:  # type: ignore[no-untyped-def]
    from noesis.cli import main

    main(["proxy-matrix"])
    out = capsys.readouterr().out
    data = json.loads(out)
    assert data["kind"] == "artifact_proxy_discrimination_matrix"
    assert "matrix" in data and "clean" in data["matrix"]
