"""FastAPI-додаток: /health, /finalize, /intent."""

from __future__ import annotations

from fastapi import FastAPI

from app.models import (
    FinalizeRequest,
    FinalizeResponse,
    IntentRequest,
    IntentResponse,
)
from app.services import decode_intent, finalize

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
