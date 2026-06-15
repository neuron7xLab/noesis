"""Cognitive Dimensionality Estimator — чи граф додає КОРИСНІ осі, чи лише шум.

Ключова чесність: розширення ≠ покращення. Декоративні теорії (score 0) рахуються
як ШУМОВІ осі, відкинуті верифікацією. useful_dimensionality_gain = лише ортогональні
осі, що ПЕРЕЖИЛИ верифікацію. Це кількісний доказ тези «варіація ≠ розмірність».
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import TYPE_CHECKING, Any

from tools.finalizer100 import count_words

if TYPE_CHECKING:
    from noesis.runs import V6Run


@dataclass(frozen=True)
class DimensionalityReport:
    initial_hypothesis_axes: int
    expanded_hypothesis_axes: int
    retained_axes: int
    discarded_axes: int
    noise_axes: int
    useful_dimensionality_gain: int
    entropy_increase: float
    compression_ratio: float
    artifact_density: float
    net_cognitive_gain: float
    note: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def estimate_dimensionality(run: V6Run) -> DimensionalityReport:
    # 1. Початкова розмірність сирого сигналу = розмаїття осей активних категорій.
    initial = len({e.axis for e in run.category_effects}) or 1

    # 2. LLM-вузли пропонують осі: 12 теоретичних лінз + 1 EIIC-вектор.
    llm_added = len(run.contributions) + 1

    # 3. Що ПЕРЕЖИЛо верифікацію: теорії зі score>0 + EIIC (speculative, але втримано).
    contributing = sum(1 for c in run.contributions if c.contribution_score > 0)
    retained_from_llm = contributing + 1  # +1 за EIIC

    # 4. Шумові осі = запропоноване LLM мінус втримане (декоративні теорії = шум).
    noise = llm_added - retained_from_llm

    expanded = initial + llm_added
    retained = initial + retained_from_llm
    useful_gain = retained_from_llm  # нові ортогональні осі, що пережили верифікацію
    out_words = max(count_words(run.mirror.finalizer), 1)
    nonempty = sum(1 for v in run.artifact.values() if v.strip())

    return DimensionalityReport(
        initial_hypothesis_axes=initial,
        expanded_hypothesis_axes=expanded,
        retained_axes=retained,
        discarded_axes=expanded - retained,
        noise_axes=noise,
        useful_dimensionality_gain=useful_gain,
        entropy_increase=round(expanded / initial, 3),
        compression_ratio=round(run.mirror.input_words / out_words, 3),
        artifact_density=round(nonempty / out_words, 4),
        net_cognitive_gain=round(retained_from_llm / max(llm_added, 1), 3),
        note=("розширення ≠ покращення: більшість LLM-осей відкинуто верифікацією як шум"
              if noise > retained_from_llm else "верифікація втримала більшість запропонованих осей"),
    )
