"""Сервісний шар: зв'язує детерміновані інструменти з API-моделями."""

from __future__ import annotations

from app.models import FinalizeResponse, IntentResponse
from tools.finalizer100 import validate_finalizer
from tools.intent_parser import parse_intent


def finalize(text: str) -> FinalizeResponse:
    result = validate_finalizer(text)
    return FinalizeResponse(
        word_count=result.word_count,
        in_range=result.in_range,
        missing_anchors=result.missing_anchors,
        ok=result.ok,
    )


def decode_intent(message: str) -> IntentResponse:
    intent = parse_intent(message)
    return IntentResponse(
        surface=intent.surface,
        process=intent.process,
        strategic=intent.strategic,
        constraint=intent.constraint,
        next_action=intent.next_action,
        assumptions=intent.assumptions,
    )
