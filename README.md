# Cognitive Mirror Methods

> Практичний brain-inspired репозиторій методів, протоколів, валідаторів і
> LLM-інтерфейсів для розширення людського мислення через мову, рефлексію,
> інтроспекцію, реверсивний інференс, зовнішнє обчислення та перевірні артефакти.

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
tools/       finalizer100 · intent_parser · reverse_inference · *_validator · artifact_checker
app/         FastAPI: /health · /finalize · /intent
examples/    10 кейсів використання
docs/        manifesto · philosophy · ethics · glossary
tests/       контрактні + smoke-тести
```

## Центральна теза
Межі мови задають межі доступного мислення. Інструмент розширює людину, не
замінює її. → `docs/manifesto.md`.

## Ліцензія
MIT © 2026 Yaroslav Vasylenko (neuron7xLab).
