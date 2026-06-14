"""Cover tools/ adapters + save paths: llm_adapter, pipeline, finalizer100, neuro save."""

from __future__ import annotations

import sys
import types
from pathlib import Path

import pytest

import tools.llm_adapter as adapter
import tools.pipeline as pipe
from noesis.neuro import run_and_save_v4
from tools.finalizer100 import MAX_WORDS, MIN_WORDS, REQUIRED_ANCHORS
from tools.finalizer100 import main as finalizer_main


# ── llm_adapter ───────────────────────────────────────────────────────────────


def test_load_prompt_returns_text() -> None:
    assert adapter.load_prompt("finalizer_mirror.md").strip()


def test_complete_unknown_backend_raises() -> None:
    with pytest.raises(ValueError):
        adapter.complete("sys", "user", backend="bogus")


def test_complete_cli_missing_binary_raises(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(adapter.shutil, "which", lambda _: None)
    with pytest.raises(RuntimeError):
        adapter.complete("sys", "user", backend="cli")


def test_complete_cli_success(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(adapter.shutil, "which", lambda _: "/usr/bin/claude")
    monkeypatch.setattr(
        adapter.subprocess,
        "run",
        lambda *a, **k: types.SimpleNamespace(returncode=0, stdout="  cli-out  ", stderr=""),
    )
    assert adapter.complete("sys", "user", backend="cli") == "cli-out"


def test_complete_cli_nonzero_raises(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(adapter.shutil, "which", lambda _: "/usr/bin/claude")
    monkeypatch.setattr(
        adapter.subprocess,
        "run",
        lambda *a, **k: types.SimpleNamespace(returncode=2, stdout="", stderr="boom"),
    )
    with pytest.raises(RuntimeError):
        adapter.complete("sys", "user", backend="cli")


def test_complete_auto_routes_to_cli_without_key(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    monkeypatch.setattr(adapter.shutil, "which", lambda _: None)
    with pytest.raises(RuntimeError):  # cli path reached -> binary missing
        adapter.complete("sys", "user", backend="auto")


def test_complete_sdk_via_fake_anthropic(monkeypatch: pytest.MonkeyPatch) -> None:
    fake = types.ModuleType("anthropic")

    class _Msgs:
        def create(self, **kwargs: object) -> object:
            return types.SimpleNamespace(
                content=[types.SimpleNamespace(type="text", text="sdk-out")]
            )

    class _Client:
        def __init__(self, *a: object, **k: object) -> None:
            self.messages = _Msgs()

    fake.Anthropic = _Client  # type: ignore[attr-defined]
    monkeypatch.setitem(sys.modules, "anthropic", fake)
    monkeypatch.setenv("ANTHROPIC_API_KEY", "x")
    assert adapter.complete("sys", "user", backend="auto") == "sdk-out"


# ── tools/pipeline ────────────────────────────────────────────────────────────


def test_parse_sections() -> None:
    from tools.artifact_checker import REQUIRED_SECTIONS

    text = "\n".join(f"{s}: value-{i}" for i, s in enumerate(REQUIRED_SECTIONS))
    parsed = pipe.parse_sections(text)
    assert set(parsed) == set(REQUIRED_SECTIONS)


def _conforming_mirror() -> str:
    n = (MIN_WORDS + MAX_WORDS) // 2
    return " ".join(list(REQUIRED_ANCHORS) + ["слово"] * (n - len(REQUIRED_ANCHORS)))


def test_run_pipeline_and_main(monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> None:
    from tools.artifact_checker import REQUIRED_SECTIONS

    mirror = _conforming_mirror()
    artifact = "\n".join(f"{s}: повноцінний зміст секції {s}" for s in REQUIRED_SECTIONS)

    def fake_complete(system: str, user: str, *, model: str = "", backend: str = "auto") -> str:
        return artifact if "value" in user or user == mirror else mirror

    monkeypatch.setattr(pipe, "load_prompt", lambda name: "prompt")
    monkeypatch.setattr(pipe, "complete", fake_complete)

    result = pipe.run_pipeline("сирий намір тут", backend="cli")
    assert result.raw_intent == "сирий намір тут"
    assert result.mirror == mirror

    rc = pipe.main(["сирий намір"])
    assert rc in (0, 1)
    assert "ТРУБА НЕСЕ ВОДУ" in capsys.readouterr().out


# ── finalizer100 main + neuro save ────────────────────────────────────────────


def test_finalizer_main(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    f = tmp_path / "art.md"
    f.write_text("намір мета блокер дія метрика ризик", encoding="utf-8")
    rc = finalizer_main([str(f)])
    out = capsys.readouterr().out
    assert rc in (0, 1)
    assert "words=" in out


def test_run_and_save_v4_writes_bundle(tmp_path: Path) -> None:
    run, manifest = run_and_save_v4("хочу зрозуміти куди рухаюсь і що блокує", tmp_path)
    assert manifest["engine"] == "cognitive-mirror-engine"
    assert manifest["version"] == "0.4"
    for name in manifest["files"]:
        assert (tmp_path / name).exists()
