"""Tests for rollback physics — every invalid discharge is reversible."""

from __future__ import annotations

import json
from pathlib import Path

import jsonschema
import pytest

from noesis.runtime.rollback import (
    ROLLBACK_TYPES,
    RollbackController,
    StateLossError,
    can_release,
    rollback_metrics,
)

_SCHEMA = json.loads(
    (Path(__file__).resolve().parents[1] / "schemas" / "rollback_condition.schema.json").read_text(
        encoding="utf-8"
    )
)


def test_rollback_restores_prior_state() -> None:
    c = RollbackController()
    c.checkpoint("s0", {"v": 0})
    c.discharge("s1", {"v": 1})
    restored = c.trigger("test_failure")
    assert restored.state_id == "s0"
    assert restored.payload == {"v": 0}
    assert c.current is not None and c.current.state_id == "s0"


def test_forbidden_claim_can_trigger_rollback() -> None:
    c = RollbackController()
    c.checkpoint("s0", {"ok": True})
    c.discharge("s1", {"claim": "AGI achieved"})
    restored = c.trigger("forbidden_claim_detected")
    assert restored.state_id == "s0"


def test_unknown_rollback_type_rejected() -> None:
    c = RollbackController()
    c.checkpoint("s0", {})
    c.discharge("s1", {})
    with pytest.raises(ValueError):
        c.trigger("not_a_real_type")


def test_state_loss_when_no_prior_valid() -> None:
    c = RollbackController()
    c.discharge("s1", {"v": 1})  # no checkpoint before it
    with pytest.raises(StateLossError):
        c.trigger("schema_failure")


def test_failed_benchmark_cannot_release() -> None:
    assert can_release(benchmark_passed=False, open_rollbacks=0) is False
    assert can_release(benchmark_passed=True, open_rollbacks=1) is False
    assert can_release(benchmark_passed=True, open_rollbacks=0) is True


def test_all_rollback_types_are_triggerable() -> None:
    for rb in ROLLBACK_TYPES:
        c = RollbackController()
        c.checkpoint("s0", {"v": 0})
        c.discharge("s1", {"v": 1})
        assert c.trigger(rb).state_id == "s0"


def test_metrics_shape_and_rates() -> None:
    events = [
        {"rollback_type": "test_failure", "was_invalid": True, "recovered": True, "state_lost": False},
        {"rollback_type": None, "was_invalid": True, "recovered": False, "state_lost": True},
        {"rollback_type": "schema_failure", "was_invalid": True, "recovered": True, "state_lost": False},
    ]
    m = rollback_metrics(events)
    assert m["rollback_defined_rate"] == pytest.approx(2 / 3, abs=1e-3)
    assert m["rollback_success_rate"] == 1.0
    assert m["invalid_state_recovery_rate"] == pytest.approx(2 / 3, abs=1e-3)
    assert m["state_loss_rate"] == pytest.approx(1 / 3, abs=1e-3)


def test_metrics_empty() -> None:
    assert rollback_metrics([])["rollback_defined_rate"] == 0.0


def test_event_validates_against_schema() -> None:
    event = {
        "rollback_type": "human_rejection",
        "was_invalid": True,
        "recovered": True,
        "state_lost": False,
    }
    jsonschema.validate(instance=event, schema=_SCHEMA)
