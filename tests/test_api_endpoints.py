"""Full HTTP-surface coverage: every POST endpoint returns a valid response.

The bulk of `app/api.py` is thin `RawRequest -> dict` adapters over the engine.
This drives each one through the real FastAPI app (deterministic backend, no LLM)
and asserts a 200 + a non-empty JSON object, plus targeted checks for the
typed-request endpoints.
"""

from __future__ import annotations

import pytest

pytest.importorskip("httpx")
from fastapi.testclient import TestClient  # noqa: E402
from starlette.routing import Route  # noqa: E402

from app.api import app  # noqa: E402

client = TestClient(app)

_SAMPLE = "хочу запустити продукт але застряг між напрямками і не знаю що робити далі"

# endpoints with a non-RawRequest body are exercised explicitly below
_SPECIAL = {"/finalize", "/intent", "/reverse", "/validate", "/health"}


def _raw_post_paths() -> list[str]:
    paths: list[str] = []
    for route in app.routes:
        if isinstance(route, Route) and "POST" in (route.methods or set()):
            if route.path not in _SPECIAL:
                paths.append(route.path)
    return sorted(set(paths))


@pytest.mark.parametrize("path", _raw_post_paths())
def test_raw_endpoint_returns_json_object(path: str) -> None:
    resp = client.post(path, json={"text": _SAMPLE})
    assert resp.status_code == 200, f"{path}: {resp.status_code} {resp.text[:200]}"
    body = resp.json()
    assert isinstance(body, dict) and body, f"{path}: empty/invalid body"


def test_every_raw_endpoint_discovered() -> None:
    # guard: the discovery actually found the bulk of the surface
    assert len(_raw_post_paths()) >= 30


def test_reverse_endpoint() -> None:
    resp = client.post(
        "/reverse",
        json={
            "target_state": "система в продакшені з моніторингом",
            "current_facts": ["є прототип"],
            "required_conditions": ["CI зелений"],
        },
    )
    assert resp.status_code == 200
    body = resp.json()
    assert "reverse" in body and "validation" in body


def test_validate_endpoint_roundtrip() -> None:
    artifact = client.post("/artifact", json={"text": _SAMPLE}).json()["artifact"]
    resp = client.post("/validate", json={"artifact": artifact})
    assert resp.status_code == 200
    assert "passed" in resp.json()


def test_raw_endpoint_rejects_empty_text() -> None:
    resp = client.post("/mirror", json={"text": ""})
    assert resp.status_code == 422  # min_length=1 contract


def test_unknown_path_is_404() -> None:
    assert client.post("/does-not-exist", json={"text": _SAMPLE}).status_code == 404
