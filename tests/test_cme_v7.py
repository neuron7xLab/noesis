"""Тести CME v0.7: граф, профілі вузлів, розмірність, IEV-гейт, broadcast, entropy, 10 гейтів."""

from __future__ import annotations

from pathlib import Path

from cme.benchmark_v7 import run_benchmark_v7
from cme.graph import build_cognitive_graph, check_graph_completeness
from cme.node_profile import bottleneck_nodes, profile_nodes
from cme.pipeline_v7 import run_and_save_v7, run_v7


def test_graph_completeness() -> None:
    g = build_cognitive_graph()
    comp = check_graph_completeness(g)
    assert comp.complete
    assert "human_intent_controller" in g.human_decision_points
    assert g.feedback_loops  # selective reentry


def test_every_node_has_profile_and_failure_risk() -> None:
    profiles = profile_nodes()
    assert len(profiles) == 11
    for p in profiles:
        assert p.failure_risk and p.bandwidth and p.validation_power
    # bottleneck = найнижча пропускна (людський контролер + IEV-гейт)
    assert set(bottleneck_nodes()) == {"human_intent_controller", "decision_gate"}


def test_dimensionality_counts_decorative_theories_as_noise() -> None:
    run = run_v7("проєктую агентну систему боюсь складності")
    d = run.dimensionality
    # LLM пропонує ~14 осей, верифікація втримує мало → більшість шум
    assert d.noise_axes > d.useful_dimensionality_gain
    assert d.net_cognitive_gain < 0.5  # розширення ≠ покращення
    assert run.flags["noise_dominated"]


def test_iev_gate_human_review_on_high_stakes() -> None:
    run = run_v7("не знаю чи розлучатися зі стосунками боюсь")
    assert run.gate.decision == "human_review"
    assert run.gate.reason  # пояснення обов'язкове
    assert 0.0 <= run.gate.precision_weight <= 1.0


def test_iev_gate_compress_on_high_noise() -> None:
    run = run_v7("проєктую агентну систему оркестратор плюс субагенти боюсь складності")
    assert run.gate.decision in ("compress", "pass", "reroute")
    assert run.gate.reason


def test_entropy_ledger_keeps_responsibility_human() -> None:
    run = run_v7("хочу запустити продукт але застряг")
    assert "moral_responsibility" in run.entropy.retained_by_human
    assert "final_acceptance" in run.entropy.retained_by_human
    g5 = next(c for c in run.validation.checks if c.name == "gate5_entropy_delegation_safety")
    assert g5.passed


def test_broadcast_identifies_suppressed_signal() -> None:
    run = run_v7("хочу запустити продукт боюсь ризику")
    assert run.broadcast.workspace_winner
    assert run.broadcast.suppressed_signals
    assert run.broadcast.suppression_assessment in ("useful", "dangerous")


def test_ten_gates_pass_on_full_graph() -> None:
    run = run_v7("хочу зібрати всі методи в один інструмент")
    assert len(run.validation.checks) == 10
    assert run.passed


def test_evidence_bundle_v7_thirteen_files(tmp_path: Path) -> None:
    run, manifest = run_and_save_v7("хочу запустити продукт але застряг між напрямками", tmp_path)
    expected = {
        "raw_input.md", "intent_vector.json", "cognitive_graph.json", "node_profiles.json",
        "dimensionality_report.json", "broadcast_trace.json", "entropy_ledger.json",
        "precision_gate_report.json", "artifact.json", "validation.json", "next_action.md",
        "verdict.md", "manifest.json",
    }
    assert {p.name for p in tmp_path.iterdir()} == expected
    assert manifest["pipeline_version"] == "0.7"
    assert manifest["nodes_used"] == 11


def test_benchmark_v7_quantifies_noise() -> None:
    b = run_benchmark_v7()
    assert b["n"] == 100
    assert b["proxy_eval"] is True
    assert b["human_labels_status"] == "pending"
    # ключове число: граф відкидає значну частку LLM-розширення як шум
    assert b["noise_rejection_rate_mean"] > 0.5
    assert b["claim_safety_rate"] == 1.0
