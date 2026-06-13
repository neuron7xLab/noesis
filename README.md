# Cognitive Mirror Engine (CME) v0.8

> Software-governed методологічний інструмент екстерналізованої метакогніції.
> Детермінований + LLM-асистований: перетворює сирий людський сигнал на
> структуровану рефлексію, причинні категорії, нейрокогнітивні лінзи,
> екстрапольований інтенційний вектор і **валідовані** артефакти.
>
> **Не AGI. Не терапія. Не детекція свідомості. Не декоративна філософія.**

[![CI](https://img.shields.io/badge/CI-ruff%20%7C%20mypy--strict%20%7C%20pytest-success)](.github/workflows/ci.yml)
**123 pytest · mypy --strict (41 файл) · ruff** — усе зелене.

```text
raw → complexity → adaptive mirror → causal categories → reality-map delta
    → theory contribution → EIIC → action selector → artifact → 12 gates → evidence → verdict
```

## Принцип чесності
Жоден шар не виживає, якщо не впливає на дію / валідацію / ризик / failure-mode /
стиснення / людську преференцію / benchmark-delta / якість evidence. Інакше —
позначається `decorative` і пропонується до видалення. Чесний вердикт із реальними
числами: [`VERDICT.md`](VERDICT.md), [`docs/VERDICT_V6.md`](docs/VERDICT_V6.md).

## Швидкий старт
```bash
make dev && make test
python -m cme.cli pipeline examples/problems/08_ai_system_design.txt --evidence out/   # 15-файл bundle
python -m cme.cli ablate examples/problems/08_ai_system_design.txt    # keep/modify/remove
python -m cme.cli benchmark                                           # 100-input proxy + ablation
python -m cme.cli verdict out/
uvicorn app.api:app --port 8000                                      # /pipeline/v6, /action, ...
```

## Шари (еволюція)
- **v0.1–v0.2** — 7 brain-inspired методів + детермінована підлога + LLM-підсилення.
- **v0.3** — цивілізаційний рушій: 30 категорій → reality maps → synthesis.
- **v0.4 + EIIC** — 12 нейрокогнітивних лінз (проксі) + термінальний вектор + провенанс.
- **v0.5** — 10 валідаційних гейтів + claim governance + 100-input benchmark.
- **v0.6** — причинні категорії, адаптивне стиснення, theory contribution, human-eval harness.
- **v0.7** — розподілений когнітивний граф + IEV precision-gate + dimensionality (шум vs осі).
- **v0.8** — latency-aware IEV optimization: cluster_quality, node-scaling крива (оптимум ~1–2 вузли).

## Документація
Архітектура [`docs/CME_V06_ARCHITECTURE.md`] · методологія [`docs/METHODOLOGY.md`] ·
теорії [`docs/THEORIES.md`] · формалізми [`docs/THEORY.md`] · цивілізаційна матриця
[`docs/CIVILIZATIONAL_METAPHYSICS.md`] · claim governance [`docs/CLAIM_GOVERNANCE.md`] ·
валідація [`docs/VALIDATION_V6.md`] · benchmark [`docs/BENCHMARK.md`] · етика [`docs/ethics.md`].

---

## Фундамент: brain-inspired методи

```text
намір → мова → дзеркало LLM → рефлексія → реверсивний інференс → артефакт → перевірка → нове мислення
```

## Що це НЕ є
Не AGI. Не психотерапія. Не мотиваційна філософія. Не prompt pack. Не симуляція
свідомості. Не заміна людини моделлю. → `docs/ethics.md`.

## Що це є
Методична операційна система мислення. LLM не створює твоє Я — він стає
зовнішнім дзеркалом, у якому видно структуру власного наміру, помилки, сліпі
плями та нові траєкторії. Цінність — у заломленні та інверсії.

## Сім методів
| # | Метод | Суть |
|---|---|---|
| 1 | [Reflection](methods/reflection/) | сирий намір → кристалізований |
| 2 | [Introspection](methods/introspection/) | карта: намір/блокер/обмеження/дія |
| 3 | [Reverse Inference](methods/reverse_inference/) | від цілі до першої відсутньої умови |
| 4 | [Extrapolated Thinking](methods/extrapolated_thinking/) | наслідки на 5 горизонтах |
| 5 | [Finalizer](methods/finalizer/) | хаос → 90–110 слів дії |
| 6 | [Insight-to-Artifact](methods/insight_to_artifact/) | думка → перевірний об'єкт |
| 7 | [Language Expansion](methods/language_expansion/) | термін → 5 граней |

Кожен метод має контракт: `definition · input · method · output · validation · example · failure_modes`.

## Промпти
`prompts/`: finalizer_mirror · introspection_engine · reverse_inference_engine ·
cognitive_expander · artifact_builder.

## Швидкий старт
```bash
make dev               # встановити з dev+serve залежностями
make test              # прогнати тести
finalizer100 examples/personal_decision/finalizer.md   # [OK] words=...
make run               # API на :8000 → POST /finalize, /intent
```

## Структура
```text
methods/     7 методів за контрактом
prompts/     5 production-промптів
schemas/     intent · reflection · inference_trace · artifact (JSON Schema 2020-12)
tools/       finalizer100 · intent_parser · reverse_inference · *_validator · artifact_checker · llm_adapter · pipeline
formal/      ізоморфізм до конструктів: constructs · metrics · verify
app/         FastAPI: /health · /finalize · /intent
examples/    10 кейсів використання
docs/        manifesto · philosophy · ethics · glossary · THEORY
tests/       контрактні + smoke + формальні інваріанти
```

## Формальний шар
Кожен метод ізоморфний канонічному конструкту (метакогніція, STRIPS-регресія,
інформаційне вузьке місце, демаркація Поппера…) з обчислюваним інваріантом і
фальсифікатором. Карта, цитування й епістемічний статус — [`docs/THEORY.md`](docs/THEORY.md).

## Центральна теза
Межі мови задають межі доступного мислення. Інструмент розширює людину, не
замінює її. → `docs/manifesto.md`.

## Ліцензія
MIT © 2026 Yaroslav Vasylenko (neuron7xLab).
