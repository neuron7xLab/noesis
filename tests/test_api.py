"""Smoke-тести HTTP-фасаду."""

from __future__ import annotations

import pytest

pytest.importorskip("httpx")  # TestClient потребує httpx
from fastapi.testclient import TestClient  # noqa: E402

from app.api import app  # noqa: E402

client = TestClient(app)


def test_health() -> None:
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}


def test_finalize_endpoint_flags_short_text() -> None:
    resp = client.post("/finalize", json={"text": "намір мета блокер дія метрика ризик"})
    assert resp.status_code == 200
    body = resp.json()
    assert body["ok"] is False
    assert body["in_range"] is False


def test_intent_endpoint_returns_five_layers() -> None:
    resp = client.post("/intent", json={"message": "Збери репо без води"})
    assert resp.status_code == 200
    body = resp.json()
    for key in ("surface", "process", "strategic", "constraint", "next_action"):
        assert key in body
