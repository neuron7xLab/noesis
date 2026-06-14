"""Типи даних CME: артефакти, карти, звіти валідації, маніфест евіденції."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass(frozen=True)
class MirrorArtifact:
    """Дев'ятипольова реконструкція наміру (Intent Mirror)."""

    surface_intent: str
    hidden_goal: str
    constraint: str
    blocker: str
    next_action: str
    success_metric: str
    time_horizon: str
    critical_risk: str
    risk_reduction: str
    finalizer: str  # стиснене представлення (90–110 слів, 6 якорів)

    def to_dict(self) -> dict[str, str]:
        return asdict(self)


@dataclass(frozen=True)
class IntrospectionMap:
    """Шестипольова карта внутрішнього стану (Introspection Engine)."""

    intent: str
    fear: str
    constraint: str
    missing_condition: str
    decision_boundary: str
    action: str

    def to_dict(self) -> dict[str, str]:
        return asdict(self)


@dataclass(frozen=True)
class Check:
    name: str
    passed: bool
    detail: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class ValidationReport:
    artifact_type: str
    checks: list[Check] = field(default_factory=list)

    @property
    def passed(self) -> bool:
        return all(c.passed for c in self.checks)

    def to_dict(self) -> dict[str, Any]:
        return {
            "artifact_type": self.artifact_type,
            "passed": self.passed,
            "checks": [c.to_dict() for c in self.checks],
        }


# ── Цивілізаційна онтологія (v0.3) ────────────────────────────────────────────


@dataclass(frozen=True)
class ActiveCategory:
    name: str
    axis: str  # europe | usa | china
    function: str
    failure_mode: str
    matched: list[str]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class RealityMaps:
    europe: list[ActiveCategory]
    usa: list[ActiveCategory]
    china: list[ActiveCategory]
    dominant_axis: str
    dormant_axes: list[str]

    def to_dict(self) -> dict[str, Any]:
        return {
            "europe": [c.to_dict() for c in self.europe],
            "usa": [c.to_dict() for c in self.usa],
            "china": [c.to_dict() for c in self.china],
            "dominant_axis": self.dominant_axis,
            "dormant_axes": self.dormant_axes,
        }


@dataclass(frozen=True)
class SynthesisAxis:
    preserve: str  # норма істини (Європа)
    test: str  # експеримент/наслідок (США)
    evolve: str  # процес/тайминг (Китай)
    refuse: str  # failure mode домінантної осі

    def to_dict(self) -> dict[str, str]:
        return asdict(self)


@dataclass(frozen=True)
class ReversePlan:
    first_missing_condition: str
    blocking_assumption: str
    minimum_viable_intervention: str
    validation_event: str

    def to_dict(self) -> dict[str, str]:
        return asdict(self)
