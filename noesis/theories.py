"""12 нейрокогнітивних теорій як ОПЕРАЦІЙНІ лінзи (детерміновані проксі).

ЧЕСНО: це не реалізації теорій (не справжній Active Inference, не Φ з IIT, не
персистентна гомологія TDA). Це названі, обмежені текстові ПРОКСІ з явним
оператором, сигналом і статусом. Жодна не претендує на свідомість/досвід/AGI.
"""

from __future__ import annotations

import re
from collections import Counter
from dataclasses import asdict, dataclass
from typing import Any

from noesis.models import MirrorArtifact, RealityMaps

_WORD = re.compile(r"[\w’'-]+", re.UNICODE)
_STOP = frozenset({"що", "це", "але", "не", "на", "як", "то", "бо", "чи", "вже", "ще",
                   "хочу", "треба", "мене", "моє", "так", "там", "тут", "для", "над"})

_REGIMES: dict[str, tuple[str, ...]] = {
    "defense": ("боюс", "страх", "захист", "тривож", "небезпек", "лякає"),
    "collapse": ("не можу", "все валиться", "вигор", "на межі", "немає сил", "сил немає", "втомив"),
    "planning": ("план", "крок", "стратег", "маю зробити", "етап"),
    "execution": ("роблю", "запуска", "вже почав", "будую", "виконую"),
    "exploration": ("ідея", "може", "цікаво", "спробува", "що якщо", "хочу"),
}
_ERROR_LEVELS: dict[str, tuple[str, ...]] = {
    "identity": ("хто я", "не той", "справжн", "сенс життя", "ким бути", "себе"),
    "strategic": ("не туди", "напрям", "стратег", "ціль", "куди"),
    "semantic": ("не розумію", "не ясно", "заплута", "сформулюва", "не можу пояснит"),
    "sensory": ("втом", "сон", "тіло", "сил немає", "енерг"),
}
_SCALES: dict[str, tuple[str, ...]] = {
    "bodily": ("втом", "сон", "тіло", "сил", "енерг", "здоров"),
    "social": ("друз", "партнер", "команд", "клієнт", "ринок", "сім", "люди", "стосунк"),
    "technological": ("систем", "продукт", "код", "агент", "інструмент", "софт"),
    "neural": ("думаю", "розумію", "увага", "памʼят", "фокус", "мисл"),
    "molecular": ("дофамін", "гормон", "серотонін", "нейромедіатор"),
}
_NOISE = ("блін", "просто", "якось", "ну ", "взагалі", "типу", "знову", "постійно", "капец")
_DOUBT = ("сумнів", "не знаю", "не впевнен", "самообман", "може", "можливо")
_CONFIDENCE = ("впевнен", "точно", "знаю що", "переконан")
_DECISION = ("чи ", " або ", "між ", "вибрат", "не знаю що обрат")


@dataclass(frozen=True)
class LensReadout:
    lens: str
    software_role: str
    operator_output: str
    signals: list[str]
    status: str  # завжди "deterministic-proxy"

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _hits(low: str, markers: tuple[str, ...]) -> list[str]:
    return [m for m in markers if m in low]


def _best(low: str, groups: dict[str, tuple[str, ...]], default: str) -> tuple[str, list[str]]:
    scored = {k: _hits(low, v) for k, v in groups.items()}
    key = max(scored, key=lambda k: len(scored[k]))
    return (key, scored[key]) if scored[key] else (default, [])


def _content_counter(raw: str) -> Counter[str]:
    return Counter(w for w in _WORD.findall(raw.lower()) if w not in _STOP and len(w) > 3)


def classify_regime(raw: str) -> tuple[str, list[str]]:
    """Switching dynamical systems — режим: exploration/defense/planning/execution/collapse."""
    return _best(raw.lower(), _REGIMES, "exploration")


def locate_prediction_error(raw: str) -> tuple[str, list[str]]:
    """Hierarchical predictive coding — рівень помилки: sensory/semantic/strategic/identity."""
    return _best(raw.lower(), _ERROR_LEVELS, "semantic")


def active_scales(raw: str) -> list[str]:
    """Systems biology of intelligence — активні шари: bodily/social/technological/neural/molecular."""
    low = raw.lower()
    return [scale for scale, markers in _SCALES.items() if _hits(low, markers)] or ["neural"]


def run_theories(raw: str, mirror: MirrorArtifact, maps: RealityMaps) -> dict[str, LensReadout]:
    low = raw.lower()
    counter = _content_counter(raw)
    top = counter.most_common(1)
    attractor = top[0][0] if top else "—"
    loop = bool(top and top[0][1] >= 2)
    noise = _hits(low, _NOISE)
    total_tokens = max(len(_WORD.findall(low)), 1)
    entropy = round(len(noise) / total_tokens, 3)
    regime, regime_sig = classify_regime(raw)
    err_level, err_sig = locate_prediction_error(raw)
    scales = active_scales(raw)
    doubt = _hits(low, _DOUBT)
    confidence = _hits(low, _CONFIDENCE)
    axes_spanned = sum(1 for m in (maps.europe, maps.usa, maps.china) if m)
    phi = round(axes_spanned / 3, 3)
    bifurcation = _hits(low, _DECISION)

    return {
        "active_inference": LensReadout(
            "Active Inference", "policy selector",
            f"Політика, що знижає невизначеність: {mirror.next_action}",
            [f"невідомих умов≈{len(maps.dormant_axes) + len(doubt)}"], "deterministic-proxy"),
        "attention_schema": LensReadout(
            "Attention Schema Theory", "attention self-model",
            f"Реальний фокус (домінанта): {maps.dominant_axis}; наратив про увагу ≠ розподіл, якщо сплячі осі є",
            maps.dormant_axes or ["узгоджено"], "deterministic-proxy"),
        "gnwt": LensReadout(
            "Global Neuronal Workspace", "workspace router",
            f"Виграє трансляцію: {(getattr(maps, maps.dominant_axis)[0].name if getattr(maps, maps.dominant_axis) else 'Дія')}; "
            f"придушено: {', '.join(maps.dormant_axes) or 'нічого'}",
            [maps.dominant_axis], "deterministic-proxy"),
        "iit": LensReadout(
            "Integrated Information (proxy, NOT consciousness)", "integration heuristic",
            f"Зв'язність структури (осей охоплено {axes_spanned}/3): φ-проксі={phi} — НЕ свідомість, НЕ досвід",
            [f"axes={axes_spanned}"], "deterministic-proxy"),
        "thermodynamics": LensReadout(
            "Thermodynamics of Computation", "entropy budget",
            f"Втрата на шум: ентропія-проксі={entropy} ({len(noise)} шумових маркерів)",
            noise or ["шуму мало"], "deterministic-proxy"),
        "tda": LensReadout(
            "Topological Data Analysis", "state-space morphology scanner",
            f"Атрактор='{attractor}', цикл={'є' if loop else 'нема'}, розриви(сплячі осі)={len(maps.dormant_axes)}",
            [attractor], "deterministic-proxy"),
        "switching": LensReadout(
            "Switching Dynamical Systems", "regime classifier",
            f"Режим: {regime}", regime_sig or ["за замовчуванням exploration"], "deterministic-proxy"),
        "predictive_coding": LensReadout(
            "Hierarchical Predictive Coding", "prediction-error stack",
            f"Помилка передбачення на рівні: {err_level}", err_sig or ["рівень виведено"], "deterministic-proxy"),
        "metacognition": LensReadout(
            "Metacognitive Monitoring Loop", "monitor-controller loop",
            f"Потрібна корекція: {'так' if len(doubt) > len(confidence) else 'ні'} "
            f"(сумнів={len(doubt)}, впевненість={len(confidence)})",
            doubt or confidence or ["нейтрально"], "deterministic-proxy"),
        "conceptual_engineering": LensReadout(
            "Conceptual Engineering", "concept refactoring engine",
            f"Переоформити концепт '{(getattr(maps, maps.dominant_axis)[0].name if getattr(maps, maps.dominant_axis) else 'Дія')}' "
            f"в операційне визначення перед дією",
            [maps.dominant_axis], "deterministic-proxy"),
        "dynamical": LensReadout(
            "Dynamical Systems Theory", "trajectory engine",
            f"Траєкторія → атрактор '{attractor}'; біфуркація={'є (вибір)' if bifurcation else 'нема'}; "
            f"стабільність={'низька' if loop else 'помірна'}",
            bifurcation or [attractor], "deterministic-proxy"),
        "systems_biology": LensReadout(
            "Systems Biology of Intelligence", "multi-scale coupling map",
            f"Активні шари: {', '.join(scales)}", scales, "deterministic-proxy"),
    }


def select_lenses(readouts: dict[str, LensReadout]) -> list[str]:
    """Лінза 'активна', якщо її сигнал не дефолтний (є реальне спрацювання)."""
    active: list[str] = []
    for key, r in readouts.items():
        if r.signals and not any(s.startswith(("за замовчуванням", "рівень виведено", "нейтрально", "узгоджено", "шуму мало")) for s in r.signals):
            active.append(key)
    return active or list(readouts)[:3]
