"""Validator Layer: детерміновані гейти для кожного типу артефакту.

Перевіряє: word count, anchor terms, required fields, artifact completeness,
hallucination risk, forbidden claims, signal/noise separation, soundness.
"""

from __future__ import annotations

from typing import Any

from cme.forbidden import check_forbidden_claims, hallucination_risk
from cme.models import Check, IntrospectionMap, MirrorArtifact, ValidationReport
from formal.metrics import falsifier_present
from tools.artifact_checker import check_artifact
from tools.finalizer100 import MAX_WORDS, MIN_WORDS, REQUIRED_ANCHORS, count_words
from tools.reverse_inference import ReverseTrace

_MIRROR_FIELDS = (
    "surface_intent", "hidden_goal", "constraint", "blocker", "next_action",
    "success_metric", "time_horizon", "critical_risk", "risk_reduction",
)
_INTROSPECTION_FIELDS = ("intent", "fear", "constraint", "missing_condition", "decision_boundary", "action")


def _forbidden_check(text: str) -> Check:
    violations = check_forbidden_claims(text)
    return Check("forbidden_claims", not violations,
                 "чисто" if not violations else "порушення: " + ", ".join(violations))


def _hallucination_check(text: str, source: str) -> Check:
    level, signals = hallucination_risk(text, source)
    return Check("hallucination_risk", level != "high",
                 f"рівень={level}" + (f"; сигнали: {', '.join(signals)}" if signals else ""))


def _fields_check(obj: dict[str, str], fields: tuple[str, ...]) -> Check:
    missing = [f for f in fields if not str(obj.get(f, "")).strip()]
    return Check("required_fields", not missing,
                 "усі поля присутні" if not missing else "відсутні: " + ", ".join(missing))


def validate_mirror(mirror: MirrorArtifact, source: str = "") -> ValidationReport:
    body = mirror.finalizer
    words = count_words(body)
    low = body.lower()
    anchors = [a for a in REQUIRED_ANCHORS if a not in low]
    return ValidationReport("mirror", [
        _fields_check(mirror.to_dict(), _MIRROR_FIELDS),
        Check("word_count", MIN_WORDS <= words <= MAX_WORDS, f"{words} слів (межа {MIN_WORDS}-{MAX_WORDS})"),
        Check("anchor_terms", not anchors, "усі якорі" if not anchors else "відсутні: " + ", ".join(anchors)),
        Check("signal_noise_separation", mirror.surface_intent != mirror.hidden_goal,
              "сигнал відокремлено від наміру-поверхні"),
        _forbidden_check(body),
        _hallucination_check(body, source),
    ])


def validate_introspection(intro: IntrospectionMap, source: str = "") -> ValidationReport:
    actions = [a for a in [intro.action] if a.strip()]
    return ValidationReport("introspection", [
        _fields_check(intro.to_dict(), _INTROSPECTION_FIELDS),
        Check("single_action_determinacy", len(actions) == 1, f"кандидатів дії: {len(actions)} (потрібно 1)"),
        _forbidden_check(intro.action + " " + intro.intent),
        _hallucination_check(" ".join(intro.to_dict().values()), source),
    ])


def validate_artifact(artifact: dict[str, str], source: str = "") -> ValidationReport:
    problems = check_artifact(artifact)
    validation_text = artifact.get("validation", "")
    blob = " ".join(str(v) for v in artifact.values())
    return ValidationReport("artifact", [
        Check("seven_sections", not problems, "усі 7 секцій" if not problems else "; ".join(problems)),
        Check("executable_falsifier", falsifier_present(validation_text),
              "validation містить виконуваний предикат/поріг"),
        _forbidden_check(blob),
        _hallucination_check(blob, source),
    ])


def validate_reverse(trace: ReverseTrace) -> ValidationReport:
    if trace.missing_constraints:
        sound = trace.missing_constraints[0].lower() in trace.next_action.lower()
    else:
        sound = "досяжна" in trace.next_action.lower()
    return ValidationReport("reverse", [
        Check("next_action_present", bool(trace.next_action.strip()), trace.next_action),
        Check("soundness", sound, "next_action посилається на першу відсутню умову"),
    ])


def report_to_dict(report: ValidationReport) -> dict[str, Any]:
    return report.to_dict()
