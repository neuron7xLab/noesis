"""CME v0.4 — Neurocognitive Theory Integration Engine.

Збирає 10-секційний нейрокогнітивний артефакт із 12 теоретичних лінз поверх
ядра v0.3. Провенанс кожної секції позначено явно. Жодних claims про свідомість/
досвід/AGI/діагноз — гейтується розширеним forbidden-шаром.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from cme.generators import build_artifact_deterministic, build_mirror_deterministic
from cme.models import Check, MirrorArtifact, RealityMaps, ValidationReport
from cme.ontology import build_reality_maps, extract_categories
from cme.theories import LensReadout, run_theories, select_lenses
from cme.validators import validate_artifact, validate_guards

PROVENANCE = ("observed", "inferred", "speculative", "forbidden")


@dataclass(frozen=True)
class Tagged:
    value: str
    provenance: str

    def to_dict(self) -> dict[str, str]:
        return {"value": self.value, "provenance": self.provenance}


@dataclass
class NeuroRun:
    raw_input: str
    intent_mirror: dict[str, str]
    theory_selection: dict[str, str]
    state_space_map: dict[str, str]
    prediction_error_stack: Tagged
    workspace_broadcast: Tagged
    active_inference_policy: Tagged
    conceptual_refactor: Tagged
    artifact: dict[str, str]
    next_action: Tagged
    readouts: dict[str, LensReadout]
    validations: list[ValidationReport] = field(default_factory=list)

    @property
    def passed(self) -> bool:
        return all(v.passed for v in self.validations)

    def sections(self) -> dict[str, Any]:
        return {
            "intent_mirror": self.intent_mirror,
            "theory_selection": self.theory_selection,
            "state_space_map": self.state_space_map,
            "prediction_error_stack": self.prediction_error_stack.to_dict(),
            "workspace_broadcast": self.workspace_broadcast.to_dict(),
            "active_inference_policy": self.active_inference_policy.to_dict(),
            "conceptual_refactor": self.conceptual_refactor.to_dict(),
            "artifact": self.artifact,
            "next_action": self.next_action.to_dict(),
        }


def _validate_provenance(run_sections: list[Tagged]) -> ValidationReport:
    bad = [t.provenance for t in run_sections if t.provenance not in PROVENANCE]
    forbidden = [t for t in run_sections if t.provenance == "forbidden"]
    return ValidationReport("provenance", [
        Check("provenance_tagged", not bad, "усі теги з дозволеного набору" if not bad else f"невалідні: {bad}"),
        Check("no_forbidden_provenance", not forbidden, "немає секцій із тегом forbidden"),
    ])


def run_v4(raw: str) -> NeuroRun:
    mirror: MirrorArtifact = build_mirror_deterministic(raw)
    maps: RealityMaps = build_reality_maps(extract_categories(raw))
    artifact = build_artifact_deterministic(mirror.hidden_goal)
    readouts = run_theories(raw, mirror, maps)
    active = select_lenses(readouts)

    intent_mirror = {
        "surface_intent": mirror.surface_intent,
        "hidden_goal": mirror.hidden_goal,
        "blocker": mirror.blocker,
        "constraint": mirror.constraint,
        "next_action": mirror.next_action,
    }
    theory_selection = {k: readouts[k].operator_output for k in active}
    state_space_map = {
        "current_state": readouts["switching"].operator_output,
        "attractor": readouts["tda"].operator_output,
        "regime_shift": readouts["dynamical"].operator_output,
        "entropy_source": readouts["thermodynamics"].operator_output,
    }
    prediction_error_stack = Tagged(readouts["predictive_coding"].operator_output, "inferred")
    workspace_broadcast = Tagged(readouts["gnwt"].operator_output, "inferred")
    active_inference_policy = Tagged(readouts["active_inference"].operator_output, "inferred")
    conceptual_refactor = Tagged(readouts["conceptual_engineering"].operator_output, "speculative")
    next_action = Tagged(
        f"{mirror.next_action} | метрика: артефакт PASS і дія виконана за {mirror.time_horizon}", "observed"
    )

    tagged = [prediction_error_stack, workspace_broadcast, active_inference_policy,
              conceptual_refactor, next_action]
    blob = " ".join([raw, *theory_selection.values(), *state_space_map.values(), *artifact.values(),
                     *(t.value for t in tagged)])
    validations = [
        validate_artifact(artifact, raw),
        validate_guards(blob, mirror.next_action, artifact.get("validation", "")),
        _validate_provenance(tagged),
    ]
    return NeuroRun(
        raw_input=raw,
        intent_mirror=intent_mirror,
        theory_selection=theory_selection,
        state_space_map=state_space_map,
        prediction_error_stack=prediction_error_stack,
        workspace_broadcast=workspace_broadcast,
        active_inference_policy=active_inference_policy,
        conceptual_refactor=conceptual_refactor,
        artifact=artifact,
        next_action=next_action,
        readouts=readouts,
        validations=validations,
    )


def render_neuro_md(run: NeuroRun) -> str:
    ss = run.state_space_map
    return (
        f"# Нейрокогнітивний артефакт (CME v0.4)\n\n"
        f"## Режим системи\n{ss['current_state']}\n\n"
        f"## Помилка передбачення (рушій)\n{run.prediction_error_stack.value} "
        f"[{run.prediction_error_stack.provenance}]\n\n"
        f"## Сигнал, що контролює workspace\n{run.workspace_broadcast.value} "
        f"[{run.workspace_broadcast.provenance}]\n\n"
        f"## Дія, що мінімізує невизначеність\n{run.active_inference_policy.value} "
        f"[{run.active_inference_policy.provenance}]\n\n"
        f"## Концепт під ремонт\n{run.conceptual_refactor.value} "
        f"[{run.conceptual_refactor.provenance}]\n\n"
        f"## Атрактор / траєкторія\n{ss['attractor']}\n{ss['regime_shift']}\n\n"
        f"## Наступна дія\n{run.next_action.value} [{run.next_action.provenance}]\n\n"
        f"## Failure mode під наглядом\n{run.artifact['failure_modes']}\n"
    )


def run_and_save_v4(raw: str, out_dir: Path, *, created_at: str | None = None) -> tuple[NeuroRun, dict[str, Any]]:
    import hashlib

    run = run_v4(raw)
    out_dir.mkdir(parents=True, exist_ok=True)

    def w(name: str, text: str) -> str:
        (out_dir / name).write_text(text, encoding="utf-8")
        return name

    files = [
        w("raw_input.md", run.raw_input),
        w("neuro_sections.json", json.dumps(run.sections(), ensure_ascii=False, indent=2)),
        w("theory_readout.json", json.dumps({k: r.to_dict() for k, r in run.readouts.items()},
                                            ensure_ascii=False, indent=2)),
        w("neuro_artifact.md", render_neuro_md(run)),
        w("validation.json", json.dumps([v.to_dict() for v in run.validations], ensure_ascii=False, indent=2)),
    ]
    manifest: dict[str, Any] = {
        "id": hashlib.sha256(raw.encode("utf-8")).hexdigest()[:12],
        "engine": "cognitive-mirror-engine",
        "version": "0.4",
        "regime": run.readouts["switching"].operator_output,
        "prediction_error": run.prediction_error_stack.value,
        "files": [*files, "manifest.json"],
        "validations_passed": run.passed,
        "created_at": created_at,
    }
    w("manifest.json", json.dumps(manifest, ensure_ascii=False, indent=2))
    return run, manifest
