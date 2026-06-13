"""Evidence Bundle: для кожного прогону зберігає повний слід рішення."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


def _write(path: Path, text: str) -> str:
    path.write_text(text, encoding="utf-8")
    return path.name


def write_evidence(
    out_dir: Path,
    *,
    raw_input: str,
    mirror_md: str,
    artifact: dict[str, str],
    validations: list[dict[str, Any]],
    decision_md: str,
    method_selected: str,
    created_at: str | None = None,
) -> dict[str, Any]:
    """Пише raw_input.md, mirror.md, artifact.json, validation.json, decision.md, manifest.json."""
    out_dir.mkdir(parents=True, exist_ok=True)
    run_id = hashlib.sha256(raw_input.encode("utf-8")).hexdigest()[:12]

    files = [
        _write(out_dir / "raw_input.md", raw_input),
        _write(out_dir / "mirror.md", mirror_md),
        _write(out_dir / "artifact.json", json.dumps(artifact, ensure_ascii=False, indent=2)),
        _write(out_dir / "validation.json", json.dumps(validations, ensure_ascii=False, indent=2)),
        _write(out_dir / "decision.md", decision_md),
    ]
    all_passed = all(v.get("passed", False) for v in validations)
    manifest: dict[str, Any] = {
        "id": run_id,
        "engine": "cognitive-mirror-engine",
        "method_selected": method_selected,
        "files": [*files, "manifest.json"],
        "validations_passed": all_passed,
        "created_at": created_at,
    }
    _write(out_dir / "manifest.json", json.dumps(manifest, ensure_ascii=False, indent=2))
    return manifest
