"""Cyclic Reverse Vertical Cognitive Loop — один застосований артефакт (не паралельний движок).

Свідомо реалізовано як ОДИН детермінований шаблон, а не 20-файловий двигун:
демонстрація принципу v0.8 «не додавай вузол, що не піднімає IEV-throughput».
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

from cme.generators import build_artifact_deterministic, build_mirror_deterministic
from cme.ontology import build_reality_maps, extract_categories
from cme.synthesis import build_reverse_plan

# Дозволені операційні дієслова (тільки необхідні вживаються).
OPERATIONS: tuple[str, ...] = (
    "integrate", "encapsulate", "orchestrate", "decouple", "aggregate", "initialize", "refactor",
    "validate", "normalize", "quantize", "adapt", "calibrate", "generate", "optimize", "filter",
    "measure", "profile", "benchmark", "falsify", "verify", "test", "visualize",
    "deploy", "monitor", "log", "scale", "isolate", "restart", "position", "onboard", "prototype", "launch",
)


@dataclass(frozen=True)
class VerticalLoop:
    intent: str
    final_state: str
    first_missing_condition: str
    architecture_layer: str
    ai_layer: str
    validation_layer: str
    production_layer: str
    operation_chain: list[str]
    artifact: dict[str, str]
    validation_gates: list[str]
    failure_modes: list[str]
    next_cycle: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def build_vertical_loop(raw: str) -> VerticalLoop:
    m = build_mirror_deterministic(raw)
    maps = build_reality_maps(extract_categories(raw))
    reverse = build_reverse_plan(m, maps)
    artifact = build_artifact_deterministic(m.hidden_goal)
    # тільки НЕОБХІДНІ дієслова (reverse-vertical мінімальний цикл)
    chain = ["generate — кандидати структури", "filter — відкинути шумові осі",
             "verify — схема/forbidden/артефакт", "falsify — спроба спростувати",
             "validate — пройти гейти", "deploy — закріпити в Evidence Bundle"]
    return VerticalLoop(
        intent=m.hidden_goal,
        final_state=f"існує перевірний артефакт для: {m.hidden_goal}",
        first_missing_condition=reverse.first_missing_condition,
        architecture_layer="encapsulate ядро методу за контрактом; orchestrate Creator→Verifier",
        ai_layer="generate кандидати → filter шум → calibrate поріг прийняття",
        validation_layer="falsify ∧ verify ∧ test → 7-секційний артефакт",
        production_layer="deploy у Evidence Bundle; monitor через cme verdict",
        operation_chain=chain,
        artifact=artifact,
        validation_gates=["артефакт має 7 секцій", "validation містить фальсифікатор", "0 forbidden claims"],
        failure_modes=["передчасний collapse", "нескінченне розширення", "хибна впевненість", "втрата мінорного сигналу"],
        next_cycle=f"перевірити умову «{reverse.first_missing_condition}» і повторити з вужчим наміром",
    )
