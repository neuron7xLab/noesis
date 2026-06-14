"""Module 4 — Latency Profile Engine: latency як проєктна змінна."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

from noesis.node_plan import NodePlan

# (latency_rank 1=fast..5=slow, bandwidth_rank, authority, best_mode)
_NODE_LATENCY: dict[str, tuple[int, int, str, str]] = {
    "Creator": (4, 5, "none", "parallel"),
    "Critic": (3, 3, "advisory", "cascade"),
    "Auditor": (3, 3, "advisory", "gate_first"),
    "Verifier": (2, 3, "gate", "gate_first"),
    "Compressor": (3, 3, "none", "compress_first"),
    "Synthesizer": (4, 3, "advisory", "serial"),
    "RedTeam": (4, 4, "advisory", "race"),
    "MemoryNode": (2, 4, "none", "parallel"),
    "Router": (1, 2, "control", "serial"),
}
_HUMAN = {"latency": "fast intuitive reject / slow explicit justify", "bandwidth": "low",
          "authority": "final", "fatigue": "sensitive"}


@dataclass(frozen=True)
class LatencyProfile:
    node_latencies: dict[str, str]
    human_profile: dict[str, str]
    bottleneck: str
    bottleneck_source: str
    latency_drag_score: float
    recommended_execution_modes: dict[str, str]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def profile_latency(plan: NodePlan, human_review: bool) -> LatencyProfile:
    ranks = [_NODE_LATENCY[n][0] for n in plan.selected_nodes]
    avg = sum(ranks) / max(len(ranks), 1)
    # drag росте з кількістю послідовних повільних вузлів; людський review додає
    drag = round(min(1.0, (avg / 5) * (len(plan.selected_nodes) / 5) + (0.3 if human_review else 0.0)), 3)
    if human_review:
        source = "human_review (IEV-bandwidth)"
        bottleneck = "human_intent_controller"
    elif len(plan.selected_nodes) >= 5:
        source = "over-routing (забагато вузлів)"
        bottleneck = "router"
    else:
        source = "model_inference"
        bottleneck = "Creator"
    return LatencyProfile(
        node_latencies={n: f"latency_rank={_NODE_LATENCY[n][0]}, bw={_NODE_LATENCY[n][1]}" for n in plan.selected_nodes},
        human_profile=_HUMAN,
        bottleneck=bottleneck,
        bottleneck_source=source,
        latency_drag_score=drag,
        recommended_execution_modes={n: _NODE_LATENCY[n][3] for n in plan.selected_nodes},
    )
