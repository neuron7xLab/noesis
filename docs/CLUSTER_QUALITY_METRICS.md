# CLUSTER_QUALITY_METRICS

Proxy-формула якості розподіленого workflow (`noesis/cluster_quality.py`):

```
cluster_quality = IEV_bw × node_diversity × intent_coherence × noise_rejection ÷ latency_drag
```

НЕ вимір мозку/свідомості/free-energy. 10 метрик: IEV_bw, diversity, coherence,
noise_rejection, latency_drag, useful_dimensionality_gain, artifact_density,
convergence_rate, overexpansion_penalty, human_bottleneck.

## Реальна крива node-scaling (`noesis node-scaling`)
| вузлів | cluster_quality |
|---|---|
| 1 | 4.46 |
| 2 | 0.99 |
| 3 | 0.50 |
| 5 | 0.20 |
| 8 | 0.12 |

**Оптимум = 1–2 вузли.** cluster_quality монотонно падає: latency_drag від зайвих
вузлів росте швидше за приріст різноманітності. Квантифікований доказ: масштабування
≠ більше моделей.
