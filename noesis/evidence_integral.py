"""Evidence integral — store the integral of the process, not only the result.

    ∫ process = ordered trace of state transitions + decisions + artifacts + hashes

Every transition is sha256-chained to its predecessor, so the whole run is one
replayable hash chain anchored by ``final_manifest_hash``. A bundle is invalid if
an artifact has no trace, a transition has no hash, a verifier result is not
linked, or the chain cannot be replayed.

Path note: lives at ``noesis/evidence_integral.py`` (flat) because
``noesis/evidence.py`` already occupies the ``evidence`` name; this is the
``cme/evidence/evidence_integral.py`` of the Task 6 spec, adapted to the package.
"""

from __future__ import annotations

import hashlib
import json
from typing import Any

from noesis.ratios import rate


def _sha(payload: Any) -> str:
    blob = json.dumps(payload, ensure_ascii=False, sort_keys=True)
    return hashlib.sha256(blob.encode("utf-8")).hexdigest()


def _chain(items: list[dict[str, Any]]) -> list[str]:
    hashes: list[str] = []
    prev = ""
    for item in items:
        prev = hashlib.sha256((prev + _sha(item)).encode("utf-8")).hexdigest()
        hashes.append(prev)
    return hashes


def build_bundle(
    *,
    run_id: str,
    input_text: str,
    transitions: list[dict[str, Any]],
    artifacts: list[dict[str, Any]],
    decisions: list[dict[str, Any]],
    verifier_outputs: list[dict[str, Any]],
    rollback_points: list[str],
) -> dict[str, Any]:
    """Assemble a hash-chained evidence bundle. Each artifact/transition must link.

    transitions/artifacts/decisions are dicts; an artifact dict must carry a
    ``transition_index`` linking it to a transition, and a transition may carry a
    ``verifier_index`` linking it to a verifier output.
    """
    bundle: dict[str, Any] = {
        "run_id": run_id,
        "input_hash": _sha(input_text),
        "state_transition_hashes": _chain(transitions),
        "artifact_hashes": [_sha(a) for a in artifacts],
        "decision_hashes": [_sha(d) for d in decisions],
        "verifier_outputs": verifier_outputs,
        "rollback_points": rollback_points,
        "transitions": transitions,
        "artifacts": artifacts,
        "decisions": decisions,
    }
    bundle["final_manifest_hash"] = _sha(
        {k: v for k, v in bundle.items() if k != "final_manifest_hash"}
    )
    return bundle


def validate_bundle(bundle: dict[str, Any]) -> list[str]:
    """Return structured problems; empty list means the bundle is sound."""
    problems: list[str] = []
    transitions = bundle.get("transitions", [])
    artifacts = bundle.get("artifacts", [])

    if len(bundle.get("state_transition_hashes", [])) != len(transitions):
        problems.append("TRACE_WITHOUT_HASH: a transition has no hash")
    if len(bundle.get("artifact_hashes", [])) != len(artifacts):
        problems.append("ARTIFACT_WITHOUT_HASH: an artifact has no hash")

    for i, art in enumerate(artifacts):
        idx = art.get("transition_index")
        if idx is None or not (0 <= idx < len(transitions)):
            problems.append(f"ARTIFACT_WITHOUT_TRACE: artifact {i} not linked to a transition")

    verifier_count = len(bundle.get("verifier_outputs", []))
    for i, tr in enumerate(transitions):
        vidx = tr.get("verifier_index")
        if vidx is not None and not (0 <= vidx < verifier_count):
            problems.append(f"VERIFIER_NOT_LINKED: transition {i} verifier_index out of range")

    if not replay(bundle):
        problems.append("BUNDLE_NOT_REPLAYABLE: hash chain does not reproduce")
    return problems


def replay(bundle: dict[str, Any]) -> bool:
    """Recompute the chain + manifest hash and compare to stored values."""
    if _chain(bundle.get("transitions", [])) != bundle.get("state_transition_hashes", []):
        return False
    expected = _sha({k: v for k, v in bundle.items() if k != "final_manifest_hash"})
    return expected == bundle.get("final_manifest_hash")


def bundle_metrics(bundle: dict[str, Any]) -> dict[str, float]:
    transitions = bundle.get("transitions", [])
    artifacts = bundle.get("artifacts", [])
    n_art = len(artifacts)
    n_tr = len(transitions)
    hashed_art = min(len(bundle.get("artifact_hashes", [])), n_art)
    traced_art = sum(
        1
        for a in artifacts
        if isinstance(a.get("transition_index"), int) and 0 <= a["transition_index"] < n_tr
    )
    with_verifier = sum(1 for t in transitions if t.get("verifier_index") is not None)
    return {
        "reproducibility_score": 1.0 if replay(bundle) else 0.0,
        "hash_coverage_rate": rate(hashed_art, n_art, default=1.0),
        "artifact_traceability_rate": rate(traced_art, n_art, default=1.0),
        "verifier_attachment_rate": rate(with_verifier, n_tr, default=0.0),
    }
