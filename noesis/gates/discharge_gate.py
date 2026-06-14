"""Gated discharge equation — decides when thought becomes action.

    w = αR + βV + γP − δK

R = relevance to intent, V = verifier strength, P = progress value,
K = cost/risk/latency. An action discharges (PASS) only when the weighted
potential crosses the threshold AND verification clears a floor AND risk is
under the human-review ceiling. Risk and verifier strength both bite: high cost
lowers w *and* can force HUMAN_REVIEW; weak verification reroutes for evidence.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from noesis.gate_functional import GateFunctional
from noesis.ratios import rate

DECISIONS: frozenset[str] = frozenset(
    {"BELOW_THRESHOLD", "PASS", "FAIL", "REROUTE", "HUMAN_REVIEW"}
)

_INPUT_NAMES = ("relevance", "verifier", "progress", "cost")


def _check_unit(name: str, value: float) -> None:
    if not 0.0 <= value <= 1.0:
        raise ValueError(f"{name} must be in [0, 1], got {value}")


@dataclass(frozen=True)
class DischargeGate:
    """The discharge gate: a GateFunctional plus a verifier floor and risk ceiling."""

    functional: GateFunctional = field(default_factory=GateFunctional)
    verifier_floor: float = 0.25
    risk_ceiling: float = 0.85

    def decide(
        self,
        *,
        relevance: float,
        verifier: float,
        progress: float,
        cost: float,
        verifier_failed: bool = False,
    ) -> dict[str, Any]:
        _check_unit("relevance", relevance)
        _check_unit("verifier", verifier)
        _check_unit("progress", progress)
        _check_unit("cost", cost)

        components = self.functional.explain(relevance, verifier, progress, cost)
        w = components["w"]
        theta = self.functional.theta

        if verifier_failed:
            decision = "FAIL"
        elif cost >= self.risk_ceiling:
            decision = "HUMAN_REVIEW"
        elif w < theta:
            decision = "BELOW_THRESHOLD"
        elif verifier < self.verifier_floor:
            decision = "REROUTE"
        else:
            decision = "PASS"

        return {
            "w": w,
            "threshold": theta,
            "decision": decision,
            "components": components,
            "inputs": {
                "relevance": relevance,
                "verifier": verifier,
                "progress": progress,
                "cost": cost,
                "verifier_failed": verifier_failed,
            },
        }

    def _decision_at(self, result: dict[str, Any], theta: float) -> str:
        inp = result["inputs"]
        if inp["verifier_failed"]:
            return "FAIL"
        if inp["cost"] >= self.risk_ceiling:
            return "HUMAN_REVIEW"
        if result["w"] < theta:
            return "BELOW_THRESHOLD"
        if inp["verifier"] < self.verifier_floor:
            return "REROUTE"
        return "PASS"

    def threshold_sensitivity(self, results: list[dict[str, Any]], epsilon: float = 0.05) -> float:
        """Fraction of decisions that flip when the threshold is nudged by ±epsilon."""
        if not results:
            return 0.0
        flips = 0
        theta = self.functional.theta
        for r in results:
            up = self._decision_at(r, theta + epsilon)
            down = self._decision_at(r, theta - epsilon)
            if up != r["decision"] or down != r["decision"]:
                flips += 1
        return round(flips / len(results), 4)


def gate_metrics(gate: DischargeGate, results: list[dict[str, Any]]) -> dict[str, float]:
    total = len(results)
    decisions = [r["decision"] for r in results]
    return {
        "gate_pass_rate": rate(decisions.count("PASS"), total),
        "noise_rejection_rate": rate(decisions.count("BELOW_THRESHOLD"), total),
        "human_review_rate": rate(decisions.count("HUMAN_REVIEW"), total),
        "threshold_sensitivity": gate.threshold_sensitivity(results),
    }
