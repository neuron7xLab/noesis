"""Canonical IEV gate functional — w(h) = α·R + β·V + γ·P − δ·K ≥ θ.

Робить ваги IEV-гейта ЯВНИМИ (формалізація користувача): R=relevance до IEV,
V=verifier score, P=progress/expected-value, K=cost/risk. Прийняти, якщо w ≥ θ.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class GateFunctional:
    alpha: float = 0.4   # relevance до наміру
    beta: float = 0.3    # verifier/evidence
    gamma: float = 0.2   # progress / expected value
    delta: float = 0.3   # cost / risk (віднімається)
    theta: float = 0.5   # поріг прийняття

    def score(self, relevance: float, verifier: float, progress: float, cost: float) -> float:
        return round(self.alpha * relevance + self.beta * verifier
                     + self.gamma * progress - self.delta * cost, 4)

    def accept(self, relevance: float, verifier: float, progress: float, cost: float) -> bool:
        return self.score(relevance, verifier, progress, cost) >= self.theta

    def explain(self, relevance: float, verifier: float, progress: float, cost: float) -> dict[str, float]:
        w = self.score(relevance, verifier, progress, cost)
        return {
            "alpha_R": round(self.alpha * relevance, 4),
            "beta_V": round(self.beta * verifier, 4),
            "gamma_P": round(self.gamma * progress, 4),
            "minus_delta_K": round(-self.delta * cost, 4),
            "w": w,
            "theta": self.theta,
            "accept": float(w >= self.theta),
        }
