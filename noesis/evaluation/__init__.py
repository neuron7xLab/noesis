"""Evaluation: fractal gate consistency + failure-weighted benchmark."""

from __future__ import annotations

from noesis.evaluation.failure_weighted_benchmark import (
    DIMENSIONS,
    BenchmarkInput,
    assemble_from_repo,
    evaluate,
)
from noesis.evaluation.fractal_gate_consistency import SCALES, check_fractal_consistency

__all__ = [
    "DIMENSIONS",
    "SCALES",
    "BenchmarkInput",
    "assemble_from_repo",
    "check_fractal_consistency",
    "evaluate",
]
