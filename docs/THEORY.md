# Формалізація: ізоморфізм методів до канонічних конструктів

> **Епістемічний статус.** Нижче — brain-inspired **ізоморфізм операцій**: кожен
> метод стеку відображено на формальний об'єкт із рецензованої літератури, з
> обчислюваним інваріантом і фальсифікатором. Це **не** валідоване твердження про
> нейрофізіологію і **не** AGI (див. `ethics.md`). Стверджується рівно одне:
> операція методу структурно ізоморфна названому конструкту, і цей ізоморфізм
> **перевіряється кодом** (`formal/`, тести `tests/test_formal.py`).

## Уніфікуюча аксіома: меанінг-замикання

Сенс артефакту формалізується як трійка **⟨I, A, V⟩**:
интенція `I` попередньо зафіксована, дія `A` виконана, верифікація `V` підтверджує
саме `A` (а не намір про `A`). Стек у цілому — **метакогнітивна петля керування**,
що мінімізує неузгодженість між наміреним і верифікованим станом.

Опори: Popper (1959) — демаркація через фальсифікованість; Powers (1973) —
керування за сприйняттям (perceptual control); Conant & Ashby (1970) — теорема
доброго регулятора («кожен добрий регулятор системи є моделлю цієї системи» —
формальна підстава тези «LLM-дзеркало = модель наміру»).

## Таблиця ізоморфізмів

| Метод | Формальний об'єкт | Інваріант (перевіряється) | Першоджерела |
|---|---|---|---|
| **Reflection** | Метарівнева функція моніторингу `M: object → judgment`; роздільність як γ | γ між впевненістю й коректністю визначене (∃ незв'язані пари) | Flavell 1979; Nelson & Narens 1990; Nelson 1984; Conant & Ashby 1970 |
| **Introspection** | Простір задачі `⟨s₀, G, O, C⟩`, аналіз засіб–ціль | Детермінованість: рівно 1 оператор як перша дія | Newell & Simon 1972 |
| **Goal Regression** *(екс-Reverse Inference)* | Зворотний пошук: `frontier = G \ F` | Soundness: `next_action` = перша відсутня умова `missing[0]` | Fikes & Nilsson 1971 (STRIPS); Newell & Simon 1972 |
| **Extrapolated Thinking** | Наслідки на осі психологічної дистанції `now ≺ 1d ≺ 1w ≺ 1m ≺ 1y` | Повнота: усі горизонти непорожні | Suddendorf & Corballis 2007; Trope & Liberman 2010 |
| **Finalizer** | Стиснення з обмеженням швидкості (rate-distortion): `min |T|` за збереження предикатів | Достатність=1.0 ∧ швидкість ∈ [90,110] | Tishby, Pereira & Bialek 1999; Rissanen 1978 |
| **Insight-to-Artifact** | Допустимість ⟺ носій виконуваного фальсифікатора | `validation` містить виконуваний предикат/поріг | Popper 1959; Clark & Chalmers 1998; Hutchins 1995; Kirsh & Maglio 1994 |
| **Language Expansion** | Componential-розклад; анти-дефініція як семантичне доповнення | Дизʼюнкція `1 − Jaccard ≥ 0.5` | Katz & Fodor 1963; Rosch 1975; Wittgenstein 1922 §5.6 |

Реалізація реєстру — `formal/constructs.py`; метрики — `formal/metrics.py`;
верифікатори інваріантів — `formal/verify.py`.

## Експертна нота: хибний друг у назві

Метод спочатку звався **«Reverse Inference»**. У нейровізуалізації цей термін має
вантажене й критиковане значення: висновок про когнітивний процес із патерну
активації мозку (**Poldrack 2006** — «reverse inference fallacy»: `P(процес|активація)`
не випливає з `P(активація|процес)` без базових ставок). Наша операція — це **не**
це: вона є **регресією цілі / зворотним ланцюгуванням** (Fikes & Nilsson 1971) —
строгим зворотним пошуком у просторі станів. Тому канонічна назва формального
конструкта — **Goal Regression (Backward Chaining)**, щоб уникнути імпорту хибної
конотації. Дисципліна найменування за рецензованою літературою, не за зручністю.

## Першоджерела

- Clark, A., & Chalmers, D. (1998). The extended mind. *Analysis*, 58(1), 7–19.
- Conant, R. C., & Ashby, W. R. (1970). Every good regulator of a system must be a model of that system. *Int. J. Systems Science*, 1(2), 89–97.
- Fikes, R. E., & Nilsson, N. J. (1971). STRIPS. *Artificial Intelligence*, 2(3–4), 189–208.
- Flavell, J. H. (1979). Metacognition and cognitive monitoring. *American Psychologist*, 34(10), 906–911.
- Goodman, L. A., & Kruskal, W. H. (1954). Measures of association for cross classifications. *JASA*, 49(268), 732–764.
- Hutchins, E. (1995). *Cognition in the Wild*. MIT Press.
- Katz, J. J., & Fodor, J. A. (1963). The structure of a semantic theory. *Language*, 39(2), 170–210.
- Kirsh, D., & Maglio, P. (1994). On distinguishing epistemic from pragmatic action. *Cognitive Science*, 18(4), 513–549.
- Nelson, T. O. (1984). A comparison of current measures of the accuracy of feeling-of-knowing predictions. *Psychological Bulletin*, 95(1), 109–133.
- Nelson, T. O., & Narens, L. (1990). Metamemory: A theoretical framework and new findings. *Psychology of Learning and Motivation*, 26, 125–173.
- Newell, A., & Simon, H. A. (1972). *Human Problem Solving*. Prentice-Hall.
- Poldrack, R. A. (2006). Can cognitive processes be inferred from neuroimaging data? *Trends in Cognitive Sciences*, 10(2), 59–63.
- Popper, K. R. (1959). *The Logic of Scientific Discovery*. Hutchinson.
- Powers, W. T. (1973). *Behavior: The Control of Perception*. Aldine.
- Rissanen, J. (1978). Modeling by shortest data description. *Automatica*, 14(5), 465–471.
- Rosch, E. (1975). Cognitive representations of semantic categories. *JEP: General*, 104(3), 192–233.
- Suddendorf, T., & Corballis, M. C. (2007). The evolution of foresight. *Behavioral and Brain Sciences*, 30(3), 299–313.
- Tishby, N., Pereira, F. C., & Bialek, W. (1999). The information bottleneck method. *Proc. 37th Allerton Conf.*, 368–377.
- Trope, Y., & Liberman, N. (2010). Construal-level theory of psychological distance. *Psychological Review*, 117(2), 440–463.
- Wittgenstein, L. (1922). *Tractatus Logico-Philosophicus*, §5.6.
