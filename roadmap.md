# ROADMAP — Cognitive Mirror Engine

Принцип: кожен інкремент закривається лише зеленим тестом (Insight-to-Artifact).

## Зроблено
- **v0.1** — 7 методів за контрактом, валідатори, finalizer100, формальний шар (THEORY).
- **v0.2** — продуктовий шар: `cme` CLI, Intent Mirror/Introspection/Artifact, Method
  Registry, Evidence Bundle, детермінована підлога + LLM-підсилення, 10 messy-прикладів.
- **v0.3** — цивілізаційний рушій: Category Extractor (30 категорій) → Reality Maps →
  Synthesis Axis → Reverse Plan; 8-файловий Evidence Bundle; 12 реальних прикладів;
  spec-документи (ARCHITECTURE/ONTOLOGY/METHODS/SCHEMAS/VALIDATION/EXAMPLES).

- **v0.4 + EIIC** — нейрокогнітивний шар: 12 теоретичних лінз як детерміновані
  проксі (`cme theories|neuro`), EIIC термінальний вектор (`cme eiic`) з примусовим
  тегуванням провенансу (observed/inferred/speculative/forbidden); forbidden-шар
  ловить claims про свідомість/IIT-досвід/AGI/долю/містику.

## Далі (8 тижнів)
| Тиждень | Інкремент | Доказ |
|---|---|---|
| 1 | Адверсивний набір на осьову класифікацію + anchor-евейжн | гейти ловлять ≥90% |
| 2 | Афективно-навантажувальна метрика (вхід/вихід дельта) | тест на 12 прикладах |
| 3 | LLM-екстрактор категорій + детермінований фолбек | контрактні тести |
| 4 | LLM-бекенд для introspection/artifact із фолбеком | гейт-паритет із mirror |
| 5 | Калібрування метакогнітивного γ на реальних парах | відтворюваний звіт |
| 6 | Веб-демо (FastAPI + мінімальний UI) | e2e smoke |
| 7 | Документація + сайт-копія без заборонених claims | review |
| 8 | Реліз v1.0: CI, пакування, публікація на neuron7xLab | теги, зелений CI |

## Назавжди поза скоупом
AGI, симуляція свідомості, діагностика/терапія, наукові claims про мозок без peer-review.
