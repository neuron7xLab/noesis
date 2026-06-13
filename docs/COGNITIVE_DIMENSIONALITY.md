# COGNITIVE_DIMENSIONALITY

Чи граф додає КОРИСНІ ортогональні осі, чи лише шум (`cme/dimensionality.py`).

## Визначення
- **expanded** = initial + 12 теоретичних лінз + 1 EIIC (LLM-пропозиція осей).
- **retained** = осі, що ПЕРЕЖИЛИ верифікацію (causal + contributing theories + EIIC).
- **noise_axes** = expanded − retained (декоративні теорії = шум).
- **useful_dimensionality_gain** = нові ортогональні осі, що пережили верифікацію.
- **net_cognitive_gain** = retained / proposed.

## Реальні числа (100 входів)
`noise_rejection_rate_mean = 0.696` · `noise_dominated_rate = 1.0` ·
`useful_dimensionality_gain_mean = 3.0` · net≈0.23.

**Квантифікований доказ тези «варіація ≠ розмірність»:** LLM пропонує ~14 осей,
верифікація втримує ~4, ~10 — шум. Цінність графа — у ВІДКИДАННІ, не в генерації.
