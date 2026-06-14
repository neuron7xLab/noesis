"""Тести CME v0.8: intent vector, entropy budget, node plan, latency, IEV bandwidth,
precision, collapse, cluster quality, bottleneck plan, 12 gates, benchmark, vertical loop."""

from __future__ import annotations

from pathlib import Path

from noesis.benchmark_v8 import node_scaling_curve, run_benchmark_v8
from noesis.intent_vector import estimate_intent_vector
from noesis.entropy_budget import estimate_entropy_budget
from noesis.pipeline_v8 import run_and_save_v8, run_v8
from noesis.vertical_loop import OPERATIONS, build_vertical_loop


def test_intent_vector_shorter_and_has_forbidden_drift() -> None:
    raw = "проєктую агентну систему треба вирішити структуру боюсь зайвої складності і не знаю з чого почати"
    iv = estimate_intent_vector(raw)
    assert iv.vector_words < iv.input_words  # коротший за вхід
    assert iv.forbidden_drift  # містить forbidden drift


def test_entropy_budget_no_research_mode_for_short_task() -> None:
    b = estimate_entropy_budget("що робити далі")
    assert b.collapse_urgency in ("immediate", "soon")
    assert b.recommended_node_count <= 2


def test_entropy_budget_high_stakes_bias() -> None:
    b = estimate_entropy_budget("не знаю чи розлучатися зі стосунками")
    assert b.human_review_bias


def test_node_plan_non_redundant_and_has_verifier() -> None:
    run = run_v8("хочу запустити продукт але застряг між напрямками")
    assert len(set(run.plan.selected_nodes)) == len(run.plan.selected_nodes)
    assert "Verifier" in run.plan.selected_nodes


def test_latency_identifies_bottleneck() -> None:
    run = run_v8("проєктую агентну систему боюсь складності")
    assert run.latency.bottleneck and run.latency.bottleneck_source
    assert 0.0 <= run.latency.latency_drag_score <= 1.0


def test_cluster_quality_formula_and_proxy() -> None:
    run = run_v8("хочу зібрати методи в один інструмент")
    cq = run.quality
    assert cq.cluster_quality >= 0
    assert "proxy" in cq.proxy_disclaimer
    assert cq.human_bottleneck_score >= 0


def test_collapse_to_one_action_or_human_review() -> None:
    run = run_v8("хочу запустити продукт але застряг")
    assert run.collapse.collapse_now or run.precision.decision in ("human_review", "fail")
    assert run.collapse.next_action.strip()


def test_high_stakes_routes_human_review_not_autopass() -> None:
    run = run_v8("не знаю чи розлучатися боюсь зі стосунками")
    assert run.precision.decision == "human_review"
    g11 = next(c for c in run.validation.checks if c.name == "gate11_human_responsibility")
    assert g11.passed


def test_bottleneck_plan_keeps_responsibility_human() -> None:
    run = run_v8("хочу запустити продукт")
    assert "moral responsibility" in " ".join(run.bottleneck.what_must_remain_human).lower() or \
           "moral_responsibility" in run.bottleneck.what_must_remain_human
    assert "final acceptance" in " ".join(run.bottleneck.what_must_remain_human).lower() or \
           "final_acceptance" in run.bottleneck.what_must_remain_human


def test_twelve_gates() -> None:
    run = run_v8("хочу зібрати всі методи в один інструмент")
    assert len(run.validation.checks) == 12
    assert run.passed


def test_evidence_bundle_v8_fifteen_files(tmp_path: Path) -> None:
    run, manifest = run_and_save_v8("хочу запустити продукт але застряг між напрямками", tmp_path)
    expected = {
        "raw_input.md", "intent_vector.json", "entropy_budget.json", "node_plan.json",
        "latency_profile.json", "iev_bandwidth_report.json", "precision_schedule.json",
        "collapse_decision.json", "cluster_quality_report.json", "bottleneck_reduction_plan.json",
        "artifact.json", "validation.json", "next_action.md", "verdict.md", "manifest.json",
    }
    assert {p.name for p in tmp_path.iterdir()} == expected
    assert manifest["pipeline_version"] == "0.8"
    assert "cluster_quality" in manifest


def test_node_scaling_curve_has_optimum() -> None:
    curve = node_scaling_curve()
    assert set(curve["curve"]) == {"k=1", "k=2", "k=3", "k=5", "k=8"}
    assert curve["optimal_node_count"] in curve["curve"]


def test_benchmark_v8_proxy() -> None:
    b = run_benchmark_v8()
    assert b["n"] == 100
    assert b["proxy_eval"] is True
    assert b["human_labels_status"] == "pending"
    assert b["collapse_success_rate"] >= 0.0


def test_vertical_loop_uses_only_allowed_verbs() -> None:
    loop = build_vertical_loop("хочу запустити продукт але застряг")
    assert loop.intent and loop.final_state and loop.first_missing_condition
    verbs_used = {step.split(" ")[0] for step in loop.operation_chain}
    assert verbs_used <= set(OPERATIONS)
    assert loop.next_cycle
