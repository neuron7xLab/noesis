"""Executable physics-boundary contract layer (Role 2).

Converts the Role 1 physics boundary audit (``data/physics_boundary_report.json``)
into machine-verifiable repository contracts: typed contract objects, a validator
that returns PASS/FAIL/MISSING/UNKNOWN with structured failures, and a release
gate. The layer fails automatically when the repository violates the boundary.
"""

from __future__ import annotations

from noesis.contracts.physics_boundary import (
    BoundaryCondition,
    CheckResult,
    ClaimStatusContract,
    Failure,
    Invariant,
    MeasurementMetric,
    MechanismResidualContract,
    OperatorContract,
    ReleaseGate,
    StateVariable,
    TrajectoryContract,
    VerifierContract,
)

__all__ = [
    "BoundaryCondition",
    "CheckResult",
    "ClaimStatusContract",
    "Failure",
    "Invariant",
    "MeasurementMetric",
    "MechanismResidualContract",
    "OperatorContract",
    "ReleaseGate",
    "StateVariable",
    "TrajectoryContract",
    "VerifierContract",
]
