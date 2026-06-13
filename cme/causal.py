"""Causal layer v0.6: категорії, карти й теорії, що РЕАЛЬНО змінюють дію.

Категорія та режим (switching-теорія) причинно модифікують next_action, тож їх
внесок вимірюється diff'ом «до/після». Теорії без downstream-ефекту чесно
позначаються decorative (score 0) — це і є брутальна знахідка v0.6.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

from cme.models import MirrorArtifact, RealityMaps
from cme.theories import classify_regime

# Операційний ефект кожної цивілізаційної осі (робить категорію причинною).
AXIS_EFFECT: dict[str, dict[str, str]] = {
    "europe": {
        "action_bias": "спершу операціоналізуй визначення, тоді дій",
        "risk_bias": "абстракція без дії",
        "validation_bias": "вимагати чіткий критерій істини/форми",
        "next_action_delta": "додати крок визначення перед дією",
    },
    "usa": {
        "action_bias": "обрати тестований крок замість концептуального прояснення",
        "risk_bias": "поверхнева інструменталізація",
        "validation_bias": "вимагати вимірюваний результат",
        "next_action_delta": "обрати експеримент замість есе",
    },
    "china": {
        "action_bias": "мінімальна інтервенція, дочекатись таймінгу",
        "risk_bias": "пасивність/конформізм",
        "validation_bias": "вимагати подію готовності, не форсувати",
        "next_action_delta": "зменшити втручання, чекати сигналу",
    },
}

# Які теорії мають downstream-ефект (решта — декоративні за чесним аудитом).
WIRED_THEORIES: dict[str, str] = {"switching": "action", "conceptual_engineering": "validation"}


@dataclass(frozen=True)
class CategoryEffect:
    category: str
    axis: str
    detected_signal: list[str]
    interpretation_bias: str
    action_bias: str
    risk_bias: str
    validation_bias: str
    next_action_delta: str
    if_removed_delta: str
    status: str  # causal | weak | decorative | harmful

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class RealityMapDelta:
    european_reading: str
    american_reading: str
    chinese_reading: str
    shared_signal: str
    conflict_between_maps: bool
    action_under_europe: str
    action_under_usa: str
    action_under_china: str
    chosen_action: str
    why_chosen: str
    what_would_change_if_axis_changed: str
    low_map_utility: bool

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class ActionDecision:
    candidate_actions: list[str]
    selected_action: str
    selection_reason: str
    category_influence: str
    theory_influence: str
    eiic_influence: str
    risk_reduction: str
    success_metric: str
    time_horizon: str
    reversibility: str
    minimum_viable_action: str
    upstream_modules_changed: list[str]
    pipeline_overbuilt: bool

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class TheoryContribution:
    theory_name: str
    operator: str
    claim_limit: str
    changed_next_action: bool
    changed_failure_mode: bool
    changed_validation: bool
    contribution_score: int
    decorative_risk: bool

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def build_category_effects(maps: RealityMaps) -> list[CategoryEffect]:
    effects: list[CategoryEffect] = []
    dominant_first = getattr(maps, maps.dominant_axis)
    for axis in ("europe", "usa", "china"):
        for idx, cat in enumerate(getattr(maps, axis)):
            eff = AXIS_EFFECT[axis]
            is_applied = bool(dominant_first) and cat is dominant_first[0]
            status = "causal" if is_applied else "weak" if idx == 0 else "decorative"
            effects.append(CategoryEffect(
                category=cat.name, axis=axis, detected_signal=cat.matched,
                interpretation_bias=f"{axis}: {cat.function}",
                action_bias=eff["action_bias"], risk_bias=eff["risk_bias"],
                validation_bias=eff["validation_bias"], next_action_delta=eff["next_action_delta"],
                if_removed_delta="дія стає абстрактною (втрачає осьовий ухил)",
                status=status,
            ))
    return effects


def _axis_action(base: str, axis: str) -> str:
    return f"{AXIS_EFFECT[axis]['action_bias']}: {base}"


def build_reality_map_delta(maps: RealityMaps, mirror: MirrorArtifact) -> RealityMapDelta:
    base = mirror.next_action
    a_eu, a_us, a_cn = _axis_action(base, "europe"), _axis_action(base, "usa"), _axis_action(base, "china")
    chosen = _axis_action(base, maps.dominant_axis)
    distinct = len({AXIS_EFFECT[a]["action_bias"] for a in ("europe", "usa", "china")}) == 3
    return RealityMapDelta(
        european_reading="що тут реальне/істинне",
        american_reading="що тут працює/тестовано",
        chinese_reading="куди тече процес/таймінг",
        shared_signal=mirror.surface_intent,
        conflict_between_maps=len(maps.dormant_axes) < 2,
        action_under_europe=a_eu, action_under_usa=a_us, action_under_china=a_cn,
        chosen_action=chosen,
        why_chosen=f"домінантна вісь {maps.dominant_axis} (найбільше активних категорій)",
        what_would_change_if_axis_changed="інша вісь дала б інший операційний ухил дії",
        low_map_utility=not distinct,
    )


def _reversibility(action: str) -> str:
    low = action.lower()
    if any(w in low for w in ("закрити", "звільнит", "видалит", "розірва")):
        return "irreversible"
    return "reversible"


def select_action(
    mirror: MirrorArtifact,
    effects: list[CategoryEffect],
    raw: str,
    eiic_first_missing: str,
) -> ActionDecision:
    base = mirror.next_action
    selected = base
    upstream: list[str] = []
    category_influence = "немає (категорії не вплинули)"

    causal_eff = next((e for e in effects if e.status == "causal"), None)
    if causal_eff is not None:
        selected = f"{causal_eff.action_bias}: {base}"
        upstream.append("category_layer")
        category_influence = causal_eff.next_action_delta

    regime, _ = classify_regime(raw)
    theory_influence = "немає (режим не змінив дію)"
    if regime == "collapse":
        selected = f"спершу віднови ресурс (режим collapse), потім {selected}"
        upstream.append("theory:switching")
        theory_influence = "switching: режим collapse → пріоритет відновлення ресурсу"

    candidates = [base, _axis_action(base, mirror_axis(effects)), f"мінімальний крок: {base}"]
    return ActionDecision(
        candidate_actions=candidates,
        selected_action=selected,
        selection_reason=f"змінено модулями: {', '.join(upstream) or 'жоден (= overbuilt)'}",
        category_influence=category_influence,
        theory_influence=theory_influence,
        eiic_influence=f"перша відсутня умова: {eiic_first_missing}",
        risk_reduction=mirror.risk_reduction,
        success_metric=mirror.success_metric,
        time_horizon=mirror.time_horizon,
        reversibility=_reversibility(selected),
        minimum_viable_action=f"мінімальний крок: {base}",
        upstream_modules_changed=upstream,
        pipeline_overbuilt=not upstream,
    )


def mirror_axis(effects: list[CategoryEffect]) -> str:
    causal = next((e for e in effects if e.status == "causal"), None)
    return causal.axis if causal else "usa"


def track_theory_contribution(raw: str, readouts_keys: list[str]) -> list[TheoryContribution]:
    regime, _ = classify_regime(raw)
    out: list[TheoryContribution] = []
    for key in readouts_keys:
        wired = WIRED_THEORIES.get(key)
        if wired == "action":
            changed_action = regime == "collapse"
            score = 4 if changed_action else 1
            out.append(TheoryContribution(key, "regime classifier", "не клінічний стан",
                                          changed_action, False, False, score, score == 0))
        elif wired == "validation":
            out.append(TheoryContribution(key, "concept refactor", "не реальність-уникання",
                                          False, False, True, 3, False))
        else:
            out.append(TheoryContribution(key, "text proxy", "не реалізація теорії",
                                          False, False, False, 0, True))
    return out


def theory_layer_status(contribs: list[TheoryContribution]) -> str:
    zero = sum(1 for c in contribs if c.contribution_score == 0)
    return "overloaded" if contribs and zero / len(contribs) > 0.5 else "healthy"
