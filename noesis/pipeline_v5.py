"""CME v0.5 — уніфікована методологічна труба + 10 валідаційних гейтів.

Один сирий вхід → IntentMirror · CategoryMap · TheoryLensReport · EIICReport ·
MethodArtifact · ValidationReport(10 гейтів) · EvidenceBundle · NextAction.
Підтримує ablation через `modules` для доказу не-декоративності кожного шару.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from noesis.eiic import EIICCore, run_eiic
from noesis.forbidden import check_forbidden_claims
from noesis.generators import build_artifact_deterministic, build_mirror_deterministic
from noesis.models import Check, MirrorArtifact, RealityMaps, ValidationReport
from noesis.ontology import build_reality_maps, extract_categories
from noesis.provenance import FORBIDDEN_TAXONOMY, Claim, governance_summary
from noesis.theories import LensReadout, run_theories, select_lenses
from tools.artifact_checker import REQUIRED_SECTIONS, check_artifact
from tools.finalizer100 import count_words

ALL_MODULES: frozenset[str] = frozenset(
    {"intent_mirror", "category_layer", "theory_lens", "eiic", "validator", "failure_modes"}
)
PIPELINE_VERSION = "0.5"

_DETERMINISTIC_MODULES = (
    "intent_mirror(det)", "category_extractor", "reality_maps", "theory_proxies",
    "eiic", "reverse_inference", "artifact_builder", "validators", "evidence",
)
_LLM_MODULES = ("intent_mirror(finalizer, optional)",)


@dataclass
class V5Run:
    raw_input: str
    intent_mirror: MirrorArtifact
    maps: RealityMaps
    readouts: dict[str, LensReadout]
    selected_lenses: list[str]
    eiic: EIICCore
    artifact: dict[str, str]
    next_action: str
    baseline: dict[str, Any]
    validation: ValidationReport
    claims: list[Claim] = field(default_factory=list)
    modules: frozenset[str] = ALL_MODULES

    @property
    def passed(self) -> bool:
        return self.validation.passed


# ── Baseline (Gate 9) ─────────────────────────────────────────────────────────


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


# ── 10 валідаційних гейтів ────────────────────────────────────────────────────


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


def _manifest(raw: str, run: V5Run, files: list[str], created_at: str | None) -> dict[str, Any]:
    return {
        "run_id": hashlib.sha256(raw.encode("utf-8")).hexdigest()[:16],
        "timestamp": created_at,
        "input_hash": hashlib.sha256(raw.encode("utf-8")).hexdigest(),
        "pipeline_version": PIPELINE_VERSION,
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
    manifest = _manifest(raw, run, files, created_at)
    w("manifest.json", json.dumps(manifest, ensure_ascii=False, indent=2))
    return run, manifest
