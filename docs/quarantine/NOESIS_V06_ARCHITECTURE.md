# CME v0.6 — Architecture

Труба, що ДОВОДИТЬ, які шари змінюють рішення (а не додають слова).

```
raw → complexity_estimator → adaptive_intent_mirror → category_extractor
    → category_action_linker (CategoryEffect) → reality_map_delta
    → theory_contribution_tracker → EIIC → action_selector → artifact
    → 12 validation_gates → ablation_runner → human_eval_packet → evidence → verdict
```

| Модуль | Файл | Що дає (виміряно) |
|---|---|---|
| Complexity Estimator | `noesis/complexity.py` | режим виходу (micro…protocol), word budget |
| Adaptive Intent Mirror | `noesis/adaptive.py` | compression_status (no padding) |
| Causal Category Layer | `noesis/causal.py` | CategoryEffect → змінює next_action (diff-доведено) |
| Reality Map Delta | `noesis/causal.py` | дія під кожною віссю + low_map_utility |
| Theory Contribution | `noesis/causal.py` | score 0–5 per theory, decorative flag |
| Action Selector v2 | `noesis/causal.py` | одна дія + reversibility + pipeline_overbuilt |
| Human Eval Harness | `noesis/human_eval.py` | packet, status=pending, без фейк-оцінок |
| Pipeline + 12 gates | `noesis/pipeline_v6.py` | 15-файловий Evidence Bundle |
| Benchmark + Ablation v2 | `noesis/benchmark_v6.py` | keep/modify/remove за впливом на дію |

Принцип: жоден шар не виживає, якщо не впливає на дію / валідацію / ризик /
failure-mode / стиснення / людську преференцію / benchmark-delta / якість evidence.
