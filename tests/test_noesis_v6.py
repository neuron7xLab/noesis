"""Тести CME v0.6: adaptive compression, causal categories, theory contribution,
ablation v2, human eval, 12 gates, evidence bundle."""

from __future__ import annotations

import json
from pathlib import Path

from noesis.adaptive import build_adaptive_mirror
from noesis.benchmark import run_ablation_v6, run_benchmark_v6
from noesis.complexity import estimate_complexity
from noesis.human_eval import build_human_eval_packet
from noesis.pipeline_core import ALL_MODULES_V6, run_and_save_v6, run_v6


def test_complexity_modes() -> None:
    assert estimate_complexity("що робити").recommended_output_mode == "micro"
    assert estimate_complexity("детально розпиши протокол виходу з вигорання").recommended_output_mode == "protocol"


def test_adaptive_does_not_pad_short_input() -> None:
    m = build_adaptive_mirror("хочу зрозуміти що далі")
    assert m.output_mode in ("micro", "brief")
    # коротко → НЕ доповнюємо до 90–110
    assert m.output_words < 90
    assert m.compression_status in ("compressed", "structured_not_compressed", "failed_compression")


def test_protocol_expansion_is_tagged() -> None:
    m = build_adaptive_mirror("детально протокол відновлення дисципліни крок за кроком")
    assert m.output_mode == "protocol"
    assert m.compression_status == "expanded_by_request"


def test_category_is_causal_changes_action() -> None:
    raw = "проєктую агентну систему треба вирішити структуру боюсь складності"
    full = run_v6(raw).action.selected_action
    without = run_v6(raw, modules=ALL_MODULES_V6 - {"category_layer"}).action.selected_action
    assert full != without  # категорія причинно змінює дію


def test_theory_contribution_flags_decorative() -> None:
    run = run_v6("хочу запустити продукт але боюсь складності")
    zero = [c for c in run.contributions if c.contribution_score == 0]
    assert zero  # є декоративні теорії
    assert all(c.decorative_risk for c in zero)


def test_ablation_identifies_keep_modify_remove() -> None:
    report = run_ablation_v6("проєктую агентну систему оркестратор плюс субагенти")
    assert report["without_category_layer"]["keep_modify_remove"] == "keep"
    verdicts = {v["keep_modify_remove"] for v in report.values()}
    assert "remove" in verdicts or "modify" in verdicts  # хоч один слабкий/декоративний


def test_human_eval_no_fake_scores() -> None:
    packet = build_human_eval_packet("c1", "general", "сирий вхід", {"full": "x"})
    assert packet.human_eval_status == "pending"
    assert packet.human_labels == {}
    assert len(packet.pairwise_questions) == 8


def test_benchmark_v6_real_numbers() -> None:
    b = run_benchmark_v6()
    assert b["n"] == 100
    assert b["proxy_eval"] is True
    # Acceptance #2: категорія змінює дію у ≥60% випадків
    assert b["category_causality_rate"] >= 0.6
    assert b["next_action_change_rate_under_ablation"] >= 0.6
    # теорії переважно декоративні — чесно зафіксовано
    assert b["decorative_theory_rate"] > 0.5
    assert b["human_eval_labels_status"] == "pending"


def test_evidence_bundle_v6_fifteen_files(tmp_path: Path) -> None:
    run, manifest = run_and_save_v6("хочу запустити продукт але застряг між напрямками", tmp_path)
    expected = {
        "raw_input.md", "complexity_profile.json", "intent_mirror_adaptive.json",
        "category_effects.json", "reality_map_delta.md", "theory_contribution.json",
        "eiic_report.json", "action_decision.json", "artifact.json", "validation_report.json",
        "ablation_report.json", "human_eval_packet.json", "next_action.md", "verdict.md", "manifest.json",
    }
    assert {p.name for p in tmp_path.iterdir()} == expected
    assert manifest["pipeline_version"] == "0.6"
    assert manifest["human_eval_status"] == "pending"
    loaded = json.loads((tmp_path / "human_eval_packet.json").read_text(encoding="utf-8"))
    assert loaded["human_eval_status"] == "pending"
