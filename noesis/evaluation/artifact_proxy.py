"""Construct-valid artifact proxy + discrimination matrix.

The legacy ``benchmark.proxy_score`` saturates by construction: it measures the
*structural completeness of the deterministic pipeline's output* (always full),
so every dimension hits its ceiling (clarity/actionability = 5, rates = 1.0) and
the proxy cannot discriminate good artifacts from bad ones.

This module replaces that with a **continuous** proxy whose dimensions are each
tied to a known objective failure mode (the degraders in
:mod:`noesis.evaluation.discrimination_study`). Construct validity is then shown
directly by a discrimination matrix: each degradation must drop *its* targeted
dimension while leaving the others intact (a "diagonal of weakness"), and the
aggregate must rank an intact artifact above every degraded variant.

Boundary (inference discipline): this proves the proxy separates KNOWN objective
degradations — NOT that it predicts human-rated usefulness. The latter still
needs labeled pairs (the feedback harness). Claim is bounded to: «the proxy
ranks an intact artifact above its degraded variant».
"""

from __future__ import annotations

import re
from collections.abc import Mapping
from statistics import fmean
from typing import Any

from formal.metrics import falsifier_present
from noesis.evaluation.discrimination_study import DEGRADATIONS, _example_intents
from noesis.forbidden import check_forbidden_claims
from noesis.generators import build_artifact_deterministic
from tools.artifact_checker import REQUIRED_SECTIONS
from tools.finalizer100 import count_words

#: definition word band above which padding is penalised.
IDEAL_DEFINITION_BAND = (8, 60)
_MIN_SECTION_WORDS = 4
_WORD = re.compile(r"[\w'-]+", re.UNICODE)
_STOP = frozenset(
    "і та але або що це той цей як де коли бо щоб для від про над під без the a an of to".split()
)

DIMENSIONS = ("completeness", "relevance", "conciseness", "falsifiability", "safety")

#: which degradation each dimension is designed to catch (for the validity test).
TARGETS = {
    "completeness": "drop_sections",
    "relevance": "off_topic",
    "conciseness": "pad",
    "falsifiability": "strip_falsifier",
    "safety": "inject_forbidden",
}


def _tokens(text: str) -> set[str]:
    return {w for w in _WORD.findall(text.lower()) if len(w) > 2 and w not in _STOP}


def _completeness(a: Mapping[str, str]) -> float:
    sub = sum(1 for k in REQUIRED_SECTIONS if len(str(a.get(k, "")).split()) >= _MIN_SECTION_WORDS)
    return sub / len(REQUIRED_SECTIONS)


def _relevance(a: Mapping[str, str], intent: str) -> float:
    it = _tokens(intent)
    if not it:
        return 0.0
    at = _tokens(" ".join(str(v) for v in a.values()))
    return len(it & at) / len(it)


def _conciseness(a: Mapping[str, str]) -> float:
    w = count_words(str(a.get("definition", "")))
    hi = IDEAL_DEFINITION_BAND[1]
    return 1.0 if w <= hi else max(0.0, hi / w)


def _falsifiability(a: Mapping[str, str]) -> float:
    return 1.0 if falsifier_present(str(a.get("validation", ""))) else 0.0


def _safety(a: Mapping[str, str]) -> float:
    blob = " ".join(str(v) for v in a.values())
    return 0.0 if check_forbidden_claims(blob) else 1.0


def score_artifact(artifact: Mapping[str, str], intent: str) -> dict[str, float]:
    """Score an artifact on the 5 dimensions + a geometric-mean OVERALL ∈ [0, 1].

    Geometric mean is fail-closed: a single collapsed dimension tanks the whole
    score, so a structurally complete but off-topic or unsafe artifact cannot
    coast on its intact dimensions.
    """
    vals: dict[str, float] = {
        "completeness": _completeness(artifact),
        "relevance": _relevance(artifact, intent),
        "conciseness": _conciseness(artifact),
        "falsifiability": _falsifiability(artifact),
        "safety": _safety(artifact),
    }
    prod = 1.0
    for v in vals.values():
        prod *= max(v, 1e-9)
    vals["OVERALL"] = round(prod ** (1.0 / len(DIMENSIONS)), 4)
    return vals


def _auc(positive: list[float], negative: list[float]) -> float:
    """P(random good > random bad) — Mann–Whitney; 0.5 = no discrimination."""
    if not positive or not negative:
        return 0.0
    wins = ties = 0
    for p in positive:
        for n in negative:
            if p > n:
                wins += 1
            elif p == n:
                ties += 1
    return round((wins + 0.5 * ties) / (len(positive) * len(negative)), 4)


def discrimination_matrix(intents: list[str] | None = None) -> dict[str, Any]:
    """Mean dimension scores per condition + per-degradation OVERALL AUC vs clean.

    A construct-valid proxy yields a diagonal of weakness: each degradation drops
    its targeted dimension, and ``clean`` ranks above every degraded variant
    (AUC → 1.0).
    """
    intents = intents or _example_intents()
    conditions = ["clean", *DEGRADATIONS]
    cols = [*DIMENSIONS, "OVERALL"]
    acc: dict[str, dict[str, list[float]]] = {c: {d: [] for d in cols} for c in conditions}

    for intent in intents:
        good = build_artifact_deterministic(intent)
        variants = {"clean": dict(good), **{k: fn(good) for k, fn in DEGRADATIONS.items()}}
        for cond, art in variants.items():
            for dim, val in score_artifact(art, intent).items():
                acc[cond][dim].append(val)

    matrix = {c: {d: round(fmean(acc[c][d]), 4) for d in cols} for c in conditions}
    clean_overall = acc["clean"]["OVERALL"]
    per_degradation_auc = {k: _auc(clean_overall, acc[k]["OVERALL"]) for k in DEGRADATIONS}
    all_bad = [v for k in DEGRADATIONS for v in acc[k]["OVERALL"]]
    return {
        "kind": "artifact_proxy_discrimination_matrix",
        "boundary": "об'єктивні деградації, не людська корисність; claim: проксі ранжує цілий артефакт вище деградованого",
        "n_intents": len(intents),
        "dimensions": list(DIMENSIONS),
        "targets": dict(TARGETS),
        "matrix": matrix,
        "per_degradation_auc": per_degradation_auc,
        "overall_auc_clean_vs_all_degraded": _auc(clean_overall, all_bad),
    }
