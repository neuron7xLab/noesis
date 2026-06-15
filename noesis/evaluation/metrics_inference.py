"""Unified Metrics Inference Report: consolidate the metrics the repo already
computes, each carrying explicit provenance.

Three tiers (operational definitions):

* ``MEASURED``    — aggregate of a real deterministic run over the fixed
  benchmark corpus (proxy scorers, no human labels, no random seeds).
* ``SIMULATED``   — a metric obtained from synthetically degraded inputs
  (mutation-testing style); ground truth is the objective degradation, not the
  field.
* ``EXTRAPOLATED`` — a projection read off a sampled curve (heuristic, with an
  explicit caveat that intermediate / beyond-sample points are not measured).

Every value below comes from a real call into existing deterministic code; no
number is hardcoded. The report is deterministic: two calls are deep-equal (no
timestamps, no hashes-of-time, no random fields).

Fail-closed safety: every asserted prose string (metric name, procedure,
caveat) is run through ``check_forbidden_claims``; a hit raises, so the report
can never carry a forbidden claim. The ``not_claimed`` list is deliberately
exempt — it is a negative declaration of what the product does NOT claim, so it
intentionally contains forbidden-flavoured phrases and must not be self-blocked.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any

from noesis.benchmark import node_scaling_curve, run_benchmark, run_benchmark_v6
from noesis.evaluation.discrimination_study import study_report
from noesis.forbidden import check_forbidden_claims

REPORT_VERSION = "1.0.0"

# Explicit, frozen list of out-of-scope claims (negative declaration). These are
# NOT run through the forbidden-claim gate — they are exactly the phrases the
# product disclaims, so self-blocking them would be incoherent.
NOT_CLAIMED: tuple[str, ...] = (
    "AGI",
    "artificial consciousness",
    "therapy",
    "medical validity",
    "scientific proof of consciousness expansion",
    "field-validated effect",
)


class MetricTier(str, Enum):
    """Provenance tier of a metric value."""

    MEASURED = "MEASURED"
    SIMULATED = "SIMULATED"
    EXTRAPOLATED = "EXTRAPOLATED"


@dataclass(frozen=True)
class MetricEntry:
    """One metric with explicit provenance."""

    name: str
    value: float | int | str
    tier: MetricTier
    procedure: str
    sample_n: int | None
    caveat: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "value": self.value,
            "tier": self.tier.value,
            "procedure": self.procedure,
            "sample_n": self.sample_n,
            "caveat": self.caveat,
        }


def _guard(*strings: str) -> None:
    """Fail-closed: raise if any asserted prose carries a forbidden claim."""
    for s in strings:
        hits = check_forbidden_claims(s)
        if hits:
            raise ValueError(f"forbidden claim in report prose {s!r}: {hits}")


def _parse_k(label: str) -> int:
    """Parse ``"k=3"`` → ``3`` (optimal_node_count from node_scaling_curve)."""
    return int(label.split("=", 1)[1])


def _measured_v5() -> list[MetricEntry]:
    bench = run_benchmark()
    n = int(bench["n"])
    proc = f"deterministic proxy scorer over the fixed N={n} benchmark corpus"
    keys = (
        "avg_clarity",
        "avg_compression",
        "avg_actionability",
        "artifact_validity_rate",
        "failure_mode_rate",
        "claim_safety_rate",
    )
    return [
        MetricEntry(
            name=key,
            value=bench[key],
            tier=MetricTier.MEASURED,
            procedure=proc,
            sample_n=n,
            caveat="proxy_eval, no human labels",
        )
        for key in keys
    ]


def _measured_v6() -> list[MetricEntry]:
    bench = run_benchmark_v6()
    n = int(bench["n"])
    proc = f"deterministic v0.6 pipeline proxy over the fixed N={n} benchmark corpus"
    keys = (
        "category_causality_rate",
        "map_delta_rate",
        "decorative_theory_rate",
        "next_action_change_rate_under_ablation",
        "pipeline_overbuilt_rate",
        "claim_safety_rate",
    )
    return [
        MetricEntry(
            name=f"v6_{key}",
            value=bench[key],
            tier=MetricTier.MEASURED,
            procedure=proc,
            sample_n=n,
            caveat="proxy_eval, no human labels",
        )
        for key in keys
    ]


def _simulated() -> list[MetricEntry]:
    study = study_report()
    n = int(study["n_intents"])
    proc = (
        "discharge-gate score over intact vs synthetically degraded artifacts "
        "(degradation families: drop_sections, off_topic, pad, strip_falsifier, "
        "inject_forbidden); AUC = P(intact score > degraded score)"
    )
    return [
        MetricEntry(
            name="gate_discriminant_auc",
            value=study["overall_auc"],
            tier=MetricTier.SIMULATED,
            procedure=proc,
            sample_n=n,
            caveat="degradations are synthetic, not field data",
        )
    ]


def _extrapolated() -> list[MetricEntry]:
    scaling = node_scaling_curve()
    curve: dict[str, float] = scaling["curve"]
    proc = (
        "cluster_quality sampled at k in {1,2,3,5,8}, optimum by argmax"
    )
    caveat = "values between/beyond sampled k are not measured"
    sample_n = len(curve)
    return [
        MetricEntry(
            name="optimal_node_count",
            value=_parse_k(scaling["optimal_node_count"]),
            tier=MetricTier.EXTRAPOLATED,
            procedure=proc,
            sample_n=sample_n,
            caveat=caveat,
        ),
        MetricEntry(
            name="projected_cluster_quality_plateau",
            value=max(curve.values()),
            tier=MetricTier.EXTRAPOLATED,
            procedure=proc,
            sample_n=sample_n,
            caveat=caveat,
        ),
    ]


def build_metrics_report() -> dict[str, Any]:
    """Assemble the unified, deterministic, provenance-tagged metrics report."""
    entries: list[MetricEntry] = (
        _measured_v5() + _measured_v6() + _simulated() + _extrapolated()
    )

    # Fail-closed over every asserted prose string before emission.
    for e in entries:
        _guard(e.name, e.procedure, e.caveat)

    entries.sort(key=lambda e: (e.tier.value, e.name))

    tiers = {t.value: sum(1 for e in entries if e.tier is t) for t in MetricTier}

    return {
        "report": "metrics_inference",
        "report_version": REPORT_VERSION,
        "tiers": tiers,
        "metrics": [e.to_dict() for e in entries],
        "not_claimed": list(NOT_CLAIMED),
    }
