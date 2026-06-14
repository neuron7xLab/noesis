"""Module 9 — IEV Bottleneck Reduction Plan: як безпечно збільшити когнітивне масштабування."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

from noesis.cluster_quality import ClusterQualityReport
from noesis.iev_bandwidth import IEVBandwidthReport


@dataclass(frozen=True)
class BottleneckReductionPlan:
    current_bottleneck: str
    recommended_automation: list[str]
    what_must_remain_human: list[str]
    node_to_add: str
    node_to_remove: str
    gate_to_automate: str
    gate_to_keep_manual: str
    expected_gain: str
    risk_of_change: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def build_bottleneck_plan(cq: ClusterQualityReport, iev: IEVBandwidthReport,
                          decorative_theory: bool, high_stakes: bool) -> BottleneckReductionPlan:
    bottleneck = ("human IEV-bandwidth" if cq.human_bottleneck_score >= 0.6 or high_stakes
                  else "latency drag (over-routing)" if cq.latency_drag_score > 0.6
                  else "verifier authority")
    return BottleneckReductionPlan(
        current_bottleneck=bottleneck,
        recommended_automation=["schema validation", "forbidden claim detection", "first-pass compression"],
        what_must_remain_human=["intent vector", "moral responsibility", "final acceptance", "life-risk decisions"],
        node_to_add="Verifier authority" if cq.noise_rejection_score < 0.5 else "—",
        node_to_remove="редундантні теоретичні вузли (10/12 декоративні)" if decorative_theory else "—",
        gate_to_automate="verifier_schema_gate, compressor_entropy_gate",
        gate_to_keep_manual="human_final_gate (high-risk)" if high_stakes else "human_final_gate",
        expected_gain="вище IEV-throughput при збереженій когерентності; менше overexpansion",
        risk_of_change="auto-гейт стає хибним авторитетом; verifier лише штампує",
    )
