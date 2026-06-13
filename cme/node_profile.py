"""Node Information Geometry Profiler — характеристика вузлів за обчислювальними властивостями.

ЧЕСНО: це інженерна ХАРАКТЕРИЗАЦІЯ дизайну (proxy), не виміряні нейро-параметри.
Жоден вузол не зветься «розумним» без вказаної операції; кожен має failure_risk.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any


@dataclass(frozen=True)
class NodeProfile:
    node_id: str
    role: str
    latency: str
    bandwidth: str  # low | medium | high
    bandwidth_rank: int  # 1..5 для bottleneck-розрахунку
    noise_level: str
    prior_strength: str
    variance_generation: str
    compression_power: str
    validation_power: str
    failure_risk: str
    best_use: str
    do_not_use_for: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


# Інформаційна геометрія кожного типу вузла (дизайн-характеризація).
PROFILES: dict[str, NodeProfile] = {
    "human_intent_controller": NodeProfile(
        "human_intent_controller", "тримає інтенційний вектор", "high", "low", 1, "low", "strong",
        "low", "low", "high", "втома, низька пропускна — bottleneck",
        "напрям, контекстна когерентність, фінальна відповідальність", "масову генерацію варіантів"),
    "prompt_encoder": NodeProfile(
        "prompt_encoder", "стискає імпульс у запит", "low", "medium", 3, "low", "medium",
        "low", "medium", "low", "втрата нюансу при стисненні",
        "формалізація наміру", "глибокий аналіз"),
    "llm_expander": NodeProfile(
        "llm_expander", "розгортає простір гіпотез", "low", "high", 5, "high", "weak",
        "high", "low", "low", "галюцинація, слабке фінальне судження",
        "варіація, абстракція, генерація гіпотез", "фінальне рішення/істину"),
    "critic": NodeProfile(
        "critic", "знаходить слабкі місця", "low", "medium", 3, "medium", "medium",
        "medium", "medium", "medium", "критика заради критики",
        "контр-аргументи, альтернативи", "генерацію нового напряму"),
    "auditor": NodeProfile(
        "auditor", "перевіряє повноту й overreach", "medium", "medium", 3, "low", "medium",
        "low", "low", "high", "overblocking, церемоніальність",
        "виявлення failure-mode, missing evidence", "творчий відбір"),
    "verifier": NodeProfile(
        "verifier", "гейтує claims за схемою", "low", "medium", 2, "low", "strong",
        "low", "low", "high", "false negatives, вбивство креативного сигналу",
        "schema/forbidden/artifact-валідація", "відкриту генерацію"),
    "compressor": NodeProfile(
        "compressor", "стискає абстракції", "low", "medium", 3, "low", "medium",
        "high", "low", "medium", "втрата при надстисненні",
        "кристалізація в артефакт", "розгортання простору"),
    "artifact_builder": NodeProfile(
        "artifact_builder", "робить перевірний об'єкт", "low", "medium", 3, "low", "medium",
        "medium", "high", "medium", "доказ-театр (артефакт без тесту)",
        "матеріалізація думки", "сирий інсайт"),
    "validator": NodeProfile(
        "validator", "виконує 12 гейтів", "low", "high", 4, "low", "strong",
        "low", "low", "high", "хибна впевненість при пропуску гейта",
        "детермінована перевірка", "оцінку суб'єктивної якості"),
    "decision_gate": NodeProfile(
        "decision_gate", "IEV: pass/fail/compress/reroute", "high", "low", 1, "low", "strong",
        "low", "low", "high", "вузьке місце людської пропускної",
        "фінальне judgement + precision-weight", "масштабну генерацію"),
    "memory_store": NodeProfile(
        "memory_store", "evidence bundle", "low", "high", 4, "low", "neutral",
        "low", "low", "low", "застарілий контекст",
        "відтворюваність, провенанс", "активне мислення"),
}


def profile_nodes() -> list[NodeProfile]:
    return list(PROFILES.values())


def bottleneck_nodes() -> list[str]:
    """Вузли з найнижчою пропускною (bandwidth_rank=1) — структурне вузьке місце."""
    return [p.node_id for p in PROFILES.values() if p.bandwidth_rank == 1]
