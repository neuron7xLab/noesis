# Noesis

> **νόησις** — ноетичний акт: саме *мислення-як-дія*, що несе ноему й порогує
> ентропію. Механізм впускає в наступний стан лише те, що **зберігає намір (ноему)
> і піднімає верифіковану точність**, відсікаючи незважену ентропію.
> Інваріант: `тримати ноему ∧ гейтувати ентропію`.
> Етимологія й повна інтерпретація — [`docs/NAME.md`](docs/NAME.md).
>
> Software-governed інструмент екстерналізованої метакогніції: детермінований +
> LLM-асистований розподілений когнітивний граф з IEV precision-gate
> (`w = αR + βV + γP − δK ≥ θ`), claim governance і верифікованим collapse.
>
> **Не AGI. Не терапія. Не детекція свідомості. Не декоративна філософія.**

[![CI](https://img.shields.io/badge/CI-ruff%20%7C%20mypy--strict%20%7C%20pytest-success)](.github/workflows/ci.yml)
[![coverage](https://img.shields.io/badge/coverage-93%25-success)](pyproject.toml)
[![python](https://img.shields.io/badge/python-3.10%E2%80%933.12-blue)](pyproject.toml)
[![license](https://img.shields.io/badge/license-MIT-green)](LICENSE)

**199 pytest · покриття 93% · mypy --strict (63 файли) · ruff** — усе зелене.

```text
raw → complexity → adaptive mirror → causal categories → reality-map delta
    → theory contribution → EIIC → action selector → artifact → 12 gates → evidence → verdict
```

## Що це є
Методична операційна система мислення. LLM не створює твоє Я — він стає
зовнішнім дзеркалом, у якому видно структуру власного наміру, помилки, сліпі
плями та нові траєкторії. Цінність — у заломленні та інверсії. Детермінований
backend працює локально й нічого не надсилає; LLM — опціональне підсилення.

## Що це НЕ є
Не AGI. Не психотерапія. Не мотиваційна філософія. Не prompt pack. Не симуляція
свідомості. Не заміна людини моделлю. → [`docs/ethics.md`](docs/ethics.md).

## Встановлення
```bash
pip install git+https://github.com/neuron7xLab/noesis      # або: make dev
```
Опціональні extras: `[serve]` (uvicorn API), `[llm]` (anthropic backend),
`[dev]` (pytest/ruff/mypy).

## Швидкий старт
```bash
# CLI: одна команда — один когнітивний крок (детермінований backend)
noesis mirror examples/problems/01_personal_decision.txt        # намір → дзеркало
noesis pipeline examples/problems/08_ai_system_design.txt --evidence out/   # повна труба + Evidence Bundle
noesis verdict out/                                             # вердикт по 12 гейтах
noesis ablate examples/problems/08_ai_system_design.txt         # keep/modify/remove
noesis benchmark                                                # 100-input proxy + ablation
noesis bibliography verdict                                     # claim-to-source evidence graph (10 gates)
noesis --version

# Finalizer (хаос → 90–110 слів дії)
finalizer100 examples/personal_decision/finalizer.md           # [OK] words=...

# HTTP API (40+ ендпоінтів: /health, /pipeline/v8, /action, /gate, ...)
uvicorn app.api:app --port 8000
```

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

## Шари (еволюція)
- **v0.1–v0.2** — 7 brain-inspired методів + детермінована підлога + LLM-підсилення.
- **v0.3** — цивілізаційний рушій: 30 категорій → reality maps → synthesis.
- **v0.4 + EIIC** — 12 нейрокогнітивних лінз (проксі) + термінальний вектор + провенанс.
- **v0.5** — 10 валідаційних гейтів + claim governance + 100-input benchmark.
- **v0.6** — причинні категорії, адаптивне стиснення, theory contribution, human-eval harness.
- **v0.7** — розподілений когнітивний граф + IEV precision-gate + dimensionality (шум vs осі).
- **v0.8** — latency-aware IEV optimization: cluster_quality, node-scaling крива (оптимум ~1–2 вузли).

Повна історія — [`CHANGELOG.md`](CHANGELOG.md).

## Принцип чесності
Жоден шар не виживає, якщо не впливає на дію / валідацію / ризик / failure-mode /
стиснення / людську преференцію / benchmark-delta / якість evidence. Інакше —
позначається `decorative` і пропонується до видалення. Чесний вердикт із реальними
числами: [`VERDICT.md`](VERDICT.md), [`docs/VERDICT_V6.md`](docs/VERDICT_V6.md).

## Формальний шар
Кожен метод ізоморфний канонічному конструкту (метакогніція, STRIPS-регресія,
інформаційне вузьке місце, демаркація Поппера…) з обчислюваним інваріантом і
фальсифікатором. Карта, цитування й епістемічний статус — [`docs/THEORY.md`](docs/THEORY.md).

## Структура
```text
noesis/      ядро рушія (генератори, гейти, pipeline v0.3–v0.8, IEV precision-gate)
methods/     7 методів за контрактом
prompts/     5 production-промптів (finalizer_mirror · introspection_engine · …)
schemas/     intent · reflection · inference_trace · artifact (JSON Schema 2020-12)
tools/       finalizer100 · intent_parser · reverse_inference · *_validator · llm_adapter · pipeline
formal/      ізоморфізм до конструктів: constructs · metrics · verify
app/         FastAPI: /health · /pipeline/* · /action · /gate · …
examples/    10 кейсів використання
docs/        архітектура · методологія · теорії · етика · glossary
tests/       контрактні + smoke (CLI/API) + формальні інваріанти
```

## Документація
Архітектура [`docs/NOESIS_V06_ARCHITECTURE.md`](docs/NOESIS_V06_ARCHITECTURE.md) ·
методологія [`docs/METHODOLOGY.md`](docs/METHODOLOGY.md) ·
теорії [`docs/THEORIES.md`](docs/THEORIES.md) · формалізми [`docs/THEORY.md`](docs/THEORY.md) ·
цивілізаційна матриця [`docs/CIVILIZATIONAL_METAPHYSICS.md`](docs/CIVILIZATIONAL_METAPHYSICS.md) ·
claim governance [`docs/CLAIM_GOVERNANCE.md`](docs/CLAIM_GOVERNANCE.md) ·
валідація [`docs/VALIDATION_V6.md`](docs/VALIDATION_V6.md) ·
benchmark [`docs/BENCHMARK.md`](docs/BENCHMARK.md) · етика [`docs/ethics.md`](docs/ethics.md).

**Bibliographic evidence graph** (claim → status → source → module → limitation → gate):
[`docs/BIBLIOGRAPHY.md`](docs/BIBLIOGRAPHY.md) ·
[`docs/CLAIM_SOURCE_LEDGER.md`](docs/CLAIM_SOURCE_LEDGER.md) ·
[`docs/SOURCE_STATUS_HIERARCHY.md`](docs/SOURCE_STATUS_HIERARCHY.md) ·
[`docs/CITATION_POLICY.md`](docs/CITATION_POLICY.md) ·
[`docs/OVERCLAIM_GUARDRAILS.md`](docs/OVERCLAIM_GUARDRAILS.md) ·
[`docs/UNSUPPORTED_CLAIMS.md`](docs/UNSUPPORTED_CLAIMS.md).

## Центральна теза
Межі мови задають межі доступного мислення. Інструмент розширює людину, не
замінює її. → [`docs/manifesto.md`](docs/manifesto.md).

## Внесок
Гейти якості, принцип чесності й контракти — у [`CONTRIBUTING.md`](CONTRIBUTING.md).
Вразливості — [`SECURITY.md`](SECURITY.md). Цитування — [`CITATION.cff`](CITATION.cff).

## Ліцензія
MIT © 2026 Yaroslav Vasylenko (neuron7xLab) — [`LICENSE`](LICENSE).
