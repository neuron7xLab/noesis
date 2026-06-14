"""Benchmark v0.8 — cluster quality + node-scaling curve (де latency > користь)."""

from __future__ import annotations

from typing import Any

from noesis.benchmark import generate_inputs
from noesis.cluster_quality import compute_cluster_quality
from noesis.iev_bandwidth import estimate_iev_bandwidth
from noesis.latency_profile import profile_latency
from noesis.node_plan import NodePlan
from noesis.entropy_budget import estimate_entropy_budget
from noesis.pipeline_v7 import run_v7
from noesis.pipeline_v8 import run_v8

_ROLES = ("Creator", "Verifier", "Critic", "Compressor", "Auditor", "Synthesizer", "RedTeam", "MemoryNode")


def run_benchmark_v8() -> dict[str, Any]:
    inputs = generate_inputs()
    n = len(inputs)
    cq = hb = drag = nodes = 0.0
    collapsed = human_review = 0
    for _d, raw in inputs:
        r = run_v8(raw)
        cq += r.quality.cluster_quality
        hb += r.quality.human_bottleneck_score
        drag += r.quality.latency_drag_score
        nodes += len(r.plan.selected_nodes)
        if r.collapse.collapse_now:
            collapsed += 1
        if r.precision.decision == "human_review":
            human_review += 1
    return {
        "n": n, "proxy_eval": True, "human_labels_status": "pending",
        "cluster_quality_mean": round(cq / n, 4),
        "human_bottleneck_score_mean": round(hb / n, 3),
        "latency_drag_score_mean": round(drag / n, 3),
        "node_count_mean": round(nodes / n, 2),
        "collapse_success_rate": round(collapsed / n, 3),
        "human_review_rate": round(human_review / n, 3),
    }


def node_scaling_curve(raw: str = "проєктую агентну систему оркестратор плюс субагенти боюсь складності") -> dict[str, Any]:
    """cluster_quality як функція кількості вузлів — знаходить оптимум."""
    v7 = run_v7(raw)
    budget = estimate_entropy_budget(raw)
    curve: dict[str, float] = {}
    for k in (1, 2, 3, 5, 8):
        nodes = list(_ROLES[:k])
        if "Verifier" not in nodes:
            nodes[-1] = "Verifier"
        plan = NodePlan(nodes, {x: "" for x in nodes}, "low", "—", "moderate",
                        "high" if k >= 5 else "low", "high")
        lat = profile_latency(plan, budget.human_review_bias)
        iev = estimate_iev_bandwidth(budget, plan)
        cq = compute_cluster_quality(v7, plan, lat, iev, budget.allowed_iterations)
        curve[f"k={k}"] = cq.cluster_quality
    best = max(curve, key=lambda kk: curve[kk])
    return {"curve": curve, "optimal_node_count": best,
            "finding": "cluster_quality падає, коли latency_drag від зайвих вузлів перевищує приріст різноманітності"}
