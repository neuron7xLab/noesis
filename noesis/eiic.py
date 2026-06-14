"""EIIC v0.1 — Extrapolated Intentional Cognitive Core.

Витягає термінальний вектор системи: куди вона СТРУКТУРНО прямує, коли прибрати
шум, страх, ресурсні обмеження й фрагментоване виконання. НЕ опис поточної
поведінки. Кожне твердження тегується провенансом; жодного містицизму/долі/AGI.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from noesis.forbidden import check_forbidden_claims
from noesis.generators import build_mirror_deterministic
from noesis.models import Check, ValidationReport
from noesis.ontology import build_reality_maps, extract_categories
from noesis.synthesis import build_reverse_plan
from noesis.theories import classify_regime, run_theories

_AXIS_LABEL = {"europe": "істина/форма (Європа)", "usa": "дія/наслідок (США)", "china": "процес/потік (Китай)"}


@dataclass(frozen=True)
class Tagged:
    value: str
    provenance: str  # observed | inferred | speculative | forbidden

    def to_dict(self) -> dict[str, str]:
        return {"value": self.value, "provenance": self.provenance}


@dataclass
class EIICCore:
    current_state: Tagged
    latent_intent: Tagged
    noise_layer: Tagged
    constraint_layer: Tagged
    extrapolated_core: Tagged
    attractor_state: Tagged
    peak_architecture: Tagged
    failure_mode: Tagged
    first_missing_condition: Tagged
    next_action: Tagged
    validation: ValidationReport

    @property
    def passed(self) -> bool:
        return self.validation.passed

    def to_dict(self) -> dict[str, Any]:
        return {
            "current_state": self.current_state.to_dict(),
            "latent_intent": self.latent_intent.to_dict(),
            "noise_layer": self.noise_layer.to_dict(),
            "constraint_layer": self.constraint_layer.to_dict(),
            "extrapolated_core": self.extrapolated_core.to_dict(),
            "attractor_state": self.attractor_state.to_dict(),
            "peak_architecture": self.peak_architecture.to_dict(),
            "failure_mode": self.failure_mode.to_dict(),
            "first_missing_condition": self.first_missing_condition.to_dict(),
            "next_action": self.next_action.to_dict(),
            "validation": self.validation.to_dict(),
        }


_AXIS_TRAP = {"europe": "абстракція без дії", "usa": "інструменталізація без глибини",
              "china": "адаптація без конфронтації"}


def run_eiic(raw: str) -> EIICCore:
    mirror = build_mirror_deterministic(raw)
    maps = build_reality_maps(extract_categories(raw))
    reverse = build_reverse_plan(mirror, maps)
    readouts = run_theories(raw, mirror, maps)
    regime, _ = classify_regime(raw)
    controlling = (getattr(maps, maps.dominant_axis)[0].name if getattr(maps, maps.dominant_axis) else "Дія")
    attractor = readouts["tda"].operator_output

    current_state = Tagged(f"{mirror.surface_intent} (режим: {regime})", "observed")
    latent_intent = Tagged(mirror.hidden_goal, "inferred")
    noise_layer = Tagged(readouts["thermodynamics"].operator_output, "observed")
    constraint_layer = Tagged(
        f"{mirror.constraint}; ресурс: {readouts['systems_biology'].operator_output}", "observed")
    extrapolated_core = Tagged(
        f"Прибравши шум і страх (режим {regime}), вектор масштабується до: «{mirror.hidden_goal}» "
        f"як стійка система на осі {_AXIS_LABEL[maps.dominant_axis]}, не як епізод", "speculative")
    attractor_state = Tagged(f"{attractor}; домінантна вісь {maps.dominant_axis}", "inferred")
    peak_architecture = Tagged(
        f"Пікова форма: {_AXIS_LABEL[maps.dominant_axis]}-домінована система, де концепт «{controlling}» "
        f"інституціоналізовано у відтворюваний артефакт+цикл", "speculative")
    failure_mode = Tagged(_AXIS_TRAP[maps.dominant_axis], "inferred")
    first_missing_condition = Tagged(reverse.first_missing_condition, "inferred")
    next_action = Tagged(f"{mirror.next_action} | метрика: один перевірний артефакт за {mirror.time_horizon}", "observed")

    fields = [current_state, latent_intent, noise_layer, constraint_layer, extrapolated_core,
              attractor_state, peak_architecture, failure_mode, first_missing_condition, next_action]
    blob = " ".join(t.value for t in fields)
    forbidden = check_forbidden_claims(blob)
    valid_prov = all(t.provenance in ("observed", "inferred", "speculative", "forbidden") for t in fields)
    validation = ValidationReport("eiic", [
        Check("forbidden_claims", not forbidden, "чисто" if not forbidden else ", ".join(forbidden)),
        Check("missing_next_action", bool(next_action.value.strip()), "наступна дія присутня"),
        Check("provenance_tagged", valid_prov, "усі поля мають валідний провенанс"),
        Check("core_is_speculative", extrapolated_core.provenance == "speculative",
              "екстрапольоване ядро НЕ видається за спостережене"),
        Check("peak_is_speculative", peak_architecture.provenance == "speculative",
              "пікова архітектура позначена як спекуляція"),
        Check("no_forbidden_provenance", all(t.provenance != "forbidden" for t in fields),
              "немає полів із тегом forbidden"),
        Check("has_observed_anchor", any(t.provenance == "observed" for t in fields),
              "є щонайменше одне спостережене закріплення"),
    ])
    return EIICCore(
        current_state, latent_intent, noise_layer, constraint_layer, extrapolated_core,
        attractor_state, peak_architecture, failure_mode, first_missing_condition, next_action, validation,
    )


def render_eiic_md(core: EIICCore) -> str:
    def line(label: str, t: Tagged) -> str:
        return f"- **{label}** [{t.provenance}]: {t.value}\n"

    return (
        "# Extrapolated Intentional Cognitive Core\n\n"
        + line("Поточний стан", core.current_state)
        + line("Латентний намір", core.latent_intent)
        + line("Шумовий шар", core.noise_layer)
        + line("Шар обмежень", core.constraint_layer)
        + line("ЕКСТРАПОЛЬОВАНЕ ЯДРО", core.extrapolated_core)
        + line("Атрактор", core.attractor_state)
        + line("Пікова архітектура", core.peak_architecture)
        + line("Failure mode", core.failure_mode)
        + line("Перша відсутня умова", core.first_missing_condition)
        + line("Наступна дія", core.next_action)
        + f"\nВАЛІДАЦІЯ: {'PASS' if core.passed else 'FAIL'}\n"
    )


def run_and_save_eiic(raw: str, out_dir: Path, *, created_at: str | None = None) -> dict[str, Any]:
    import hashlib

    core = run_eiic(raw)
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "raw_input.md").write_text(raw, encoding="utf-8")
    (out_dir / "eiic_core.json").write_text(json.dumps(core.to_dict(), ensure_ascii=False, indent=2), encoding="utf-8")
    (out_dir / "eiic_core.md").write_text(render_eiic_md(core), encoding="utf-8")
    manifest: dict[str, Any] = {
        "id": hashlib.sha256(raw.encode("utf-8")).hexdigest()[:12],
        "engine": "eiic",
        "version": "0.1",
        "dominant_axis": core.attractor_state.value,
        "files": ["raw_input.md", "eiic_core.json", "eiic_core.md", "manifest.json"],
        "validations_passed": core.passed,
        "created_at": created_at,
    }
    (out_dir / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    return manifest
