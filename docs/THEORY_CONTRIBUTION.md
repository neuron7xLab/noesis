# THEORY_CONTRIBUTION

Міряє, чи кожна теорія реально щось дає, чи лише термінологія.

## contribution_score (0–5)
0 = лише термінологія · 1 = пояснення без зміни дії · 2 = змінює failure mode ·
3 = змінює валідацію · 4 = змінює дію · 5 = дія + валідація + failure mode.

## Wired (мають downstream-ефект)
- **switching** → дія (score 4 коли режим=collapse, інакше 1);
- **conceptual_engineering** → валідація (score 3).

## Decorative (score 0) — чесно названо
Решта 10 лінз: Active Inference, Attention Schema, GNWT, IIT, Thermodynamics, TDA,
Predictive Coding, Metacognition, Dynamical Systems, Systems Biology — лише термінологія.

## Результат (100 входів)
`decorative_theory_rate = 0.833`, `theory_contribution_mean = 0.358`,
`theory_layer_status = overloaded` (>50% score 0). Система **рекомендує вимкнути** низько-внескові.
