"""Method Registry: формальний опис кожного когнітивного методу + селектор."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any


@dataclass(frozen=True)
class MethodSpec:
    name: str
    use_case: str
    trigger: tuple[str, ...]
    input_schema: str
    output_schema: str
    failure_modes: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


REGISTRY: dict[str, MethodSpec] = {
    "mirror": MethodSpec(
        name="Intent Mirror",
        use_case="Витягнути операційний сигнал із розмитого наміру.",
        trigger=("хочу", "треба", "ціль", "мета", "запит"),
        input_schema="raw_text",
        output_schema="MirrorArtifact(9 полів + finalizer)",
        failure_modes=("лестощі замість дзеркала", "галюцинований намір", "розмивання"),
    ),
    "introspection": MethodSpec(
        name="Introspection Engine",
        use_case="Розкласти емоційний/хаотичний вхід на структуру дії.",
        trigger=("боюс", "страх", "тривож", "не знаю", "не можу", "втом", "знову"),
        input_schema="raw_text (emotional)",
        output_schema="IntrospectionMap(intent,fear,constraint,missing,boundary,action)",
        failure_modes=("псевдодіагноз", "зациклення на емоції", ">1 перша дія"),
    ),
    "reverse": MethodSpec(
        name="Reverse Inference (Goal Regression)",
        use_case="Від цілі назад до першої відсутньої умови.",
        trigger=("ціль", "результат", "досягти", "запустити", "опублікувати"),
        input_schema="{target_state, current_facts[], required_conditions[]}",
        output_schema="ReverseTrace(target,required,missing,next_action)",
        failure_modes=("стрибок до цілі", "неповні умови", "змішування горизонтів"),
    ),
    "artifact": MethodSpec(
        name="Artifact Builder",
        use_case="Перетворити інсайт на 7-секційний перевірний MethodArtifact.",
        trigger=("інсайт", "ідея", "метод", "висновок", "патерн"),
        input_schema="raw_insight_text",
        output_schema="MethodArtifact(definition..failure_modes)",
        failure_modes=("інсайт без артефакту", "артефакт без тесту", "доказ-театр"),
    ),
}


def select_method(raw: str) -> str:
    """Обирає первинну лінзу за тригерами; емоція → introspection, інакше mirror."""
    low = raw.lower()
    intro = REGISTRY["introspection"]
    if any(t in low for t in intro.trigger):
        return "introspection"
    reverse = REGISTRY["reverse"]
    if sum(t in low for t in reverse.trigger) >= 2:
        return "reverse"
    return "mirror"
