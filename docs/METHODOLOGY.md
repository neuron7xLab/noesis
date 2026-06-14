# METHODOLOGY — CME v0.5

Формальний метод екстерналізованої метакогніції. Чотири методологічні страти;
кожна детермінована (де можливо) і гейтована. Не наука з фантастики.

## Чотири страти
| Стратум | Призначення | Об'єкт | Модуль |
|---|---|---|---|
| 1 — Intentional | витягти, що користувач реально хоче | IntentMirror (9 полів + provenance) | `noesis/generators.py` |
| 2 — Category/Metaphysics | які категорії керують інтерпретацією | RealityMap (домінанта/сплячі осі) | `noesis/ontology.py` |
| 3 — Neurocognitive | теорії як оператори, не декор | TheoryLensReport (12 проксі) | `noesis/theories.py` |
| 4 — EIIC | термінальний вектор при масштабуванні | EIICReport (provenance-теговано) | `noesis/eiic.py` |

## Сигнал/шум
Кожен шар відокремлює сигнал (намір/категорія/режим/вектор) від шуму (емоція,
надвпевненість, метафора без перевірки). Шум вимірюється проксі
(`thermodynamics` лінза: ентропія = шумові маркери / токени).

## Труба v0.5
```
raw → intent mirror → signal/noise → category extraction → theory lenses
    → reality maps → reverse inference → EIIC → artifact → 10 gates → evidence → next action
```
Реалізація: `noesis/pipeline_v5.py:run_v5`. Кожен прогін → 10 валідаційних гейтів
(`run_gates`) + claim governance + baseline-порівняння.

## Що система робить і чого НЕ робить
Робить: екстерналізує, стискає (де вхід довгий), структурує, валідує,
операціоналізує. НЕ робить: не «розуміє» як людина, не діагностує, не детектує
свідомість, не претендує на AGI. Межі — `docs/CLAIM_GOVERNANCE.md`, `docs/ethics.md`.
