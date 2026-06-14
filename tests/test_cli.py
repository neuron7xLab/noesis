"""Контрактний smoke по ВСІХ підкомандах CLI `noesis`.

Список команд береться напряму з парсера, тож кожна нова підкоманда
автоматично потрапляє під цей контракт. Перевіряємо: команда виконується
без винятку, повертає валідний exit-код і друкує парсабельний JSON там, де
це передбачено. LLM не потрібен — усе на детермінованому backend.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import pytest

from noesis import __version__
from noesis.cli import build_parser, main

EXAMPLE = "examples/problems/08_ai_system_design.txt"

# команди з нестандартним входом — тестуються окремо нижче
_SPECIAL = {
    "reverse",
    "validate",
    "verdict",
    "human-eval",
    "benchmark",
    "bibliography",
    "physics-boundary",
    "recovery",
}
# команди, що друкують не-JSON (markdown / звіт)
_NON_JSON = {"human-eval", "eiic", "neuro"}


def _subcommands() -> list[str]:
    parser = build_parser()
    action = next(a for a in parser._actions if isinstance(a, argparse._SubParsersAction))
    return sorted(action.choices)


def _run(capsys: pytest.CaptureFixture[str], argv: list[str]) -> tuple[int, str]:
    rc = main(argv)
    return rc, capsys.readouterr().out


def _last_json(text: str) -> object:
    """Дістати JSON-обʼєкт із виводу, що може мати markdown-преамбулу + JSON-хвіст."""
    text = text.strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass
    start = text.rfind("\n{")
    if start != -1:
        return json.loads(text[start + 1 :])
    return json.loads(text[text.index("{") :])


# --- мета-контракт: жодна команда не загублена -------------------------------

def test_all_subcommands_covered() -> None:
    cmds = set(_subcommands())
    # все, що не в _SPECIAL, має приймати позиційний input-файл (text-вхід)
    assert _SPECIAL <= cmds
    assert len(cmds) >= 40, f"очікували ≥40 підкоманд, є {len(cmds)}"


def test_version(capsys: pytest.CaptureFixture[str]) -> None:
    with pytest.raises(SystemExit) as exc:
        main(["--version"])
    assert exc.value.code == 0
    assert __version__ in capsys.readouterr().out


# --- усі text-вхідні команди -------------------------------------------------

_TEXT_CMDS = [c for c in _subcommands() if c not in _SPECIAL]


@pytest.mark.parametrize("cmd", _TEXT_CMDS)
def test_text_command_runs(cmd: str, capsys: pytest.CaptureFixture[str]) -> None:
    rc, out = _run(capsys, [cmd, EXAMPLE])
    assert rc in (0, 1), f"{cmd}: несподіваний exit-код {rc}"
    assert out.strip(), f"{cmd}: порожній вивід"
    if cmd not in _NON_JSON:
        _last_json(out)  # JSON-команди мусять друкувати валідний JSON-обʼєкт


# --- спец-входи --------------------------------------------------------------

def test_reverse(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    spec = tmp_path / "goal.json"
    spec.write_text(
        json.dumps(
            {
                "target_state": "система в продакшені з моніторингом",
                "current_facts": ["є прототип"],
                "required_conditions": ["CI зелений", "є алерти"],
            }
        ),
        encoding="utf-8",
    )
    rc, out = _run(capsys, ["reverse", str(spec)])
    assert rc in (0, 1)
    payload = json.loads(out)
    assert "reverse" in payload and "validation" in payload


def test_validate_roundtrip(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    # спершу згенеруй артефакт, тоді провалідуй його через CLI
    rc, out = _run(capsys, ["artifact", EXAMPLE])
    assert rc in (0, 1)
    artifact = json.loads(out)["artifact"]
    art_file = tmp_path / "artifact.json"
    art_file.write_text(json.dumps({"artifact": artifact}, ensure_ascii=False), encoding="utf-8")
    rc2, out2 = _run(capsys, ["validate", str(art_file)])
    assert rc2 in (0, 1)
    assert json.loads(out2)


def test_benchmark(capsys: pytest.CaptureFixture[str]) -> None:
    rc, out = _run(capsys, ["benchmark"])
    assert rc in (0, 1)
    assert json.loads(out)


def test_evidence_bundle_then_verdict_and_human_eval(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    out_dir = tmp_path / "bundle"
    rc, _ = _run(capsys, ["pipeline", EXAMPLE, "--evidence", str(out_dir)])
    assert rc in (0, 1)
    assert (out_dir / "manifest.json").exists()
    assert (out_dir / "human_eval_packet.json").exists()

    rc_v, out_v = _run(capsys, ["verdict", str(out_dir)])
    assert rc_v in (0, 1)
    assert _last_json(out_v)["overall_status"] in {"PASS", "FAIL", "PARTIAL"}

    rc_h, out_h = _run(capsys, ["human-eval", str(out_dir)])
    assert rc_h in (0, 1)
    assert out_h.strip()


def test_physics_boundary_validate_runs(capsys: pytest.CaptureFixture[str]) -> None:
    rc, out = _run(capsys, ["physics-boundary", "validate"])
    assert rc in (0, 1), f"physics-boundary: несподіваний exit-код {rc}"
    assert "PHYSICS CONTRACT:" in out


def test_recovery_self_check_runs(capsys: pytest.CaptureFixture[str]) -> None:
    rc, out = _run(capsys, ["recovery", "self-check"])
    assert rc == 0, f"recovery self-check should pass, got {rc}"
    payload = json.loads(out)
    assert payload["healthy"] is True
    assert payload["statuses"] == ["RECOVERED", "RECOVERED", "ESCALATED"]
