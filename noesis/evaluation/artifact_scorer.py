"""Score an artifact into the discharge-gate inputs (R, V, P, K).

Wires the abstract IEV gate (w = αR + βV + γP − δK) to real artifact text for
the first time, using ONLY pre-existing quality primitives — no test-specific
tuning:

* R relevance — частка змістовних токенів наміру, покритих артефактом;
* V verifier  — наявність required-секцій ∧ виконуваного фальсифікатора у
  `validation` (falsifier_present + повнота секцій);
* P progress  — повнота: частка непорожніх секцій + довжина в межах фіналайзера;
* K cost/risk — forbidden-claims + hallucination_risk + перевищення довжини.

Кожен ∈ [0,1]. Деградації рухають їх у очевидний бік завдяки самим примітивам,
не за нашим декретом — саме це й перевіряє discrimination-study.
"""

from __future__ import annotations

import re
from collections.abc import Mapping
from typing import Any

from formal.metrics import falsifier_present
from noesis.forbidden import check_forbidden_claims, hallucination_risk
from noesis.gates.discharge_gate import DischargeGate
from tools.artifact_checker import REQUIRED_SECTIONS
from tools.finalizer100 import MAX_WORDS, MIN_WORDS

_WORD = re.compile(r"[\w’'-]+", re.UNICODE)
_RISK = {"low": 0.0, "medium": 0.5, "high": 1.0}


def _tokens(text: str) -> set[str]:
    return {w for w in _WORD.findall(text.lower()) if len(w) > 2}


def _text(artifact: Mapping[str, str]) -> str:
    return " ".join(str(v) for v in artifact.values())


def _relevance(intent: str, artifact: Mapping[str, str]) -> float:
    intent_tokens = _tokens(intent)
    if not intent_tokens:
        return 0.0
    covered = intent_tokens & _tokens(_text(artifact))
    return round(len(covered) / len(intent_tokens), 4)


def _section_rate(artifact: Mapping[str, str]) -> float:
    present = sum(1 for s in REQUIRED_SECTIONS if str(artifact.get(s, "")).strip())
    return present / len(REQUIRED_SECTIONS)


def _verifier(artifact: Mapping[str, str]) -> float:
    has_falsifier = falsifier_present(str(artifact.get("validation", "")))
    return round(0.5 * _section_rate(artifact) + 0.5 * (1.0 if has_falsifier else 0.0), 4)


def _progress(artifact: Mapping[str, str]) -> float:
    word_count = len(_text(artifact).split())
    in_band = 1.0 if MIN_WORDS <= word_count <= MAX_WORDS else 0.0
    return round(0.7 * _section_rate(artifact) + 0.3 * in_band, 4)


def _cost(artifact: Mapping[str, str]) -> float:
    text = _text(artifact)
    word_count = len(text.split())
    forbidden = 1.0 if check_forbidden_claims(text) else 0.0
    level, _ = hallucination_risk(text)
    overrun = min(1.0, (word_count - MAX_WORDS) / MAX_WORDS) if word_count > MAX_WORDS else 0.0
    return round(min(1.0, 0.5 * forbidden + 0.3 * _RISK[level] + 0.2 * overrun), 4)


def score_artifact(intent: str, artifact: Mapping[str, str]) -> dict[str, float]:
    """Map (intent, artifact) → discharge-gate inputs {relevance, verifier, progress, cost}."""
    return {
        "relevance": _relevance(intent, artifact),
        "verifier": _verifier(artifact),
        "progress": _progress(artifact),
        "cost": _cost(artifact),
    }


def verifier_failed(artifact: Mapping[str, str]) -> bool:
    """Категоріальний провал верифікації — гейт мусить FAIL, не лише знизити w.

    Discrimination-study виявив, що БЕЗ цього вето артефакт без виконуваного
    фальсифікатора або з інжектованою forbidden-claim ПРОХОДИВ гейт (w>θ): score
    ранжував його нижче, але рішення не вето. Це категоріальні, не градуальні
    провали, тож вони мапляться на наявний verifier_failed-канал гейта.
    """
    no_falsifier = not falsifier_present(str(artifact.get("validation", "")))
    has_forbidden = bool(check_forbidden_claims(_text(artifact)))
    return no_falsifier or has_forbidden


def gate_decision(intent: str, artifact: Mapping[str, str], gate: DischargeGate) -> dict[str, Any]:
    """Повне рішення гейта для артефакта: score + категоріальне вето в один виклик."""
    return gate.decide(**score_artifact(intent, artifact), verifier_failed=verifier_failed(artifact))
