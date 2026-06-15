"""Physics-boundary contract validator (Role 2 enforcement core).

Reads the Role 1 audit (``data/physics_boundary_report.json``), enforces the ten
contract objects, and emits ``data/physics_boundary_contract.json``. Fails
automatically (hard gate) when the repository violates the boundary — e.g. an
operator marked KEEP without a validator, an unblocked forbidden claim, or absent
trajectory fields. No silent failure: every violation is a structured ``Failure``.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import jsonschema

from noesis.contracts.physics_boundary import (
    FORBIDDEN_CLAIMS,
    METRIC_STATUSES,
    OPERATOR_DECISIONS,
    REQUIRED_STATE_VARIABLES,
    REQUIRED_TRAJECTORY_FIELDS,
    STATE_STATUSES,
    CheckResult,
    Failure,
)

CONTRACT_VERSION = "1.0"

# category -> max points (sum = 100)
_SCORE_WEIGHTS: dict[str, int] = {
    "state_contract": 10,
    "boundary_contract": 10,
    "invariant_contract": 10,
    "operator_contract": 15,
    "mechanism_residual_contract": 10,
    "trajectory_contract": 10,
    "measurement_contract": 10,
    "verification_contract": 10,
    "claim_status_contract": 10,
    "role_3_handoff_contract": 5,
}


def repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _report_path(root: Path) -> Path:
    return root / "data" / "physics_boundary_report.json"


def _report_schema_path(root: Path) -> Path:
    return root / "schemas" / "physics_boundary_report.schema.json"


def contract_path(root: Path) -> Path:
    return root / "data" / "physics_boundary_contract.json"


def _load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _present(value: object) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _rel(root: Path, path: Path) -> str:
    try:
        return path.resolve().relative_to(root.resolve()).as_posix()
    except ValueError:
        return str(path)


# ── individual checks ─────────────────────────────────────────────────────────


def check_report_schema(root: Path, report: dict[str, Any]) -> CheckResult:
    schema_file = _report_schema_path(root)
    if not schema_file.exists():
        return CheckResult(
            "report_schema",
            "MISSING",
            [
                Failure(
                    "REPORT_SCHEMA_MISSING",
                    _rel(root, schema_file),
                    "Role 1 report schema is absent",
                    "restore schemas/physics_boundary_report.schema.json",
                )
            ],
        )
    try:
        jsonschema.validate(instance=report, schema=_load_json(schema_file))
    except jsonschema.ValidationError as exc:
        return CheckResult(
            "report_schema",
            "FAIL",
            [
                Failure(
                    "REPORT_SCHEMA_INVALID",
                    _rel(root, _report_path(root)),
                    f"report does not match schema: {exc.message}",
                    "fix the Role 1 report to satisfy the schema",
                )
            ],
        )
    return CheckResult("report_schema", "PASS")


def check_state_variables(root: Path, report: dict[str, Any]) -> CheckResult:
    variables = report["state_model"]["state_variables"]
    names = {v["name"] for v in variables}
    failures: list[Failure] = []
    for required in REQUIRED_STATE_VARIABLES:
        if required not in names:
            failures.append(
                Failure(
                    "STATE_VARIABLE_MISSING",
                    _rel(root, _report_path(root)),
                    f"required state variable absent: {required}",
                    f"declare state variable {required} with repo evidence",
                )
            )
    for var in variables:
        if var["status"] not in STATE_STATUSES:
            failures.append(
                Failure(
                    "STATE_STATUS_INVALID",
                    _rel(root, _report_path(root)),
                    f"{var['name']} has invalid status {var['status']}",
                    f"use one of {sorted(STATE_STATUSES)}",
                )
            )
    return CheckResult("state", "FAIL" if failures else "PASS", failures)


def check_operators(root: Path, report: dict[str, Any]) -> CheckResult:
    failures: list[Failure] = []
    for op in report["operator_map"]:
        name = op.get("operator_name", "<unnamed>")
        for field_name in ("input_state", "operation", "output_state"):
            if not _present(op.get(field_name)):
                failures.append(
                    Failure(
                        "OPERATOR_FIELD_MISSING",
                        _rel(root, _report_path(root)),
                        f"operator {name} missing {field_name}",
                        f"declare {field_name} for {name}",
                    )
                )
        decision = op.get("decision", "")
        if decision not in OPERATOR_DECISIONS:
            failures.append(
                Failure(
                    "OPERATOR_DECISION_INVALID",
                    _rel(root, _report_path(root)),
                    f"operator {name} has invalid decision {decision}",
                    f"use one of {sorted(OPERATOR_DECISIONS)}",
                )
            )
        has_validator = _present(op.get("validator")) and "MISSING" not in op.get("validator", "")
        if not has_validator and decision not in {"MODIFY", "CREATE"}:
            failures.append(
                Failure(
                    "OPERATOR_NO_VALIDATOR",
                    _rel(root, _report_path(root)),
                    f"operator {name} has no validator but decision is {decision}",
                    "add a validator or set decision to MODIFY/CREATE",
                )
            )
        has_location = _present(op.get("repo_location")) and "ABSENT" not in op.get(
            "repo_location", ""
        )
        if not has_location and decision == "KEEP":
            failures.append(
                Failure(
                    "OPERATOR_KEEP_NO_LOCATION",
                    _rel(root, _report_path(root)),
                    f"operator {name} is KEEP but has no repo_location",
                    "set decision to CREATE or add repo_location",
                )
            )
    return CheckResult("operator", "FAIL" if failures else "PASS", failures)


def check_trajectory(root: Path, report: dict[str, Any]) -> tuple[CheckResult, dict[str, bool]]:
    model = report["trajectory_model"]
    missing_raw = model.get("missing_trace_fields", [])
    support = model.get("current_trace_support", "ABSENT")

    def implemented(field_name: str) -> bool:
        if support == "ABSENT":
            return False
        for entry in missing_raw:
            if entry == field_name or entry.startswith(field_name + " "):
                return False
        return True

    fields: dict[str, bool] = {f: implemented(f) for f in REQUIRED_TRAJECTORY_FIELDS}
    fields["trace_id_required"] = True
    failures: list[Failure] = []
    for field_name in REQUIRED_TRAJECTORY_FIELDS:
        if not fields[field_name]:
            failures.append(
                Failure(
                    "TRAJECTORY_FIELD_ABSENT",
                    _rel(root, _report_path(root)),
                    f"trajectory field not implemented: {field_name}",
                    f"persist {field_name} in a per-operator trajectory trace",
                )
            )
    status = "FAIL" if failures else "PASS"
    return CheckResult("trajectory", status, failures), fields


def check_metrics(root: Path, report: dict[str, Any]) -> CheckResult:
    failures: list[Failure] = []
    for metric in report["measurement_model"]["metrics"]:
        name = metric.get("metric_name", "<unnamed>")
        status = metric.get("status", "")
        if status not in METRIC_STATUSES:
            failures.append(
                Failure(
                    "METRIC_STATUS_INVALID",
                    _rel(root, _report_path(root)),
                    f"metric {name} has invalid status {status}",
                    f"use one of {sorted(METRIC_STATUSES)}",
                )
            )
        has_threshold = _present(metric.get("threshold")) and metric.get("threshold") != "n/a"
        if not has_threshold and status == "IMPLEMENTED":
            failures.append(
                Failure(
                    "METRIC_NO_THRESHOLD",
                    _rel(root, _report_path(root)),
                    f"IMPLEMENTED metric {name} has no threshold",
                    "add a threshold or tag the metric PROXY/MISSING",
                )
            )
    return CheckResult("measurement", "FAIL" if failures else "PASS", failures)


def check_verifiers(root: Path, report: dict[str, Any]) -> CheckResult:
    failures: list[Failure] = []
    for ver in report["verification_model"]["verifiers"]:
        if not _present(ver.get("command_or_file")):
            failures.append(
                Failure(
                    "VERIFIER_NO_COMMAND",
                    _rel(root, _report_path(root)),
                    f"verifier {ver.get('verifier_name')} has no command_or_file",
                    "add a command or file check",
                )
            )
    return CheckResult("verification", "FAIL" if failures else "PASS", failures)


def check_forbidden_claims(root: Path, report: dict[str, Any]) -> CheckResult:
    failures: list[Failure] = []
    detected = report["claim_audit"].get("forbidden_claims_detected", [])
    for claim in detected:
        failures.append(
            Failure(
                "FORBIDDEN_CLAIM_UNBLOCKED",
                _rel(root, _report_path(root)),
                f"forbidden claim present and unblocked: {claim}",
                "remove the claim or route it through the forbidden gate",
            )
        )
    return CheckResult("forbidden_claims", "FAIL" if failures else "PASS", failures)


# ── contract object builders (Role 1 -> contract rows) ────────────────────────


def _claim_rows(report: dict[str, Any]) -> list[dict[str, Any]]:
    audit = report["claim_audit"]
    rows: list[dict[str, Any]] = []
    for text in audit.get("proxy_claims", []):
        rows.append(
            {
                "claim_text": text,
                "claim_status": "S5_PROXY",
                "source_or_repo_evidence": "VERDICT.md / docs/THEORIES.md",
                "allowed_wording": "operational proxy metric (proxy, not measurement)",
                "forbidden_wording": "physical measurement",
                "gate": "Gate 8 (proxy honesty)",
            }
        )
    for text in audit.get("unsupported_claims", []):
        rows.append(
            {
                "claim_text": text,
                "claim_status": "UNSUPPORTED",
                "source_or_repo_evidence": "self-flagged in VERDICT.md",
                "allowed_wording": "not yet demonstrated",
                "forbidden_wording": "validated",
                "gate": "release_blocked",
            }
        )
    for text in audit.get("speculative_claims", []):
        rows.append(
            {
                "claim_text": text,
                "claim_status": "S6_SPECULATIVE",
                "source_or_repo_evidence": "force-tagged speculative (Gate 8)",
                "allowed_wording": "speculative engineering extrapolation",
                "forbidden_wording": "observed",
                "gate": "Gate 8",
            }
        )
    for needle, replacement in FORBIDDEN_CLAIMS:
        rows.append(
            {
                "claim_text": f"<forbidden pattern> {needle}",
                "claim_status": "X_FORBIDDEN",
                "source_or_repo_evidence": "noesis/forbidden.py detector",
                "allowed_wording": replacement,
                "forbidden_wording": needle,
                "gate": "forbidden_gate",
            }
        )
    return rows


def _release_gates() -> list[dict[str, str]]:
    return [
        {
            "gate_name": "tests",
            "condition": "all tests pass with >=90% coverage",
            "command": "python -m pytest -q",
            "pass_threshold": "exit 0, coverage>=90%",
            "fail_action": "block release",
        },
        {
            "gate_name": "lint_types",
            "condition": "ruff + mypy --strict clean",
            "command": "ruff check . && mypy",
            "pass_threshold": "exit 0",
            "fail_action": "block release",
        },
        {
            "gate_name": "forbidden_claims",
            "condition": "no unblocked forbidden claim",
            "command": "python -m noesis.cli bibliography validate",
            "pass_threshold": "exit 0",
            "fail_action": "block release",
        },
        {
            "gate_name": "unsupported_claims",
            "condition": "UNSUPPORTED claims cannot pass release",
            "command": "python -m noesis.contracts.physics_boundary_cli validate",
            "pass_threshold": "no UNSUPPORTED claim asserted as validated",
            "fail_action": "block release",
        },
        {
            "gate_name": "trajectory_trace",
            "condition": "per-operator trajectory trace implemented",
            "command": "python -m noesis.contracts.physics_boundary_cli validate",
            "pass_threshold": "all trajectory fields implemented",
            "fail_action": "hand off to Role 3",
        },
    ]


def _blocked_promotion_conditions() -> list[str]:
    return [
        "LLM/residual output without a passing deterministic gate",
        "LLM/residual output without a schema-valid artifact",
        "literature claim without a bibliographic source edge",
        "proxy metric reported as a physical measurement",
    ]


def _role3_handoff(first_failing_gate: str) -> dict[str, Any]:
    mapping: dict[str, dict[str, Any]] = {
        "operator": {
            "role_name": "OPERATOR IMPLEMENTATION AGENT",
            "task": "Give every KEEP operator a real validator and repo_location.",
            "files_to_create": ["tests/test_operator_validators.py"],
            "files_to_modify": ["noesis/cli.py"],
        },
        "trajectory": {
            "role_name": "TRAJECTORY TRACE IMPLEMENTER",
            "task": "Persist a per-operator trajectory trace (score_t, decision_t, "
            "rollback_condition_t, state_t->state_t+1) into the Evidence Bundle.",
            "files_to_create": [
                "schemas/trajectory_trace.schema.json",
                "noesis/trajectory.py",
                "tests/test_trajectory_trace.py",
            ],
            "files_to_modify": ["noesis/pipeline_core.py", "noesis/evidence.py", "noesis/cli.py"],
        },
        "claim_status": {
            "role_name": "CLAIM GOVERNANCE GATE IMPLEMENTER",
            "task": "Block unsupported/forbidden claims at a deterministic gate.",
            "files_to_create": ["tests/test_claim_gate.py"],
            "files_to_modify": ["noesis/forbidden.py"],
        },
        "measurement": {
            "role_name": "METRIC INSTRUMENTATION AGENT",
            "task": "Implement thresholds for IMPLEMENTED metrics.",
            "files_to_create": ["tests/test_metric_thresholds.py"],
            "files_to_modify": ["noesis/pipeline_core.py"],
        },
        "verification": {
            "role_name": "VERIFIER HARNESS IMPLEMENTER",
            "task": "Give every verifier an executable command or file check.",
            "files_to_create": ["tests/test_verifier_harness.py"],
            "files_to_modify": ["noesis/cli.py"],
        },
        "none": {
            "role_name": "BENCHMARK + ABLATION AGENT",
            "task": "Run benchmark + ablation to separate structural consistency "
            "from usefulness.",
            "files_to_create": ["tests/test_benchmark_ablation.py"],
            "files_to_modify": ["noesis/benchmark.py"],
        },
    }
    chosen = mapping.get(first_failing_gate, mapping["none"])
    chosen["validation_commands"] = [
        "python -m pytest -q",
        "ruff check .",
        "python -m noesis.contracts.physics_boundary_cli validate",
    ]
    chosen["pass_fail_criteria"] = [
        "python -m noesis.contracts.physics_boundary_cli validate exits 0",
        "contract_status == PASS and no hard failures",
        "pytest + ruff + mypy green and coverage >=90%",
    ]
    return chosen


# ── top-level build ───────────────────────────────────────────────────────────


def build_contract(root: Path | None = None) -> dict[str, Any]:
    root = root or repo_root()
    report_file = _report_path(root)
    if not report_file.exists():
        return {
            "contract_version": CONTRACT_VERSION,
            "contract_status": "FAIL",
            "state_variables_checked": [],
            "boundary_conditions_checked": [],
            "invariants_checked": [],
            "operators_checked": [],
            "mechanism_residual_checked": {},
            "trajectory_checked": {},
            "metrics_checked": [],
            "verifiers_checked": [],
            "claim_status_checked": [],
            "release_gates_checked": _release_gates(),
            "score": 0,
            "score_breakdown": {},
            "hard_failures": ["REPORT_MISSING"],
            "failures": [
                Failure(
                    "REPORT_MISSING",
                    _rel(root, report_file),
                    "Role 1 physics boundary report is absent",
                    "run Role 1 to produce data/physics_boundary_report.json",
                ).to_dict()
            ],
            "role_3_handoff": {
                "role_name": "FIRST_PRINCIPLES_PHYSICS_AUDITOR (re-run Role 1)",
                "task": "Regenerate the Role 1 physics boundary report.",
                "files_to_create": ["data/physics_boundary_report.json"],
                "files_to_modify": [],
                "validation_commands": ["python -m noesis.contracts.physics_boundary_cli validate"],
                "pass_fail_criteria": ["data/physics_boundary_report.json exists and is schema-valid"],
            },
        }

    report: dict[str, Any] = _load_json(report_file)

    schema_check = check_report_schema(root, report)
    state_check = check_state_variables(root, report)
    operator_check = check_operators(root, report)
    trajectory_check, trajectory_fields = check_trajectory(root, report)
    metric_check = check_metrics(root, report)
    verifier_check = check_verifiers(root, report)
    forbidden_check = check_forbidden_claims(root, report)

    invariants = report["invariants"]
    invariant_status = "PASS" if invariants else "FAIL"
    residual = report["mechanism_residual_split"]
    residual_status = "PASS" if _present(residual.get("promotion_rule")) else "FAIL"
    boundary_status = "PASS" if report["constraints"]["boundary_conditions"] else "FAIL"
    claim_rows = _claim_rows(report)
    claim_status = forbidden_check.status

    # scoring: full weight when the category check passes; trajectory is scored by
    # the fraction of implemented fields (it is the binding gap on the current tree).
    present_traj = sum(1 for f in REQUIRED_TRAJECTORY_FIELDS if trajectory_fields[f])
    score_breakdown: dict[str, int] = {
        "state_contract": _SCORE_WEIGHTS["state_contract"] if state_check.status == "PASS" else 0,
        "boundary_contract": _SCORE_WEIGHTS["boundary_contract"] if boundary_status == "PASS" else 0,
        "invariant_contract": (
            _SCORE_WEIGHTS["invariant_contract"] if invariant_status == "PASS" else 0
        ),
        "operator_contract": (
            _SCORE_WEIGHTS["operator_contract"] if operator_check.status == "PASS" else 0
        ),
        "mechanism_residual_contract": (
            _SCORE_WEIGHTS["mechanism_residual_contract"] if residual_status == "PASS" else 0
        ),
        "trajectory_contract": int(
            _SCORE_WEIGHTS["trajectory_contract"] * present_traj / len(REQUIRED_TRAJECTORY_FIELDS)
        ),
        "measurement_contract": (
            _SCORE_WEIGHTS["measurement_contract"] if metric_check.status == "PASS" else 0
        ),
        "verification_contract": (
            _SCORE_WEIGHTS["verification_contract"] if verifier_check.status == "PASS" else 0
        ),
        "claim_status_contract": (
            _SCORE_WEIGHTS["claim_status_contract"] if claim_status == "PASS" else 0
        ),
        "role_3_handoff_contract": _SCORE_WEIGHTS["role_3_handoff_contract"],
    }
    total_score = sum(score_breakdown.values())

    all_checks = [
        schema_check,
        state_check,
        operator_check,
        trajectory_check,
        metric_check,
        verifier_check,
        forbidden_check,
    ]
    failures = [f.to_dict() for c in all_checks for f in c.failures]

    # hard-fail gates, in priority order; first failure picks the Role 3 handoff.
    hard_failures: list[str] = []
    first_failing_gate = "none"
    hard_gate_order: list[tuple[str, str, str]] = [
        ("report_schema", schema_check.status, "claim_status"),
        ("forbidden_claims", forbidden_check.status, "claim_status"),
        ("operator", operator_check.status, "operator"),
        ("trajectory", trajectory_check.status, "trajectory"),
        ("measurement", metric_check.status, "measurement"),
        ("verification", verifier_check.status, "verification"),
    ]
    for gate_name, status, role in hard_gate_order:
        if status not in {"PASS"}:
            hard_failures.append(gate_name)
            if first_failing_gate == "none":
                first_failing_gate = role

    contract_status = "FAIL" if (hard_failures or total_score < 80) else "PASS"

    return {
        "contract_version": CONTRACT_VERSION,
        "contract_status": contract_status,
        "state_variables_checked": [
            {
                "name": v["name"],
                "status": v["status"],
                "required": v["name"] in REQUIRED_STATE_VARIABLES,
            }
            for v in report["state_model"]["state_variables"]
        ],
        "boundary_conditions_checked": report["constraints"]["boundary_conditions"],
        "invariants_checked": [i["name"] for i in invariants],
        "operators_checked": [
            {
                "operator_name": op["operator_name"],
                "decision": op["decision"],
                "has_validator": _present(op.get("validator"))
                and "MISSING" not in op.get("validator", ""),
            }
            for op in report["operator_map"]
        ],
        "mechanism_residual_checked": {
            "promotion_rule": residual.get("promotion_rule", ""),
            "blocked_promotion_conditions": _blocked_promotion_conditions(),
            "status": residual_status,
        },
        "trajectory_checked": {
            "trace_id_required": True,
            **{f: trajectory_fields[f] for f in REQUIRED_TRAJECTORY_FIELDS},
            "status": trajectory_check.status,
        },
        "metrics_checked": [
            {"metric_name": m["metric_name"], "status": m["status"], "threshold": m["threshold"]}
            for m in report["measurement_model"]["metrics"]
        ],
        "verifiers_checked": [
            {"verifier_name": v["verifier_name"], "current_status": v["current_status"]}
            for v in report["verification_model"]["verifiers"]
        ],
        "claim_status_checked": claim_rows,
        "release_gates_checked": _release_gates(),
        "score": total_score,
        "score_breakdown": score_breakdown,
        "hard_failures": hard_failures,
        "failures": failures,
        "role_3_handoff": _role3_handoff(first_failing_gate),
    }


def write_contract(root: Path | None = None) -> dict[str, Any]:
    root = root or repo_root()
    contract = build_contract(root)
    out = contract_path(root)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(contract, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return contract
