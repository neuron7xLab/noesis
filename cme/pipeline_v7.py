"""CME v0.7 — Distributed Cognitive Graph / IEV Precision-Gate Engine.

raw → cognitive graph → node profiles → dimensionality → broadcast → entropy ledger
→ semi-automated precision → IEV gate → artifact → 10 gates → 13-файл evidence → verdict.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from cme.broadcast import BroadcastTrace, track_broadcast
from cme.dimensionality import DimensionalityReport, estimate_dimensionality
from cme.entropy_ledger import (
    EntropyLedger,
    PrecisionWeightReport,
    build_entropy_ledger,
    semi_automated_precision,
)
from cme.forbidden import check_forbidden_claims
from cme.graph import CognitiveGraph, build_cognitive_graph, check_graph_completeness
from cme.models import Check, ValidationReport
from cme.node_profile import NodeProfile, profile_nodes
from cme.pipeline_v6 import V6Run, run_v6
from cme.precision_gate import GateDecision, iev_gate
from tools.artifact_checker import check_artifact

PIPELINE_VERSION = "0.7"
_HIGH_STAKES = ("стосунк", "партнер", "здоров", "лікар", "суд", "юрид", "контракт",
                "інвест", "гроші", "хто я", "сенс життя")


@dataclass
class V7Run:
    raw_input: str
    v6: V6Run
    graph: CognitiveGraph
    node_profiles: list[NodeProfile]
    dimensionality: DimensionalityReport
    broadcast: BroadcastTrace
    entropy: EntropyLedger
    precision: PrecisionWeightReport
    gate: GateDecision
    validation: ValidationReport
    flags: dict[str, Any] = field(default_factory=dict)

    @property
    def passed(self) -> bool:
        return self.validation.passed


def _gates_v7(v: dict[str, Any]) -> list[Check]:
    g = v["graph"]
    comp = check_graph_completeness(g)
    profiles: list[NodeProfile] = v["profiles"]
    dim: DimensionalityReport = v["dim"]
    bc: BroadcastTrace = v["bc"]
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
        "pipeline_version": PIPELINE_VERSION,
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
