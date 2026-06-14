# LATENCY_ASYMMETRY

Розрив між швидким біологічним precision-рішенням і повільнішим, але ширшим LLM-
інференсом (`noesis/latency_profile.py`). latency як проєктна змінна.

Human: fast intuitive reject / slow explicit justify, low bandwidth, fatigue-sensitive.
LLM: high generative bandwidth, slower latency, weak prior, high variance.
Execution modes: serial/parallel/race/cascade/human_interrupt/gate_first/compress_first.
Pipeline зобов'язаний назвати bottleneck і його джерело (human/model/over-routing).
