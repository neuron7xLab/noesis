"""Tests for the trajectory contract (per-operator stepwise trace fields)."""

from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path
from typing import Any

import jsonschema

from noesis.contracts import physics_boundary_validator as v

_ROOT = v.repo_root()
_TRAJ_SCHEMA = _ROOT / "schemas" / "trajectory_contract.schema.json"
_REQUIRED_FIELD_KEYS = (
    "trace_id_required",
    "state_t",
    "operation_t",
    "decision_t",
    "rollback_condition_t",
    "state_t_plus_1",
)


def _load(path: Path) -> dict[str, Any]:
    data: dict[str, Any] = json.loads(path.read_text(encoding="utf-8"))
    return data


def _report() -> dict[str, Any]:
    return deepcopy(_load(_ROOT / "data" / "physics_boundary_report.json"))


def _write_repo(tmp_path: Path, report: dict[str, Any]) -> Path:
    (tmp_path / "data").mkdir(parents=True, exist_ok=True)
    (tmp_path / "schemas").mkdir(parents=True, exist_ok=True)
    (tmp_path / "schemas" / "physics_boundary_report.schema.json").write_text(
        (_ROOT / "schemas" / "physics_boundary_report.schema.json").read_text(encoding="utf-8"),
        encoding="utf-8",
    )
    (tmp_path / "data" / "physics_boundary_report.json").write_text(
        json.dumps(report, ensure_ascii=False), encoding="utf-8"
    )
    return tmp_path


def test_trajectory_checked_has_all_required_keys() -> None:
    traj = v.build_contract(_ROOT)["trajectory_checked"]
    for key in _REQUIRED_FIELD_KEYS:
        assert key in traj


def test_trajectory_checked_validates_against_schema() -> None:
    traj = v.build_contract(_ROOT)["trajectory_checked"]
    jsonschema.validate(instance=traj, schema=_load(_TRAJ_SCHEMA))


def test_trace_id_is_required() -> None:
    traj = v.build_contract(_ROOT)["trajectory_checked"]
    assert traj["trace_id_required"] is True


def test_current_tree_trajectory_now_complete() -> None:
    # Role 3 implemented the per-operator trace; the report declares FULL support.
    result, fields = v.check_trajectory(_ROOT, _report())
    assert result.status == "PASS"
    assert fields["rollback_condition_t"] is True
    assert fields["state_t_plus_1"] is True
    assert result.failures == []


def test_missing_trajectory_fields_fail_validation(tmp_path: Path) -> None:
    # A regressed report (fields dropped) must hard-fail the trajectory gate.
    report = _report()
    report["trajectory_model"]["current_trace_support"] = "PARTIAL"
    report["trajectory_model"]["missing_trace_fields"] = ["rollback_condition_t", "state_t_plus_1"]
    root = _write_repo(tmp_path, report)
    result, fields = v.check_trajectory(root, report)
    assert result.status == "FAIL"
    assert fields["rollback_condition_t"] is False
    assert fields["state_t_plus_1"] is False
    codes = {f.failure_code for f in result.failures}
    assert codes == {"TRAJECTORY_FIELD_ABSENT"}


def test_full_trace_passes_all_fields(tmp_path: Path) -> None:
    report = _report()
    report["trajectory_model"]["current_trace_support"] = "FULL"
    report["trajectory_model"]["missing_trace_fields"] = []
    root = _write_repo(tmp_path, report)
    result, fields = v.check_trajectory(root, _load(root / "data" / "physics_boundary_report.json"))
    assert result.status == "PASS"
    assert all(fields[f] for f in v.REQUIRED_TRAJECTORY_FIELDS)


def test_absent_trace_marks_all_fields_missing(tmp_path: Path) -> None:
    report = _report()
    report["trajectory_model"]["current_trace_support"] = "ABSENT"
    root = _write_repo(tmp_path, report)
    result, fields = v.check_trajectory(root, _load(root / "data" / "physics_boundary_report.json"))
    assert result.status == "FAIL"
    assert not any(fields[f] for f in v.REQUIRED_TRAJECTORY_FIELDS)
