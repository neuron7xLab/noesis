"""Тести CME v0.5: 10 гейтів, ablation, benchmark, claim governance, evidence, verdict."""

from __future__ import annotations

from pathlib import Path

from cme.benchmark import generate_inputs, run_ablation, run_benchmark
from cme.pipeline_v5 import ALL_MODULES, run_and_save_v5, run_v5
from cme.provenance import PROVENANCE, Claim, governance_summary, is_valid_provenance
from cme.verdict import read_verdict


def test_full_pipeline_passes_ten_gates() -> None:
    run = run_v5("хочу зібрати всі методи в один інструмент але боюсь що це знову хаос")
    assert run.passed
    assert len(run.validation.checks) == 10
    names = {c.name for c in run.validation.checks}
    assert "gate8_eiic_discipline" in names and "gate9_baseline_comparison" in names


def test_gate8_eiic_is_speculative() -> None:
    run = run_v5("вірю що ринок вибухне хочу запустити продукт")
    assert run.eiic.extrapolated_core.provenance == "speculative"
    g8 = next(c for c in run.validation.checks if c.name == "gate8_eiic_discipline")
    assert g8.passed


def test_claim_governance_tags() -> None:
    claims = [Claim("a", "x", "observed"), Claim("b", "y", "speculative")]
    assert all(is_valid_provenance(c.provenance) for c in claims)
    summary = governance_summary(claims)
    assert summary["observed"] == 1 and summary["speculative"] == 1
    assert set(summary) == set(PROVENANCE)


def test_ablation_proves_module_value() -> None:
    abl = run_ablation()
    # mirror, theory, eiic, failure_modes — кожен ламає конкретний гейт
    assert "gate5_actionability" in abl["without_intent_mirror"]["gates_failed"]
    assert "gate7_theory_discipline" in abl["without_theory_lens"]["gates_failed"]
    assert "gate8_eiic_discipline" in abl["without_eiic"]["gates_failed"]
    assert "gate4_artifact_completeness" in abl["without_failure_modes"]["gates_failed"]
    # validator вимкнено → гейти не виконуються (сліпа безпека)
    assert abl["without_validator"]["gates_run"] == 0
    # full — без провалів
    assert abl["full_pipeline"]["gates_failed"] == []


def test_benchmark_is_proxy_eval_over_100() -> None:
    assert len(generate_inputs()) == 100
    bench = run_benchmark()
    assert bench["n"] == 100
    assert bench["proxy_eval"] is True
    assert bench["claim_safety_rate"] == 1.0
    assert bench["artifact_validity_rate"] == 1.0


def test_evidence_bundle_v5_ten_files(tmp_path: Path) -> None:
    run, manifest = run_and_save_v5("хочу нарешті зробити щось своє але немає сил", tmp_path)
    expected = {
        "raw_input.md", "intent_mirror.json", "category_map.json", "reality_maps.md",
        "theory_lens_report.json", "eiic_report.json", "artifact.json", "validation.json",
        "next_action.md", "manifest.json",
    }
    assert {p.name for p in tmp_path.iterdir()} == expected
    assert manifest["pipeline_version"] == "0.5"
    assert manifest["overall_status"] == "PASS"
    assert manifest["forbidden_claims_checked"]


def test_verdict_reader(tmp_path: Path) -> None:
    run_and_save_v5("хочу запустити продукт але застряг", tmp_path)
    v = read_verdict(tmp_path)
    assert v["gates_total"] == 10
    assert v["overall_status"] == "PASS"
    assert v["gates_failed"] == []


def test_all_modules_constant() -> None:
    assert ALL_MODULES == frozenset(
        {"intent_mirror", "category_layer", "theory_lens", "eiic", "validator", "failure_modes"}
    )
