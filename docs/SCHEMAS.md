# SCHEMAS — JSON-контракти

Усі схеми — JSON Schema draft 2020-12, у `schemas/`. Валідуються через
`jsonschema` (`tools/reflection_validator.py` патерн).

| Схема | Об'єкт | Ключові поля |
|---|---|---|
| `category.schema.json` | ActiveCategory | name, axis∈{europe,usa,china}, function, failure_mode, matched[] |
| `reality_map.schema.json` | RealityMaps | europe[], usa[], china[], dominant_axis, dormant_axes[] |
| `synthesis_axis.schema.json` | SynthesisAxis | preserve, test, evolve, refuse |
| `artifact.schema.json` | MethodArtifact | definition, input, method, output, validation, example, failure_modes |
| `validation.schema.json` | ValidationReport | artifact_type, passed, checks[]{name,passed,detail} |
| `intent.schema.json` · `reflection.schema.json` · `inference_trace.schema.json` | (ядро) | див. `docs/THEORY.md` |
| `mirror.schema.json` · `introspection.schema.json` | (v0.2) | 9-/6-польові карти |

Кожен `additionalProperties: false` — контракт строгий, зайві поля відхиляються.
