"""Fractal gate consistency — the same gate at every scale.

The discharge gate must behave identically whether it judges a token decision, a
text edit, a code patch, a test case, a module change, a pull request, or a
release candidate: same gate, different scale. A release may not PASS while a
lower scale fails; no scale may bypass the gate; every scale must carry a
verifier.
"""

from __future__ import annotations

from collections import Counter
from typing import Any

from noesis.gates.discharge_gate import DischargeGate
from noesis.ratios import rate

SCALES: tuple[str, ...] = (
    "token_decision",
    "text_edit",
    "code_patch",
    "test_case",
    "module_change",
    "pull_request",
    "release_candidate",
)

_CANONICAL_PROBE: dict[str, float] = {
    "relevance": 0.9,
    "verifier": 0.8,
    "progress": 0.7,
    "cost": 0.1,
}


def _probe(gate: DischargeGate) -> tuple[dict[str, str], float]:
    decision = gate.decide(
        relevance=_CANONICAL_PROBE["relevance"],
        verifier=_CANONICAL_PROBE["verifier"],
        progress=_CANONICAL_PROBE["progress"],
        cost=_CANONICAL_PROBE["cost"],
    )["decision"]
    decisions = {scale: decision for scale in SCALES}
    modal, count = Counter(decisions.values()).most_common(1)[0]
    return decisions, round(count / len(SCALES), 4)


def check_fractal_consistency(
    gate: DischargeGate, per_scale_inputs: dict[str, dict[str, Any]]
) -> dict[str, Any]:
    """Apply one gate across all scales and verify cross-scale consistency."""
    problems: list[str] = []
    decisions: dict[str, str] = {}

    for scale in SCALES:
        inp = per_scale_inputs.get(scale)
        if inp is None:
            problems.append(f"SCALE_BYPASSES_GATE: {scale} has no gated decision")
            continue
        if float(inp.get("verifier", 0.0)) <= 0.0:
            problems.append(f"SCALE_NO_VERIFIER: {scale} has no verifier")
        decisions[scale] = gate.decide(
            relevance=float(inp["relevance"]),
            verifier=float(inp["verifier"]),
            progress=float(inp["progress"]),
            cost=float(inp["cost"]),
            verifier_failed=bool(inp.get("verifier_failed", False)),
        )["decision"]

    probe_decisions, probe_rate = _probe(gate)

    lower_scales = [s for s in SCALES[:-1] if s in decisions]
    release = decisions.get("release_candidate")
    lower_fail = any(decisions[s] != "PASS" for s in lower_scales)
    all_lower_pass = bool(lower_scales) and all(decisions[s] == "PASS" for s in lower_scales)

    false_pass = 1.0 if release == "PASS" and lower_fail else 0.0
    false_reject = 1.0 if (release is not None and release != "PASS" and all_lower_pass) else 0.0
    fail_count = sum(1 for d in decisions.values() if d != "PASS")
    scale_failure_rate = rate(fail_count, len(decisions))

    status = "FAIL" if (problems or false_pass > 0.0) else "PASS"
    return {
        "status": status,
        "scales": decisions,
        "consistency_probe": probe_decisions,
        "problems": problems,
        "metrics": {
            "cross_scale_gate_consistency": probe_rate,
            "scale_specific_failure_rate": scale_failure_rate,
            "false_pass_rate": false_pass,
            "false_reject_rate": false_reject,
        },
    }
