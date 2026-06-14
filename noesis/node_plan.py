"""Module 3 — Node Diversity Planner: вузли для комплементарних операцій, не повтору."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

from noesis.entropy_budget import EntropyBudget

# Ролі вузлів з НЕперетинними функціями.
NODE_ROLES: dict[str, str] = {
    "Creator": "розгортає гіпотези й структуру",
    "Critic": "знаходить суперечності, слабку логіку",
    "Auditor": "детектує overreach, failure-mode, ризик",
    "Verifier": "схема, докази, forbidden, валідність артефакту",
    "Compressor": "стискає ентропію в щільний артефакт",
    "Synthesizer": "інтегрує гілки в одне рішення",
    "RedTeam": "адверсивна атака на вихід",
    "MemoryNode": "дістає попередній контекст",
    "Router": "обирає наступний вузол за рішенням гейта",
}
# Порядок вибору вузлів за бюджетом (мінімальний достатній набір).
_PRIORITY = ("Creator", "Verifier", "Critic", "Compressor", "Auditor", "Synthesizer", "RedTeam", "MemoryNode")


@dataclass(frozen=True)
class NodePlan:
    selected_nodes: list[str]
    why_each_node_is_needed: dict[str, str]
    redundancy_risk: str
    missing_node_risk: str
    expected_entropy_expansion: str
    expected_noise_generation: str
    expected_validation_gain: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def plan_nodes(budget: EntropyBudget) -> NodePlan:
    k = max(1, min(budget.recommended_node_count, len(_PRIORITY)))
    selected = list(_PRIORITY[:k])
    if "Verifier" not in selected:  # верифікатор обов'язковий за наявності генерації
        selected[-1] = "Verifier"
    why = {n: NODE_ROLES[n] for n in selected}
    distinct = len(set(selected)) == len(selected)
    return NodePlan(
        selected_nodes=selected,
        why_each_node_is_needed=why,
        redundancy_risk="low" if distinct else "high (дубльовані ролі)",
        missing_node_risk="немає" if "Verifier" in selected else "відсутній Verifier — claim-leakage",
        expected_entropy_expansion=budget.required_expansion,
        expected_noise_generation="high" if k >= 5 else "medium" if k >= 3 else "low",
        expected_validation_gain="high" if "Verifier" in selected and "Auditor" in selected else "medium",
    )
