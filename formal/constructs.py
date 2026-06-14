"""Реєстр конструктів: метод стеку → формальний об'єкт → цитування → інваріант.

Це формальна онтологія системи. Кожен запис стверджує ізоморфізм між
операцією методу й канонічним конструктом, з фальсифікатором інваріанта.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Construct:
    key: str
    method: str
    literature: str
    citations: tuple[str, ...]
    formal_object: str
    invariant: str
    falsifier: str


REGISTRY: dict[str, Construct] = {
    "reflection": Construct(
        key="reflection",
        method="Reflection",
        literature="Метакогнітивний моніторинг (object-level ↔ meta-level)",
        citations=("Flavell 1979", "Nelson & Narens 1990", "Conant & Ashby 1970"),
        formal_object="Метарівнева функція моніторингу M: object-state → judgment, "
        "з роздільністю, вимірюваною γ (Nelson 1984).",
        invariant="Моніторинг інформативний: γ між впевненістю й коректністю визначене (∃ незв'язані пари).",
        falsifier="Усі пари зв'язані → γ невизначене → дзеркало не несе метакогнітивної інформації.",
    ),
    "introspection": Construct(
        key="introspection",
        method="Introspection",
        literature="Простір задачі та аналіз засіб–ціль",
        citations=("Newell & Simon 1972",),
        formal_object="Простір задачі ⟨s₀, G, O, C⟩: початковий стан, ціль, оператори, обмеження.",
        invariant="Детермінованість: рівно один оператор обрано першою дією.",
        falsifier="Нуль або >1 кандидатів першої дії → неоднозначність наступного кроку.",
    ),
    "goal_regression": Construct(
        key="goal_regression",
        method="Reverse Inference → Goal Regression (Backward Chaining)",
        literature="Регресія цілі / зворотне ланцюгування у плануванні",
        citations=("Fikes & Nilsson 1971 (STRIPS)", "Newell & Simon 1972"),
        formal_object="Зворотний пошук у просторі станів: frontier = G \\ F; "
        "next_action — оператор, що досягає першої відсутньої умови.",
        invariant="Коректність (soundness): next_action посилається саме на missing[0].",
        falsifier="next_action описує ціль загалом, а не першу відсутню умову.",
    ),
    "extrapolated_thinking": Construct(
        key="extrapolated_thinking",
        method="Extrapolated Thinking",
        literature="Ментальна подорож у часі та теорія рівня конструювання",
        citations=("Suddendorf & Corballis 2007", "Trope & Liberman 2010"),
        formal_object="Відображення наслідків на впорядкованій осі психологічної дистанції "
        "{now ≺ 1d ≺ 1w ≺ 1m ≺ 1y}.",
        invariant="Повнота: усі канонічні горизонти присутні й непорожні.",
        falsifier="Порожній горизонт → сліпий хвіст, відкладений наслідок невидимий.",
    ),
    "finalizer": Construct(
        key="finalizer",
        method="Finalizer",
        literature="Інформаційне вузьке місце / мінімальна довжина опису",
        citations=("Tishby, Pereira & Bialek 1999", "Rissanen 1978"),
        formal_object="Стиснення з обмеженням швидкості: min|T| за умови збереження "
        "обов'язкових предикатів; швидкість ∈ [90,110] слів.",
        invariant="Достатність=1.0 (усі 6 якорів) ∧ швидкість у межах.",
        falsifier="Втрачений якір (достатність<1) або вихід за межі швидкості.",
    ),
    "insight_to_artifact": Construct(
        key="insight_to_artifact",
        method="Insight-to-Artifact",
        literature="Критерій демаркації / розширене та розподілене пізнання",
        citations=("Popper 1959", "Clark & Chalmers 1998", "Hutchins 1995", "Kirsh & Maglio 1994"),
        formal_object="Артефакт допустимий ⟺ несе виконуваний фальсифікатор "
        "(секція validation — перевірка, а не проза).",
        invariant="Фальсифікованість: validation містить виконуваний предикат або поріг.",
        falsifier="validation суто прозова → твердження непроверне → гіпотеза, не факт.",
    ),
    "language_expansion": Construct(
        key="language_expansion",
        method="Language Expansion",
        literature="Componential semantics / межі мови",
        citations=("Katz & Fodor 1963", "Rosch 1975", "Wittgenstein 1922 §5.6"),
        formal_object="Componential-розклад терміна на 5 граней; анти-дефініція як "
        "семантичне доповнення дефініції.",
        invariant="Дизʼюнкція: 1 − Jaccard(дефініція, анти-дефініція) ≥ 0.5.",
        falsifier="Анти-дефініція = перефраз дефініції (дизʼюнкція < 0.5) → межу не розсунуто.",
    ),
}

# Уніфікуюча аксіома стеку: МЕАНІНГ-ЗАМИКАННЯ.
MEANING_CLOSURE_AXIOM = (
    "Сенс = ⟨I, A, V⟩: намір I попередньо зафіксований, дія A виконана, "
    "верифікація V підтверджує A (Popper 1959; Powers 1973 — керування за неузгодженістю; "
    "Conant & Ashby 1970 — добрий регулятор моделює систему). Стек у цілому — "
    "метакогнітивна петля керування, що мінімізує неузгодженість між наміреним і верифікованим станом."
)
