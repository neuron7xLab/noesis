"""Typed physics-boundary contract objects + governance constants.

Dataclasses (matching the repo idiom in ``noesis/models.py``) plus the canonical
constant sets the validator enforces. No Pydantic: the project validates JSON with
``jsonschema`` and models data with frozen dataclasses, so the contract layer does
the same to stay dependency-light and mypy --strict clean.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any

# ── Status / decision vocabularies ────────────────────────────────────────────

STATE_STATUSES: frozenset[str] = frozenset(
    {
        "S0_REPO_FACT",
        "S1_TESTED",
        "S2_LITERATURE",
        "S5_PROXY",
        "S6_SPECULATIVE",
        "UNSUPPORTED",
        "X_FORBIDDEN",
    }
)
OPERATOR_DECISIONS: frozenset[str] = frozenset({"KEEP", "MODIFY", "REMOVE", "CREATE"})
METRIC_STATUSES: frozenset[str] = frozenset({"IMPLEMENTED", "MISSING", "PROXY"})
VERIFIER_STATUSES: frozenset[str] = frozenset({"PASS", "FAIL", "MISSING", "UNKNOWN"})
CHECK_STATUSES: frozenset[str] = frozenset({"PASS", "FAIL", "MISSING", "UNKNOWN"})

# ── Canonical enforcement constants ───────────────────────────────────────────

REQUIRED_STATE_VARIABLES: tuple[str, ...] = (
    "intent_state",
    "context_state",
    "candidate_state",
    "claim_state",
    "evidence_state",
    "gate_state",
    "artifact_state",
    "verification_state",
    "release_state",
)

REQUIRED_TRAJECTORY_FIELDS: tuple[str, ...] = (
    "trace_id",
    "state_t",
    "operation_t",
    "candidate_t",
    "score_t",
    "decision_t",
    "artifact_delta_t",
    "rollback_condition_t",
    "state_t_plus_1",
)

# Forbidden claim -> safe research-software replacement (governance law).
FORBIDDEN_CLAIMS: tuple[tuple[str, str], ...] = (
    ("is agi", "CME/Noesis is research software, not AGI"),
    ("artificial general intelligence", "research software, not AGI"),
    ("detects consciousness", "no consciousness detection; forbidden by Gate"),
    ("measures consciousness", "no consciousness measurement; forbidden by Gate"),
    ("measures brain bandwidth", "uses an operational IEV proxy, not brain measurement"),
    ("proves gnwt", "uses GNWT as an operational analogy, not biological proof"),
    ("performs therapy", "not therapy; preserves human responsibility"),
    ("diagnoses", "no diagnosis; preserves human responsibility"),
    ("spacex", "physics-grade engineering principles methodologically, gated by tests"),
    ("xai quality", "physics-grade engineering principles methodologically, gated by tests"),
    ("llm judge is final", "high-stakes claims require deterministic or human gates"),
    ("proxy metric is physical measurement", "proxy metrics are labelled proxy, not measurement"),
    ("more agents automatically", "more agents do not automatically improve cognition"),
)

ALLOWED_REPLACEMENTS: tuple[str, ...] = (
    "research software",
    "operational proxy metrics",
    "physics-grade engineering principles methodologically",
    "preserves human responsibility",
    "externalizes candidate generation and partial verification",
    "deterministic or human gates for high-stakes claims",
)


# ── Structured result types ───────────────────────────────────────────────────


@dataclass(frozen=True)
class Failure:
    """A single contract violation. No silent failure: every field is mandatory."""

    failure_code: str
    file_path: str
    reason: str
    required_fix: str

    def to_dict(self) -> dict[str, str]:
        return asdict(self)


@dataclass(frozen=True)
class CheckResult:
    """Outcome of one contract check: status in {PASS, FAIL, MISSING, UNKNOWN}."""

    name: str
    status: str
    failures: list[Failure] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "status": self.status,
            "failures": [f.to_dict() for f in self.failures],
        }


# ── Contract objects (Role 1 -> machine-verifiable) ───────────────────────────


@dataclass(frozen=True)
class StateVariable:
    name: str
    definition: str
    source_files: list[str]
    status: str
    required: bool
    validator: str
    failure_mode: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class BoundaryCondition:
    condition_id: str
    statement: str
    blocked_claims: list[str]
    safe_replacement: str
    gate: str
    severity: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class Invariant:
    name: str
    must_conserve: str
    checked_by: str
    failure_if_broken: str
    required: bool

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class OperatorContract:
    operator_name: str
    input_state: str
    operation: str
    output_state: str
    repo_location: str
    validator: str
    failure_mode: str
    decision: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class MechanismResidualContract:
    deterministic_mechanisms: list[str]
    llm_residual_spaces: list[str]
    promotion_rule: str
    blocked_promotion_conditions: list[str]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class TrajectoryContract:
    trace_id_required: bool
    state_t: bool
    operation_t: bool
    candidate_t: bool
    score_t: bool
    decision_t: bool
    artifact_delta_t: bool
    rollback_condition_t: bool
    state_t_plus_1: bool

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class MeasurementMetric:
    metric_name: str
    definition: str
    measurement_method: str
    threshold: str
    status: str
    required: bool

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class VerifierContract:
    verifier_name: str
    command_or_file: str
    checks: str
    required: bool
    current_status: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class ClaimStatusContract:
    claim_text: str
    claim_status: str
    source_or_repo_evidence: str
    allowed_wording: str
    forbidden_wording: str
    gate: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class ReleaseGate:
    gate_name: str
    condition: str
    command: str
    pass_threshold: str
    fail_action: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
