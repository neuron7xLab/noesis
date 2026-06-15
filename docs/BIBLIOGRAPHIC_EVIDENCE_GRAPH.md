<!-- GENERATED from data/*.json by noesis.bibliography — do not edit by hand. -->

# Bibliographic Evidence Graph

How claims map to sources and statuses. Canonical data lives in `data/*.json`;
`data/source_graph.json` holds the machine-readable graph.

## Status distribution
- files scanned: **94**, claims: **19**, sources: **35**, present theory terms: **16**
- claims by status: `{'S0': 1, 'S1': 2, 'S3': 1, 'S4': 7, 'S5': 7, 'S6': 1}`
- proxy claims: 7, speculative (S6): 1, forbidden guarded: 12
- bibliography gate status: **PASS**

## Claim → sources → module → gate

### `low_bandwidth_controller` (S4, analogy_claim)
> The human acts as a low-bandwidth, high-coherence controller over a higher-entropy candidate space.
- sources: `cowan_2001_working_memory`, `miller_1956_magical_seven`, `miller_cohen_2001_pfc`, `baddeley_hitch_1974_working_memory`
- repo: `docs/HUMAN_BOTTLENECK.md`, `docs/IEV_BANDWIDTH.md`, `noesis/iev_bandwidth.py`
- module: pipeline_v8, iev_bandwidth · gate: `gate5_iev_bandwidth_safety`
- failure mode: Presenting the bandwidth abstraction as a biological measurement.

### `intent_vector` (S4, analogy_claim)
> The Intent Vector is a compressed control packet that holds the user's intent invariant across passes.
- sources: `miller_cohen_2001_pfc`, `cowan_2001_working_memory`, `nelson_narens_1990_metamemory`, `badre_2008_hierarchical_control`
- repo: `noesis/intent_vector.py`, `schemas/intent_vector.schema.json`, `docs/IEV_PRECISION_GATE.md`
- module: pipeline_v7, pipeline_v8 · gate: `gate1_intent_coherence`
- failure mode: Claiming the intent vector is a model of prefrontal goal representation.

### `iev_precision_gate` (S5, proxy_claim)
> The IEV gate w = αR + βV + γP − δK ≥ θ admits a candidate into the next state only if it preserves intent and raises verified precision.
- sources: `lightman_2023_process_supervision`, `uesato_2022_process_outcome`, `zheng_2023_llm_as_judge`, `gu_2024_judge_survey`, `friston_2010_free_energy`
- repo: `docs/IEV_PRECISION_GATE.md`, `noesis/precision_gate.py`, `noesis/gate_functional.py`, `schemas/precision_gate.schema.json`
- module: pipeline_v7, pipeline_v8 · gate: `gate6_iev_precision_gate`
- failure mode: Presenting the proxy functional as a learned verifier or as variational free energy.

### `iev_bandwidth_proxy` (S5, proxy_claim)
> IEV bandwidth is an operational proxy for human validation throughput.
- sources: `cowan_2001_working_memory`, `risko_gilbert_2016_cognitive_offloading`, `lightman_2023_process_supervision`
- repo: `docs/IEV_BANDWIDTH.md`, `noesis/iev_bandwidth.py`, `schemas/iev_bandwidth_report.schema.json`
- module: pipeline_v8 · gate: `gate5_iev_bandwidth_safety`
- failure mode: Presenting the proxy as measured PFC bandwidth.

### `delegated_computational_entropy` (S5, proxy_claim)
> Delegated Computational Entropy is candidate-state expansion offloaded to test-time compute, ledgered and then collapsed by the human gate.
- sources: `risko_gilbert_2016_cognitive_offloading`, `hutchins_1995_cognition_in_the_wild`, `wang_2023_self_consistency`, `clark_chalmers_1998_extended_mind`
- repo: `docs/ENTROPY_DELEGATION.md`, `noesis/entropy_ledger.py`, `noesis/entropy_budget.py`, `schemas/entropy_ledger.schema.json`
- module: pipeline_v8 · gate: `gate5_entropy_delegation_safety`
- failure mode: Presenting the entropy proxy as physical entropy.

### `gnwt_analogy` (S4, analogy_claim)
> Broadcast and re-entry across the cognitive graph are a structural analogy to the Global Neuronal Workspace.
- sources: `baars_1988_global_workspace`, `mashour_2020_gnwt_review`, `dehaene_changeux_2011_conscious_processing`
- repo: `docs/quarantine/GNWT_OPERATIONAL_ANALOGY.md`, `noesis/broadcast.py`, `schemas/broadcast_trace.schema.json`
- module: pipeline_v7 · gate: `gate4_broadcast_awareness`
- failure mode: Using GNWT to imply a biological workspace or consciousness in software.

### `externalized_active_inference` (S4, analogy_claim)
> The pipeline is an active-inference-inspired loop closed through a human, not an autonomous sensorimotor agent.
- sources: `friston_2010_free_energy`, `parr_pezzulo_friston_2022_active_inference`, `clark_2013_predictive_processing`
- repo: `docs/quarantine/EXTERNALIZED_ACTIVE_INFERENCE.md`, `noesis/precision_scheduler.py`, `schemas/precision_schedule.schema.json`
- module: pipeline_v8 · gate: `gate6_iev_precision_gate`
- failure mode: Claiming an autonomous active-inference loop.

### `cognitive_dimensionality_proxy` (S5, proxy_claim)
> Cognitive dimensionality is an effective-dimensionality proxy (participation ratio over accepted hypotheses) distinguishing useful axes from noise.
- sources: `du_2023_multiagent_debate`, `wang_2023_self_consistency`
- repo: `docs/COGNITIVE_DIMENSIONALITY.md`, `noesis/dimensionality.py`, `noesis/effective_dim.py`, `schemas/dimensionality_report.schema.json`
- module: pipeline_v7, pipeline_v8 · gate: `gate3_dimensionality_discipline`
- failure mode: Claiming the metric measures neural/brain dimensionality.

### `cluster_quality_proxy` (S5, proxy_claim)
> Cluster quality is a composite proxy over IEV bandwidth, node diversity, latency drag, noise rejection, and artifact convergence.
- sources: `cowan_2001_working_memory`, `du_2023_multiagent_debate`, `risko_gilbert_2016_cognitive_offloading`
- repo: `docs/CLUSTER_QUALITY_METRICS.md`, `noesis/cluster_quality.py`, `schemas/cluster_quality_report.schema.json`
- module: pipeline_v8 · gate: `gate10_overexpansion_control`
- failure mode: Presenting the composite score as a validated quality measurement.

### `theory_lenses_proxy` (S5, proxy_claim)
> Each neurocognitive theory lens is a deterministic text-structural proxy unless an actual computation is implemented.
- sources: `graziano_2013_attention_schema`, `mashour_2020_gnwt_review`, `parr_pezzulo_friston_2022_active_inference`
- repo: `docs/THEORIES.md`, `docs/THEORY_CONTRIBUTION.md`, `noesis/theories.py`, `schemas/theory_readout.schema.json`
- module: pipeline_v6, pipeline_v7 · gate: `gate7_theory_discipline`
- failure mode: Claiming a lens computes the theory it is named after.

### `eiic_speculative` (S6, theory_claim)
> EIIC (Extrapolated Intentional Identity Core) is a speculative trajectory construct, framed by possible-selves and narrative-identity psychology, with no predictive validation.
- sources: `markus_nurius_1986_possible_selves`, `mcadams_2001_narrative_identity`
- repo: `noesis/eiic.py`, `schemas/eiic.schema.json`
- module: pipeline_v6 · gate: `gate7_eiic_discipline`
- failure mode: Presenting EIIC as predicting a person's future or destiny.

### `category_layer_conceptual_engineering` (S4, analogy_claim)
> The category / reality-map layer is conceptual engineering over the user's terms, not metaphysical discovery.
- sources: `cappelen_2018_conceptual_engineering`, `chalmers_2020_conceptual_engineering`, `whitehead_1929_process_reality`
- repo: `docs/CAUSAL_CATEGORY_LAYER.md`, `docs/ONTOLOGY.md`, `noesis/ontology.py`, `noesis/causal.py`
- module: pipeline_v6 · gate: `gate2_category_causality`
- failure mode: Reading category outputs as objective metaphysics or civilizational essence.

### `artifact_stability` (S1, implementation_claim)
> Artifact stability is software verification, regression, and rollback discipline over generated artifacts.
- sources: `fowler_2018_refactoring`, `parnas_1972_modular_decomposition`, `wroblewski_2022_jsonschema`
- repo: `docs/COLLAPSE_CONTROLLER.md`, `noesis/collapse_controller.py`, `noesis/validators.py`, `schemas/artifact.schema.json`
- module: pipeline_v8 · gate: `gate7_collapse_discipline`
- failure mode: Claiming schema-valid artifacts are semantically true.

### `evidence_bundle_provenance` (S0, implementation_claim)
> The Evidence Bundle is software observability, reproducibility, and provenance for each run.
- sources: `parnas_1972_modular_decomposition`, `wroblewski_2022_jsonschema`
- repo: `noesis/evidence.py`, `noesis/provenance.py`, `schemas/evidence_bundle_v8.schema.json`
- module: pipeline_v8 · gate: `gate2_provenance`
- failure mode: Treating bundle provenance as proof of correctness.

### `human_responsibility` (S3, limitation_claim)
> High-stakes or ambiguous outputs route to a human; final responsibility stays with the human.
- sources: `risko_gilbert_2016_cognitive_offloading`, `gu_2024_judge_survey`, `zheng_2023_llm_as_judge`
- repo: `docs/CLAIM_GOVERNANCE.md`, `docs/ethics.md`, `noesis/forbidden.py`
- module: pipeline_v8 · gate: `gate11_human_responsibility`
- failure mode: Letting the tool make high-stakes decisions autonomously.

### `forbidden_guard` (S1, implementation_claim)
> A deterministic guard blocks AGI / consciousness / therapy / diagnosis / destiny overclaims from output.
- sources: `tononi_2016_iit`, `mashour_2020_gnwt_review`
- repo: `noesis/forbidden.py`, `docs/OVERCLAIM_GUARDRAILS.md`
- module: pipeline_v6, pipeline_v7, pipeline_v8 · gate: `gate12_forbidden`
- failure mode: Relying on the guard as a complete safety proof.

### `externalized_metacognition` (S4, analogy_claim)
> Noesis externalizes the user's metacognitive monitoring/control loop; it supports human metacognition rather than possessing its own.
- sources: `fleming_lau_2014_metacognition`, `nelson_narens_1990_metamemory`
- repo: `README.md`, `docs/METHODOLOGY.md`, `noesis/adaptive.py`
- module: pipeline_v6 · gate: `gate1_intent_coherence`
- failure mode: Claiming the tool is metacognitive rather than supporting the user's metacognition.

### `iterative_refinement_loop` (S5, proxy_claim)
> The vertical loop is a critique-and-refine pass over candidates, in the self-refine / reflexion style.
- sources: `madaan_2023_self_refine`, `shinn_2023_reflexion`, `wang_2023_self_consistency`
- repo: `noesis/vertical_loop.py`, `docs/METHODOLOGY.md`
- module: pipeline_v8 · gate: `gate7_collapse_discipline`
- failure mode: Treating self-critique as ground-truth verification.

### `agent_orchestration` (S4, analogy_claim)
> Multi-node candidate generation and critique use test-time agent-orchestration patterns.
- sources: `wu_2023_autogen`, `du_2023_multiagent_debate`, `wang_2023_self_consistency`
- repo: `docs/DISTRIBUTED_COGNITIVE_GRAPH.md`, `noesis/graph.py`, `noesis/node_profile.py`
- module: pipeline_v7 · gate: `gate1_graph_completeness`
- failure mode: Claiming multi-agent orchestration guarantees better reasoning.
