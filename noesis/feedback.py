"""Feedback harness — the node that turns proxy into anchored measurement.

The whole stack is fail-closed on *proxy* metrics (structural consistency, not
demonstrated usefulness). This node ingests human-labeled pairs

    input -> artifact -> human verdict ("works" / "fails")  [+ optional HRV]

and calibrates the proxy score against the real outcome. Until enough labels
exist it returns ``INSUFFICIENT_DATA`` and never claims a calibrated PASS — no
proxy is promoted to a measurement without ground truth (see
``noesis/gates/residual_promotion.py``: data *is* the verifier).
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from math import isfinite, sqrt
from typing import Any

from noesis.ratios import rate

MIN_PAIRS = 12
_GAP_TOLERANCE = 0.15  # proxy may exceed reality by at most this before it overclaims
_VERDICTS = ("works", "fails")
CALIBRATION_STATES = frozenset({"INSUFFICIENT_DATA", "CALIBRATED"})


@dataclass(frozen=True)
class LabeledPair:
    pair_id: str
    input_hash: str
    artifact_ref: str
    human_verdict: str  # "works" | "fails"
    proxy_score: float  # what the system's proxy claimed, in [0, 1]
    hrv: float | None = None
    provenance: str = "unknown"

    def __post_init__(self) -> None:
        # Self-validating: closes the bypass where direct construction (vs the
        # dict path through _validate_pair) fed NaN/inf into calibrate() and
        # produced a CALIBRATED verdict over poison (знайдено хаос-стрес-тестом).
        if self.human_verdict not in _VERDICTS:
            raise ValueError(f"human_verdict must be one of {_VERDICTS}, got {self.human_verdict!r}")
        if not (isfinite(self.proxy_score) and 0.0 <= self.proxy_score <= 1.0):
            raise ValueError(f"proxy_score must be a finite value in [0, 1], got {self.proxy_score}")
        if self.hrv is not None and not isfinite(self.hrv):
            raise ValueError(f"hrv must be finite or None, got {self.hrv}")

    def reward(self) -> float:
        return 1.0 if self.human_verdict == "works" else 0.0

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _validate_pair(raw: dict[str, Any]) -> LabeledPair:
    verdict = str(raw.get("human_verdict", ""))
    if verdict not in _VERDICTS:
        raise ValueError(f"human_verdict must be one of {_VERDICTS}, got {verdict!r}")
    score = float(raw.get("proxy_score", -1.0))
    if not 0.0 <= score <= 1.0:
        raise ValueError(f"proxy_score must be in [0, 1], got {score}")
    hrv_raw = raw.get("hrv")
    return LabeledPair(
        pair_id=str(raw["pair_id"]),
        input_hash=str(raw["input_hash"]),
        artifact_ref=str(raw["artifact_ref"]),
        human_verdict=verdict,
        proxy_score=score,
        hrv=None if hrv_raw is None else float(hrv_raw),
        provenance=str(raw.get("provenance", "unknown")),
    )


def load_pairs(payload: dict[str, Any]) -> list[LabeledPair]:
    return [_validate_pair(p) for p in payload.get("pairs", [])]


def _mean(xs: list[float]) -> float:
    return sum(xs) / len(xs)


def _pearson(xs: list[float], ys: list[float]) -> float | None:
    mx, my = _mean(xs), _mean(ys)
    sx = sum((x - mx) ** 2 for x in xs)
    sy = sum((y - my) ** 2 for y in ys)
    if sx == 0.0 or sy == 0.0:
        return None  # degenerate variance -> alignment undefined
    cov = sum((x - mx) * (y - my) for x, y in zip(xs, ys, strict=True))
    return round(cov / sqrt(sx * sy), 4)


def calibrate(pairs: list[LabeledPair], *, min_pairs: int = MIN_PAIRS) -> dict[str, Any]:
    """Calibrate proxy against real outcome. Fail-closed below ``min_pairs``."""
    n = len(pairs)
    provenance = sorted({p.provenance for p in pairs}) or ["none"]
    hrv_coverage = rate(sum(1 for p in pairs if p.hrv is not None), n)

    if n < min_pairs:
        return {
            "status": "INSUFFICIENT_DATA",
            "n": n,
            "min_pairs": min_pairs,
            "anchored_quality": None,
            "calibration_gap": None,
            "proxy_reality_alignment": None,
            "verdict": "INSUFFICIENT_DATA",
            "provenance": provenance,
            "hrv_coverage": hrv_coverage,
            "reason": f"need >= {min_pairs} labeled pairs, have {n}; proxy stays proxy",
        }

    rewards = [p.reward() for p in pairs]
    proxies = [p.proxy_score for p in pairs]
    anchored = round(_mean(rewards), 4)
    gap = round(_mean(proxies) - anchored, 4)
    verdict = "PROXY_OVERCLAIMS" if gap > _GAP_TOLERANCE else "ALIGNED"
    return {
        "status": "CALIBRATED",
        "n": n,
        "min_pairs": min_pairs,
        "anchored_quality": anchored,
        "calibration_gap": gap,
        "proxy_reality_alignment": _pearson(proxies, rewards),
        "verdict": verdict,
        "provenance": provenance,
        "hrv_coverage": hrv_coverage,
        "reason": (
            "proxy exceeds measured reality beyond tolerance"
            if verdict == "PROXY_OVERCLAIMS"
            else "proxy tracks measured reality within tolerance"
        ),
    }


def ingest(payload: dict[str, Any], *, min_pairs: int = MIN_PAIRS) -> dict[str, Any]:
    return calibrate(load_pairs(payload), min_pairs=min_pairs)
