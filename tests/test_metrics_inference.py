"""Tests for the unified Metrics Inference Report."""

from __future__ import annotations

import json
from pathlib import Path

import jsonschema
import pytest

from noesis.cli import main
from noesis.evaluation.metrics_inference import (
    MetricEntry,
    MetricTier,
    build_metrics_report,
)
from noesis.forbidden import check_forbidden_claims

_ROOT = Path(__file__).resolve().parents[1]
_SCHEMA = json.loads(
    (_ROOT / "schemas" / "metrics_inference_report.schema.json").read_text(encoding="utf-8")
)

_REQUIRED_FIELDS = ("name", "value", "tier", "procedure", "sample_n", "caveat")
_TIER_VALUES = {t.value for t in MetricTier}


def test_metric_entries_have_all_fields() -> None:
    report = build_metrics_report()
    assert report["metrics"]
    for m in report["metrics"]:
        for field in _REQUIRED_FIELDS:
            assert field in m, field
        assert m["tier"] in _TIER_VALUES
        assert isinstance(m["procedure"], str) and m["procedure"].strip()
        assert isinstance(m["name"], str) and m["name"].strip()


def test_metric_entry_to_dict_roundtrip() -> None:
    entry = MetricEntry(
        name="x",
        value=1.0,
        tier=MetricTier.MEASURED,
        procedure="p",
        sample_n=3,
        caveat="",
    )
    d = entry.to_dict()
    assert d == {
        "name": "x",
        "value": 1.0,
        "tier": "MEASURED",
        "procedure": "p",
        "sample_n": 3,
        "caveat": "",
    }


def test_report_is_deterministic() -> None:
    assert build_metrics_report() == build_metrics_report()


def test_tier_counts_match_metrics_and_all_present() -> None:
    report = build_metrics_report()
    tiers = report["tiers"]
    for tier in _TIER_VALUES:
        actual = sum(1 for m in report["metrics"] if m["tier"] == tier)
        assert tiers[tier] == actual
        assert tiers[tier] >= 1


def test_metrics_sorted_by_tier_then_name() -> None:
    report = build_metrics_report()
    keys = [(m["tier"], m["name"]) for m in report["metrics"]]
    assert keys == sorted(keys)


def test_report_validates_against_schema() -> None:
    jsonschema.validate(instance=build_metrics_report(), schema=_SCHEMA)


def test_no_forbidden_claims_in_any_string_field() -> None:
    report = build_metrics_report()
    chunks: list[str] = []
    for m in report["metrics"]:
        chunks += [m["name"], m["procedure"], m["caveat"]]
    chunks.append(report["report"])
    chunks.append(report["report_version"])
    assert check_forbidden_claims(" ".join(chunks)) == []


def test_not_claimed_is_explicit_negative_declaration() -> None:
    report = build_metrics_report()
    assert "AGI" in report["not_claimed"]
    assert "therapy" in report["not_claimed"]


def test_cli_metrics_returns_zero_and_emits_json(capsys: pytest.CaptureFixture[str]) -> None:
    rc = main(["metrics"])
    assert rc == 0
    payload = json.loads(capsys.readouterr().out)
    assert "metrics" in payload
    assert payload["report"] == "metrics_inference"


def test_api_metrics_endpoint() -> None:
    pytest.importorskip("httpx")
    from fastapi.testclient import TestClient

    from app.api import app

    client = TestClient(app)
    for method in ("post", "get"):
        resp = getattr(client, method)("/metrics")
        assert resp.status_code == 200
        body = resp.json()
        assert body["report"] == "metrics_inference"
        assert isinstance(body["metrics"], list) and body["metrics"]
        assert set(body["tiers"]) == _TIER_VALUES
