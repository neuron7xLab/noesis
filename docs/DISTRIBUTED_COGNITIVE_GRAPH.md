# DISTRIBUTED_COGNITIVE_GRAPH

Людина + LLM як направлений граф інференсу, не «використання GPT».

## Топологія (Cognitive Scaling Loop)
```
human_intent_controller → prompt_encoder → llm_expander → critic → auditor
→ verifier → compressor → artifact_builder → validator → decision_gate
                                                              ↓ (selective reentry)
                                                    human_intent_controller
```
11 типів вузлів (`cme/graph.py`, `cme/node_profile.py`). Кожен — actor (human/llm/auto)
+ інформаційна геометрія (latency/bandwidth/noise/prior/failure_risk).

## Bottleneck
`human_intent_controller` + `decision_gate` — найнижча пропускна (bandwidth_rank=1).
Структурне вузьке місце розподіленої когніції — людський IEV-bandwidth, не вузли.
