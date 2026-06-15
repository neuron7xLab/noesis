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


def _join(x: Any) -> str:
    return ", ".join(map(str, x)) if isinstance(x, list) else ""


def render_verdict_md(v: dict[str, Any]) -> str:
    """Render a verdict. Fail-closed on partial/corrupt input: a manifest read
    from disk may be truncated, so missing fields degrade to «—», never KeyError
    (знайдено хаос-стрес-тестом)."""
    run_id = v.get("run_id") or "—"
    version = v.get("pipeline_version") or "—"
    status = v.get("overall_status") or "—"
    passed = v.get("gates_passed", 0)
    total = v.get("gates_total", 0)
    return (
        f"# VERDICT — run {run_id} (CME v{version})\n\n"
        f"**Статус:** {status} — гейтів пройдено {passed}/{total}\n"
        f"**Провалені гейти:** {_join(v.get('gates_failed')) or 'немає'}\n\n"
        f"## Реальне vs проксі vs спекулятивне\n"
        f"- claim governance: {v.get('claim_governance', {})}\n"
        f"- baseline: {v.get('baseline', {})}\n"
        f"- детерміновані модулі: {_join(v.get('deterministic_modules'))}\n"
        f"- LLM-модулі: {_join(v.get('llm_modules')) or 'немає (детермінований прогін)'}\n"
    )
