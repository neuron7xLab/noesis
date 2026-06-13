"""Module 8 — Cluster Quality Metrics (proxy).

cluster_quality = IEV_bw × node_diversity × intent_coherence × noise_rejection ÷ latency_drag.
НЕ фізичний вимір — операційний proxy якості розподіленого когнітивного workflow.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

from cme.iev_bandwidth import IEVBandwidthReport
from cme.latency_profile import LatencyProfile
from cme.node_plan import NodePlan
from cme.pipeline_v7 import V7Run


@dataclass(frozen=True)
class ClusterQualityReport:
    iev_bandwidth_score: float
    node_diversity_score: float
    intent_coherence_score: float
    noise_rejection_score: float
    latency_drag_score: float
    useful_dimensionality_gain: int
    artifact_density: float
    convergence_rate: int
    overexpansion_penalty: float
    human_bottleneck_score: float
    cluster_quality: float
    proxy_disclaimer: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def compute_cluster_quality(v7: V7Run, plan: NodePlan, lat: LatencyProfile,
                            iev: IEVBandwidthReport, iterations: int) -> ClusterQualityReport:
    iev_bw = round(iev.automatable_gate_fraction * (0.5 if iev.overload_risk == "high" else 1.0), 3)
    diversity = round(len(set(plan.selected_nodes)) / max(len(plan.selected_nodes), 1), 3)
    d = v7.dimensionality
    coherence = round(v7.gate.intent_match, 3)
    noise_rej = round(d.noise_axes / max(d.expanded_hypothesis_axes, 1), 3)
    drag = max(lat.latency_drag_score, 0.05)
    overexp = round(d.noise_axes / max(d.expanded_hypothesis_axes, 1), 3)
    quality = round((max(iev_bw, 0.05) * max(diversity, 0.05) * max(coherence, 0.05)
                     * max(noise_rej, 0.05)) / drag, 4)
    return ClusterQualityReport(
        iev_bandwidth_score=iev_bw,
        node_diversity_score=diversity,
        intent_coherence_score=coherence,
        noise_rejection_score=noise_rej,
        latency_drag_score=lat.latency_drag_score,
        useful_dimensionality_gain=d.useful_dimensionality_gain,
        artifact_density=d.artifact_density,
        convergence_rate=iterations,
        overexpansion_penalty=overexp,
        human_bottleneck_score=v7.entropy.human_bottleneck_score,
        cluster_quality=quality,
        proxy_disclaimer="proxy only — не вимір мозку/свідомості/free-energy",
    )
