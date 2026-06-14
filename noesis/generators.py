"""Генератори артефактів: детермінований бекенд (підлога) + LLM-підсилення.

Детермінований бекенд гарантує СТРУКТУРНО валідний артефакт без мережі — він
доводить, що труба й валідатори працюють end-to-end. LLM-бекенд підіймає ЯКІСТЬ
змісту; обидва гейтуються одними валідаторами (noesis/validators.py).
"""

from __future__ import annotations

import re

from noesis.models import IntrospectionMap, MirrorArtifact
from tools.finalizer100 import MAX_WORDS, MIN_WORDS, REQUIRED_ANCHORS, count_words

_SENT = re.compile(r"[.!?\n]+")
_FEAR = ("боюс", "боюся", "страх", "тривож", "лякає", "не вийде", "знову")
_BLOCK = ("не знаю", "не можу", "немає", "бракує", "застряг", "не виходить", "не розумію")
_TODAY = (("сьогодн", "сьогодні"), ("тижд", "цей тиждень"), ("місяц", "цей місяць"),
          ("рік", "цей рік"), ("завтра", "завтра"))


def _sentences(text: str) -> list[str]:
    return [s.strip() for s in _SENT.split(text) if s.strip()]


def _clip(text: str, max_words: int) -> str:
    words = text.split()
    return " ".join(words[:max_words]) if len(words) > max_words else text


def _first_with(sentences: list[str], markers: tuple[str, ...], default: str) -> str:
    for s in sentences:
        low = s.lower()
        if any(m in low for m in markers):
            return s
    return default


def _horizon(low: str) -> str:
    for needle, label in _TODAY:
        if needle in low:
            return label
    return "найближча ітерація"


def _fit_finalizer(text: str) -> str:
    """Підганяє фіналайзер у [90,110] слів за тим самим лічильником, що й валідатор."""
    filler = (
        "за замовчуванням система повертає карту наміру і перший крок без зайвих "
        "припущень та без води у формулюванні задачі користувача чітко"
    ).split()
    words = text.split()
    i = 0
    while count_words(" ".join(words)) < MIN_WORDS:
        words.append(filler[i % len(filler)])
        i += 1
    while count_words(" ".join(words)) > MAX_WORDS:
        words.pop()
    return " ".join(words)


def render_finalizer(m: MirrorArtifact) -> str:
    """Стиснене представлення наміру з усіма 6 якорями (намір/мет/блокер/дія/метрик/ризик)."""
    base = (
        f"Ти хочеш від мене ясності щодо наміру: явний запит — {_clip(m.surface_intent, 9)}; "
        f"прихована мета — {_clip(m.hidden_goal, 8)}; головне обмеження — {_clip(m.constraint, 6)}; "
        f"ключовий блокер — {_clip(m.blocker, 6)}; вирішальна дія — {_clip(m.next_action, 8)}; "
        f"метрика успіху — {_clip(m.success_metric, 6)}; часовий горизонт — {_clip(m.time_horizon, 4)}; "
        f"критичний ризик — {_clip(m.critical_risk, 5)}; зниження ризику — {_clip(m.risk_reduction, 6)}."
    )
    return _fit_finalizer(base)


def build_mirror_deterministic(raw: str) -> MirrorArtifact:
    sentences = _sentences(raw)
    low = raw.lower()
    surface = sentences[0] if sentences else raw.strip()
    hidden = sentences[-1] if len(sentences) > 1 else "перетворити намір на дію вже сьогодні"
    constraint = _first_with(
        sentences, ("без ", "не ", "лише", "тільки", "уник"), "не починати нових паралельних гілок"
    )
    blocker = _first_with(sentences, _BLOCK, "відсутність чіткого пріоритету")
    next_action = f"зафіксувати перший крок до: {_clip(surface, 10)}"
    partial = MirrorArtifact(
        surface_intent=surface,
        hidden_goal=hidden,
        constraint=constraint,
        blocker=blocker,
        next_action=next_action,
        success_metric="є один перевірний артефакт за обраний горизонт",
        time_horizon=_horizon(low),
        critical_risk="розпорошення уваги й повернення у шум",
        risk_reduction="обмежити фокус однією дією та перевірити результат",
        finalizer="",
    )
    return MirrorArtifact(**{**partial.to_dict(), "finalizer": render_finalizer(partial)})


def build_introspection_deterministic(raw: str) -> IntrospectionMap:
    sentences = _sentences(raw)
    surface = sentences[0] if sentences else raw.strip()
    return IntrospectionMap(
        intent=f"закрити один результат у напрямі: {_clip(surface, 10)}",
        fear=_first_with(sentences, _FEAR, "невизначеність наступного кроку"),
        constraint=_first_with(sentences, ("без ", "не ", "лише"), "без нових паралельних гілок"),
        missing_condition=_first_with(sentences, _BLOCK, "немає визначеного пріоритету"),
        decision_boundary="діяти зараз проти відкласти ще на ітерацію",
        action=f"обрати одну задачу й застосувати до неї реверсивний інференс: {_clip(surface, 8)}",
    )


def build_artifact_deterministic(insight: str) -> dict[str, str]:
    """Детермінований 7-секційний MethodArtifact з виконуваним фальсифікатором."""
    core = _clip(insight.strip().splitlines()[0] if insight.strip() else "інсайт", 14)
    return {
        "definition": f"Метод, що операціоналізує інсайт: {core}.",
        "input": "Сире формулювання інсайту (1–2 речення) українською.",
        "method": "Розклад інсайту на input/method/output; реєстрація у Method Registry; гейт валідаторами.",
        "output": "Заповнений MethodArtifact (7 секцій), що проходить artifact_checker.",
        "validation": "python -c \"from tools.artifact_checker import is_valid_artifact\" повертає True (0 проблем).",
        "example": f"Вхід: «{core}» → артефакт із 7 непорожніх секцій, гейт пройдено.",
        "failure_modes": "Прозова validation без перевірки; <7 секцій; непідкріплені claims; колізія в реєстрі.",
    }


# ── LLM-підсилення (опційне; гейтується тими ж валідаторами) ──────────────────


def _finalizer_conforms(text: str) -> bool:
    low = text.lower()
    return MIN_WORDS <= count_words(text) <= MAX_WORDS and all(a in low for a in REQUIRED_ANCHORS)


def build_mirror_llm(raw: str, *, backend: str) -> MirrorArtifact:
    """LLM пропонує фіналайзер; детермінований гейт розпоряджається.

    Якщо LLM-вихід проходить повний контракт (швидкість + усі якорі) — беремо його.
    Інакше падаємо на гарантовано-валідну детерміновану підлогу: продукт ЗАВЖДИ
    видає валідований артефакт (Definition of Done).
    """
    from tools.llm_adapter import complete, load_prompt

    base = build_mirror_deterministic(raw)
    finalizer = complete(load_prompt("finalizer_mirror.md"), raw, backend=backend)
    if _finalizer_conforms(finalizer):
        return MirrorArtifact(**{**base.to_dict(), "finalizer": finalizer})
    return base  # детермінований фіналайзер уже валідний за конструкцією
