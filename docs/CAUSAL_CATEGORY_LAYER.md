# CAUSAL_CATEGORY_LAYER

Виправляє слабкість v0.5 (категорії інтерпретували, але не змінювали гейти).

## CategoryEffect
Кожна категорія → axis-специфічний ефект: action_bias, risk_bias, validation_bias,
next_action_delta, if_removed_delta, status (causal/weak/decorative/harmful).

Домінантна категорія = `causal` (її action_bias модифікує `selected_action`).
Інші активні = `weak`/`decorative`.

## Доказ причинності (diff, не декларація)
`category_causality_rate = 1.0`; ablation `without_category_layer` → `next_action_changed=True`
→ verdict **keep**. Тобто видалення категорій ВИМІРЮВАНО змінює дію.

## Межа чесності
Доведено, що категорія ЗМІНЮЄ дію (diff). НЕ доведено, що ПОКРАЩУЄ — це потребує людської
оцінки (HumanEvalPacket). Механічна причинність ≠ якісна користь.
