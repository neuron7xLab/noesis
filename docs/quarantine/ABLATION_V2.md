# ABLATION_V2

8 варіантів; keep/modify/remove за впливом на ДІЮ (не на власний гейт).

## Правило рішення
- **keep** — видалення змінює next_action АБО (validator) лишає систему сліпою;
- **modify** — ламає лише власний гейт, дію не змінює (структура без рішення);
- **remove** — не змінює нічого.

## Результат (ai_system_design)
| Варіант | verdict |
|---|---|
| without_category_layer | **keep** (змінює дію) |
| without_artifact_validation | **keep** (сліпа безпека) |
| without_reality_maps | modify (лише gate3) |
| without_eiic | modify (лише gate7) |
| without_claim_governance | modify (лише gate6) |
| without_theory_layer | **remove** (0 змін) |
| without_adaptive_compression | **remove** (для довгого входу) |

Доказ не-декоративності: category_layer і artifact_validation — load-bearing;
theory_layer — кандидат на видалення.
