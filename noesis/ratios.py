"""Shared ratio helper for the metrics functions across the runtime.

Every ``*_metrics`` function computed rates as ``round(n / total, 4)`` guarded by
an explicit zero-denominator branch. That idiom was duplicated ~18 times. ``rate``
centralises it with the same rounding (4 dp) and an explicit per-call default for
the empty case, so behaviour is identical while the call sites read as intent.
"""

from __future__ import annotations


def rate(numerator: float, denominator: float, *, default: float = 0.0) -> float:
    """Return round(numerator / denominator, 4), or ``default`` when denominator is 0."""
    if denominator == 0:
        return default
    return round(numerator / denominator, 4)
