"""Benchmark + ablation: 100 messy входів × 10 доменів, proxy_eval (без фейк-людей).

ЧЕСНО: усі оцінки — детерміновані ПРОКСІ, позначені proxy_eval=True. Жодної
імітації людської розмітки. Мета — виміряти структурний внесок кожного модуля.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

from cme.pipeline_v5 import ALL_MODULES, run_v5
from tools.artifact_checker import check_artifact
from tools.finalizer100 import count_words

DOMAINS: tuple[str, ...] = (
    "personal_decision", "research_idea", "product_strategy", "relationship_conflict",
    "career_transition", "philosophical_confusion", "ai_architecture", "startup_positioning",
    "ethical_dilemma", "learning_protocol",
)

_STEMS: dict[str, str] = {
    "personal_decision": "не знаю чи {x} боюсь помилитись але далі так не можу",
    "research_idea": "маю гіпотезу про {x} але не знаю чи це сигнал чи самообман і як перевірити",
    "product_strategy": "продукт {x} не злітає клієнти не повертаються пивотити чи закривати",
    "relationship_conflict": "ми сваримось через {x} хочу гармонії але боюсь говорити прямо",
    "career_transition": "втомився від роботи хочу {x} але немає сил це вигорання чи реально треба",
    "philosophical_confusion": "що таке {x} насправді це визначає як я живу хочу зрозуміти суть",
    "ai_architecture": "проєктую {x} систему оркестратор плюс субагенти боюсь зайвої складності",
    "startup_positioning": "вірю що ринок {x} вибухне хочу запустити але лише інтуїція потрібен експеримент",
    "ethical_dilemma": "пропонують вигідний {x} але клієнт сумнівний користь велика чесність під питанням",
    "learning_protocol": "хочу вивчити {x} але кидаю немає системи і дисципліни розпорошуюсь",
}
_FILLERS: tuple[str, ...] = ("це", "новий напрям", "цей крок", "складну тему", "ту ідею",
                             "інший шлях", "це рішення", "той проєкт", "цю задачу", "нове")


def generate_inputs() -> list[tuple[str, str]]:
    """100 входів: 10 доменів × 10 варіацій (детерміновано)."""
    out: list[tuple[str, str]] = []
    for domain in DOMAINS:
        stem = _STEMS[domain]
        for i in range(10):
            out.append((domain, stem.format(x=_FILLERS[i])))
    return out


@dataclass(frozen=True)
class ProxyScore:
    domain: str
    clarity: int          # 1–5
    compression: int      # 1–5
    actionability: int    # 1–5
    artifact_validity: bool
    failure_mode_detected: bool
    claim_safety: bool
    proxy_eval: bool = True

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _clamp(x: int) -> int:
    return max(1, min(5, x))


def proxy_score(domain: str, raw: str) -> ProxyScore:
    run = run_v5(raw)
    base_w = max(count_words(raw), 1)
    cme_w = max(count_words(run.intent_mirror.finalizer), 1)
    compression = _clamp(round(base_w / cme_w * 3))
    structured = sum(1 for v in run.intent_mirror.to_dict().values() if v.strip())
    clarity = _clamp(round(structured / 2))  # 10 полів → ~5
    actionability = 5 if run.next_action.strip() else 1
    gates = {c.name: c.passed for c in run.validation.checks}
    return ProxyScore(
        domain=domain,
        clarity=clarity,
        compression=compression,
        actionability=actionability,
        artifact_validity=gates.get("gate4_artifact_completeness", False),
        failure_mode_detected=gates.get("gate6_failure_awareness", False),
        claim_safety=gates.get("gate3_forbidden_claims", False),
    )


def run_benchmark() -> dict[str, Any]:
    scores = [proxy_score(d, raw) for d, raw in generate_inputs()]
    n = len(scores)
    return {
        "n": n,
        "proxy_eval": True,
        "avg_clarity": round(sum(s.clarity for s in scores) / n, 2),
        "avg_compression": round(sum(s.compression for s in scores) / n, 2),
        "avg_actionability": round(sum(s.actionability for s in scores) / n, 2),
        "artifact_validity_rate": round(sum(s.artifact_validity for s in scores) / n, 3),
        "failure_mode_rate": round(sum(s.failure_mode_detected for s in scores) / n, 3),
        "claim_safety_rate": round(sum(s.claim_safety for s in scores) / n, 3),
    }


_ABLATIONS: dict[str, frozenset[str]] = {
    "full_pipeline": ALL_MODULES,
    "without_intent_mirror": ALL_MODULES - {"intent_mirror"},
    "without_category_layer": ALL_MODULES - {"category_layer"},
    "without_theory_lens": ALL_MODULES - {"theory_lens"},
    "without_eiic": ALL_MODULES - {"eiic"},
    "without_validator": ALL_MODULES - {"validator"},
    "without_failure_modes": ALL_MODULES - {"failure_modes"},
}


def run_ablation(raw: str = "хочу запустити продукт але застряг між двома напрямками і боюсь") -> dict[str, Any]:
    """Який модуль реально щось дає: показує гейти, що ламаються без нього."""
    result: dict[str, Any] = {}
    for name, modules in _ABLATIONS.items():
        run = run_v5(raw, modules=modules)
        failed = [c.name for c in run.validation.checks if not c.passed]
        result[name] = {
            "passed": run.passed,
            "gates_run": len(run.validation.checks),
            "gates_failed": failed,
            "next_actions": 1 if run.next_action.strip() else 0,
            "artifact_complete": not check_artifact(run.artifact),
        }
    return result
