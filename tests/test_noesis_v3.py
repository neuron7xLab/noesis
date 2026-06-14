"""Тести CME v0.3: онтологія, карти, синтез, reverse plan, 12 прикладів, evidence."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from noesis.engine import run_and_save_v3, run_v3
from noesis.ontology import AXES, build_reality_maps, extract_categories
from noesis.synthesis import build_synthesis
from noesis.validators import validate_categories, validate_maps, validate_synthesis

_PROBLEMS = sorted((Path(__file__).resolve().parent.parent / "examples" / "problems").glob("*.txt"))


def test_extractor_fires_on_signal() -> None:
    active = extract_categories("хочу змінити роботу бо немає сенсу і боюсь ризику")
    names = {c.name for c in active}
    assert "Зміна" in names  # china
    assert validate_categories(active).passed


def test_extractor_never_empty() -> None:
    active = extract_categories("...")  # без жодного маркера
    assert len(active) == 1
    assert active[0].matched  # дефолтна категорія


def test_reality_maps_axes_and_dominant() -> None:
    maps = build_reality_maps(extract_categories("треба зробити продукт перевірити гіпотезу й оцінити результат"))
    assert maps.dominant_axis in AXES
    assert validate_maps(maps).passed


def test_synthesis_four_axes() -> None:
    synth = build_synthesis(build_reality_maps(extract_categories("хочу зрозуміти суть і змінити підхід")))
    for value in synth.to_dict().values():
        assert value.strip()
    assert validate_synthesis(synth).passed


def test_twelve_problem_examples_present() -> None:
    assert len(_PROBLEMS) >= 12


@pytest.mark.parametrize("path", _PROBLEMS, ids=lambda p: p.name)
def test_problem_end_to_end_dod(path: Path) -> None:
    raw = path.read_text(encoding="utf-8").strip()
    run = run_v3(raw)
    # Definition of Done — у одну команду показано все необхідне:
    assert run.passed, [v.to_dict() for v in run.validations if not v.passed]
    assert run.maps.dominant_axis in AXES                       # яка карта активна
    assert run.controlling_category                              # яка категорія керує
    assert run.reverse.first_missing_condition.strip()          # перша відсутня умова
    assert run.next_action.strip()                              # наступна дія
    assert run.synthesis.refuse.strip()                         # failure mode під наглядом


def test_evidence_bundle_v3_eight_files(tmp_path: Path) -> None:
    run, manifest = run_and_save_v3("хочу запустити продукт але застряг між двома напрямками", tmp_path)
    expected = {
        "raw_input.md", "category_map.json", "reality_maps.md", "synthesis_axis.md",
        "artifact.json", "validation.json", "next_action.md", "manifest.json",
    }
    assert {p.name for p in tmp_path.iterdir()} == expected
    assert manifest["validations_passed"] is True
    assert manifest["version"] == "0.3"
    loaded = json.loads((tmp_path / "category_map.json").read_text(encoding="utf-8"))
    assert isinstance(loaded, list) and loaded
