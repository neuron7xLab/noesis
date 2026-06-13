"""Уніфікований CLI `cme`: mirror · introspect · reverse · artifact · pipeline · validate."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from cme.engine import (
    render_next_action_md,
    render_reality_maps_md,
    render_synthesis_md,
    run_and_save_v3,
    run_v3,
)
from cme.generators import (
    build_artifact_deterministic,
    build_introspection_deterministic,
    build_mirror_deterministic,
    build_mirror_llm,
)
from cme.ontology import build_reality_maps, extract_categories
from cme.synthesis import build_synthesis
from cme.validators import (
    validate_artifact,
    validate_categories,
    validate_introspection,
    validate_maps,
    validate_mirror,
    validate_reverse,
    validate_synthesis,
)
from tools.reverse_inference import plan_backwards

_BACKENDS = ("deterministic", "llm", "cli", "sdk", "auto")


def _read(path: str) -> str:
    return Path(path).read_text(encoding="utf-8").strip()


def _emit(report_passed: bool) -> int:
    return 0 if report_passed else 1


def _cmd_mirror(args: argparse.Namespace) -> int:
    raw = _read(args.input)
    mirror = build_mirror_deterministic(raw) if args.backend == "deterministic" else build_mirror_llm(
        raw, backend="auto" if args.backend == "llm" else args.backend
    )
    report = validate_mirror(mirror, raw)
    print(json.dumps({"mirror": mirror.to_dict(), "validation": report.to_dict()}, ensure_ascii=False, indent=2))
    return _emit(report.passed)


def _cmd_introspect(args: argparse.Namespace) -> int:
    raw = _read(args.input)
    intro = build_introspection_deterministic(raw)
    report = validate_introspection(intro, raw)
    print(json.dumps({"introspection": intro.to_dict(), "validation": report.to_dict()}, ensure_ascii=False, indent=2))
    return _emit(report.passed)


def _cmd_reverse(args: argparse.Namespace) -> int:
    spec = json.loads(_read(args.input))
    trace = plan_backwards(
        target_state=spec["target_state"],
        current_facts=spec.get("current_facts", []),
        required_conditions=spec.get("required_conditions", []),
    )
    report = validate_reverse(trace)
    print(json.dumps({"reverse": trace.to_dict(), "validation": report.to_dict()}, ensure_ascii=False, indent=2))
    return _emit(report.passed)


def _cmd_artifact(args: argparse.Namespace) -> int:
    insight = _read(args.input)
    artifact = build_artifact_deterministic(insight)
    report = validate_artifact(artifact, insight)
    print(json.dumps({"artifact": artifact, "validation": report.to_dict()}, ensure_ascii=False, indent=2))
    return _emit(report.passed)


def _cmd_ontology(args: argparse.Namespace) -> int:
    raw = _read(args.input)
    active = extract_categories(raw)
    report = validate_categories(active)
    print(json.dumps({"categories": [c.to_dict() for c in active], "validation": report.to_dict()},
                     ensure_ascii=False, indent=2))
    return _emit(report.passed)


def _cmd_maps(args: argparse.Namespace) -> int:
    raw = _read(args.input)
    maps = build_reality_maps(extract_categories(raw))
    report = validate_maps(maps)
    print(json.dumps({"reality_maps": maps.to_dict(), "validation": report.to_dict()},
                     ensure_ascii=False, indent=2))
    return _emit(report.passed)


def _cmd_synthesize(args: argparse.Namespace) -> int:
    raw = _read(args.input)
    maps = build_reality_maps(extract_categories(raw))
    synth = build_synthesis(maps)
    report = validate_synthesis(synth)
    print(json.dumps({"synthesis_axis": synth.to_dict(), "validation": report.to_dict()},
                     ensure_ascii=False, indent=2))
    return _emit(report.passed)


def _cmd_pipeline(args: argparse.Namespace) -> int:
    raw = _read(args.input)
    if args.evidence:
        run, manifest = run_and_save_v3(raw, Path(args.evidence))
        print(json.dumps(manifest, ensure_ascii=False, indent=2))
    else:
        run = run_v3(raw)
        print(render_reality_maps_md(run))
        print(render_synthesis_md(run))
        print(render_next_action_md(run))
    print(f"\nВАЛІДАЦІЯ: {'PASS' if run.passed else 'FAIL'}", file=sys.stderr)
    return _emit(run.passed)


def _cmd_validate(args: argparse.Namespace) -> int:
    payload = json.loads(_read(args.input))
    artifact = payload.get("artifact", payload)
    report = validate_artifact(artifact)
    print(json.dumps(report.to_dict(), ensure_ascii=False, indent=2))
    return _emit(report.passed)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="cme", description="Cognitive Mirror Engine.")
    sub = parser.add_subparsers(dest="command", required=True)

    def add_backend(p: argparse.ArgumentParser) -> None:
        p.add_argument("--backend", default="deterministic", choices=_BACKENDS)

    p_mirror = sub.add_parser("mirror", help="намір → дзеркало")
    p_mirror.add_argument("input")
    add_backend(p_mirror)
    p_mirror.set_defaults(func=_cmd_mirror)

    p_intro = sub.add_parser("introspect", help="емоція → карта стану")
    p_intro.add_argument("input")
    p_intro.set_defaults(func=_cmd_introspect)

    p_rev = sub.add_parser("reverse", help="ціль.json → перша відсутня умова")
    p_rev.add_argument("input")
    p_rev.set_defaults(func=_cmd_reverse)

    p_art = sub.add_parser("artifact", help="інсайт → 7-секційний артефакт")
    p_art.add_argument("input")
    p_art.set_defaults(func=_cmd_artifact)

    p_ont = sub.add_parser("ontology", help="текст → активні метафізичні категорії")
    p_ont.add_argument("input")
    p_ont.set_defaults(func=_cmd_ontology)

    p_maps = sub.add_parser("maps", help="текст → три карти реальності")
    p_maps.add_argument("input")
    p_maps.set_defaults(func=_cmd_maps)

    p_syn = sub.add_parser("synthesize", help="текст → синтез-вісь (preserve/test/evolve/refuse)")
    p_syn.add_argument("input")
    p_syn.set_defaults(func=_cmd_synthesize)

    p_pipe = sub.add_parser("pipeline", help="повна труба v0.3 + Evidence Bundle (8 файлів)")
    p_pipe.add_argument("input")
    p_pipe.add_argument("--evidence", help="директорія для Evidence Bundle")
    add_backend(p_pipe)
    p_pipe.set_defaults(func=_cmd_pipeline)

    p_val = sub.add_parser("validate", help="перевірити артефакт.json")
    p_val.add_argument("input")
    p_val.set_defaults(func=_cmd_validate)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    func = args.func
    assert callable(func)
    return int(func(args))


if __name__ == "__main__":
    raise SystemExit(main())
