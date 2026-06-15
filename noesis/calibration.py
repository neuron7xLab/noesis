"""Калібрувальний реєстр — усі настроювані пороги в одному місці.

Це КАРТА, не рішення: для кожного «магічного числа» подаємо його поточне
значення (з єдиного джерела — модуля, де воно живе), рекомендований діапазон,
ефект і **виміряну** чутливість. Жодної вигаданої істини:

* пороги discharge-гейта (θ, α/β/γ/δ, verifier_floor, risk_ceiling) міряються
  як функція відгуку на рівномірній сітці входів R×V×P×K — це власна крива
  гейта, референс не потрібен;
* data-залежні пороги (MIN_PAIRS, _GAP_TOLERANCE, DISJOINTNESS…) несуть чесну
  позначку «потрібні розмічені пари / корпус», а не псевдо-число.

Робоча точка обирається з цих даних, не з відчуття.
"""

from __future__ import annotations

from dataclasses import dataclass, replace
from typing import Any

from noesis.gate_functional import GateFunctional
from noesis.gates.discharge_gate import DischargeGate
from noesis.ratios import rate

_GRID: tuple[float, ...] = (0.0, 0.25, 0.5, 0.75, 1.0)
_DEFAULT_THETAS: tuple[float, ...] = (0.3, 0.4, 0.5, 0.6, 0.7)


@dataclass(frozen=True)
class Knob:
    """One tunable threshold: where it lives, its value, range, effect, response."""

    name: str
    module: str
    current: float
    lo: float
    hi: float
    effect: str
    sensitivity: float | None = None  # виміряна Δповедінки/Δзнобу; None = data-залежний
    note: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "module": self.module,
            "current": self.current,
            "recommended_range": [self.lo, self.hi],
            "effect": self.effect,
            "sensitivity": self.sensitivity,
            "note": self.note,
        }


def _sample_inputs() -> list[tuple[float, float, float, float]]:
    """Детермінована рівномірна сітка R×V×P×K (5⁴ = 625 точок)."""
    return [(r, v, p, k) for r in _GRID for v in _GRID for p in _GRID for k in _GRID]


def _pass_rate(gate: DischargeGate, samples: list[tuple[float, float, float, float]]) -> float:
    passes = sum(
        1
        for r, v, p, k in samples
        if gate.decide(relevance=r, verifier=v, progress=p, cost=k)["decision"] == "PASS"
    )
    return rate(passes, len(samples))


def gate_operating_curve(thetas: tuple[float, ...] = _DEFAULT_THETAS) -> list[dict[str, float]]:
    """Частки рішень по θ-сітці — операційна крива гейта."""
    samples = _sample_inputs()
    curve: list[dict[str, float]] = []
    for theta in thetas:
        gate = DischargeGate(functional=GateFunctional(theta=theta))
        decisions = [
            gate.decide(relevance=r, verifier=v, progress=p, cost=k)["decision"]
            for r, v, p, k in samples
        ]
        n = len(decisions)
        curve.append(
            {
                "theta": theta,
                "pass_rate": rate(decisions.count("PASS"), n),
                "below_threshold_rate": rate(decisions.count("BELOW_THRESHOLD"), n),
                "reroute_rate": rate(decisions.count("REROUTE"), n),
                "human_review_rate": rate(decisions.count("HUMAN_REVIEW"), n),
            }
        )
    return curve


def gate_weight_sensitivity(step: float = 0.1) -> dict[str, float]:
    """Центральна різниця d(pass_rate)/d(knob) для кожної ваги гейта.

    Знак інформативний: θ і δ (вартість) мають знижувати pass_rate (−),
    α/β/γ — підвищувати (+). Величина ранжує крихкі vs стійкі знобі.
    """
    samples = _sample_inputs()
    base = GateFunctional()
    base_gate = DischargeGate()
    out: dict[str, float] = {}

    for w in ("alpha", "beta", "gamma", "delta", "theta"):
        cur = float(getattr(base, w))
        up = _pass_rate(DischargeGate(functional=replace(base, **{w: cur + step})), samples)
        down = _pass_rate(
            DischargeGate(functional=replace(base, **{w: max(0.0, cur - step)})), samples
        )
        out[w] = round((up - down) / (2 * step), 4)

    vf = base_gate.verifier_floor
    out["verifier_floor"] = round(
        (
            _pass_rate(DischargeGate(verifier_floor=min(1.0, vf + step)), samples)
            - _pass_rate(DischargeGate(verifier_floor=max(0.0, vf - step)), samples)
        )
        / (2 * step),
        4,
    )
    rc = base_gate.risk_ceiling
    out["risk_ceiling"] = round(
        (
            _pass_rate(DischargeGate(risk_ceiling=min(1.0, rc + step)), samples)
            - _pass_rate(DischargeGate(risk_ceiling=max(0.0, rc - step)), samples)
        )
        / (2 * step),
        4,
    )

    return out


def knobs() -> list[Knob]:
    """Усі настроювані пороги з поточними значеннями (єдине джерело правди)."""
    import formal.verify as fv
    import noesis.evaluation.failure_weighted_benchmark as fwb
    import noesis.feedback as fb
    import tools.finalizer100 as fin
    from noesis import bibliography as bib

    f = GateFunctional()
    g = DischargeGate()
    s = gate_weight_sensitivity()

    return [
        Knob("theta", "noesis.gate_functional", f.theta, 0.3, 0.7,
             "поріг w для PASS; нижче → BELOW_THRESHOLD", s["theta"]),
        Knob("alpha", "noesis.gate_functional", f.alpha, 0.2, 0.6,
             "вага релевантності R у w", s["alpha"]),
        Knob("beta", "noesis.gate_functional", f.beta, 0.1, 0.5,
             "вага сили верифікатора V у w", s["beta"]),
        Knob("gamma", "noesis.gate_functional", f.gamma, 0.1, 0.4,
             "вага прогресу P у w", s["gamma"]),
        Knob("delta", "noesis.gate_functional", f.delta, 0.1, 0.5,
             "вага вартості/ризику K (віднімається з w)", s["delta"]),
        Knob("verifier_floor", "noesis.gates.discharge_gate", g.verifier_floor, 0.1, 0.4,
             "мін. V для PASS; нижче → REROUTE по докази", s["verifier_floor"]),
        Knob("risk_ceiling", "noesis.gates.discharge_gate", g.risk_ceiling, 0.7, 0.95,
             "K на/вище → HUMAN_REVIEW (вето ризику)", s["risk_ceiling"]),
        Knob("MIN_PAIRS", "noesis.feedback", fb.MIN_PAIRS, 8, 30,
             "розмічених пар до статусу CALIBRATED", None,
             "data-залежний: обери з бажаної ширини CI на anchored_quality"),
        Knob("_GAP_TOLERANCE", "noesis.feedback", fb._GAP_TOLERANCE, 0.05, 0.25,
             "наскільки проксі може перевищити реальність до PROXY_OVERCLAIMS", None,
             "data-залежний: з розподілу спостереженого proxy−reality gap"),
        Knob("DISJOINTNESS_THRESHOLD", "formal.verify", fv.DISJOINTNESS_THRESHOLD, 0.3, 0.7,
             "мін. 1−Jaccard для PASS language_expansion", None,
             "корпус-залежний: з розмічених пар дефініція/анти-дефініція"),
        Knob("MIN_WORDS", "tools.finalizer100", float(fin.MIN_WORDS), 60, 120,
             "нижня межа довжини артефакту", None, "стиль-залежний"),
        Knob("MAX_WORDS", "tools.finalizer100", float(fin.MAX_WORDS), 100, 200,
             "верхня межа довжини артефакту", None, "стиль-залежний"),
        Knob("_SCORE_THRESHOLD", "noesis.evaluation.failure_weighted_benchmark",
             fwb._SCORE_THRESHOLD, 0.4, 0.7, "мін. бал кейса у failure-weighted бенчмарку", None,
             "корпус-залежний"),
        Knob("_READINESS_THRESHOLD", "noesis.evaluation.failure_weighted_benchmark",
             fwb._READINESS_THRESHOLD, 0.4, 0.7, "поріг readiness релізного вердикту", None,
             "корпус-залежний"),
        Knob("_THEORY_HEAVY_MIN_TERMS", "noesis.bibliography",
             float(bib._THEORY_HEAVY_MIN_TERMS), 1, 4,
             "мін. термінів, щоб док вважався теорієнасиченим", None, "евристика"),
    ]


def calibration_report() -> dict[str, Any]:
    """Єдиний калібрувальний звіт: реєстр порогів + операційна крива гейта."""
    return {
        "kind": "calibration_map",
        "disclaimer": "карта, не рішення — робоча точка обирається з даних, не з відчуття",
        "grid_size": len(_sample_inputs()),
        "knobs": [k.to_dict() for k in knobs()],
        "gate_operating_curve": gate_operating_curve(),
        "data_dependent_knobs": [k.name for k in knobs() if k.sensitivity is None],
    }
