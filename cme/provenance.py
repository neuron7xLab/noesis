"""Claim governance: модель провенансу та таксономія заборонених claims.

Кожне високорівневе твердження тегується рівно одним статусом. Це формальний
центр чесності CME: відокремлює спостережене від виведеного, спекулятивного й
забороненого.
"""

from __future__ import annotations

from dataclasses import dataclass

PROVENANCE: tuple[str, ...] = ("observed", "inferred", "speculative", "forbidden")

# Категорії заборонених claims (детектори в cme/forbidden.py).
FORBIDDEN_TAXONOMY: tuple[str, ...] = (
    "AGI achieved",
    "consciousness detected/measured",
    "IIT proves experience",
    "therapy/medical diagnosis",
    "destiny / karma / mysticism",
    "unmeasured brain claim",
    "validated neuroscience without data",
    "universal truth claim",
)


@dataclass(frozen=True)
class Claim:
    field: str
    value: str
    provenance: str

    def to_dict(self) -> dict[str, str]:
        return {"field": self.field, "value": self.value, "provenance": self.provenance}


def is_valid_provenance(tag: str) -> bool:
    return tag in PROVENANCE


def governance_summary(claims: list[Claim]) -> dict[str, int]:
    """Зведення розподілу провенансу по claims."""
    summary = dict.fromkeys(PROVENANCE, 0)
    for c in claims:
        if c.provenance in summary:
            summary[c.provenance] += 1
    return summary
