"""Canonical run dataclasses for the layered CME funnel (v0.5 → v0.8).

These were previously defined one-per-`pipeline_vN` module. They live here so the
helper modules (broadcast, entropy_ledger, dimensionality, …) can type-annotate
against them under ``TYPE_CHECKING`` without importing the pipeline runtime,
breaking what would otherwise be an import cycle once the pipelines are unified
in :mod:`noesis.pipeline_core`.

Behaviour is identical to the pre-collapse dataclasses: same fields, same
defaults, same ``passed`` property.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from noesis.adaptive import IntentMirrorAdaptive
from noesis.bottleneck_plan import BottleneckReductionPlan
from noesis.broadcast import BroadcastTrace
from noesis.causal import (
    ActionDecision,
    CategoryEffect,
    RealityMapDelta,
    TheoryContribution,
)
from noesis.cluster_quality import ClusterQualityReport
from noesis.collapse_controller import CollapseDecision
from noesis.complexity import ComplexityProfile
from noesis.dimensionality import DimensionalityReport
from noesis.eiic import EIICCore
from noesis.entropy_budget import EntropyBudget
from noesis.entropy_ledger import EntropyLedger, PrecisionWeightReport
from noesis.graph import CognitiveGraph
from noesis.iev_bandwidth import IEVBandwidthReport
from noesis.intent_vector import IntentVector
from noesis.latency_profile import LatencyProfile
from noesis.models import MirrorArtifact, RealityMaps, ValidationReport
from noesis.node_plan import NodePlan
from noesis.node_profile import NodeProfile
from noesis.precision_gate import GateDecision
from noesis.precision_scheduler import PrecisionSchedule
from noesis.provenance import Claim
from noesis.theories import LensReadout

ALL_MODULES: frozenset[str] = frozenset(
    {"intent_mirror", "category_layer", "theory_lens", "eiic", "validator", "failure_modes"}
)
ALL_MODULES_V6: frozenset[str] = frozenset(
    {"category_layer", "reality_maps", "theory_layer", "eiic", "claim_governance",
     "adaptive_compression", "artifact_validation"}
)


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


@dataclass
class V8Run:
    raw_input: str
    v7: V7Run
    intent: IntentVector
    budget: EntropyBudget
    plan: NodePlan
    latency: LatencyProfile
    iev: IEVBandwidthReport
    precision: PrecisionSchedule
    collapse: CollapseDecision
    quality: ClusterQualityReport
    bottleneck: BottleneckReductionPlan
    validation: ValidationReport
    flags: dict[str, Any] = field(default_factory=dict)

    @property
    def passed(self) -> bool:
        return self.validation.passed
