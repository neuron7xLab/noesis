# VALIDATION — модель валідації

Жодний LLM-вихід не довіряється напряму: кожен артефакт гейтується детермінованими
перевірками. `passed` = кон'юнкція всіх checks.

## Перевірки за типом артефакту
| Тип | Checks |
|---|---|
| categories | category_completeness (≥1), axis_separation (вісь∈{europe,usa,china}) |
| reality_maps | maps_nonempty, dominant_axis_valid |
| synthesis_axis | four_axes_present (preserve/test/evolve/refuse) |
| mirror | required_fields(9), word_count(90–110), anchor_terms(6), signal_noise_separation, forbidden_claims, hallucination_risk |
| introspection | required_fields(6), single_action_determinacy, forbidden_claims, hallucination_risk |
| artifact | seven_sections, executable_falsifier(Popper), forbidden_claims, hallucination_risk |
| guards | forbidden_claims, agi_overclaim, therapy_overclaim, missing_next_action, empty_abstraction, unverifiable_metaphors |

## Forbidden / overclaim
`cme/forbidden.py`: жорсткий список заборонених claims (AGI, діагноз, лікування,
заміна судження, фізичне розширення свідомості…). Будь-яке спрацювання → FAIL.

## Hallucination risk (груба проксі)
Маркери надвпевненості ("гарантовано", "доведено науково") + числа без джерела →
рівні low/medium/high; `high` → FAIL. Це проксі, не вимірювання фактичності.

## Unverifiable metaphors / empty abstraction
Метафора у валідації допустима лише якщо поруч є виконуваний фальсифікатор;
артефакт без дії+фальсифікатора = порожня абстракція → FAIL.
