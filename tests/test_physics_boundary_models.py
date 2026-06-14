"""Cover the typed contract dataclasses' to_dict serialization."""

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


def test_failure_and_check_result_to_dict() -> None:
    f = Failure("CODE", "path.py", "reason", "fix it")
    assert f.to_dict() == {
        "failure_code": "CODE",
        "file_path": "path.py",
        "reason": "reason",
        "required_fix": "fix it",
    }
    cr = CheckResult("name", "PASS", [f])
    d = cr.to_dict()
    assert d["name"] == "name" and d["status"] == "PASS"
    assert d["failures"][0]["failure_code"] == "CODE"


def test_state_variable_to_dict() -> None:
    sv = StateVariable("s", "def", ["a.py"], "S1_TESTED", True, "v", "fm")
    assert sv.to_dict()["status"] == "S1_TESTED"
    assert sv.to_dict()["source_files"] == ["a.py"]


def test_all_contract_objects_roundtrip_to_dict() -> None:
    objects = [
        BoundaryCondition("c1", "stmt", ["x"], "safe", "gate", "high"),
        Invariant("inv", "conserve", "by", "broke", True),
        OperatorContract("op", "in", "do", "out", "loc", "val", "fm", "KEEP"),
        MechanismResidualContract(["m"], ["r"], "rule", ["blocked"]),
        TrajectoryContract(True, True, True, True, True, True, True, True, True),
        MeasurementMetric("m", "d", "method", "thr", "IMPLEMENTED", True),
        VerifierContract("v", "cmd", "checks", True, "PASS"),
        ClaimStatusContract("text", "S5_PROXY", "ev", "allowed", "forbidden", "gate"),
        ReleaseGate("g", "cond", "cmd", "thr", "block"),
    ]
    for obj in objects:
        d = obj.to_dict()
        assert isinstance(d, dict) and d
        # every declared field is serialized
        assert len(d) >= 4
