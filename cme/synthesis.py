"""Synthesis Axis Engine + Reverse Inference (v0.3).

Зводить три карти реальності в один синтез: що зберегти (істина), що перевірити
(наслідок), чому дати еволюціонувати (процес), від чого відмовитись (пастка осі).
"""

from __future__ import annotations

from cme.models import ActiveCategory, MirrorArtifact, RealityMaps, ReversePlan, SynthesisAxis
from tools.reverse_inference import plan_backwards

# Цивілізаційна пастка кожної осі (failure mode на рівні ОС реальності).
_AXIS_TRAP: dict[str, str] = {
    "europe": "абстракція без дії",
    "usa": "інструменталізація без глибини",
    "china": "адаптація без конфронтації",
}
_AXIS_BLOCKING_ASSUMPTION: dict[str, str] = {
    "europe": "що достатньо правильно ЗРОЗУМІТИ, аби зрушити",
    "usa": "що більше ДІЇ автоматично = більше прогресу",
    "china": "що достатньо ПЛИСТИ за потоком, не вступаючи в конфлікт",
}


def _first(cats: list[ActiveCategory]) -> ActiveCategory | None:
    return cats[0] if cats else None


def build_synthesis(maps: RealityMaps) -> SynthesisAxis:
    eu = _first(maps.europe)
    us = _first(maps.usa)
    cn = _first(maps.china)
    preserve = (
        f"Зберегти норму істини/структури: {eu.name} ({eu.function})." if eu
        else "Європейська вісь спляча → додай критерій валідності, інакше дія без норми істини."
    )
    test = (
        f"Перевірити експериментом і оцінити за наслідком: {us.name} ({us.function})." if us
        else "США-вісь спляча → нема механізму перевірки; додай тест/наслідок."
    )
    evolve = (
        f"Дати еволюціонувати без форсування (мінімальна інтервенція): {cn.name} ({cn.function})." if cn
        else "Китайська вісь спляча → процес ігнорується; врахуй тайминг і дай дозріти."
    )
    refuse = f"Відмовитись від пастки домінантної осі ({maps.dominant_axis}): {_AXIS_TRAP[maps.dominant_axis]}."
    return SynthesisAxis(preserve=preserve, test=test, evolve=evolve, refuse=refuse)


def build_reverse_plan(mirror: MirrorArtifact, maps: RealityMaps) -> ReversePlan:
    trace = plan_backwards(
        target_state=mirror.hidden_goal,
        current_facts=[mirror.surface_intent],
        required_conditions=[mirror.blocker, mirror.next_action],
    )
    missing = trace.missing_constraints[0] if trace.missing_constraints else mirror.next_action
    return ReversePlan(
        first_missing_condition=missing,
        blocking_assumption=f"Припущення, {_AXIS_BLOCKING_ASSUMPTION[maps.dominant_axis]}.",
        minimum_viable_intervention=f"Один крок без форсування: {mirror.next_action}.",
        validation_event="Артефакт проходить `cme validate` (0 порушень) і next_action виконано за горизонт.",
    )
