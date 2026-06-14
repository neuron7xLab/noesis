# METHODS — модулі CME v0.3

Сім продуктивних модулів. Кожен детермінований (де можливо) і гейтований.

## 1. Category Extractor — `noesis/ontology.py:extract_categories`
- **input:** raw text. **output:** список активних категорій
  (`category, axis, function, failure_mode, matched`).
- **failure_modes:** надмірне/недостатнє спрацювання маркерів; дефолт маскує порожнечу.

## 2. Reality Map Builder — `noesis/ontology.py:build_reality_maps`
- **input:** активні категорії. **output:** три карти (Європа/США/Китай) +
  домінантна вісь + сплячі осі.
- **failure_modes:** одновісна сліпота (дві сплячі осі) — це сигнал, не помилка.

## 3. Synthesis Axis Engine — `noesis/synthesis.py:build_synthesis`
- **input:** три карти. **output:** `preserve` (істина/Європа) · `test`
  (наслідок/США) · `evolve` (процес/Китай) · `refuse` (пастка домінантної осі).
- **failure_modes:** спляча вісь → відповідна порада вироджується в попередження.

## 4. Reverse Inference Engine — `noesis/synthesis.py:build_reverse_plan`
- **input:** бажаний стан (mirror.hidden_goal). **output:** `first_missing_condition`
  · `blocking_assumption` · `minimum_viable_intervention` · `validation_event`.
- **failure_modes:** неповні умови → хибно «досяжно»; припущення евристичне.

## 5. Artifact Builder — `noesis/generators.py:build_artifact_deterministic`
- **input:** інсайт. **output:** MethodArtifact з 7 секцій
  (definition · input · method · output · validation · example · failure_modes).
- **failure_modes:** прозова validation; <7 секцій; доказ-театр.

## 6. Validator Layer — `noesis/validators.py`
Перевіряє: category completeness · axis separation · artifact completeness ·
forbidden claims · unverifiable metaphors · AGI overclaim · therapy overclaim ·
empty abstraction · missing next action. Деталі — [`VALIDATION.md`](VALIDATION.md).

## 7. Pipeline + Evidence Bundle — `noesis/engine.py`
Повна труба v0.3 → 8-файловий Evidence Bundle. CLI: `noesis pipeline input.txt --evidence out/`.
