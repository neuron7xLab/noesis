# HUMAN_EVALUATION

Готовий формат для РЕАЛЬНОЇ людської оцінки. Жодного фейку.

## HumanEvalPacket (per case)
case_id, domain, raw_input, baseline_output (proxy_naive, позначено), cme_full_output,
cme_without_{category,theory,eiic,validator}, pairwise_questions (8), rating_schema, blind_labels.

## Правила
- Людські рейтинги НЕ заповнюються автоматично.
- Немає лейблів → `human_eval_status = "pending"`.
- proxy-оцінки й людські лейбли — ОКРЕМІ поля (`human_labels = {}` поки порожнє).

## 8 pairwise-питань
ясність · корисність дії · уникнення overclaim · збереження наміру · шум ·
чи використав би · over-engineered · ховання невизначеності.

## Статус
Генерується для кожного benchmark-кейсу (`completion_rate = 1.0`), але
`human_eval_labels_status = pending` — корисність НЕ доведена без людей.
