"""`noesis verdict out/` — читає Evidence Bundle і виносить чесний вердикт по гейтах."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def read_verdict(out_dir: Path) -> dict[str, Any]:
    manifest = json.loads((out_dir / "manifest.json").read_text(encoding="utf-8"))
    validation = json.loads((out_dir / "validation.json").read_text(encoding="utf-8"))
    gates = validation.get("gates", {}).get("checks", [])
    return {
        "run_id": manifest.get("run_id"),
        "pipeline_version": manifest.get("pipeline_version"),
        "overall_status": manifest.get("overall_status"),
        "gates_passed": sum(1 for g in gates if g.get("passed")),
        "gates_total": len(gates),
        "gates_failed": [g["name"] for g in gates if not g.get("passed")],
        "claim_governance": validation.get("claim_governance", {}),
        "baseline": validation.get("baseline", {}),
        "deterministic_modules": manifest.get("deterministic_modules", []),
        "llm_modules": manifest.get("llm_modules", []),
    }


def render_verdict_md(v: dict[str, Any]) -> str:
    return (
        f"# VERDICT — run {v['run_id']} (CME v{v['pipeline_version']})\n\n"
        f"**Статус:** {v['overall_status']} — гейтів пройдено {v['gates_passed']}/{v['gates_total']}\n"
        f"**Провалені гейти:** {', '.join(v['gates_failed']) or 'немає'}\n\n"
        f"## Реальне vs проксі vs спекулятивне\n"
        f"- claim governance: {v['claim_governance']}\n"
        f"- baseline: {v['baseline']}\n"
        f"- детерміновані модулі: {', '.join(v['deterministic_modules'])}\n"
        f"- LLM-модулі: {', '.join(v['llm_modules']) or 'немає (детермінований прогін)'}\n"
    )
