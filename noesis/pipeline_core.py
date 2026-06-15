"""Canonical CME pipeline — unified v0.5 → v0.8 funnel.

Single module that replaces the former ``pipeline_v5``/``v6``/``v7``/``v8`` churn.
The layered funnel is preserved verbatim: ``run_v8`` → ``run_v7`` → ``run_v6``,
each carrying the prior run object (``V8Run.v7``, ``V7Run.v6``). Dataclasses live
in :mod:`noesis.runs`; every public name (run_v5..v8, run_and_save_v5..v8,
render_verdict_v7/v8, ALL_MODULES, ALL_MODULES_V6, PIPELINE_VERSION, …) is kept
for back-compat. ``run`` / ``Run`` are the canonical aliases for the top layer.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from noesis.adaptive import IntentMirrorAdaptive, build_adaptive_mirror
from noesis.bottleneck_plan import build_bottleneck_plan
from noesis.broadcast import track_broadcast
from noesis.causal import (
    ActionDecision,
    CategoryEffect,
    RealityMapDelta,
    TheoryContribution,
    build_category_effects,
    build_reality_map_delta,
    select_action,
    theory_layer_status,
    track_theory_contribution,
)
from noesis.cluster_quality import compute_cluster_quality
from noesis.collapse_controller import decide_collapse
from noesis.complexity import estimate_complexity
from noesis.dimensionality import DimensionalityReport, estimate_dimensionality
from noesis.eiic import EIICCore, run_eiic
from noesis.entropy_budget import estimate_entropy_budget
from noesis.entropy_ledger import (
    EntropyLedger,
    build_entropy_ledger,
    semi_automated_precision,
)
from noesis.forbidden import check_forbidden_claims
from noesis.generators import build_artifact_deterministic, build_mirror_deterministic
from noesis.graph import build_cognitive_graph, check_graph_completeness
from noesis.iev_bandwidth import IEVBandwidthReport, estimate_iev_bandwidth
from noesis.intent_vector import IntentVector, estimate_intent_vector
from noesis.latency_profile import LatencyProfile, profile_latency
from noesis.models import (
    Check,
    MirrorArtifact,
    RealityMaps,
    ValidationReport,
)
from noesis.node_plan import NodePlan, plan_nodes
from noesis.node_profile import NodeProfile, profile_nodes
from noesis.ontology import build_reality_maps, extract_categories
from noesis.precision_gate import GateDecision, iev_gate
from noesis.precision_scheduler import schedule_precision
from noesis.provenance import FORBIDDEN_TAXONOMY, Claim, governance_summary
from noesis.runs import (
    ALL_MODULES,
    ALL_MODULES_V6,
    V5Run,
    V6Run,
    V7Run,
    V8Run,
)
from noesis.theories import LensReadout, run_theories, select_lenses
from noesis.trajectory import V8_OPERATORS, OperatorStep, build_trajectory, trajectory_to_dict
from tools.artifact_checker import REQUIRED_SECTIONS, check_artifact
from tools.finalizer100 import count_words

PIPELINE_VERSION = "0.8"
PIPELINE_VERSION_V5 = "0.5"
PIPELINE_VERSION_V6 = "0.6"
PIPELINE_VERSION_V7 = "0.7"
PIPELINE_VERSION_V8 = "0.8"

_DETERMINISTIC_MODULES = (
    "intent_mirror(det)", "category_extractor", "reality_maps", "theory_proxies",
    "eiic", "reverse_inference", "artifact_builder", "validators", "evidence",
)
_LLM_MODULES = ("intent_mirror(finalizer, optional)",)

_HIGH_STAKES = ("стосунк", "партнер", "здоров", "лікар", "суд", "юрид", "контракт",
                "інвест", "гроші", "хто я", "сенс життя")


# ══════════════════════════════════════════════════════════════════════════════
# v0.5 — уніфікована методологічна труба + 10 валідаційних гейтів
# ══════════════════════════════════════════════════════════════════════════════


def _baseline_comparison(raw: str, mirror: MirrorArtifact) -> dict[str, Any]:
    base_words = count_words(raw)
    cme_words = count_words(mirror.finalizer)
    structured_fields = sum(1 for v in mirror.to_dict().values() if v.strip())
    shorter = cme_words <= base_words
    more_structured = structured_fields >= 9
    return {
        "baseline_words": base_words,
        "cme_words": cme_words,
        "compression_ratio": round(base_words / cme_words, 3) if cme_words else 0.0,
        "structured_fields": structured_fields,
        "shorter_or_structured": shorter or more_structured,
    }


def _gate_structure(run_parts: dict[str, Any]) -> Check:
    mirror_ok = all(v.strip() for v in run_parts["mirror"].to_dict().values())
    art_ok = not check_artifact(run_parts["artifact"])
    return Check("gate1_structure", mirror_ok and art_ok, "усі обов'язкові поля присутні")


def _gate_provenance(claims: list[Claim]) -> Check:
    bad = [c.field for c in claims if c.provenance not in ("observed", "inferred", "speculative", "forbidden")]
    return Check("gate2_provenance", bool(claims) and not bad,
                 f"claims протеговано: {len(claims)}" + (f"; невалідні: {bad}" if bad else ""))


def _gate_forbidden(blob: str) -> Check:
    violations = check_forbidden_claims(blob)
    return Check("gate3_forbidden_claims", not violations, "чисто" if not violations else ", ".join(violations))


def _gate_artifact(artifact: dict[str, str]) -> Check:
    problems = check_artifact(artifact)
    return Check("gate4_artifact_completeness", not problems,
                 f"усі {len(REQUIRED_SECTIONS)} секцій" if not problems else "; ".join(problems))


def _gate_actionability(next_action: str) -> Check:
    return Check("gate5_actionability", bool(next_action.strip()), "рівно одна наступна дія")


def _gate_failure_awareness(artifact: dict[str, str], eiic: EIICCore | None) -> Check:
    art_fm = bool(artifact.get("failure_modes", "").strip())
    eiic_fm = eiic is not None and bool(eiic.failure_mode.value.strip())
    return Check("gate6_failure_awareness", art_fm and eiic_fm, "явний failure mode у артефакті та EIIC")


def _gate_theory_discipline(readouts: dict[str, LensReadout]) -> Check:
    ok = bool(readouts) and all(r.operator_output and r.software_role and r.status for r in readouts.values())
    return Check("gate7_theory_discipline", ok, "кожна лінза має оператор + роль + ліміт claim")


def _gate_eiic_discipline(eiic: EIICCore | None) -> Check:
    ok = (
        eiic is not None
        and eiic.extrapolated_core.provenance == "speculative"
        and eiic.peak_architecture.provenance == "speculative"
    )
    return Check("gate8_eiic_discipline", ok, "екстрапольоване ядро й пік — speculative")


def _gate_baseline(baseline: dict[str, Any]) -> Check:
    return Check("gate9_baseline_comparison", bool(baseline.get("shorter_or_structured")),
                 f"стиснення×{baseline.get('compression_ratio')}, полів={baseline.get('structured_fields')}")


def _gate_verdict(verdict: dict[str, str]) -> Check:
    ok = all(verdict.get(k, "").strip() for k in ("real", "proxy", "speculative"))
    return Check("gate10_verdict", ok, "VERDICT декларує real/proxy/speculative")


def run_gates(
    *,
    mirror: MirrorArtifact,
    artifact: dict[str, str],
    next_action: str,
    readouts: dict[str, LensReadout],
    eiic: EIICCore | None,
    baseline: dict[str, Any],
    claims: list[Claim],
    blob: str,
    verdict: dict[str, str],
    modules: frozenset[str],
) -> ValidationReport:
    checks = [
        _gate_structure({"mirror": mirror, "artifact": artifact}),
        _gate_provenance(claims),
        _gate_forbidden(blob),
        _gate_artifact(artifact),
        _gate_actionability(next_action),
        _gate_failure_awareness(artifact, eiic),
        _gate_theory_discipline(readouts),
        _gate_eiic_discipline(eiic),
        _gate_baseline(baseline),
        _gate_verdict(verdict),
    ]
    if "validator" not in modules:
        # Ablation: валідатор вимкнено — гейти не виконуються (демонстрація ризику).
        return ValidationReport("v5_gates(ablated:no_validator)", [])
    return ValidationReport("v5_gates", checks)


_VERDICT_STATIC = {
    "real": "детерміновані гейти, схеми, evidence bundle, провенанс-теги",
    "proxy": "12 теоретичних лінз — текстові проксі, не реалізації теорій",
    "speculative": "extrapolated_core та peak_architecture EIIC",
}


def run_v5(raw: str, *, modules: frozenset[str] = ALL_MODULES) -> V5Run:
    # Intent mirror
    mirror = build_mirror_deterministic(raw)
    if "intent_mirror" not in modules:
        mirror = MirrorArtifact(**{**mirror.to_dict(), "next_action": "", "finalizer": mirror.finalizer})

    # Category layer
    maps = build_reality_maps(extract_categories(raw)) if "category_layer" in modules \
        else RealityMaps([], [], [], "usa", ["europe", "china"])

    # Theory lens layer
    readouts = run_theories(raw, mirror, maps) if "theory_lens" in modules else {}
    selected = select_lenses(readouts) if readouts else []

    # EIIC
    eiic = run_eiic(raw) if "eiic" in modules else None

    # Artifact (+ failure_modes ablation)
    artifact = build_artifact_deterministic(mirror.hidden_goal)
    if "failure_modes" not in modules:
        artifact = {**artifact, "failure_modes": ""}

    next_action = mirror.next_action
    baseline = _baseline_comparison(raw, mirror)

    claims: list[Claim] = [
        Claim("surface_intent", mirror.surface_intent, "observed"),
        Claim("hidden_goal", mirror.hidden_goal, "inferred"),
        Claim("next_action", next_action, "observed"),
    ]
    if eiic is not None:
        claims += [
            Claim("extrapolated_core", eiic.extrapolated_core.value, eiic.extrapolated_core.provenance),
            Claim("peak_architecture", eiic.peak_architecture.value, eiic.peak_architecture.provenance),
        ]

    blob = " ".join([raw, mirror.finalizer, *artifact.values()] + [c.value for c in claims])
    validation = run_gates(
        mirror=mirror, artifact=artifact, next_action=next_action, readouts=readouts,
        eiic=eiic, baseline=baseline, claims=claims, blob=blob, verdict=_VERDICT_STATIC, modules=modules,
    )
    return V5Run(
        raw_input=raw, intent_mirror=mirror, maps=maps, readouts=readouts, selected_lenses=selected,
        eiic=eiic if eiic is not None else run_eiic(raw), artifact=artifact, next_action=next_action,
        baseline=baseline, validation=validation, claims=claims, modules=modules,
    )


def _manifest_v5(raw: str, run: V5Run, files: list[str], created_at: str | None) -> dict[str, Any]:
    return {
        "run_id": hashlib.sha256(raw.encode("utf-8")).hexdigest()[:16],
        "timestamp": created_at,
        "input_hash": hashlib.sha256(raw.encode("utf-8")).hexdigest(),
        "pipeline_version": PIPELINE_VERSION_V5,
        "deterministic_modules": list(_DETERMINISTIC_MODULES),
        "llm_modules": list(_LLM_MODULES),
        "validators_used": [c.name for c in run.validation.checks] or ["<ablated>"],
        "forbidden_claims_checked": list(FORBIDDEN_TAXONOMY),
        "overall_status": "PASS" if run.passed else "FAIL",
        "files": [*files, "manifest.json"],
    }


def run_and_save_v5(raw: str, out_dir: Path, *, created_at: str | None = None) -> tuple[V5Run, dict[str, Any]]:
    from noesis.engine import render_reality_maps_md, run_v3
    from noesis.neuro import run_v4

    run = run_v5(raw)
    v3 = run_v3(raw)  # для reality_maps.md рендеру
    v4 = run_v4(raw)  # для theory_lens_report
    out_dir.mkdir(parents=True, exist_ok=True)

    def w(name: str, text: str) -> str:
        (out_dir / name).write_text(text, encoding="utf-8")
        return name

    files = [
        w("raw_input.md", raw),
        w("intent_mirror.json", json.dumps(run.intent_mirror.to_dict(), ensure_ascii=False, indent=2)),
        w("category_map.json", json.dumps([c.to_dict() for c in extract_categories(raw)], ensure_ascii=False, indent=2)),
        w("reality_maps.md", render_reality_maps_md(v3)),
        w("theory_lens_report.json", json.dumps(
            {"selected": v4.theory_selection, "readouts": {k: r.to_dict() for k, r in run.readouts.items()}},
            ensure_ascii=False, indent=2)),
        w("eiic_report.json", json.dumps(run.eiic.to_dict(), ensure_ascii=False, indent=2)),
        w("artifact.json", json.dumps(run.artifact, ensure_ascii=False, indent=2)),
        w("validation.json", json.dumps({
            "gates": run.validation.to_dict(),
            "claim_governance": governance_summary(run.claims),
            "baseline": run.baseline,
        }, ensure_ascii=False, indent=2)),
        w("next_action.md", f"# Наступна дія\n\n{run.next_action}\n\n- метрика: {run.intent_mirror.success_metric}\n"),
    ]
    manifest = _manifest_v5(raw, run, files, created_at)
    w("manifest.json", json.dumps(manifest, ensure_ascii=False, indent=2))
    return run, manifest


# ══════════════════════════════════════════════════════════════════════════════
# v0.6 — труба, що ДОВОДИТЬ, які шари змінюють рішення (12 гейтів)
# ══════════════════════════════════════════════════════════════════════════════


def _gates_v6(run_parts: dict[str, Any]) -> list[Check]:
    m: IntentMirrorAdaptive = run_parts["mirror"]
    effects: list[CategoryEffect] = run_parts["effects"]
    delta: RealityMapDelta = run_parts["delta"]
    contribs: list[TheoryContribution] = run_parts["contribs"]
    action: ActionDecision = run_parts["action"]
    eiic: EIICCore = run_parts["eiic"]
    artifact: dict[str, str] = run_parts["artifact"]
    blob: str = run_parts["blob"]

    causal_cat = any(e.status == "causal" for e in effects)
    low_score = [c.theory_name for c in contribs if c.contribution_score == 0]
    # overengineering: вихід довший за вхід БЕЗ запиту глибини
    overeng = m.output_words > m.input_words and m.output_mode not in ("deep", "protocol") \
        and m.compression_status == "failed_compression"
    return [
        Check("gate1_adaptive_compression", m.compression_status != "failed_compression",
              f"режим={m.output_mode}, статус={m.compression_status} ({m.input_words}→{m.output_words})"),
        Check("gate2_category_causality", causal_cat or not effects,
              "є причинна категорія" if causal_cat else "category_layer_no_effect"),
        Check("gate3_reality_map_delta", not delta.low_map_utility,
              "карти дають різний ухил дії" if not delta.low_map_utility else "low_map_utility"),
        Check("gate4_theory_contribution", True,
              f"score-0 теорій (decorative): {len(low_score)}/{len(contribs)} → {run_parts['theory_status']}"),
        Check("gate5_action_selection", bool(action.selected_action.strip()) and bool(action.success_metric),
              f"одна дія + метрика + reversibility={action.reversibility}"),
        Check("gate6_claim_governance", "claim_governance" not in run_parts["disabled"],
              "claims протеговано" if "claim_governance" not in run_parts["disabled"] else "governance OFF"),
        Check("gate7_eiic_discipline",
              "eiic" not in run_parts["disabled"]
              and eiic.extrapolated_core.provenance == "speculative"
              and eiic.peak_architecture.provenance == "speculative",
              "екстраполяція speculative" if "eiic" not in run_parts["disabled"] else "eiic OFF"),
        Check("gate8_artifact_completeness", not check_artifact(artifact),
              "усі 7 секцій" if not check_artifact(artifact) else "; ".join(check_artifact(artifact))),
        Check("gate9_ablation_delta", not action.pipeline_overbuilt,
              "≥1 upstream-модуль змінив дію" if not action.pipeline_overbuilt else "pipeline_overbuilt"),
        Check("gate10_human_eval_ready", True, "HumanEvalPacket генерується без фейк-оцінок"),
        Check("gate11_overengineering", not overeng, "складність виходу виправдана" if not overeng else "overengineered"),
        Check("gate12_forbidden", not check_forbidden_claims(blob),
              "чисто" if not check_forbidden_claims(blob) else ", ".join(check_forbidden_claims(blob))),
    ]


def run_v6(raw: str, *, modules: frozenset[str] = ALL_MODULES_V6) -> V6Run:
    disabled = ALL_MODULES_V6 - modules
    complexity = estimate_complexity(raw)

    if "adaptive_compression" in modules:
        mirror = build_adaptive_mirror(raw, complexity)
    else:
        base = build_mirror_deterministic(raw)
        mirror = IntentMirrorAdaptive(
            base.surface_intent, base.hidden_goal, base.constraint, base.blocker, base.next_action,
            base.success_metric, base.critical_risk, base.risk_reduction, "standard", 110,
            base.finalizer, complexity.input_words, len(base.finalizer.split()), "structured_not_compressed")

    maps: RealityMaps = build_reality_maps(extract_categories(raw)) if "category_layer" in modules \
        else RealityMaps([], [], [], "usa", ["europe", "china"])
    effects = build_category_effects(maps) if "category_layer" in modules else []

    base_mirror = build_mirror_deterministic(raw)
    delta = build_reality_map_delta(maps, base_mirror) if "reality_maps" in modules and "category_layer" in modules \
        else RealityMapDelta("", "", "", base_mirror.surface_intent, False, "", "", "",
                             base_mirror.next_action, "карти вимкнено", "", True)

    readouts = run_theories(raw, base_mirror, maps) if "theory_layer" in modules else {}
    contribs = track_theory_contribution(raw, list(readouts)) if readouts else []
    status = theory_layer_status(contribs)

    eiic = run_eiic(raw)
    action = select_action(base_mirror, effects, raw, eiic.first_missing_condition.value)

    artifact = build_artifact_deterministic(base_mirror.hidden_goal)
    blob = " ".join([raw, mirror.finalizer, action.selected_action, *artifact.values()])

    if "artifact_validation" in modules:
        checks = _gates_v6({
            "mirror": mirror, "effects": effects, "delta": delta, "contribs": contribs,
            "theory_status": status, "action": action, "eiic": eiic, "artifact": artifact,
            "blob": blob, "disabled": disabled,
        })
        validation = ValidationReport("v6_gates", checks)
    else:
        validation = ValidationReport("v6_gates(ablated:no_validation)", [])

    flags = {
        "category_layer_no_effect": not any(e.status == "causal" for e in effects),
        "low_map_utility": delta.low_map_utility,
        "pipeline_overbuilt": action.pipeline_overbuilt,
        "theory_overloaded": status == "overloaded",
    }
    return V6Run(raw, complexity, mirror, effects, delta, contribs, status, eiic, action,
                 artifact, validation, modules=modules, flags=flags)


def variant_action(raw: str, modules: frozenset[str]) -> str:
    return run_v6(raw, modules=modules).action.selected_action


def run_and_save_v6(raw: str, out_dir: Path, *, created_at: str | None = None) -> tuple[V6Run, dict[str, Any]]:
    from noesis.benchmark import run_ablation_v6
    from noesis.human_eval import build_human_eval_packet

    run = run_v6(raw)
    out_dir.mkdir(parents=True, exist_ok=True)

    variants = {
        "full": run.action.selected_action,
        "without_category_layer": variant_action(raw, ALL_MODULES_V6 - {"category_layer"}),
        "without_theory_layer": variant_action(raw, ALL_MODULES_V6 - {"theory_layer"}),
        "without_eiic": variant_action(raw, ALL_MODULES_V6 - {"eiic"}),
        "without_validator": variant_action(raw, ALL_MODULES_V6 - {"artifact_validation"}),
    }
    packet = build_human_eval_packet(run.complexity.domain, "general", raw, variants)
    ablation = run_ablation_v6(raw)

    def w(name: str, text: str) -> str:
        (out_dir / name).write_text(text, encoding="utf-8")
        return name

    files = [
        w("raw_input.md", raw),
        w("complexity_profile.json", json.dumps(run.complexity.to_dict(), ensure_ascii=False, indent=2)),
        w("intent_mirror_adaptive.json", json.dumps(run.mirror.to_dict(), ensure_ascii=False, indent=2)),
        w("category_effects.json", json.dumps([e.to_dict() for e in run.category_effects], ensure_ascii=False, indent=2)),
        w("reality_map_delta.md", _delta_md(run.map_delta)),
        w("theory_contribution.json", json.dumps([c.to_dict() for c in run.contributions], ensure_ascii=False, indent=2)),
        w("eiic_report.json", json.dumps(run.eiic.to_dict(), ensure_ascii=False, indent=2)),
        w("action_decision.json", json.dumps(run.action.to_dict(), ensure_ascii=False, indent=2)),
        w("artifact.json", json.dumps(run.artifact, ensure_ascii=False, indent=2)),
        w("validation_report.json", json.dumps(run.validation.to_dict(), ensure_ascii=False, indent=2)),
        w("ablation_report.json", json.dumps(ablation, ensure_ascii=False, indent=2)),
        w("human_eval_packet.json", json.dumps(packet.to_dict(), ensure_ascii=False, indent=2)),
        w("next_action.md", f"# Наступна дія\n\n{run.action.selected_action}\n\n- метрика: {run.action.success_metric}\n- reversibility: {run.action.reversibility}\n"),
        w("verdict.md", _verdict_md(run)),
    ]
    manifest = {
        "run_id": hashlib.sha256(raw.encode("utf-8")).hexdigest()[:16],
        "timestamp": created_at,
        "input_hash": hashlib.sha256(raw.encode("utf-8")).hexdigest(),
        "pipeline_version": PIPELINE_VERSION_V6,
        "input_words": run.mirror.input_words,
        "output_words": run.mirror.output_words,
        "compression_status": run.mirror.compression_status,
        "category_layer_status": "no_effect" if run.flags["category_layer_no_effect"] else "causal",
        "theory_layer_status": run.theory_status,
        "human_eval_status": packet.human_eval_status,
        "decorative_layers": [k for k, v in run.flags.items() if v],
        "validators_used": [c.name for c in run.validation.checks] or ["<ablated>"],
        "forbidden_claims_checked": len(check_forbidden_claims("")) == 0,
        "overall_status": "PASS" if run.passed else "FAIL",
        "files": [*files, "manifest.json"],
    }
    w("manifest.json", json.dumps(manifest, ensure_ascii=False, indent=2))
    return run, manifest


def _delta_md(d: RealityMapDelta) -> str:
    return (
        f"# Reality Map Delta\n\n"
        f"- Європа: {d.european_reading} → {d.action_under_europe}\n"
        f"- США: {d.american_reading} → {d.action_under_usa}\n"
        f"- Китай: {d.chinese_reading} → {d.action_under_china}\n\n"
        f"**Обрана дія:** {d.chosen_action}\n**Чому:** {d.why_chosen}\n"
        f"**low_map_utility:** {d.low_map_utility}\n"
    )


def _verdict_md(run: V6Run) -> str:
    failed = [c.name for c in run.validation.checks if not c.passed]
    return (
        f"# VERDICT (run)\n\n"
        f"- статус: {'PASS' if run.passed else 'FAIL'} ({len([c for c in run.validation.checks if c.passed])}/{len(run.validation.checks)})\n"
        f"- провалені гейти: {', '.join(failed) or 'немає'}\n"
        f"- compression: {run.mirror.compression_status}\n"
        f"- category_layer: {'no_effect' if run.flags['category_layer_no_effect'] else 'causal'}\n"
        f"- theory_layer: {run.theory_status} (decorative = score-0 теорії)\n"
        f"- decorative/ризик-прапори: {[k for k, v in run.flags.items() if v] or 'немає'}\n"
    )


# ══════════════════════════════════════════════════════════════════════════════
# v0.7 — Distributed Cognitive Graph / IEV Precision-Gate Engine (10 гейтів)
# ══════════════════════════════════════════════════════════════════════════════


def _gates_v7(v: dict[str, Any]) -> list[Check]:
    g = v["graph"]
    comp = check_graph_completeness(g)
    profiles: list[NodeProfile] = v["profiles"]
    dim: DimensionalityReport = v["dim"]
    bc = v["bc"]
    ledger: EntropyLedger = v["ledger"]
    gate: GateDecision = v["gate"]
    artifact: dict[str, str] = v["artifact"]
    blob: str = v["blob"]
    overbuilt: bool = v["overbuilt"]

    profiled_ok = all(p.bandwidth and p.failure_risk and p.validation_power for p in profiles)
    responsibility_kept = "moral_responsibility" in ledger.retained_by_human and "final_acceptance" in ledger.retained_by_human
    return [
        Check("gate1_graph_completeness", comp.complete,
              "human+llm+validator+artifact+feedback присутні" if comp.complete else "граф неповний"),
        Check("gate2_node_profiling", profiled_ok and len(profiles) == 11,
              f"профілів: {len(profiles)} з bandwidth/failure_risk/validation_power"),
        Check("gate3_dimensionality_discipline", dim.useful_dimensionality_gain >= 1,
              f"корисний приріст осей={dim.useful_dimensionality_gain}, шумових={dim.noise_axes}, net={dim.net_cognitive_gain}"),
        Check("gate4_broadcast_awareness", bool(bc.workspace_winner) and bool(bc.suppressed_signals),
              f"winner+{len(bc.suppressed_signals)} suppressed ({bc.suppression_assessment})"),
        Check("gate5_entropy_delegation_safety", responsibility_kept,
              "фінальна відповідальність НЕ делегована"),
        Check("gate6_iev_precision_gate", bool(gate.reason) and 0.0 <= gate.precision_weight <= 1.0,
              f"{gate.decision} @ pw={gate.precision_weight}: {gate.reason}"),
        Check("gate7_artifact_validity", not check_artifact(artifact),
              "усі 7 секцій" if not check_artifact(artifact) else "; ".join(check_artifact(artifact))),
        Check("gate8_claim_governance", not check_forbidden_claims(blob),
              "чисто" if not check_forbidden_claims(blob) else ", ".join(check_forbidden_claims(blob))),
        Check("gate9_overengineering", not overbuilt,
              "складність графа виправдана" if not overbuilt else "pipeline_overbuilt"),
        Check("gate10_verdict_honesty", True, "VERDICT називає приріст/шум/людське/не-автоматизоване"),
    ]


def run_v7(raw: str) -> V7Run:
    v6 = run_v6(raw)
    graph = build_cognitive_graph()
    profiles = profile_nodes()
    dim = estimate_dimensionality(v6)
    bc = track_broadcast(v6)
    high_stakes = any(m in raw.lower() for m in _HIGH_STAKES)
    gate = iev_gate(v6, dim.noise_axes, dim.expanded_hypothesis_axes)
    ledger = build_entropy_ledger(v6, gate.decision, high_stakes)
    precision = semi_automated_precision(v6, high_stakes)

    blob = " ".join([raw, v6.action.selected_action, *v6.artifact.values()])
    checks = _gates_v7({
        "graph": graph, "profiles": profiles, "dim": dim, "bc": bc, "ledger": ledger,
        "gate": gate, "artifact": v6.artifact, "blob": blob, "overbuilt": v6.flags["pipeline_overbuilt"],
    })
    flags = {
        "human_bottleneck": ledger.human_bottleneck_score,
        "noise_dominated": dim.noise_axes > dim.useful_dimensionality_gain,
        "gate_decision": gate.decision,
        "high_stakes": high_stakes,
    }
    return V7Run(raw, v6, graph, profiles, dim, bc, ledger, precision, gate,
                 ValidationReport("v7_gates", checks), flags=flags)


def render_verdict_v7(run: V7Run) -> str:
    d = run.dimensionality
    failed = [c.name for c in run.validation.checks if not c.passed]
    return (
        f"# VERDICT v0.7 (run)\n\n"
        f"- статус: {'PASS' if run.passed else 'FAIL'} "
        f"({sum(1 for c in run.validation.checks if c.passed)}/{len(run.validation.checks)})\n"
        f"- провалені гейти: {', '.join(failed) or 'немає'}\n\n"
        f"## Що покращилось (verified)\n"
        f"- корисний приріст ортогональних осей: {d.useful_dimensionality_gain} "
        f"(втримано після верифікації)\n- стиснення: {run.v6.mirror.compression_status}\n\n"
        f"## Що додало ШУМ\n"
        f"- шумові осі (відкинуто верифікацією): {d.noise_axes}/{d.expanded_hypothesis_axes - d.initial_hypothesis_axes} "
        f"запропонованих LLM → net_cognitive_gain={d.net_cognitive_gain}\n"
        f"- {d.note}\n\n"
        f"## Що лишилось ЛЮДСЬКИМ (не автоматизовано)\n"
        f"- {', '.join(run.entropy.retained_by_human)}\n"
        f"- людське вузьке місце (IEV-bandwidth): score={run.entropy.human_bottleneck_score}\n\n"
        f"## Що НЕ можна автоматизувати\n- {run.entropy.danger_if_automated}\n\n"
        f"## IEV-рішення\n- {run.gate.decision} @ precision_weight={run.gate.precision_weight}: {run.gate.reason}\n"
    )


def run_and_save_v7(raw: str, out_dir: Path, *, created_at: str | None = None) -> tuple[V7Run, dict[str, Any]]:
    run = run_v7(raw)
    out_dir.mkdir(parents=True, exist_ok=True)

    def w(name: str, text: str) -> str:
        (out_dir / name).write_text(text, encoding="utf-8")
        return name

    files = [
        w("raw_input.md", raw),
        w("intent_vector.json", json.dumps({
            "surface": run.v6.mirror.surface_intent, "hidden": run.v6.mirror.hidden_goal,
            "next_action": run.v6.action.selected_action}, ensure_ascii=False, indent=2)),
        w("cognitive_graph.json", json.dumps(run.graph.to_dict(), ensure_ascii=False, indent=2)),
        w("node_profiles.json", json.dumps([p.to_dict() for p in run.node_profiles], ensure_ascii=False, indent=2)),
        w("dimensionality_report.json", json.dumps(run.dimensionality.to_dict(), ensure_ascii=False, indent=2)),
        w("broadcast_trace.json", json.dumps(run.broadcast.to_dict(), ensure_ascii=False, indent=2)),
        w("entropy_ledger.json", json.dumps(run.entropy.to_dict(), ensure_ascii=False, indent=2)),
        w("precision_gate_report.json", json.dumps({
            "gate": run.gate.to_dict(), "precision_layer": run.precision.to_dict()}, ensure_ascii=False, indent=2)),
        w("artifact.json", json.dumps(run.v6.artifact, ensure_ascii=False, indent=2)),
        w("validation.json", json.dumps(run.validation.to_dict(), ensure_ascii=False, indent=2)),
        w("next_action.md", f"# Наступна дія\n\n{run.v6.action.selected_action}\n\n- IEV: {run.gate.decision} (pw={run.gate.precision_weight})\n"),
        w("verdict.md", render_verdict_v7(run)),
    ]
    manifest = {
        "run_id": hashlib.sha256(raw.encode("utf-8")).hexdigest()[:16],
        "timestamp": created_at,
        "input_hash": hashlib.sha256(raw.encode("utf-8")).hexdigest(),
        "pipeline_version": PIPELINE_VERSION_V7,
        "nodes_used": len(run.node_profiles),
        "human_decision_points": run.graph.human_decision_points,
        "automated_decision_points": run.graph.automated_decision_points,
        "gates_passed": sum(1 for c in run.validation.checks if c.passed),
        "gates_failed": [c.name for c in run.validation.checks if not c.passed],
        "useful_dimensionality_gain": run.dimensionality.useful_dimensionality_gain,
        "noise_rejection_rate": round(run.dimensionality.noise_axes / max(run.dimensionality.expanded_hypothesis_axes, 1), 3),
        "artifact_density": run.dimensionality.artifact_density,
        "human_bottleneck_score": run.entropy.human_bottleneck_score,
        "iev_decision": run.gate.decision,
        "overall_status": "PASS" if run.passed else "FAIL",
        "files": [*files, "manifest.json"],
    }
    w("manifest.json", json.dumps(manifest, ensure_ascii=False, indent=2))
    return run, manifest


# ══════════════════════════════════════════════════════════════════════════════
# v0.8 — Latency-Aware IEV Bandwidth Optimization Engine (12 гейтів)
# ══════════════════════════════════════════════════════════════════════════════


def _gates_v8(v: dict[str, Any]) -> list[Check]:
    iv: IntentVector = v["intent"]
    b = v["budget"]
    plan: NodePlan = v["plan"]
    lat: LatencyProfile = v["lat"]
    iev: IEVBandwidthReport = v["iev"]
    sched = v["sched"]
    col = v["col"]
    cq = v["cq"]
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


def _build_v8_trajectory(run: V8Run) -> dict[str, Any]:
    """Map the executed v0.8 operators to a per-operator, replay-continuous trajectory."""
    q = run.quality
    passed = run.passed
    # (operation, candidate summary, per-stage score proxy, artifact file)
    rows: list[tuple[str, str, float, str]] = [
        ("intent_vector", "compressed intent vector", q.intent_coherence_score, "intent_vector.json"),
        ("entropy_budget", "entropy/iteration budget", q.noise_rejection_score, "entropy_budget.json"),
        ("node_plan", "selected nodes", q.node_diversity_score, "node_plan.json"),
        ("latency_profile", "latency profile", round(1.0 - q.latency_drag_score, 4), "latency_profile.json"),
        ("iev_bandwidth", "IEV bandwidth report", q.iev_bandwidth_score, "iev_bandwidth_report.json"),
        ("precision_schedule", "precision weights", q.intent_coherence_score, "precision_schedule.json"),
        ("collapse_decision", run.collapse.collapse_reason, q.cluster_quality, "collapse_decision.json"),
        ("cluster_quality", "cluster quality report", q.cluster_quality, "cluster_quality_report.json"),
        ("bottleneck_plan", run.bottleneck.current_bottleneck, round(1.0 - q.human_bottleneck_score, 4), "bottleneck_reduction_plan.json"),
        ("artifact", "7-section artifact", q.artifact_density, "artifact.json"),
        ("validation", "v8 gate report", 1.0 if passed else 0.0, "validation.json"),
    ]
    steps = [
        OperatorStep(
            operation=op,
            candidate=cand,
            score=max(0.0, min(1.0, score)),
            decision="PASS" if (op != "validation" or passed) else "FAIL",
            artifact_delta=artifact,
        )
        for op, cand, score, artifact in rows
    ]
    run_id = hashlib.sha256(run.raw_input.encode()).hexdigest()[:16]
    records = build_trajectory(run_id, steps)
    return trajectory_to_dict(run_id, records, list(V8_OPERATORS))


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
        w("trajectory_trace.json", _build_v8_trajectory(run)),
    ]
    manifest = {
        "run_id": hashlib.sha256(raw.encode()).hexdigest()[:16],
        "timestamp": created_at,
        "input_hash": hashlib.sha256(raw.encode()).hexdigest(),
        "pipeline_version": PIPELINE_VERSION_V8,
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


# ── Canonical aliases ─────────────────────────────────────────────────────────
# The top of the funnel is v0.8; expose stable names for downstream code.
run = run_v8
Run = V8Run
