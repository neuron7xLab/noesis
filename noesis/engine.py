"""CME v0.3 Engine: raw → ontology → maps → synthesis → reverse → artifact → validate → action.

Канонічна труба v0.3 + Evidence Bundle (8 файлів). Детермінований кістяк; LLM
лишається опційним підсиленням фіналайзера (через mirror).
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from noesis.generators import build_artifact_deterministic, build_mirror_deterministic
from noesis.models import (
    ActiveCategory,
    MirrorArtifact,
    RealityMaps,
    ReversePlan,
    SynthesisAxis,
    ValidationReport,
)
from noesis.ontology import build_reality_maps, extract_categories
from noesis.synthesis import build_reverse_plan, build_synthesis
from noesis.validators import (
    validate_artifact,
    validate_categories,
    validate_guards,
    validate_maps,
    validate_synthesis,
)

_AXIS_LABEL = {"europe": "Європа (Буття/істина)", "usa": "США (Дія/наслідок)", "china": "Китай (Становлення/потік)"}


@dataclass
class EngineRun:
    raw_input: str
    categories: list[ActiveCategory]
    maps: RealityMaps
    synthesis: SynthesisAxis
    reverse: ReversePlan
    mirror: MirrorArtifact
    artifact: dict[str, str]
    next_action: str
    validations: list[ValidationReport] = field(default_factory=list)

    @property
    def controlling_category(self) -> str:
        dominant = getattr(self.maps, self.maps.dominant_axis)
        return dominant[0].name if dominant else "Дія"

    @property
    def passed(self) -> bool:
        return all(v.passed for v in self.validations)


def run_v3(raw: str) -> EngineRun:
    categories = extract_categories(raw)
    maps = build_reality_maps(categories)
    synthesis = build_synthesis(maps)
    mirror = build_mirror_deterministic(raw)
    reverse = build_reverse_plan(mirror, maps)
    artifact = build_artifact_deterministic(mirror.hidden_goal)
    blob = " ".join([raw, synthesis.preserve, synthesis.test, synthesis.evolve, *artifact.values()])
    validations = [
        validate_categories(categories),
        validate_maps(maps),
        validate_synthesis(synthesis),
        validate_artifact(artifact, raw),
        validate_guards(blob, mirror.next_action, artifact.get("validation", "")),
    ]
    return EngineRun(
        raw_input=raw,
        categories=categories,
        maps=maps,
        synthesis=synthesis,
        reverse=reverse,
        mirror=mirror,
        artifact=artifact,
        next_action=mirror.next_action,
        validations=validations,
    )


def render_reality_maps_md(run: EngineRun) -> str:
    def section(axis: str) -> str:
        cats = getattr(run.maps, axis)
        if not cats:
            return f"### {_AXIS_LABEL[axis]} — **спляча** (сліпа зона)\n"
        rows = "\n".join(f"- **{c.name}** — {c.function} (сигнал: {', '.join(c.matched)})" for c in cats)
        return f"### {_AXIS_LABEL[axis]}\n{rows}\n"

    return (
        f"# Карти реальності\n\n"
        f"**Активна (домінантна) карта:** {_AXIS_LABEL[run.maps.dominant_axis]}\n"
        f"**Сплячі осі:** {', '.join(run.maps.dormant_axes) or 'немає'}\n\n"
        f"{section('europe')}\n{section('usa')}\n{section('china')}"
    )


def render_synthesis_md(run: EngineRun) -> str:
    s = run.synthesis
    return (
        f"# Синтез-вісь\n\n"
        f"- **Зберегти (істина):** {s.preserve}\n"
        f"- **Перевірити (наслідок):** {s.test}\n"
        f"- **Дати еволюціонувати (процес):** {s.evolve}\n"
        f"- **Відмовитись:** {s.refuse}\n"
    )


def render_next_action_md(run: EngineRun) -> str:
    status = "PASS" if run.passed else "FAIL"
    return (
        f"# Наступна дія\n\n"
        f"**Що робити:** {run.next_action}\n\n"
        f"- активна карта реальності: {_AXIS_LABEL[run.maps.dominant_axis]}\n"
        f"- категорія, що керує інтерпретацією: {run.controlling_category}\n"
        f"- перша відсутня умова: {run.reverse.first_missing_condition}\n"
        f"- блокуюче припущення: {run.reverse.blocking_assumption}\n"
        f"- мінімальна інтервенція: {run.reverse.minimum_viable_intervention}\n"
        f"- подія валідації: {run.reverse.validation_event}\n"
        f"- failure mode під наглядом: {run.synthesis.refuse}\n"
        f"- валідація: {status}\n"
    )


def run_and_save_v3(
    raw: str, out_dir: Path, *, created_at: str | None = None
) -> tuple[EngineRun, dict[str, Any]]:
    import hashlib

    run = run_v3(raw)
    out_dir.mkdir(parents=True, exist_ok=True)

    def w(name: str, text: str) -> str:
        (out_dir / name).write_text(text, encoding="utf-8")
        return name

    files = [
        w("raw_input.md", run.raw_input),
        w("category_map.json", json.dumps([c.to_dict() for c in run.categories], ensure_ascii=False, indent=2)),
        w("reality_maps.md", render_reality_maps_md(run)),
        w("synthesis_axis.md", render_synthesis_md(run)),
        w("artifact.json", json.dumps(run.artifact, ensure_ascii=False, indent=2)),
        w("validation.json", json.dumps([v.to_dict() for v in run.validations], ensure_ascii=False, indent=2)),
        w("next_action.md", render_next_action_md(run)),
    ]
    manifest: dict[str, Any] = {
        "id": hashlib.sha256(raw.encode("utf-8")).hexdigest()[:12],
        "engine": "cognitive-mirror-engine",
        "version": "0.3",
        "dominant_axis": run.maps.dominant_axis,
        "controlling_category": run.controlling_category,
        "files": [*files, "manifest.json"],
        "validations_passed": run.passed,
        "created_at": created_at,
    }
    w("manifest.json", json.dumps(manifest, ensure_ascii=False, indent=2))
    return run, manifest
