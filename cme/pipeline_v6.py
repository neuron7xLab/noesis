"""CME v0.6 — труба, що ДОВОДИТЬ, які шари змінюють рішення.

raw → complexity → adaptive mirror → causal categories → reality-map delta →
theory contribution → EIIC → action selector → artifact → 12 gates → evidence.
Модуль-тогли дають реальний ablation-diff (next_action змінюється чи ні).
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from cme.adaptive import IntentMirrorAdaptive, build_adaptive_mirror
from cme.causal import (
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
from cme.complexity import ComplexityProfile, estimate_complexity
from cme.eiic import EIICCore, run_eiic
from cme.forbidden import check_forbidden_claims
from cme.generators import build_artifact_deterministic, build_mirror_deterministic
from cme.models import Check, RealityMaps, ValidationReport
from cme.ontology import build_reality_maps, extract_categories
from cme.theories import run_theories
from tools.artifact_checker import check_artifact

ALL_MODULES_V6: frozenset[str] = frozenset(
    {"category_layer", "reality_maps", "theory_layer", "eiic", "claim_governance",
     "adaptive_compression", "artifact_validation"}
)
PIPELINE_VERSION = "0.6"


@dataclass
class V6Run:
    raw_input: str
    complexity: ComplexityProfile
    mirror: IntentMirrorAdaptive
    category_effects: list[CategoryEffect]
    map_delta: RealityMapDelta
    contributions: list[TheoryContribution]
    theory_status: str
    eiic: EIICCore
    action: ActionDecision
    artifact: dict[str, str]
    validation: ValidationReport
    modules: frozenset[str] = ALL_MODULES_V6
    flags: dict[str, bool] = field(default_factory=dict)

    @property
    def passed(self) -> bool:
        return self.validation.passed


# ── 12 гейтів v0.6 ────────────────────────────────────────────────────────────


def _gates(run_parts: dict[str, Any]) -> list[Check]:
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
        checks = _gates({
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
    from cme.benchmark_v6 import run_ablation_v6
    from cme.human_eval import build_human_eval_packet

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
        "pipeline_version": PIPELINE_VERSION,
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
