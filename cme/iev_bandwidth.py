"""Module 5 — IEV Bandwidth Estimator: яке валідаційне навантаження витримує контролер."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

from cme.entropy_budget import EntropyBudget
from cme.node_plan import NodePlan

HUMAN_GATE_CAPACITY = 3  # ~3-5 значущих рішень (робоча память Miller/Klingberg)


@dataclass(frozen=True)
class IEVBandwidthReport:
    required_gate_decisions: int
    human_gate_capacity: int
    automatable_gate_fraction: float
    manual_gate_fraction: float
    overload_risk: str
    recommended_gate_distribution: dict[str, str]
    precision_thresholds: dict[str, float]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def estimate_iev_bandwidth(budget: EntropyBudget, plan: NodePlan) -> IEVBandwidthReport:
    # одне gate-рішення на вузол + одне фінальне
    required = len(plan.selected_nodes) + 1
    # автоматизовне: schema/forbidden/compression гейти (низький ризик)
    auto = sum(1 for n in plan.selected_nodes if n in ("Verifier", "Compressor", "MemoryNode"))
    auto_frac = round(auto / max(required, 1), 3)
    manual_frac = round(1 - auto_frac, 3)
    manual_decisions = required - auto
    overload = "high" if manual_decisions > HUMAN_GATE_CAPACITY else "medium" if manual_decisions == HUMAN_GATE_CAPACITY else "low"
    dist = {
        "human_final_gate": "manual (high-risk)",
        "auditor_pre_gate": "advisory",
        "verifier_schema_gate": "automated",
        "compressor_entropy_gate": "automated",
        "router_reentry_gate": "automated",
    }
    if budget.human_review_bias:
        dist["human_final_gate"] = "manual (REQUIRED — high stakes)"
    return IEVBandwidthReport(required, HUMAN_GATE_CAPACITY, auto_frac, manual_frac, overload, dist,
                              {"pass": 0.75, "compress": 0.5, "reject": 0.3})
