# Приклад: Reverse Inference для дослідницької задачі

**Ціль:** дослідницький результат опубліковано як препринт.

```python
from tools.reverse_inference import plan_backwards

trace = plan_backwards(
    target_state="препринт опубліковано на arXiv",
    current_facts=["є чернетка тексту", "є дані"],
    required_conditions=[
        "є чернетка тексту",
        "є дані",
        "результат відтворюється з фіксованим seed",
        "є endorsement на arXiv",
    ],
)
print(trace.missing_constraints)  # ['результат відтворюється з фіксованим seed', 'є endorsement на arXiv']
print(trace.next_action)          # Забезпечити: результат відтворюється з фіксованим seed
```

**Висновок:** наступна дія — не «писати текст» (він є), а закрити відтворюваність.
Метод відсік уявний пріоритет і показав реальну першу відсутню умову.
