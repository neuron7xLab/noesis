# EXAMPLES — 12 реальних прикладів

Усі в `examples/problems/`, проходять трубу end-to-end детерміновано
(`tests/test_cme_v3.py`), кожен видає валідований артефакт.

| # | Тип | Файл |
|---|---|---|
| 1 | Особисте рішення | `01_personal_decision.txt` |
| 2 | Дослідницька ідея | `02_research_idea.txt` |
| 3 | Продуктова стратегія | `03_product_strategy.txt` |
| 4 | Конфлікт у стосунках | `04_relationship_conflict.txt` |
| 5 | Карʼєрний шлях | `05_career_path.txt` |
| 6 | Стартап-теза | `06_startup_thesis.txt` |
| 7 | Філософський концепт | `07_philosophical_concept.txt` |
| 8 | Дизайн AI-системи | `08_ai_system_design.txt` |
| 9 | Етична дилема | `09_ethics_dilemma.txt` |
| 10 | Протокол навчання | `10_learning_protocol.txt` |
| 11 | Ринкове позиціонування | `11_market_positioning.txt` |
| 12 | Метафізичне порівняння | `12_metaphysical_comparison.txt` |

## Запуск
```bash
python -m noesis.cli pipeline examples/problems/05_career_path.txt --evidence out/
# → domain china (Ци), failure_mode під наглядом: "адаптація без конфронтації", PASS
```

Приклад показує: активна карта реальності, керівна категорія, перша відсутня
умова, наступна дія, failure mode під наглядом — усе в одну команду.
