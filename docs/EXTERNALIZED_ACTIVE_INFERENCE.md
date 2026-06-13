# EXTERNALIZED_ACTIVE_INFERENCE

НЕ автономний active inference (Friston). Петля НЕ замкнута сенсор-моторно —
вона замкнута вручну через IEV-гейт. Людина = precision-weight модулятор.

| Роль | Функція |
|---|---|
| Human | precision-weight модулятор, тримач інтенційного prior, фінальний валідатор |
| LLM | генератор гіпотез, семантичний розширювач, виробник артефактів, шукач failure-mode |
| Auditor/Verifier | частковий генератор precision-weights (`cme/entropy_ledger.py`) |

**Критично для масштабування:** без автономного замикання ентропія контуру обмежена
IEV-bandwidth людини. Semi-automated precision layer масштабує ПРОПУСКНУ судження,
не його РОЗМІРНІСТЬ — поки auditor/verifier не ортогональні людині, вони клонують її prior.
