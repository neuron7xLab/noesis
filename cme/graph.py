"""Cognitive Graph Builder — людина + LLM як направлений граф інференсу.

Не «використання GPT», не автоматизація. Розподілена когніція: біологічний
контролер наміру тримає вектор; зовнішні вузли розширюють простір гіпотез.
Граф детермінований; вузли типізовані; bottleneck = вузол із найнижчою
пропускною на критичному шляху (як правило — людський контролер / IEV-гейт).
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

NODE_TYPES: tuple[str, ...] = (
    "human_intent_controller", "prompt_encoder", "llm_expander", "critic", "auditor",
    "verifier", "compressor", "artifact_builder", "validator", "decision_gate", "memory_store",
)
HUMAN_NODES = frozenset({"human_intent_controller", "decision_gate"})
LLM_NODES = frozenset({"llm_expander"})
VALIDATION_NODES = frozenset({"verifier", "validator", "auditor"})
ARTIFACT_NODES = frozenset({"artifact_builder"})


@dataclass(frozen=True)
class GraphNode:
    node_id: str
    role: str
    actor: str  # human | llm | auto

    def to_dict(self) -> dict[str, str]:
        return asdict(self)


@dataclass(frozen=True)
class CognitiveGraph:
    nodes: list[GraphNode]
    edges: list[tuple[str, str]]
    feedback_loops: list[tuple[str, str]]
    human_decision_points: list[str]
    automated_decision_points: list[str]
    bottlenecks: list[str]

    def to_dict(self) -> dict[str, Any]:
        return {
            "nodes": [n.to_dict() for n in self.nodes],
            "edges": [list(e) for e in self.edges],
            "feedback_loops": [list(e) for e in self.feedback_loops],
            "human_decision_points": self.human_decision_points,
            "automated_decision_points": self.automated_decision_points,
            "bottlenecks": self.bottlenecks,
        }


# Канонічна топологія Cognitive Scaling Loop.
_ACTOR = {
    "human_intent_controller": "human", "decision_gate": "human",
    "llm_expander": "llm",
    "prompt_encoder": "auto", "critic": "auto", "auditor": "auto", "verifier": "auto",
    "compressor": "auto", "artifact_builder": "auto", "validator": "auto", "memory_store": "auto",
}
_CHAIN = (
    "human_intent_controller", "prompt_encoder", "llm_expander", "critic", "auditor",
    "verifier", "compressor", "artifact_builder", "validator", "decision_gate",
)


def build_cognitive_graph() -> CognitiveGraph:
    nodes = [GraphNode(t, t.replace("_", " "), _ACTOR[t]) for t in NODE_TYPES]
    edges = list(zip(_CHAIN, _CHAIN[1:]))
    edges.append(("artifact_builder", "memory_store"))
    feedback = [("decision_gate", "human_intent_controller")]  # selective reentry
    human_dp = [n.node_id for n in nodes if n.actor == "human"]
    auto_dp = [n.node_id for n in nodes if n.actor in ("auto", "llm")]
    # bottleneck: людський контролер (низька пропускна) + IEV-гейт (ручне рішення)
    bottlenecks = ["human_intent_controller", "decision_gate"]
    return CognitiveGraph(nodes, edges, feedback, human_dp, auto_dp, bottlenecks)


@dataclass(frozen=True)
class GraphCompleteness:
    has_human_controller: bool
    has_llm_node: bool
    has_validator: bool
    has_artifact: bool
    has_feedback_loop: bool

    @property
    def complete(self) -> bool:
        return all(asdict(self).values())


def check_graph_completeness(g: CognitiveGraph) -> GraphCompleteness:
    roles = {n.node_id for n in g.nodes}
    return GraphCompleteness(
        has_human_controller=bool(roles & HUMAN_NODES),
        has_llm_node=bool(roles & LLM_NODES),
        has_validator=bool(roles & VALIDATION_NODES),
        has_artifact=bool(roles & ARTIFACT_NODES),
        has_feedback_loop=bool(g.feedback_loops),
    )
