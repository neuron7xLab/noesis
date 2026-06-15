"""Discriminant-validity study of the IEV gate against controlled degradation.

Ground truth = **objective degradations** (mutation-testing style), not human
ratings: a section-stripped / off-topic / padded / unfalsifiable / forbidden-
injected artifact is provably worse. We score good vs degraded artifacts into the
gate and measure whether it separates the classes (AUC of w + PASS-rates).

Boundary (inference discipline): this proves the scorer+gate discriminate KNOWN
objective degradations — NOT that they predict human-rated usefulness. The latter
still needs labeled pairs (the feedback harness). The claim is bounded to:
«the gate ranks an intact artifact above its degraded variant».
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

from noesis.evaluation.artifact_scorer import gate_decision
from noesis.gates.discharge_gate import DischargeGate
from noesis.generators import build_artifact_deterministic
from noesis.ratios import rate
from tools.artifact_checker import REQUIRED_SECTIONS

_FILLER = "загальні слова без звʼязку з наміром " * 30
_OFF_TOPIC = (
    "погода сьогодні мінлива хмари вітер дощ можливий ввечері температура "
    "комфортна для прогулянки парком біля річки "
) * 3


def _drop_sections(artifact: Mapping[str, str]) -> dict[str, str]:
    """Лишити лише перші дві секції, решту спорожнити (неповний артефакт)."""
    keep = set(REQUIRED_SECTIONS[:2])
    return {k: (v if k in keep else "") for k, v in artifact.items()}


def _off_topic(artifact: Mapping[str, str]) -> dict[str, str]:
    """Замінити вміст не повʼязаним з наміром текстом (нульова релевантність)."""
    return {k: _OFF_TOPIC for k in artifact}


def _pad(artifact: Mapping[str, str]) -> dict[str, str]:
    """Роздути definition far past the word band (порожнє padding)."""
    out = dict(artifact)
    out["definition"] = str(out.get("definition", "")) + " " + _FILLER
    return out


def _strip_falsifier(artifact: Mapping[str, str]) -> dict[str, str]:
    """Замінити validation чистою прозою без виконуваного фальсифікатора."""
    out = dict(artifact)
    out["validation"] = "це працює бо так задумано і виглядає переконливо назагал"
    return out


def _inject_forbidden(artifact: Mapping[str, str]) -> dict[str, str]:
    """Вколоти заборонену claim (AGI/медичну) у визначення."""
    out = dict(artifact)
    out["definition"] = str(out.get("definition", "")) + " ця система — загальний штучний інтелект"
    return out


DEGRADATIONS = {
    "drop_sections": _drop_sections,
    "off_topic": _off_topic,
    "pad": _pad,
    "strip_falsifier": _strip_falsifier,
    "inject_forbidden": _inject_forbidden,
}


def _auc(positive: list[float], negative: list[float]) -> float:
    """P(random good w > random bad w) — Mann-Whitney; 0.5 = no discrimination."""
    if not positive or not negative:
        return 0.0
    wins = ties = 0
    for p in positive:
        for n in negative:
            if p > n:
                wins += 1
            elif p == n:
                ties += 1
    return round((wins + 0.5 * ties) / (len(positive) * len(negative)), 4)


def run_study(intents: Sequence[str], gate: DischargeGate | None = None) -> dict[str, Any]:
    """Score good vs degraded artifacts per intent; measure gate discrimination."""
    gate = gate or DischargeGate()
    good_w: list[float] = []
    good_pass = 0
    per_deg: dict[str, list[float]] = {k: [] for k in DEGRADATIONS}
    deg_pass: dict[str, int] = {k: 0 for k in DEGRADATIONS}

    for intent in intents:
        good = build_artifact_deterministic(intent)
        gd = gate_decision(intent, good, gate)
        good_w.append(gd["w"])
        good_pass += gd["decision"] == "PASS"
        for kind, fn in DEGRADATIONS.items():
            dd = gate_decision(intent, fn(good), gate)
            per_deg[kind].append(dd["w"])
            deg_pass[kind] += dd["decision"] == "PASS"

    n = len(intents)
    all_bad = [w for ws in per_deg.values() for w in ws]
    return {
        "kind": "discriminant_validity",
        "boundary": "об'єктивні деградації, не людська корисність; claim: гейт ранжує цілий артефакт вище деградованого",
        "n_intents": n,
        "overall_auc": _auc(good_w, all_bad),
        "good_pass_rate": rate(good_pass, n),
        "good_mean_w": round(sum(good_w) / n, 4) if n else 0.0,
        "per_degradation": {
            kind: {
                "auc": _auc(good_w, per_deg[kind]),
                "pass_rate": rate(deg_pass[kind], n),
                "mean_w": round(sum(per_deg[kind]) / n, 4) if n else 0.0,
            }
            for kind in DEGRADATIONS
        },
    }


def _example_intents() -> list[str]:
    from pathlib import Path

    root = Path(__file__).resolve().parents[2] / "examples" / "problems"
    return [p.read_text(encoding="utf-8").strip() for p in sorted(root.glob("*.txt"))]


def study_report() -> dict[str, Any]:
    """Run the study over the bundled example intents."""
    return run_study(_example_intents())
