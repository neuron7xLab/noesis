# ARCHITECTURE — Cognitive Mirror Engine v0.3

Методологічна когнітивна інженерія: **філософія як граматика категорій**,
**когнітивна наука як модель процесу**, **софт як субстрат валідації**. Не наука
з фантастики, не AGI, не терапія.

## Цикл (core thesis)
```
raw signal → category extraction → reality-map selection → synthesis axis
           → reverse inference → artifact → validation → next action
```

## Шари
```
┌────────────────────────────────────────────────────────────┐
│ CLI (cme) · FastAPI            ← інтерфейси                  │
├────────────────────────────────────────────────────────────┤
│ engine.run_v3                  ← оркестратор труби           │
├───────────────┬───────────────┬────────────────────────────┤
│ ontology      │ synthesis     │ generators (mirror/artifact)│
│ (Category     │ (Synthesis    │ deterministic floor +       │
│  Extractor +  │  Axis +       │ optional LLM enhancement    │
│  Reality Maps)│  Reverse Plan)│                             │
├───────────────┴───────────────┴────────────────────────────┤
│ validators (Validator Layer) · forbidden · formal invariants│
├────────────────────────────────────────────────────────────┤
│ evidence (Evidence Bundle, 8 файлів) · schemas              │
└────────────────────────────────────────────────────────────┘
```

## Принцип: детермінована підлога + LLM-підсилення
- Детермінований кістяк працює офлайн і ЗАВЖДИ видає валідований артефакт.
- LLM (опційно, `--backend cli|sdk|llm`) підіймає якість фіналайзера; гейтується
  тими ж валідаторами. **LLM пропонує — детермінований контракт розпоряджається.**

## Розташування коду
| Модуль | Файл |
|---|---|
| Category Extractor + Reality Maps | `cme/ontology.py` |
| Synthesis Axis + Reverse Inference | `cme/synthesis.py` |
| Engine (труба + Evidence Bundle) | `cme/engine.py` |
| Artifact Builder / Intent Mirror | `cme/generators.py` |
| Validator Layer | `cme/validators.py`, `cme/forbidden.py` |
| Method Registry | `cme/registry.py` |
| Формальні інваріанти | `formal/`, `docs/THEORY.md` |
