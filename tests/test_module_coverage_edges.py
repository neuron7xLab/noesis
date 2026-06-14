"""Cover edge paths: eiic save, hallucination levels, complexity modes, llm fallback."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from noesis.complexity import estimate_complexity
from noesis.eiic import run_and_save_eiic
from noesis.forbidden import hallucination_risk
from noesis.generators import build_mirror_deterministic, build_mirror_llm
from tools.finalizer100 import MAX_WORDS, MIN_WORDS, REQUIRED_ANCHORS


def test_run_and_save_eiic_writes_bundle(tmp_path: Path) -> None:
    manifest = run_and_save_eiic("хочу зрозуміти себе і куди рухаюсь далі", tmp_path)
    assert manifest["engine"] == "eiic"
    for name in manifest["files"]:
        assert (tmp_path / name).exists()
    core = json.loads((tmp_path / "eiic_core.json").read_text(encoding="utf-8"))
    assert core


def test_hallucination_risk_levels() -> None:
    high, sig_h = hallucination_risk("це гарантовано стовідсотково працює")
    assert high == "high" and len(sig_h) >= 2
    medium, sig_m = hallucination_risk("це гарантовано працює")
    assert medium == "medium" and len(sig_m) == 1
    low, sig_l = hallucination_risk("можливо це спрацює")
    assert low == "low" and sig_l == []


def test_hallucination_risk_flags_unsourced_numbers() -> None:
    level, signals = hallucination_risk("точність 95 відсотків", source="без чисел")
    assert any("числа без джерела" in s for s in signals)


@pytest.mark.parametrize(
    "text,expected",
    [
        ("старт", "micro"),
        ("хочу запустити продукт але застряг трохи між кількома напрямками", "brief"),
    ],
)
def test_complexity_modes(text: str, expected: str) -> None:
    assert estimate_complexity(text).to_dict()["recommended_output_mode"] == expected


def test_complexity_standard_and_deep() -> None:
    standard = "слово " * 50
    assert estimate_complexity(standard).to_dict()["recommended_output_mode"] == "standard"
    deep = "слово " * 120
    assert estimate_complexity(deep).to_dict()["recommended_output_mode"] == "deep"


def test_build_mirror_llm_falls_back_when_nonconforming(monkeypatch: pytest.MonkeyPatch) -> None:
    import tools.llm_adapter as adapter

    monkeypatch.setattr(adapter, "load_prompt", lambda name: "prompt", raising=False)
    monkeypatch.setattr(adapter, "complete", lambda *a, **k: "too short", raising=False)
    raw = "хочу запустити продукт але застряг між напрямками"
    out = build_mirror_llm(raw, backend="cli")
    # non-conforming LLM output -> deterministic floor (identical to deterministic build)
    assert out.finalizer == build_mirror_deterministic(raw).finalizer


def test_build_mirror_llm_accepts_conforming(monkeypatch: pytest.MonkeyPatch) -> None:
    import tools.llm_adapter as adapter

    n = (MIN_WORDS + MAX_WORDS) // 2
    conforming = " ".join(list(REQUIRED_ANCHORS) + ["слово"] * (n - len(REQUIRED_ANCHORS)))
    monkeypatch.setattr(adapter, "load_prompt", lambda name: "prompt", raising=False)
    monkeypatch.setattr(adapter, "complete", lambda *a, **k: conforming, raising=False)
    out = build_mirror_llm("хочу запустити продукт але застряг", backend="cli")
    assert out.finalizer == conforming
