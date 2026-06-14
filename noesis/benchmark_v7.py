"""Cognitive Scaling Benchmark v0.7 — граф проти single-LLM, proxy_eval.

Жодних фейкових людських лейблів. Структурні метрики окремо від суб'єктивної
користі. Ключове число: яка частка LLM-розширення — шум, відкинутий верифікацією.
"""

from __future__ import annotations

from typing import Any

from noesis.benchmark import generate_inputs
from noesis.pipeline_v7 import run_v7


def run_benchmark_v7() -> dict[str, Any]:
    inputs = generate_inputs()
    n = len(inputs)
    useful = noise_rej = artifact_density = claim_safe = human_review = overbuilt = 0.0
    noise_dominated = 0
    decisions: dict[str, int] = {}

    for _domain, raw in inputs:
        r = run_v7(raw)
        d = r.dimensionality
        useful += d.useful_dimensionality_gain
        noise_rej += d.noise_axes / max(d.expanded_hypothesis_axes, 1)
        artifact_density += d.artifact_density
        if d.noise_axes > d.useful_dimensionality_gain:
            noise_dominated += 1
        gates = {c.name: c.passed for c in r.validation.checks}
        claim_safe += int(gates.get("gate8_claim_governance", False))
        decisions[r.gate.decision] = decisions.get(r.gate.decision, 0) + 1
        if r.gate.decision == "human_review":
            human_review += 1
        if r.v6.flags["pipeline_overbuilt"]:
            overbuilt += 1

    return {
        "n": n,
        "proxy_eval": True,
        "human_labels_status": "pending",
        "useful_dimensionality_gain_mean": round(useful / n, 3),
        "noise_rejection_rate_mean": round(noise_rej / n, 3),
        "noise_dominated_rate": round(noise_dominated / n, 3),
        "artifact_density_mean": round(artifact_density / n, 4),
        "claim_safety_rate": round(claim_safe / n, 3),
        "human_review_load": round(human_review / n, 3),
        "overengineering_rate": round(overbuilt / n, 3),
        "iev_decision_distribution": decisions,
        "note": "noise_rejection_rate висока = граф відкидає шум, який single-LLM лишив би (структурний proxy, не людська якість)",
    }
