"""Повна труба CME: raw → method_selection → generate → validate → artifact → next_action."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from noesis.evidence import write_evidence
from noesis.generators import (
    build_artifact_deterministic,
    build_introspection_deterministic,
    build_mirror_deterministic,
    build_mirror_llm,
)
from noesis.models import IntrospectionMap, MirrorArtifact, ValidationReport
from noesis.registry import select_method
from noesis.validators import (
    validate_artifact,
    validate_introspection,
    validate_mirror,
    validate_reverse,
)
from tools.reverse_inference import ReverseTrace, plan_backwards


def _make_mirror(raw: str, backend: str) -> MirrorArtifact:
    if backend == "deterministic":
        return build_mirror_deterministic(raw)
    adapter_backend = "auto" if backend == "llm" else backend
    return build_mirror_llm(raw, backend=adapter_backend)


@dataclass
class PipelineRun:
    raw_input: str
    method_selected: str
    mirror: MirrorArtifact
    introspection: IntrospectionMap
    artifact: dict[str, str]
    reverse: ReverseTrace
    next_action: str
    validations: list[ValidationReport] = field(default_factory=list)

    @property
    def passed(self) -> bool:
        return all(v.passed for v in self.validations)


def run_pipeline(raw: str, *, backend: str = "deterministic") -> PipelineRun:
    method = select_method(raw)
    mirror = _make_mirror(raw, backend)
    introspection = build_introspection_deterministic(raw)
    artifact = build_artifact_deterministic(mirror.hidden_goal)
    reverse = plan_backwards(
        target_state=mirror.hidden_goal,
        current_facts=[mirror.surface_intent],
        required_conditions=[mirror.blocker, mirror.next_action],
    )
    validations = [
        validate_mirror(mirror, raw),
        validate_introspection(introspection, raw),
        validate_artifact(artifact, raw),
        validate_reverse(reverse),
    ]
    return PipelineRun(
        raw_input=raw,
        method_selected=method,
        mirror=mirror,
        introspection=introspection,
        artifact=artifact,
        reverse=reverse,
        next_action=mirror.next_action,
        validations=validations,
    )


def render_mirror_md(run: PipelineRun) -> str:
    m = run.mirror
    return (
        f"# Дзеркало наміру (метод: {run.method_selected})\n\n"
        f"- **Явний запит:** {m.surface_intent}\n"
        f"- **Прихована мета:** {m.hidden_goal}\n"
        f"- **Обмеження:** {m.constraint}\n"
        f"- **Блокер:** {m.blocker}\n"
        f"- **Наступна дія:** {m.next_action}\n"
        f"- **Метрика успіху:** {m.success_metric}\n"
        f"- **Часовий горизонт:** {m.time_horizon}\n"
        f"- **Критичний ризик:** {m.critical_risk}\n"
        f"- **Зниження ризику:** {m.risk_reduction}\n\n"
        f"## Фіналайзер\n{m.finalizer}\n"
    )


def render_decision_md(run: PipelineRun) -> str:
    status = "PASS" if run.passed else "FAIL"
    return (
        f"# Рішення\n\n"
        f"**Одна наступна дія:** {run.next_action}\n\n"
        f"- метод: {run.method_selected}\n"
        f"- валідація: {status}\n"
        f"- реверсивний крок: {run.reverse.next_action}\n"
    )


def run_and_save(
    raw: str, out_dir: Path, *, backend: str = "deterministic", created_at: str | None = None
) -> tuple[PipelineRun, dict[str, Any]]:
    run = run_pipeline(raw, backend=backend)
    manifest = write_evidence(
        out_dir,
        raw_input=raw,
        mirror_md=render_mirror_md(run),
        artifact=run.artifact,
        validations=[v.to_dict() for v in run.validations],
        decision_md=render_decision_md(run),
        method_selected=run.method_selected,
        created_at=created_at,
    )
    return run, manifest
