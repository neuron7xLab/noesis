"""Уніфікований CLI `cme`: mirror · introspect · reverse · artifact · pipeline · validate."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from cme.adaptive import build_adaptive_mirror
from cme.benchmark import run_ablation, run_benchmark
from cme.benchmark_v6 import run_ablation_v6, run_benchmark_v6
from cme.causal import build_category_effects, build_reality_map_delta, track_theory_contribution
from cme.complexity import estimate_complexity
from cme.eiic import render_eiic_md, run_and_save_eiic, run_eiic
from cme.ontology import build_reality_maps as _brm
from cme.theories import run_theories as _rt
from cme.generators import build_mirror_deterministic as _bmd
from cme.pipeline_v6 import run_and_save_v6, run_v6
from cme.generators import (
    build_artifact_deterministic,
    build_introspection_deterministic,
    build_mirror_deterministic,
    build_mirror_llm,
)
from cme.neuro import render_neuro_md, run_and_save_v4, run_v4
from cme.ontology import build_reality_maps, extract_categories
from cme.synthesis import build_synthesis
from cme.theories import run_theories
from cme.verdict import read_verdict, render_verdict_md
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
        run, manifest = run_and_save_v6(raw, Path(args.evidence))
        print(json.dumps(manifest, ensure_ascii=False, indent=2))
    else:
        run = run_v6(raw)
        print(json.dumps({
            "selected_action": run.action.selected_action,
            "compression_status": run.mirror.compression_status,
            "category_layer": "no_effect" if run.flags["category_layer_no_effect"] else "causal",
            "theory_status": run.theory_status,
            "decorative_flags": [k for k, v in run.flags.items() if v],
            "gates": run.validation.to_dict(),
        }, ensure_ascii=False, indent=2))
    print(f"\nВАЛІДАЦІЯ: {'PASS' if run.passed else 'FAIL'}", file=sys.stderr)
    return _emit(run.passed)


def _cmd_verdict(args: argparse.Namespace) -> int:
    out = Path(args.out)
    verdict_md = out / "verdict.md"
    manifest = json.loads((out / "manifest.json").read_text(encoding="utf-8"))
    if verdict_md.exists():  # v0.6 bundle
        print(verdict_md.read_text(encoding="utf-8"))
        print(json.dumps({k: manifest[k] for k in (
            "pipeline_version", "compression_status", "category_layer_status",
            "theory_layer_status", "human_eval_status", "decorative_layers", "overall_status",
        ) if k in manifest}, ensure_ascii=False, indent=2))
        return _emit(manifest.get("overall_status") == "PASS")
    v = read_verdict(out)  # v0.5 fallback
    print(render_verdict_md(v))
    return _emit(v["overall_status"] == "PASS")


def _cmd_benchmark(args: argparse.Namespace) -> int:
    print(json.dumps({"benchmark_v6": run_benchmark_v6(), "ablation_v6": run_ablation_v6(),
                      "benchmark_v5": run_benchmark(), "ablation_v5": run_ablation()},
                     ensure_ascii=False, indent=2))
    return 0


def _cmd_complexity(args: argparse.Namespace) -> int:
    print(json.dumps(estimate_complexity(_read(args.input)).to_dict(), ensure_ascii=False, indent=2))
    return 0


def _cmd_mirror_adaptive(args: argparse.Namespace) -> int:
    print(json.dumps(build_adaptive_mirror(_read(args.input)).to_dict(), ensure_ascii=False, indent=2))
    return 0


def _cmd_categories_causal(args: argparse.Namespace) -> int:
    raw = _read(args.input)
    effects = build_category_effects(_brm(extract_categories(raw)))
    print(json.dumps([e.to_dict() for e in effects], ensure_ascii=False, indent=2))
    return _emit(any(e.status == "causal" for e in effects) or not effects)


def _cmd_maps_delta(args: argparse.Namespace) -> int:
    raw = _read(args.input)
    delta = build_reality_map_delta(_brm(extract_categories(raw)), _bmd(raw))
    print(json.dumps(delta.to_dict(), ensure_ascii=False, indent=2))
    return _emit(not delta.low_map_utility)


def _cmd_theories_contribution(args: argparse.Namespace) -> int:
    raw = _read(args.input)
    contribs = track_theory_contribution(raw, list(_rt(raw, _bmd(raw), _brm(extract_categories(raw)))))
    print(json.dumps([c.to_dict() for c in contribs], ensure_ascii=False, indent=2))
    return 0


def _cmd_action(args: argparse.Namespace) -> int:
    run = run_v6(_read(args.input))
    print(json.dumps(run.action.to_dict(), ensure_ascii=False, indent=2))
    return _emit(not run.action.pipeline_overbuilt)


def _cmd_ablate(args: argparse.Namespace) -> int:
    raw = _read(args.input)
    report = run_ablation_v6(raw)
    if args.evidence:
        run_and_save_v6(raw, Path(args.evidence))
    print(json.dumps(report, ensure_ascii=False, indent=2))
    decorative = [k for k, v in report.items() if v["keep_modify_remove"] == "remove"]
    print(f"\nDECORATIVE (remove-кандидати): {decorative or 'немає'}", file=sys.stderr)
    return 0


def _cmd_human_eval(args: argparse.Namespace) -> int:
    packet = json.loads((Path(args.out) / "human_eval_packet.json").read_text(encoding="utf-8"))
    print(json.dumps({
        "human_eval_status": packet["human_eval_status"],
        "baseline_source": packet["baseline_source"],
        "pairwise_questions": len(packet["pairwise_questions"]),
        "human_labels": packet["human_labels"],
        "note": "людські оцінки НЕ заповнені автоматично — статус pending",
    }, ensure_ascii=False, indent=2))
    return 0


def _cmd_theories(args: argparse.Namespace) -> int:
    raw = _read(args.input)
    mirror = build_mirror_deterministic(raw)
    maps = build_reality_maps(extract_categories(raw))
    readouts = run_theories(raw, mirror, maps)
    print(json.dumps({k: r.to_dict() for k, r in readouts.items()}, ensure_ascii=False, indent=2))
    return 0


def _cmd_neuro(args: argparse.Namespace) -> int:
    raw = _read(args.input)
    if args.evidence:
        run, manifest = run_and_save_v4(raw, Path(args.evidence))
        print(json.dumps(manifest, ensure_ascii=False, indent=2))
    else:
        run = run_v4(raw)
        print(render_neuro_md(run))
    print(f"\nВАЛІДАЦІЯ: {'PASS' if run.passed else 'FAIL'}", file=sys.stderr)
    return _emit(run.passed)


def _cmd_eiic(args: argparse.Namespace) -> int:
    raw = _read(args.input)
    if args.evidence:
        manifest = run_and_save_eiic(raw, Path(args.evidence))
        print(json.dumps(manifest, ensure_ascii=False, indent=2))
        passed = bool(manifest["validations_passed"])
    else:
        core = run_eiic(raw)
        print(render_eiic_md(core))
        passed = core.passed
    return _emit(passed)


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

    p_th = sub.add_parser("theories", help="текст → 12 нейрокогнітивних лінз (проксі)")
    p_th.add_argument("input")
    p_th.set_defaults(func=_cmd_theories)

    p_neuro = sub.add_parser("neuro", help="нейрокогнітивний артефакт v0.4 (10 секцій)")
    p_neuro.add_argument("input")
    p_neuro.add_argument("--evidence", help="директорія для Evidence Bundle")
    p_neuro.set_defaults(func=_cmd_neuro)

    p_eiic = sub.add_parser("eiic", help="екстрапольований інтенційний ядро-вектор")
    p_eiic.add_argument("input")
    p_eiic.add_argument("--evidence", help="директорія для Evidence Bundle")
    p_eiic.set_defaults(func=_cmd_eiic)

    p_verdict = sub.add_parser("verdict", help="читає Evidence Bundle і виносить вердикт по гейтах")
    p_verdict.add_argument("out", help="директорія Evidence Bundle")
    p_verdict.set_defaults(func=_cmd_verdict)

    p_bench = sub.add_parser("benchmark", help="100-input proxy benchmark + ablation (v6+v5)")
    p_bench.set_defaults(func=_cmd_benchmark)

    p_cx = sub.add_parser("complexity", help="оцінка складності → режим виходу")
    p_cx.add_argument("input")
    p_cx.set_defaults(func=_cmd_complexity)

    p_ma = sub.add_parser("mirror-adaptive", help="адаптивне дзеркало (без padding)")
    p_ma.add_argument("input")
    p_ma.set_defaults(func=_cmd_mirror_adaptive)

    p_cc = sub.add_parser("categories-causal", help="категорії як причинні ефекти")
    p_cc.add_argument("input")
    p_cc.set_defaults(func=_cmd_categories_causal)

    p_md = sub.add_parser("maps-delta", help="дельта карт реальності")
    p_md.add_argument("input")
    p_md.set_defaults(func=_cmd_maps_delta)

    p_tc = sub.add_parser("theories-contribution", help="внесок кожної теорії (0–5)")
    p_tc.add_argument("input")
    p_tc.set_defaults(func=_cmd_theories_contribution)

    p_act = sub.add_parser("action", help="вибір однієї дії з причинних входів")
    p_act.add_argument("input")
    p_act.set_defaults(func=_cmd_action)

    p_abl = sub.add_parser("ablate", help="ablation v2 (keep/modify/remove)")
    p_abl.add_argument("input")
    p_abl.add_argument("--evidence", help="директорія для Evidence Bundle")
    p_abl.set_defaults(func=_cmd_ablate)

    p_he = sub.add_parser("human-eval", help="звіт HumanEvalPacket з bundle (без фейк-оцінок)")
    p_he.add_argument("out", help="директорія Evidence Bundle")
    p_he.set_defaults(func=_cmd_human_eval)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    func = args.func
    assert callable(func)
    return int(func(args))


if __name__ == "__main__":
    raise SystemExit(main())
