"""Tests for the feedback harness — proxy -> anchored measurement."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import jsonschema
import pytest

from noesis.cli import main
from noesis.feedback import (
    MIN_PAIRS,
    LabeledPair,
    calibrate,
    ingest,
    load_pairs,
)

_ROOT = Path(__file__).resolve().parents[1]
_SCHEMA = json.loads(
    (_ROOT / "schemas" / "feedback_calibration.schema.json").read_text(encoding="utf-8")
)
_EXAMPLE = _ROOT / "data" / "feedback_pairs.example.json"


def _pair(verdict: str, score: float, i: int = 0, hrv: float | None = None) -> LabeledPair:
    return LabeledPair(f"p{i}", f"h{i}", f"a{i}.json", verdict, score, hrv, "test")


def _many(n: int, verdict: str = "works", score: float = 0.7) -> list[LabeledPair]:
    return [_pair(verdict if i % 2 == 0 else "fails", score, i) for i in range(n)]


def test_insufficient_data_is_fail_closed() -> None:
    report = calibrate(_many(MIN_PAIRS - 1))
    assert report["status"] == "INSUFFICIENT_DATA"
    assert report["anchored_quality"] is None
    assert report["verdict"] == "INSUFFICIENT_DATA"


def test_calibrated_aligned() -> None:
    pairs = [_pair("works", 0.7, i) for i in range(7)] + [_pair("fails", 0.35, i) for i in range(7)]
    report = calibrate(pairs)
    assert report["status"] == "CALIBRATED"
    assert report["verdict"] == "ALIGNED"
    assert report["anchored_quality"] == 0.5
    assert report["proxy_reality_alignment"] is not None


def test_proxy_overclaim_detected() -> None:
    # proxy says ~0.9 everywhere, but reality is mostly failure -> overclaim
    pairs = [_pair("fails", 0.9, i) for i in range(10)] + [_pair("works", 0.95, i) for i in range(4)]
    report = calibrate(pairs)
    assert report["status"] == "CALIBRATED"
    assert report["verdict"] == "PROXY_OVERCLAIMS"
    assert report["calibration_gap"] > 0


def test_degenerate_alignment_is_none() -> None:
    # all "works" -> reward variance zero -> alignment undefined
    report = calibrate([_pair("works", 0.5 + i * 0.01, i) for i in range(MIN_PAIRS)])
    assert report["proxy_reality_alignment"] is None


def test_bad_verdict_rejected() -> None:
    with pytest.raises(ValueError):
        load_pairs({"pairs": [{"pair_id": "x", "input_hash": "h", "artifact_ref": "a",
                               "human_verdict": "maybe", "proxy_score": 0.5}]})


def test_bad_score_rejected() -> None:
    with pytest.raises(ValueError):
        load_pairs({"pairs": [{"pair_id": "x", "input_hash": "h", "artifact_ref": "a",
                               "human_verdict": "works", "proxy_score": 1.5}]})


def test_hrv_coverage_counts() -> None:
    pairs = [_pair("works", 0.7, i, hrv=60.0) for i in range(6)] + [
        _pair("fails", 0.3, i) for i in range(6)
    ]
    report = calibrate(pairs)
    assert report["hrv_coverage"] == 0.5


def test_ingest_validates_against_schema() -> None:
    payload = {"pairs": [_pair("works" if i % 2 else "fails", 0.6, i).to_dict() for i in range(MIN_PAIRS)]}
    report = ingest(payload)
    jsonschema.validate(instance=report, schema=_SCHEMA)


def test_example_is_calibrated_and_synthetic() -> None:
    payload = json.loads(_EXAMPLE.read_text(encoding="utf-8"))
    report = ingest(payload)
    jsonschema.validate(instance=report, schema=_SCHEMA)
    assert report["status"] == "CALIBRATED"
    assert report["provenance"] == ["synthetic_fixture"]


def test_cli_ingest_then_status(tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
                               capsys: pytest.CaptureFixture[str]) -> None:
    monkeypatch.chdir(tmp_path)
    pairs_file = tmp_path / "pairs.json"
    payload: dict[str, Any] = {
        "pairs": [_pair("works" if i % 2 else "fails", 0.6, i).to_dict() for i in range(MIN_PAIRS)]
    }
    pairs_file.write_text(json.dumps(payload), encoding="utf-8")

    rc = main(["feedback", "ingest", str(pairs_file)])
    out = json.loads(capsys.readouterr().out)
    assert rc == 0
    assert out["status"] == "CALIBRATED"
    assert (tmp_path / "data" / "feedback_calibration.json").exists()

    rc2 = main(["feedback", "status"])
    out2 = json.loads(capsys.readouterr().out)
    assert rc2 == 0
    assert out2["status"] == "CALIBRATED"


def test_cli_status_without_report_is_fail_closed(tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
                                                  capsys: pytest.CaptureFixture[str]) -> None:
    monkeypatch.chdir(tmp_path)
    rc = main(["feedback", "status"])
    out = json.loads(capsys.readouterr().out)
    assert rc == 1
    assert out["status"] == "INSUFFICIENT_DATA"
