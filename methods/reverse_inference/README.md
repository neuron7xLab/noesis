# Reverse Inference Method — Мислення назад

> Від бажаного результату до поточного стану. Перша відсутня умова = наступна дія.

> **Формальна назва — Goal Regression (Backward Chaining).** Термін «reverse
> inference» у нейровізуалізації позначає інше й критиковане поняття (Poldrack
> 2006, «reverse inference fallacy»). Наша операція — регресія цілі / зворотне
> ланцюгування (Fikes & Nilsson 1971). Деталі: [`docs/THEORY.md`](../../docs/THEORY.md).

## definition
Побудова траєкторії від цільового стану назад до теперішнього через ланцюг
необхідних умов, щоб знайти першу відсутню ланку.

## input
Чітко названий цільовий стан + список наявних фактів.

## method
1. Назвати `target_state` одним реченням.
2. Виписати `required_conditions` — без чого ціль неможлива.
3. Звірити з наявними фактами → `missing_constraints`.
4. Перша відсутня умова стає `next_action`.

Інструмент: `tools/reverse_inference.py:plan_backwards`.

## output
`inference_trace`: `target_state → required_conditions → missing_constraints → next_action`
(схема `schemas/inference_trace.schema.json`).

## validation
- Слід валідний за схемою (`validate_inference_trace`).
- `next_action` посилається саме на **першу** відсутню умову, не на ціль загалом.

## example
```python
plan_backwards(
    target_state="репо опубліковано",
    current_facts=["код є"],
    required_conditions=["код є", "тести зелені", "ліцензія"],
)
# → missing=["тести зелені", "ліцензія"]; next_action="Забезпечити: тести зелені"
```

## failure_modes
- **Стрибок до цілі**: дія описує результат, а не наступний крок → завжди бери `missing[0]`.
- **Неповні умови**: пропущена прихована умова → ціль «досяжна», але насправді ні.
- **Змішування рівнів**: умови різного масштабу в одному списку → розділи горизонти.
