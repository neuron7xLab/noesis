"""Уніфікований CLI `noesis`: mirror · introspect · reverse · artifact · pipeline · validate."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from noesis import __version__
from noesis.adaptive import build_adaptive_mirror
from noesis.benchmark import run_ablation, run_benchmark
from noesis.benchmark_v6 import run_ablation_v6, run_benchmark_v6
from noesis.causal import build_category_effects, build_reality_map_delta, track_theory_contribution
from noesis.complexity import estimate_complexity
from noesis.eiic import render_eiic_md, run_and_save_eiic, run_eiic
from noesis.ontology import build_reality_maps as _brm
from noesis.theories import run_theories as _rt
from noesis.generators import build_mirror_deterministic as _bmd
from noesis.pipeline_v6 import run_and_save_v6, run_v6
from noesis.pipeline_v7 import run_and_save_v7, run_v7
from noesis.pipeline_v8 import run_and_save_v8, run_v8
from noesis.benchmark_v8 import node_scaling_curve
from noesis.vertical_loop import build_vertical_loop
from noesis.effective_dim import effective_dimensionality
from noesis.gate_functional import GateFunctional
from noesis.generators import (
    build_artifact_deterministic,
    build_introspection_deterministic,
    build_mirror_deterministic,
    build_mirror_llm,
)
from noesis.neuro import render_neuro_md, run_and_save_v4, run_v4
from noesis.ontology import build_reality_maps, extract_categories
from noesis.synthesis import build_synthesis
from noesis.theories import run_theories
from noesis.verdict import read_verdict, render_verdict_md
from noesis.validators import (
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


def _cmd_graph(args: argparse.Namespace) -> int:
    raw = _read(args.input)
    if args.evidence:
        _, manifest = run_and_save_v7(raw, Path(args.evidence))
        print(json.dumps(manifest, ensure_ascii=False, indent=2))
        return _emit(manifest["overall_status"] == "PASS")
    run = run_v7(raw)
    print(json.dumps(run.graph.to_dict(), ensure_ascii=False, indent=2))
    return 0


def _cmd_dimensionality(args: argparse.Namespace) -> int:
    print(json.dumps(run_v7(_read(args.input)).dimensionality.to_dict(), ensure_ascii=False, indent=2))
    return 0


def _cmd_gate(args: argparse.Namespace) -> int:
    run = run_v7(_read(args.input))
    print(json.dumps(run.gate.to_dict(), ensure_ascii=False, indent=2))
    return _emit(run.gate.decision in ("pass", "compress"))


def _cmd_broadcast(args: argparse.Namespace) -> int:
    print(json.dumps(run_v7(_read(args.input)).broadcast.to_dict(), ensure_ascii=False, indent=2))
    return 0


def _cmd_entropy(args: argparse.Namespace) -> int:
    print(json.dumps(run_v7(_read(args.input)).entropy.to_dict(), ensure_ascii=False, indent=2))
    return 0


def _cmd_precision(args: argparse.Namespace) -> int:
    print(json.dumps(run_v7(_read(args.input)).precision.to_dict(), ensure_ascii=False, indent=2))
    return 0


def _cmd_pipeline_v7(args: argparse.Namespace) -> int:
    raw = _read(args.input)
    if args.evidence:
        run, manifest = run_and_save_v7(raw, Path(args.evidence))
        print(json.dumps(manifest, ensure_ascii=False, indent=2))
    else:
        run = run_v7(raw)
        print(json.dumps({
            "dimensionality": run.dimensionality.to_dict(),
            "iev_gate": run.gate.to_dict(),
            "human_bottleneck": run.entropy.human_bottleneck_score,
            "gates": run.validation.to_dict(),
        }, ensure_ascii=False, indent=2))
    print(f"\nВАЛІДАЦІЯ: {'PASS' if run.passed else 'FAIL'}", file=sys.stderr)
    return _emit(run.passed)


def _cmd_v8_part(args: argparse.Namespace) -> int:
    run = run_v8(_read(args.input))
    parts: dict[str, dict[str, object]] = {
        "intent-vector": run.intent.to_dict(), "entropy-budget": run.budget.to_dict(),
        "node-plan": run.plan.to_dict(), "latency": run.latency.to_dict(),
        "iev-bandwidth": run.iev.to_dict(), "precision": run.precision.to_dict(),
        "collapse": run.collapse.to_dict(), "cluster-quality": run.quality.to_dict(),
        "bottleneck-plan": run.bottleneck.to_dict(),
    }
    print(json.dumps(parts[args.part], ensure_ascii=False, indent=2))
    return 0


def _cmd_pipeline_v8(args: argparse.Namespace) -> int:
    raw = _read(args.input)
    if args.evidence:
        run, manifest = run_and_save_v8(raw, Path(args.evidence))
        print(json.dumps(manifest, ensure_ascii=False, indent=2))
    else:
        run = run_v8(raw)
        print(json.dumps({"cluster_quality": run.quality.to_dict(), "bottleneck": run.bottleneck.to_dict(),
                          "collapse": run.collapse.to_dict(), "gates": run.validation.to_dict()},
                         ensure_ascii=False, indent=2))
    print(f"\nВАЛІДАЦІЯ: {'PASS' if run.passed else 'FAIL'}", file=sys.stderr)
    return _emit(run.passed)


def _cmd_vertical_loop(args: argparse.Namespace) -> int:
    print(json.dumps(build_vertical_loop(_read(args.input)).to_dict(), ensure_ascii=False, indent=2))
    return 0


def _accepted_texts(raw: str) -> list[str]:
    run = run_v7(raw)
    texts = [e.category for e in run.v6.category_effects if e.status == "causal"]
    texts += [c.theory_name for c in run.v6.contributions if c.contribution_score > 0]
    texts += [run.v6.action.category_influence, run.v6.eiic.latent_intent.value]
    return [t for t in texts if t.strip()]


def _cmd_effdim(args: argparse.Namespace) -> int:
    raw = _read(args.input)
    run = run_v7(raw)
    texts = _accepted_texts(raw)
    deff = effective_dimensionality(texts)
    print(json.dumps({
        "effective_dimensionality_D_eff": deff,
        "heuristic_useful_axes_count": run.dimensionality.useful_dimensionality_gain,
        "accepted_hypotheses": len(texts),
        "note": "D_eff = tr(Σ)²/tr(Σ²) (participation ratio); часто < евристичного count → "
                "прийняті осі менш ортогональні, ніж їх кількість",
    }, ensure_ascii=False, indent=2))
    return 0


def _cmd_gate_functional(args: argparse.Namespace) -> int:
    run = run_v7(_read(args.input))
    g = run.gate
    func = GateFunctional()
    relevance, verifier = g.intent_match, g.evidence_strength
    progress = min(1.0, run.dimensionality.useful_dimensionality_gain / 5)
    cost = round(g.noise_risk * 0.5 + (1 - g.claim_safety) * 0.5, 3)
    print(json.dumps({
        "canonical": "w(h) = αR + βV + γP − δK ≥ θ",
        "inputs": {"R": relevance, "V": verifier, "P": progress, "K": cost},
        **func.explain(relevance, verifier, progress, cost),
    }, ensure_ascii=False, indent=2))
    return 0


def _cmd_node_scaling(args: argparse.Namespace) -> int:
    print(json.dumps(node_scaling_curve(_read(args.input)), ensure_ascii=False, indent=2))
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


def _cmd_bibliography(args: argparse.Namespace) -> int:
    from noesis import bibliography as bib

    lib = bib.load_library()
    scan = bib.scan_repo(lib)
    cmd = args.bib_command

    if cmd == "scan":
        print(json.dumps(
            {"files_scanned": scan.files_scanned,
             "present_terms": sorted(scan.present_terms),
             "theory_heavy_docs": scan.theory_heavy_docs},
            ensure_ascii=False, indent=2))
        return 0
    if cmd == "ledger":
        print(json.dumps([c.__dict__ for c in lib.claims], ensure_ascii=False, indent=2))
        return 0
    if cmd == "missing":
        print(json.dumps(bib.missing(lib, scan), ensure_ascii=False, indent=2))
        return 0
    if cmd == "graph":
        if args.write:
            bib.write_generated(lib, scan)
        print(json.dumps(bib.build_source_graph(lib), ensure_ascii=False, indent=2))
        return 0
    if cmd == "export-bibtex":
        print(bib.export_bibtex(lib))
        return 0
    if cmd == "validate":
        results = bib.validate(lib, scan)
        ok = bib.gates_pass(results)
        print(json.dumps([r.to_dict() for r in results], ensure_ascii=False, indent=2))
        return 0 if ok else 1
    # verdict
    v = bib.verdict(lib, scan)
    if args.write:
        bib.write_generated(lib, scan)
    print(json.dumps(v, ensure_ascii=False, indent=2))
    return 0 if v["overall_status"] == "PASS" else 1


def _cmd_physics_boundary(args: argparse.Namespace) -> int:
    from noesis.contracts import physics_boundary_cli

    return physics_boundary_cli.run(["validate"])


def _cmd_recovery(args: argparse.Namespace) -> int:
    from noesis.runtime.recovery_supervisor import self_check

    result = self_check()
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["healthy"] else 1


def _cmd_calibrate(args: argparse.Namespace) -> int:
    from noesis.calibration import calibration_report

    print(json.dumps(calibration_report(), ensure_ascii=False, indent=2))
    return 0


def _cmd_discriminate(args: argparse.Namespace) -> int:
    from noesis.evaluation.discrimination_study import study_report

    report = study_report()
    print(json.dumps(report, ensure_ascii=False, indent=2))
    # Fail-closed gate on the system's own validity: weak discrimination is a red flag.
    return 0 if report["overall_auc"] >= 0.7 else 1


def _cmd_validity(args: argparse.Namespace) -> int:
    from noesis.evaluation.calibration_loop import validity_report

    report = validity_report()
    print(json.dumps(report, ensure_ascii=False, indent=2))
    # Closed-loop self-proof: AUC + good-pass + hard-reject + θ-in-plateau, fail-closed.
    return 0 if report["verdict"] == "PASS" else 1


def _cmd_feedback(args: argparse.Namespace) -> int:
    from noesis.feedback import ingest

    report_path = Path("data") / "feedback_calibration.json"
    if args.fb_command == "status":
        if report_path.exists():
            report = json.loads(report_path.read_text(encoding="utf-8"))
        else:
            report = {"status": "INSUFFICIENT_DATA", "reason": "no calibration report yet"}
        print(json.dumps(report, ensure_ascii=False, indent=2))
        return 0 if report.get("status") == "CALIBRATED" else 1

    payload = json.loads(_read(args.input))
    report = ingest(payload)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report["status"] == "CALIBRATED" else 1


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="noesis",
        description="Noesis — externalized metacognition with an IEV precision gate.",
    )
    parser.add_argument("--version", action="version", version=f"noesis {__version__}")
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

    # v0.7 — distributed cognitive graph
    for cmd, fn, helptext in (
        ("graph", _cmd_graph, "когнітивний граф (+ --evidence для bundle v0.7)"),
        ("dimensionality", _cmd_dimensionality, "оцінка корисної розмірності проти шуму"),
        ("gate", _cmd_gate, "IEV precision gate: pass/fail/compress/reroute/human_review"),
        ("broadcast", _cmd_broadcast, "broadcast/reentry (GNWT-аналогія)"),
        ("entropy", _cmd_entropy, "ledger делегованої ентропії"),
        ("precision", _cmd_precision, "semi-automated auditor/verifier precision"),
        ("pipeline-v7", _cmd_pipeline_v7, "повна труба v0.7 + 13-файл Evidence Bundle"),
    ):
        p = sub.add_parser(cmd, help=helptext)
        p.add_argument("input")
        if cmd in ("graph", "pipeline-v7"):
            p.add_argument("--evidence", help="директорія для Evidence Bundle")
        p.set_defaults(func=fn)

    # v0.8 — latency-aware IEV optimization
    for part in ("intent-vector", "entropy-budget", "node-plan", "latency", "iev-bandwidth",
                 "precision-v8", "collapse", "cluster-quality", "bottleneck-plan"):
        p = sub.add_parser(part, help=f"v0.8 {part}")
        p.add_argument("input")
        p.set_defaults(func=_cmd_v8_part, part=part.replace("precision-v8", "precision"))

    p_p8 = sub.add_parser("pipeline-v8", help="повна труба v0.8 + 15-файл Evidence Bundle")
    p_p8.add_argument("input")
    p_p8.add_argument("--evidence", help="директорія для Evidence Bundle")
    p_p8.set_defaults(func=_cmd_pipeline_v8)

    p_vl = sub.add_parser("vertical-loop", help="cyclic reverse vertical cognitive loop")
    p_vl.add_argument("input")
    p_vl.set_defaults(func=_cmd_vertical_loop)

    p_ns = sub.add_parser("node-scaling", help="крива cluster_quality vs кількість вузлів")
    p_ns.add_argument("input")
    p_ns.set_defaults(func=_cmd_node_scaling)

    p_ed = sub.add_parser("effdim", help="D_eff = tr(Σ)²/tr(Σ²) прийнятих гіпотез (participation ratio)")
    p_ed.add_argument("input")
    p_ed.set_defaults(func=_cmd_effdim)

    p_gf = sub.add_parser("gate-functional", help="канонічний gating-функціонал w=αR+βV+γP−δK")
    p_gf.add_argument("input")
    p_gf.set_defaults(func=_cmd_gate_functional)

    # bibliographic evidence graph
    p_bib = sub.add_parser("bibliography", help="claim-to-source evidence graph")
    bsub = p_bib.add_subparsers(dest="bib_command", required=True)
    for name, helptext in (
        ("scan", "сканувати репо на theory-терміни"),
        ("ledger", "claim → status → source → module → gate"),
        ("validate", "10 bibliography-гейтів (non-zero на фейлі)"),
        ("missing", "claims без джерел / спекулятивні / background"),
        ("export-bibtex", "BibTeX зі sources"),
    ):
        bp = bsub.add_parser(name, help=helptext)
        bp.set_defaults(func=_cmd_bibliography)
    for name, helptext in (
        ("graph", "source → claim → module → gate граф"),
        ("verdict", "повний bibliographic вердикт (non-zero на фейлі)"),
    ):
        bp = bsub.add_parser(name, help=helptext)
        bp.add_argument("--write", action="store_true", help="перегенерувати docs/data артефакти")
        bp.set_defaults(func=_cmd_bibliography)

    # physics-boundary contract gate (Role 2)
    p_pb = sub.add_parser("physics-boundary", help="physics-boundary contract gate")
    pbsub = p_pb.add_subparsers(dest="pb_command", required=True)
    pbsub.add_parser("validate", help="enforce the physics-boundary contract (non-zero on fail)")
    p_pb.set_defaults(func=_cmd_physics_boundary)

    # calibration registry — every tunable threshold + measured sensitivity
    p_cal = sub.add_parser("calibrate", help="калібрувальна карта: усі пороги + sensitivity")
    p_cal.set_defaults(func=_cmd_calibrate)

    # discriminant validity — does the gate separate good vs degraded artifacts?
    p_disc = sub.add_parser("discriminate", help="дискримінантна валідність гейта (AUC проти деградацій)")
    p_disc.set_defaults(func=_cmd_discriminate)

    # closed-loop validity gate — calibrated θ + continuous self-proof (fail-closed)
    p_validity = sub.add_parser("validity", help="замкнений гейт валідності: AUC + калібрування θ")
    p_validity.set_defaults(func=_cmd_validity)

    # recovery supervisor — reversive recovery loop self-check (Layer -1)
    p_rec = sub.add_parser("recovery", help="recovery supervisor (reversive recovery loop)")
    recsub = p_rec.add_subparsers(dest="rec_command", required=True)
    recsub.add_parser("self-check", help="run the reversive recovery reflex self-test")
    p_rec.set_defaults(func=_cmd_recovery)

    # feedback harness — calibrate proxy against human-labeled real outcomes
    p_fb = sub.add_parser("feedback", help="calibrate proxy metrics against real outcomes")
    fbsub = p_fb.add_subparsers(dest="fb_command", required=True)
    p_fb_ing = fbsub.add_parser("ingest", help="ingest labeled pairs JSON and calibrate")
    p_fb_ing.add_argument("input")
    fbsub.add_parser("status", help="show the last calibration report")
    p_fb.set_defaults(func=_cmd_feedback)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    func = args.func
    assert callable(func)
    # Fail-closed: a bad path or corrupt JSON file is a clean error + exit 1, not
    # a raw traceback dumped at the user (знайдено хаос-стрес-тестом).
    try:
        return int(func(args))
    except FileNotFoundError as exc:
        print(f"error: file not found: {exc.filename}", file=sys.stderr)
        return 1
    except json.JSONDecodeError as exc:
        print(f"error: invalid JSON: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
