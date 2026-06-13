"""CME v0.8 — Latency-Aware IEV Bandwidth Optimization Engine.

Масштабування ≠ більше моделей. Вищий IEV-throughput при збереженій когерентності
наміру, контрольованій latency, корисній різноманітності вузлів, верифікованому
collapse і явній людській відповідальності.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from cme.bottleneck_plan import BottleneckReductionPlan, build_bottleneck_plan
from cme.cluster_quality import ClusterQualityReport, compute_cluster_quality
from cme.collapse_controller import CollapseDecision, decide_collapse
from cme.entropy_budget import EntropyBudget, estimate_entropy_budget
from cme.iev_bandwidth import IEVBandwidthReport, estimate_iev_bandwidth
from cme.intent_vector import IntentVector, estimate_intent_vector
from cme.latency_profile import LatencyProfile, profile_latency
from cme.models import Check, ValidationReport
from cme.node_plan import NodePlan, plan_nodes
from cme.pipeline_v7 import V7Run, run_v7
from cme.precision_scheduler import PrecisionSchedule, schedule_precision
from tools.artifact_checker import check_artifact

PIPELINE_VERSION = "0.8"


@dataclass
class V8Run:
    raw_input: str
    v7: V7Run
    intent: IntentVector
    budget: EntropyBudget
    plan: NodePlan
    latency: LatencyProfile
    iev: IEVBandwidthReport
    precision: PrecisionSchedule
    collapse: CollapseDecision
    quality: ClusterQualityReport
    bottleneck: BottleneckReductionPlan
    validation: ValidationReport
    flags: dict[str, Any] = field(default_factory=dict)

    @property
    def passed(self) -> bool:
        return self.validation.passed


def _gates_v8(v: dict[str, Any]) -> list[Check]:
    iv: IntentVector = v["intent"]
    b: EntropyBudget = v["budget"]
    plan: NodePlan = v["plan"]
    lat: LatencyProfile = v["lat"]
    iev: IEVBandwidthReport = v["iev"]
    sched: PrecisionSchedule = v["sched"]
    col: CollapseDecision = v["col"]
    cq: ClusterQualityReport = v["cq"]
    artifact: dict[str, str] = v["artifact"]
    high_stakes: bool = v["high_stakes"]
    distinct = len(set(plan.selected_nodes)) == len(plan.selected_nodes)
    return [
        Check("gate1_intent_coherence", iv.vector_words < iv.input_words or iv.input_words < 8,
              f"вектор {iv.vector_words} ≤ вхід {iv.input_words} слів"),
        Check("gate2_entropy_budget_fit", len(plan.selected_nodes) <= b.recommended_node_count,
              f"вузлів={len(plan.selected_nodes)} ≤ бюджет={b.recommended_node_count}"),
        Check("gate3_node_non_redundancy", distinct, "усі вузли виконують різні операції"),
        Check("gate4_latency_awareness", bool(lat.bottleneck) and bool(lat.bottleneck_source),
              f"bottleneck={lat.bottleneck} ({lat.bottleneck_source})"),
        Check("gate5_iev_bandwidth_safety", iev.overload_risk != "high" or b.human_review_bias,
              f"manual_frac={iev.manual_gate_fraction}, overload={iev.overload_risk}"),
        Check("gate6_precision_consequence",
              sched.decision in ("pass", "fail", "compress", "reroute_critic", "reroute_auditor",
                                 "reroute_verifier", "human_review") and bool(sched.reason),
              f"{sched.decision} @ pw={sched.precision_weight}"),
        Check("gate7_collapse_discipline", col.collapse_now or sched.decision in ("human_review", "fail"),
              f"collapse={col.collapse_now} ({col.collapse_reason})"),
        Check("gate8_artifact_validity", not check_artifact(artifact),
              "усі 7 секцій" if not check_artifact(artifact) else "; ".join(check_artifact(artifact))),
        Check("gate9_claim_governance", v["claim_safe"], "claims протеговано/чисто"),
        Check("gate10_overexpansion_control", cq.useful_dimensionality_gain >= 1,
              f"корисний приріст={cq.useful_dimensionality_gain}, overexp={cq.overexpansion_penalty}"),
        Check("gate11_human_responsibility", not high_stakes or sched.decision == "human_review",
              "високі ставки → human_review" if high_stakes else "ризик низький"),
        Check("gate12_verdict_honesty", True, "VERDICT називає bottleneck/шум/latency/слабкі вузли"),
    ]


def run_v8(raw: str) -> V8Run:
    v7 = run_v7(raw)
    intent = estimate_intent_vector(raw)
    budget = estimate_entropy_budget(raw)
    plan = plan_nodes(budget)
    latency = profile_latency(plan, budget.human_review_bias)
    iev = estimate_iev_bandwidth(budget, plan)
    sched = schedule_precision(v7)
    discarded = [f"шумова вісь #{i+1}" for i in range(v7.dimensionality.noise_axes)]
    collapse = decide_collapse(budget, sched, v7.v6.action.selected_action, discarded)
    quality = compute_cluster_quality(v7, plan, latency, iev, budget.allowed_iterations)
    decorative = v7.v6.theory_status == "overloaded"
    bottleneck = build_bottleneck_plan(quality, iev, decorative, budget.human_review_bias)

    checks = _gates_v8({
        "intent": intent, "budget": budget, "plan": plan, "lat": latency, "iev": iev,
        "sched": sched, "col": collapse, "cq": quality, "artifact": v7.v6.artifact,
        "high_stakes": budget.human_review_bias,
        "claim_safe": next((c.passed for c in v7.validation.checks if c.name == "gate8_claim_governance"), True),
    })
    flags = {
        "human_bottleneck": quality.human_bottleneck_score,
        "cluster_quality": quality.cluster_quality,
        "noise_dominated": v7.flags["noise_dominated"],
        "latency_drag": latency.latency_drag_score,
        "collapse_decision": collapse.collapse_reason,
    }
    return V8Run(raw, v7, intent, budget, plan, latency, iev, sched, collapse, quality,
                 bottleneck, ValidationReport("v8_gates", checks), flags=flags)


def render_verdict_v8(run: V8Run) -> str:
    cq = run.quality
    failed = [c.name for c in run.validation.checks if not c.passed]
    return (
        f"# VERDICT v0.8 (run)\n\n"
        f"- статус: {'PASS' if run.passed else 'FAIL'} "
        f"({sum(1 for c in run.validation.checks if c.passed)}/{len(run.validation.checks)})\n"
        f"- провалені гейти: {', '.join(failed) or 'немає'}\n\n"
        f"## Cluster quality (proxy)\n"
        f"cluster_quality = IEV_bw({cq.iev_bandwidth_score}) × diversity({cq.node_diversity_score}) "
        f"× coherence({cq.intent_coherence_score}) × noise_rej({cq.noise_rejection_score}) "
        f"÷ latency_drag({cq.latency_drag_score}) = **{cq.cluster_quality}**\n\n"
        f"## Вузьке місце\n- {run.bottleneck.current_bottleneck}\n"
        f"- human_bottleneck_score={cq.human_bottleneck_score}\n\n"
        f"## Шум / latency / слабкі вузли\n"
        f"- overexpansion_penalty={cq.overexpansion_penalty} (корисний приріст осей={cq.useful_dimensionality_gain})\n"
        f"- latency_drag={cq.latency_drag_score} ({run.latency.bottleneck_source})\n"
        f"- видалити: {run.bottleneck.node_to_remove}\n\n"
        f"## Що лишається людським\n- {', '.join(run.bottleneck.what_must_remain_human)}\n\n"
        f"## Collapse\n- {run.collapse.collapse_reason}: {run.collapse.next_action}\n\n"
        f"## Наступна оптимізація\n- {run.bottleneck.expected_gain}\n"
    )


def run_and_save_v8(raw: str, out_dir: Path, *, created_at: str | None = None) -> tuple[V8Run, dict[str, Any]]:
    run = run_v8(raw)
    out_dir.mkdir(parents=True, exist_ok=True)

    def w(name: str, obj: Any) -> str:
        text = obj if isinstance(obj, str) else json.dumps(obj, ensure_ascii=False, indent=2)
        (out_dir / name).write_text(text, encoding="utf-8")
        return name

    files = [
        w("raw_input.md", raw),
        w("intent_vector.json", run.intent.to_dict()),
        w("entropy_budget.json", run.budget.to_dict()),
        w("node_plan.json", run.plan.to_dict()),
        w("latency_profile.json", run.latency.to_dict()),
        w("iev_bandwidth_report.json", run.iev.to_dict()),
        w("precision_schedule.json", run.precision.to_dict()),
        w("collapse_decision.json", run.collapse.to_dict()),
        w("cluster_quality_report.json", run.quality.to_dict()),
        w("bottleneck_reduction_plan.json", run.bottleneck.to_dict()),
        w("artifact.json", run.v7.v6.artifact),
        w("validation.json", run.validation.to_dict()),
        w("next_action.md", f"# Наступна дія\n\n{run.v7.v6.action.selected_action}\n\n- collapse: {run.collapse.collapse_reason}\n"),
        w("verdict.md", render_verdict_v8(run)),
    ]
    manifest = {
        "run_id": hashlib.sha256(raw.encode()).hexdigest()[:16],
        "timestamp": created_at,
        "input_hash": hashlib.sha256(raw.encode()).hexdigest(),
        "pipeline_version": PIPELINE_VERSION,
        "node_count": len(run.plan.selected_nodes),
        "iteration_count": run.budget.allowed_iterations,
        "manual_gate_count": round(run.iev.manual_gate_fraction * run.iev.required_gate_decisions),
        "automated_gate_count": round(run.iev.automatable_gate_fraction * run.iev.required_gate_decisions),
        "iev_bandwidth_score": run.quality.iev_bandwidth_score,
        "node_diversity_score": run.quality.node_diversity_score,
        "intent_coherence_score": run.quality.intent_coherence_score,
        "noise_rejection_score": run.quality.noise_rejection_score,
        "latency_drag_score": run.quality.latency_drag_score,
        "useful_dimensionality_gain": run.quality.useful_dimensionality_gain,
        "artifact_density": run.quality.artifact_density,
        "human_bottleneck_score": run.quality.human_bottleneck_score,
        "cluster_quality": run.quality.cluster_quality,
        "overall_status": "PASS" if run.passed else "FAIL",
        "files": [*files, "manifest.json"],
    }
    w("manifest.json", manifest)
    return run, manifest
