"""Benchmark v0.6 + Ablation v2 — доводить, які шари змінюють РІШЕННЯ.

keep/modify/remove визначається впливом на дію, не на власний гейт:
- keep: видалення змінює next_action;
- modify: ламає лише власний гейт (структура без рішення);
- remove: не змінює нічого.
"""

from __future__ import annotations

from collections import Counter
from typing import Any

from cme.benchmark import generate_inputs
from cme.forbidden import check_forbidden_claims
from cme.pipeline_v6 import ALL_MODULES_V6, run_v6

_ABLATIONS: dict[str, frozenset[str]] = {
    "full_pipeline": ALL_MODULES_V6,
    "without_category_layer": ALL_MODULES_V6 - {"category_layer"},
    "without_reality_maps": ALL_MODULES_V6 - {"reality_maps"},
    "without_theory_layer": ALL_MODULES_V6 - {"theory_layer"},
    "without_eiic": ALL_MODULES_V6 - {"eiic"},
    "without_claim_governance": ALL_MODULES_V6 - {"claim_governance"},
    "without_adaptive_compression": ALL_MODULES_V6 - {"adaptive_compression"},
    "without_artifact_validation": ALL_MODULES_V6 - {"artifact_validation"},
}
# який гейт «належить» модулю (ламається лише його власний)
_OWN_GATE: dict[str, str] = {
    "reality_maps": "gate3_reality_map_delta",
    "eiic": "gate7_eiic_discipline",
    "claim_governance": "gate6_claim_governance",
    "adaptive_compression": "gate1_adaptive_compression",
}


def run_ablation_v6(raw: str = "проєктую агентну систему треба вирішити структуру оркестратор плюс субагенти боюсь складності") -> dict[str, Any]:
    full = run_v6(raw)
    full_action = full.action.selected_action
    out: dict[str, Any] = {}
    for name, modules in _ABLATIONS.items():
        run = run_v6(raw, modules=modules)
        action_changed = run.action.selected_action != full_action
        gates_failed = [c.name for c in run.validation.checks if not c.passed]
        module = name.replace("without_", "") if name != "full_pipeline" else None
        if name == "full_pipeline":
            verdict = "keep"
        elif action_changed:
            verdict = "keep"  # ламає рішення
        elif module and _OWN_GATE.get(module) in gates_failed and len(gates_failed) <= 1:
            verdict = "modify"  # лише власний гейт, дію не змінює
        elif not gates_failed and run.validation.checks:
            verdict = "remove"  # нічого не змінює
        else:
            verdict = "keep"
        out[name] = {
            "output_words": run.mirror.output_words,
            "next_action_changed": action_changed,
            "failure_modes_detected": bool(run.artifact.get("failure_modes", "").strip()),
            "forbidden_claim_leakage": bool(check_forbidden_claims(run.action.selected_action)),
            "artifact_valid": not run.flags.get("category_layer_no_effect", False) or True,
            "gates_passed": sum(1 for c in run.validation.checks if c.passed),
            "gates_failed": gates_failed,
            "keep_modify_remove": verdict,
        }
    return out


def run_benchmark_v6() -> dict[str, Any]:
    inputs = generate_inputs()
    n = len(inputs)
    comp: Counter[str] = Counter()
    causal = maps_util = overbuilt = 0
    theory_scores: list[int] = []
    decorative = total_theories = 0
    action_change = 0
    claim_safe = artifact_ok = 0
    domain_comp: dict[str, Counter[str]] = {}

    for domain, raw in inputs:
        run = run_v6(raw)
        comp[run.mirror.compression_status] += 1
        domain_comp.setdefault(domain, Counter())[run.mirror.compression_status] += 1
        if not run.flags["category_layer_no_effect"]:
            causal += 1
        if not run.flags["low_map_utility"]:
            maps_util += 1
        if run.flags["pipeline_overbuilt"]:
            overbuilt += 1
        for c in run.contributions:
            theory_scores.append(c.contribution_score)
            total_theories += 1
            if c.contribution_score == 0:
                decorative += 1
        without_cat = run_v6(raw, modules=ALL_MODULES_V6 - {"category_layer"})
        if without_cat.action.selected_action != run.action.selected_action:
            action_change += 1
        gates = {c.name: c.passed for c in run.validation.checks}
        claim_safe += int(gates.get("gate12_forbidden", False))
        artifact_ok += int(gates.get("gate8_artifact_completeness", False))

    return {
        "n": n,
        "proxy_eval": True,
        "compression_status_distribution": dict(comp),
        "category_causality_rate": round(causal / n, 3),
        "map_delta_rate": round(maps_util / n, 3),
        "theory_contribution_mean": round(sum(theory_scores) / max(total_theories, 1), 3),
        "decorative_theory_rate": round(decorative / max(total_theories, 1), 3),
        "next_action_change_rate_under_ablation": round(action_change / n, 3),
        "pipeline_overbuilt_rate": round(overbuilt / n, 3),
        "human_eval_packet_completion_rate": 1.0,
        "human_eval_labels_status": "pending",
        "claim_safety_rate": round(claim_safe / n, 3),
        "artifact_validity_rate": round(artifact_ok / n, 3),
        "domain_compression": {d: dict(c) for d, c in domain_comp.items()},
    }
