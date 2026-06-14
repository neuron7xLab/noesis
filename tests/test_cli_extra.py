"""Cover cli.py --evidence branches, bibliography subcommands, verdict v0.5 fallback."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from noesis.cli import main

EXAMPLE = "examples/problems/08_ai_system_design.txt"


@pytest.mark.parametrize("cmd", ["pipeline", "ablate", "graph", "neuro", "eiic", "pipeline-v7", "pipeline-v8"])
def test_evidence_branch_writes_bundle(cmd: str, tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    out = tmp_path / cmd
    rc = main([cmd, EXAMPLE, "--evidence", str(out)])
    capsys.readouterr()
    assert rc in (0, 1)
    assert out.exists() and any(out.iterdir())
    assert (out / "manifest.json").exists()


@pytest.mark.parametrize("sub", ["scan", "ledger", "missing", "graph", "export-bibtex"])
def test_bibliography_subcommands(sub: str, capsys: pytest.CaptureFixture[str]) -> None:
    rc = main(["bibliography", sub])
    out = capsys.readouterr().out
    assert rc == 0
    assert out.strip()


def test_verdict_v05_fallback(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    # bundle with manifest.json but no verdict.md -> read_verdict + render_verdict_md path
    (tmp_path / "manifest.json").write_text(
        json.dumps(
            {
                "run_id": "r1",
                "pipeline_version": "0.5",
                "overall_status": "PASS",
                "deterministic_modules": ["mirror"],
                "llm_modules": [],
            }
        ),
        encoding="utf-8",
    )
    (tmp_path / "validation.json").write_text(
        json.dumps(
            {
                "gates": {"checks": [{"name": "g1", "passed": True}]},
                "claim_governance": {"observed": 1},
                "baseline": {},
            }
        ),
        encoding="utf-8",
    )
    rc = main(["verdict", str(tmp_path)])
    out = capsys.readouterr().out
    assert rc == 0
    assert "VERDICT" in out and "r1" in out
