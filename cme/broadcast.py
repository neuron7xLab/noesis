"""Broadcast-Reentry Tracker — який сигнал домінує в графі (GNWT-аналогія).

Операційна аналогія GNWT: broadcast (сигнал стає глобально доступним), selective
reentry (що повертається в наступний цикл), workspace winner, suppressed signal.
Жодного claim про вимір нейронного workspace.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

from cme.pipeline_v6 import V6Run


@dataclass(frozen=True)
class BroadcastTrace:
    candidate_signals: list[str]
    workspace_winner: str
    suppressed_signals: list[str]
    why_winner_won: str
    reentry_signal: str
    reentry_target_node: str
    lost_signal_risk: str
    suppression_assessment: str  # useful | dangerous

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


_AXIS_LABEL = {"europe": "істина/форма", "usa": "дія/наслідок", "china": "процес/потік"}


def track_broadcast(run: V6Run) -> BroadcastTrace:
    # кандидати: причинна категорія, критичний ризик, EIIC-вектор
    candidates = [
        f"категорія: {run.action.category_influence}",
        f"ризик: {run.mirror.risk}",
        f"EIIC-вектор: {run.eiic.latent_intent.value}",
    ]
    winner = f"дія під впливом: {run.action.selection_reason}"
    suppressed = [f"придушено: критичний ризик «{run.mirror.risk}»"]
    # небезпечне придушення: коли гладка дія перекриває ризик
    dangerous = bool(run.mirror.risk.strip())
    return BroadcastTrace(
        candidate_signals=candidates,
        workspace_winner=winner,
        suppressed_signals=suppressed,
        why_winner_won="домінантна вісь дала причинний ухил дії (найбільше активних категорій)",
        reentry_signal=run.action.selected_action,
        reentry_target_node="human_intent_controller",
        lost_signal_risk=f"ризик «{run.mirror.risk}» може бути перекритий гладкою дією",
        suppression_assessment="dangerous" if dangerous else "useful",
    )
