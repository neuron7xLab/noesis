"""FastAPI-додаток: /health, /finalize, /intent."""

from __future__ import annotations

from typing import Any

from fastapi import FastAPI

from app.models import (
    ArtifactRequest,
    FinalizeRequest,
    FinalizeResponse,
    IntentRequest,
    IntentResponse,
    RawRequest,
    ReverseRequest,
)
from app.services import decode_intent, finalize
from cme.generators import (
    build_artifact_deterministic,
    build_introspection_deterministic,
    build_mirror_deterministic,
)
from cme.pipeline import run_pipeline
from cme.validators import (
    validate_artifact,
    validate_introspection,
    validate_mirror,
    validate_reverse,
)
from tools.reverse_inference import plan_backwards

app = FastAPI(
    title="Cognitive Mirror Methods",
    version="0.1.0",
    description="Практичні brain-inspired методи мислення з LLM-дзеркалом.",
)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/finalize", response_model=FinalizeResponse)
def finalize_endpoint(req: FinalizeRequest) -> FinalizeResponse:
    """Перевіряє Finalizer-100 артефакт на контракт 90–110 слів + якорі."""
    return finalize(req.text)


@app.post("/intent", response_model=IntentResponse)
def intent_endpoint(req: IntentRequest) -> IntentResponse:
    """Розкладає сире повідомлення на 5 шарів наміру."""
    return decode_intent(req.message)


@app.post("/mirror")
def mirror_endpoint(req: RawRequest) -> dict[str, Any]:
    mirror = build_mirror_deterministic(req.text)
    return {"mirror": mirror.to_dict(), "validation": validate_mirror(mirror, req.text).to_dict()}


@app.post("/introspect")
def introspect_endpoint(req: RawRequest) -> dict[str, Any]:
    intro = build_introspection_deterministic(req.text)
    return {"introspection": intro.to_dict(), "validation": validate_introspection(intro, req.text).to_dict()}


@app.post("/reverse")
def reverse_endpoint(req: ReverseRequest) -> dict[str, Any]:
    trace = plan_backwards(
        target_state=req.target_state,
        current_facts=req.current_facts,
        required_conditions=req.required_conditions,
    )
    return {"reverse": trace.to_dict(), "validation": validate_reverse(trace).to_dict()}


@app.post("/artifact")
def artifact_endpoint(req: RawRequest) -> dict[str, Any]:
    artifact = build_artifact_deterministic(req.text)
    return {"artifact": artifact, "validation": validate_artifact(artifact, req.text).to_dict()}


@app.post("/pipeline")
def pipeline_endpoint(req: RawRequest) -> dict[str, Any]:
    run = run_pipeline(req.text, backend="deterministic")
    return {
        "method_selected": run.method_selected,
        "mirror": run.mirror.to_dict(),
        "introspection": run.introspection.to_dict(),
        "artifact": run.artifact,
        "next_action": run.next_action,
        "passed": run.passed,
        "validations": [v.to_dict() for v in run.validations],
    }


@app.post("/validate")
def validate_endpoint(req: ArtifactRequest) -> dict[str, Any]:
    return validate_artifact(req.artifact).to_dict()
