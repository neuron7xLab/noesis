"""Effective dimensionality via participation ratio — D_eff = tr(Σ)² / tr(Σ²).

Канонічна метрика ефективної розмірності прийнятої хмари гіпотез (формалізація
користувача). Замінює евристичний підрахунок «осей» на математично грунтований
participation ratio: зростає, коли вузли тримають незалежні корисні осі, а не
near-duplicates. Pure Python (Gram-форма, n малий), без numpy.
"""

from __future__ import annotations

import re
from collections.abc import Sequence

_WORD = re.compile(r"[\w’'-]+", re.UNICODE)
_STOP = frozenset({"що", "це", "але", "не", "на", "як", "то", "бо", "для", "над", "під", "із", "зі"})


def _dot(a: Sequence[float], b: Sequence[float]) -> float:
    return sum(x * y for x, y in zip(a, b))


def participation_ratio(vectors: Sequence[Sequence[float]]) -> float:
    """D_eff = tr(Σ)² / tr(Σ²) над центрованими векторами (Gram-форма, точно).

    Властивості: N однакових векторів → 1.0; N ортогональних → N−1 (центрування
    знімає 1 ступінь). Нуль-варіація → 1.0 (колапс).
    """
    n = len(vectors)
    if n == 0:
        return 0.0
    d = len(vectors[0])
    mean = [sum(v[k] for v in vectors) / n for k in range(d)]
    centered = [[v[k] - mean[k] for k in range(d)] for v in vectors]
    tr_sigma = sum(_dot(x, x) for x in centered) / n
    tr_sigma2 = sum(_dot(centered[i], centered[j]) ** 2 for i in range(n) for j in range(n)) / (n * n)
    if tr_sigma2 <= 1e-12:
        return 1.0
    return tr_sigma**2 / tr_sigma2


def feature_vectors(texts: Sequence[str]) -> list[list[float]]:
    """Bag-of-content-words над спільним словником (детерміновано)."""
    tokenized = [[w for w in _WORD.findall(t.lower()) if w not in _STOP and len(w) > 2] for t in texts]
    vocab = sorted({w for toks in tokenized for w in toks})
    index = {w: i for i, w in enumerate(vocab)}
    out: list[list[float]] = []
    for toks in tokenized:
        vec = [0.0] * len(vocab)
        for w in toks:
            vec[index[w]] += 1.0
        out.append(vec)
    return out


def effective_dimensionality(texts: Sequence[str]) -> float:
    """D_eff прийнятих гіпотез: 1.0 для дублікатів, росте з ортогональністю."""
    if len(texts) < 2:
        return float(len(texts))
    return round(participation_ratio(feature_vectors(texts)), 4)
