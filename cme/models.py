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
