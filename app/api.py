"""FastAPI-додаток: /health, /finalize, /intent."""

from __future__ import annotations

from typing import Any

from fastapi import FastAPI

from app.models import (
    ArtifactRequest,
    FinalizeRequest,
    FinalizeResponse,
    IntentRequest,
    IntentResponse,
    RawRequest,
    ReverseRequest,
)
from app.services import decode_intent, finalize
from noesis.adaptive import build_adaptive_mirror
from noesis.benchmark import run_ablation_v6
from noesis.causal import build_category_effects, build_reality_map_delta, track_theory_contribution
from noesis.complexity import estimate_complexity
from noesis.eiic import run_eiic
from noesis.engine import run_v3
from noesis.neuro import run_v4
from noesis.pipeline_core import run_v6, run_v7, run_v8
from noesis.effective_dim import effective_dimensionality
from noesis.gate_functional import GateFunctional
from noesis.theories import run_theories
from noesis.generators import (
    build_artifact_deterministic,
    build_introspection_deterministic,
    build_mirror_deterministic,
)
from noesis.ontology import build_reality_maps, extract_categories
from noesis.synthesis import build_synthesis
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

app = FastAPI(
    title="Cognitive Mirror Methods",
    version="0.1.0",
    description="Практичні brain-inspired методи мислення з LLM-дзеркалом.",
)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/finalize", response_model=FinalizeResponse)
def finalize_endpoint(req: FinalizeRequest) -> FinalizeResponse:
    """Перевіряє Finalizer-100 артефакт на контракт 90–110 слів + якорі."""
    return finalize(req.text)


@app.post("/intent", response_model=IntentResponse)
def intent_endpoint(req: IntentRequest) -> IntentResponse:
    """Розкладає сире повідомлення на 5 шарів наміру."""
    return decode_intent(req.message)


@app.post("/mirror")
def mirror_endpoint(req: RawRequest) -> dict[str, Any]:
    mirror = build_mirror_deterministic(req.text)
    return {"mirror": mirror.to_dict(), "validation": validate_mirror(mirror, req.text).to_dict()}


@app.post("/introspect")
def introspect_endpoint(req: RawRequest) -> dict[str, Any]:
    intro = build_introspection_deterministic(req.text)
    return {"introspection": intro.to_dict(), "validation": validate_introspection(intro, req.text).to_dict()}


@app.post("/reverse")
def reverse_endpoint(req: ReverseRequest) -> dict[str, Any]:
    trace = plan_backwards(
        target_state=req.target_state,
        current_facts=req.current_facts,
        required_conditions=req.required_conditions,
    )
    return {"reverse": trace.to_dict(), "validation": validate_reverse(trace).to_dict()}


@app.post("/artifact")
def artifact_endpoint(req: RawRequest) -> dict[str, Any]:
    artifact = build_artifact_deterministic(req.text)
    return {"artifact": artifact, "validation": validate_artifact(artifact, req.text).to_dict()}


@app.post("/ontology")
def ontology_endpoint(req: RawRequest) -> dict[str, Any]:
    active = extract_categories(req.text)
    return {
        "categories": [c.to_dict() for c in active],
        "validation": validate_categories(active).to_dict(),
    }


@app.post("/maps")
def maps_endpoint(req: RawRequest) -> dict[str, Any]:
    maps = build_reality_maps(extract_categories(req.text))
    return {"reality_maps": maps.to_dict(), "validation": validate_maps(maps).to_dict()}


@app.post("/synthesize")
def synthesize_endpoint(req: RawRequest) -> dict[str, Any]:
    maps = build_reality_maps(extract_categories(req.text))
    synth = build_synthesis(maps)
    return {"synthesis_axis": synth.to_dict(), "validation": validate_synthesis(synth).to_dict()}


@app.post("/pipeline")
def pipeline_endpoint(req: RawRequest) -> dict[str, Any]:
    run = run_v3(req.text)
    return {
        "version": "0.3",
        "dominant_axis": run.maps.dominant_axis,
        "controlling_category": run.controlling_category,
        "reality_maps": run.maps.to_dict(),
        "synthesis_axis": run.synthesis.to_dict(),
        "reverse_plan": run.reverse.to_dict(),
        "artifact": run.artifact,
        "next_action": run.next_action,
        "passed": run.passed,
        "validations": [v.to_dict() for v in run.validations],
    }


@app.post("/validate")
def validate_endpoint(req: ArtifactRequest) -> dict[str, Any]:
    return validate_artifact(req.artifact).to_dict()


@app.post("/neuro")
def neuro_endpoint(req: RawRequest) -> dict[str, Any]:
    run = run_v4(req.text)
    return {
        "version": "0.4",
        "sections": run.sections(),
        "theory_readout": {k: r.to_dict() for k, r in run.readouts.items()},
        "passed": run.passed,
        "validations": [v.to_dict() for v in run.validations],
    }


@app.post("/eiic")
def eiic_endpoint(req: RawRequest) -> dict[str, Any]:
    return run_eiic(req.text).to_dict()


@app.post("/complexity")
def complexity_endpoint(req: RawRequest) -> dict[str, Any]:
    return estimate_complexity(req.text).to_dict()


@app.post("/mirror/adaptive")
def mirror_adaptive_endpoint(req: RawRequest) -> dict[str, Any]:
    return build_adaptive_mirror(req.text).to_dict()


@app.post("/categories/causal")
def categories_causal_endpoint(req: RawRequest) -> dict[str, Any]:
    effects = build_category_effects(build_reality_maps(extract_categories(req.text)))
    return {"effects": [e.to_dict() for e in effects]}


@app.post("/maps/delta")
def maps_delta_endpoint(req: RawRequest) -> dict[str, Any]:
    delta = build_reality_map_delta(build_reality_maps(extract_categories(req.text)),
                                    build_mirror_deterministic(req.text))
    return delta.to_dict()


@app.post("/theories/contribution")
def theories_contribution_endpoint(req: RawRequest) -> dict[str, Any]:
    contribs = track_theory_contribution(
        req.text, list(run_theories(req.text, build_mirror_deterministic(req.text),
                                    build_reality_maps(extract_categories(req.text)))))
    return {"contributions": [c.to_dict() for c in contribs]}


@app.post("/action")
def action_endpoint(req: RawRequest) -> dict[str, Any]:
    return run_v6(req.text).action.to_dict()


@app.post("/pipeline/v6")
def pipeline_v6_endpoint(req: RawRequest) -> dict[str, Any]:
    run = run_v6(req.text)
    return {
        "version": "0.6",
        "selected_action": run.action.selected_action,
        "compression_status": run.mirror.compression_status,
        "category_layer": "no_effect" if run.flags["category_layer_no_effect"] else "causal",
        "theory_status": run.theory_status,
        "flags": run.flags,
        "passed": run.passed,
        "validation": run.validation.to_dict(),
    }


@app.post("/ablation/v6")
def ablation_v6_endpoint(req: RawRequest) -> dict[str, Any]:
    return run_ablation_v6(req.text)


@app.post("/graph")
def graph_endpoint(req: RawRequest) -> dict[str, Any]:
    return run_v7(req.text).graph.to_dict()


@app.post("/node-profile")
def node_profile_endpoint(req: RawRequest) -> dict[str, Any]:
    return {"profiles": [p.to_dict() for p in run_v7(req.text).node_profiles]}


@app.post("/dimensionality")
def dimensionality_endpoint(req: RawRequest) -> dict[str, Any]:
    return run_v7(req.text).dimensionality.to_dict()


@app.post("/gate")
def gate_endpoint(req: RawRequest) -> dict[str, Any]:
    return run_v7(req.text).gate.to_dict()


@app.post("/broadcast")
def broadcast_endpoint(req: RawRequest) -> dict[str, Any]:
    return run_v7(req.text).broadcast.to_dict()


@app.post("/entropy")
def entropy_endpoint(req: RawRequest) -> dict[str, Any]:
    return run_v7(req.text).entropy.to_dict()


@app.post("/precision")
def precision_endpoint(req: RawRequest) -> dict[str, Any]:
    return run_v7(req.text).precision.to_dict()


@app.post("/pipeline/v7")
def pipeline_v7_endpoint(req: RawRequest) -> dict[str, Any]:
    run = run_v7(req.text)
    return {
        "version": "0.7",
        "dimensionality": run.dimensionality.to_dict(),
        "iev_gate": run.gate.to_dict(),
        "human_bottleneck_score": run.entropy.human_bottleneck_score,
        "passed": run.passed,
        "validation": run.validation.to_dict(),
    }


@app.post("/intent-vector")
def intent_vector_endpoint(req: RawRequest) -> dict[str, Any]:
    return run_v8(req.text).intent.to_dict()


@app.post("/entropy-budget")
def entropy_budget_endpoint(req: RawRequest) -> dict[str, Any]:
    return run_v8(req.text).budget.to_dict()


@app.post("/node-plan")
def node_plan_endpoint(req: RawRequest) -> dict[str, Any]:
    return run_v8(req.text).plan.to_dict()


@app.post("/latency")
def latency_endpoint(req: RawRequest) -> dict[str, Any]:
    return run_v8(req.text).latency.to_dict()


@app.post("/iev-bandwidth")
def iev_bandwidth_endpoint(req: RawRequest) -> dict[str, Any]:
    return run_v8(req.text).iev.to_dict()


@app.post("/collapse")
def collapse_endpoint(req: RawRequest) -> dict[str, Any]:
    return run_v8(req.text).collapse.to_dict()


@app.post("/cluster-quality")
def cluster_quality_endpoint(req: RawRequest) -> dict[str, Any]:
    return run_v8(req.text).quality.to_dict()


@app.post("/bottleneck-plan")
def bottleneck_plan_endpoint(req: RawRequest) -> dict[str, Any]:
    return run_v8(req.text).bottleneck.to_dict()


@app.post("/effective-dim")
def effective_dim_endpoint(req: RawRequest) -> dict[str, Any]:
    run = run_v7(req.text)
    texts = [e.category for e in run.v6.category_effects if e.status == "causal"]
    texts += [c.theory_name for c in run.v6.contributions if c.contribution_score > 0]
    texts += [run.v6.action.category_influence, run.v6.eiic.latent_intent.value]
    texts = [t for t in texts if t.strip()]
    return {
        "effective_dimensionality_D_eff": effective_dimensionality(texts),
        "heuristic_useful_axes_count": run.dimensionality.useful_dimensionality_gain,
        "accepted_hypotheses": len(texts),
    }


@app.post("/gate-functional")
def gate_functional_endpoint(req: RawRequest) -> dict[str, Any]:
    run = run_v7(req.text)
    g = run.gate
    func = GateFunctional()
    progress = min(1.0, run.dimensionality.useful_dimensionality_gain / 5)
    cost = round(g.noise_risk * 0.5 + (1 - g.claim_safety) * 0.5, 3)
    return {"canonical": "w(h) = αR + βV + γP − δK ≥ θ",
            **func.explain(g.intent_match, g.evidence_strength, progress, cost)}


@app.post("/pipeline/v8")
def pipeline_v8_endpoint(req: RawRequest) -> dict[str, Any]:
    run = run_v8(req.text)
    return {
        "version": "0.8",
        "cluster_quality": run.quality.to_dict(),
        "bottleneck": run.bottleneck.to_dict(),
        "collapse": run.collapse.to_dict(),
        "passed": run.passed,
        "validation": run.validation.to_dict(),
    }


# --- bibliographic evidence graph -------------------------------------------
def _bib_load() -> tuple[Any, Any]:
    from noesis import bibliography as bib

    lib = bib.load_library()
    return lib, bib.scan_repo(lib)


@app.get("/bibliography")
def bibliography_root() -> dict[str, Any]:
    from noesis import bibliography as bib

    lib, scan = _bib_load()
    return {"sources": len(lib.sources), "claims": len(lib.claims),
            "forbidden": len(lib.forbidden), "audit": bib.audit(lib, scan)}


@app.post("/bibliography/scan")
def bibliography_scan() -> dict[str, Any]:
    _lib, scan = _bib_load()
    return {"files_scanned": scan.files_scanned,
            "present_terms": sorted(scan.present_terms),
            "theory_heavy_docs": scan.theory_heavy_docs}


@app.post("/bibliography/validate")
def bibliography_validate() -> dict[str, Any]:
    from noesis import bibliography as bib

    lib, scan = _bib_load()
    results = bib.validate(lib, scan)
    return {"passed": bib.gates_pass(results), "gates": [r.to_dict() for r in results]}


@app.post("/bibliography/missing")
def bibliography_missing() -> dict[str, Any]:
    from noesis import bibliography as bib

    lib, scan = _bib_load()
    return bib.missing(lib, scan)


@app.get("/bibliography/graph")
def bibliography_graph() -> dict[str, Any]:
    from noesis import bibliography as bib

    lib, _scan = _bib_load()
    return bib.build_source_graph(lib)


@app.get("/bibliography/verdict")
def bibliography_verdict() -> dict[str, Any]:
    from noesis import bibliography as bib

    lib, scan = _bib_load()
    return bib.verdict(lib, scan)


@app.post("/metrics")
@app.get("/metrics")
def metrics_endpoint() -> dict[str, Any]:
    from noesis.evaluation.metrics_inference import build_metrics_report

    return build_metrics_report()
