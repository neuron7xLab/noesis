"""Pydantic-моделі запитів/відповідей API."""

from __future__ import annotations

from pydantic import BaseModel, Field


class FinalizeRequest(BaseModel):
    text: str = Field(..., min_length=1, description="Текст-кандидат на Finalizer-100.")


class FinalizeResponse(BaseModel):
    word_count: int
    in_range: bool
    missing_anchors: list[str]
    ok: bool


class IntentRequest(BaseModel):
    message: str = Field(..., min_length=1, description="Сире повідомлення користувача.")


class IntentResponse(BaseModel):
    surface: str
    process: str
    strategic: str
    constraint: str
    next_action: str
    assumptions: list[str]
