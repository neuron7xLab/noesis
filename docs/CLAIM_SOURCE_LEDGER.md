<!-- GENERATED from data/*.json by noesis.bibliography — do not edit by hand. -->

# Claim → Source Ledger

claim → status → source → module → limitation → gate.

| claim | type | status | sources | module | gate | limitation |
|---|---|---|---|---|---|---|
| `low_bandwidth_controller` | analogy_claim | S4 | `cowan_2001_working_memory`, `miller_1956_magical_seven`, `miller_cohen_2001_pfc`, `baddeley_hitch_1974_working_memory` | pipeline_v8, iev_bandwidth | `gate5_iev_bandwidth_safety` | Capacity limits are a cognitive-science analogy, not a measured human bitrate. |
| `intent_vector` | analogy_claim | S4 | `miller_cohen_2001_pfc`, `cowan_2001_working_memory`, `nelson_narens_1990_metamemory`, `badre_2008_hierarchical_control` | pipeline_v7, pipeline_v8 | `gate1_intent_coherence` | Cognitive-control analogy; the vector is a text/structural representation, not a neural goal code. |
| `iev_precision_gate` | proxy_claim | S5 | `lightman_2023_process_supervision`, `uesato_2022_process_outcome`, `zheng_2023_llm_as_judge`, `gu_2024_judge_survey`, `friston_2010_free_energy` | pipeline_v7, pipeline_v8 | `gate6_iev_precision_gate` | A computable proxy inspired by process supervision and precision-weighting, not a trained process reward model nor a free-energy computation. |
| `iev_bandwidth_proxy` | proxy_claim | S5 | `cowan_2001_working_memory`, `risko_gilbert_2016_cognitive_offloading`, `lightman_2023_process_supervision` | pipeline_v8 | `gate5_iev_bandwidth_safety` | Not measured neural bandwidth; a throughput heuristic over validation events. |
| `delegated_computational_entropy` | proxy_claim | S5 | `risko_gilbert_2016_cognitive_offloading`, `hutchins_1995_cognition_in_the_wild`, `wang_2023_self_consistency`, `clark_chalmers_1998_extended_mind` | pipeline_v8 | `gate5_entropy_delegation_safety` | Entropy here is an information-structural proxy over candidate sets, not physical/thermodynamic entropy. |
| `gnwt_analogy` | analogy_claim | S4 | `baars_1988_global_workspace`, `mashour_2020_gnwt_review`, `dehaene_changeux_2011_conscious_processing` | pipeline_v7 | `gate4_broadcast_awareness` | A structural analogy only; not biological identity, not a consciousness or brain-measurement claim. |
| `externalized_active_inference` | analogy_claim | S4 | `friston_2010_free_energy`, `parr_pezzulo_friston_2022_active_inference`, `clark_2013_predictive_processing` | pipeline_v8 | `gate6_iev_precision_gate` | Human-in-the-loop analogy; no autonomous perception-action cycle and no free-energy computation. |
| `cognitive_dimensionality_proxy` | proxy_claim | S5 | `du_2023_multiagent_debate`, `wang_2023_self_consistency` | pipeline_v7, pipeline_v8 | `gate3_dimensionality_discipline` | A statistical proxy over candidate representations; not measured brain dimensionality. |
| `cluster_quality_proxy` | proxy_claim | S5 | `cowan_2001_working_memory`, `du_2023_multiagent_debate`, `risko_gilbert_2016_cognitive_offloading` | pipeline_v8 | `gate10_overexpansion_control` | A composite heuristic; component weights are engineering choices, not fitted parameters. |
| `theory_lenses_proxy` | proxy_claim | S5 | `graziano_2013_attention_schema`, `mashour_2020_gnwt_review`, `parr_pezzulo_friston_2022_active_inference` | pipeline_v6, pipeline_v7 | `gate7_theory_discipline` | Lenses are labelled 'deterministic-proxy'; they do not implement the underlying theories. |
| `eiic_speculative` | theory_claim | S6 | `markus_nurius_1986_possible_selves`, `mcadams_2001_narrative_identity` | pipeline_v6 | `gate7_eiic_discipline` | Research hypothesis with no validation; must never be presented as predictive of identity or destiny. |
| `category_layer_conceptual_engineering` | analogy_claim | S4 | `cappelen_2018_conceptual_engineering`, `chalmers_2020_conceptual_engineering`, `whitehead_1929_process_reality` | pipeline_v6 | `gate2_category_causality` | Conceptual refactoring of terms; no civilizational essentialism and no claim of metaphysical truth. |
| `artifact_stability` | implementation_claim | S1 | `fowler_2018_refactoring`, `parnas_1972_modular_decomposition`, `wroblewski_2022_jsonschema` | pipeline_v8 | `gate7_collapse_discipline` | Validated by tests and schemas; structural correctness, not semantic truth of content. |
| `evidence_bundle_provenance` | implementation_claim | S0 | `parnas_1972_modular_decomposition`, `wroblewski_2022_jsonschema` | pipeline_v8 | `gate2_provenance` | Records what ran; does not certify the truth of the recorded content. |
| `human_responsibility` | limitation_claim | S3 | `risko_gilbert_2016_cognitive_offloading`, `gu_2024_judge_survey`, `zheng_2023_llm_as_judge` | pipeline_v8 | `gate11_human_responsibility` | Offloading can create dependence; the tool advises, the human decides. |
| `forbidden_guard` | implementation_claim | S1 | `tononi_2016_iit`, `mashour_2020_gnwt_review` | pipeline_v6, pipeline_v7, pipeline_v8 | `gate12_forbidden` | Substring/heuristic guard; reduces but does not eliminate overclaim risk. |
| `externalized_metacognition` | analogy_claim | S4 | `fleming_lau_2014_metacognition`, `nelson_narens_1990_metamemory` | pipeline_v6 | `gate1_intent_coherence` | An externalized monitoring/control analogy; the tool has no metacognition of its own. |
| `iterative_refinement_loop` | proxy_claim | S5 | `madaan_2023_self_refine`, `shinn_2023_reflexion`, `wang_2023_self_consistency` | pipeline_v8 | `gate7_collapse_discipline` | A refinement proxy; self-critique is bounded by the base model and needs external verification. |
| `agent_orchestration` | analogy_claim | S4 | `wu_2023_autogen`, `du_2023_multiagent_debate`, `wang_2023_self_consistency` | pipeline_v7 | `gate1_graph_completeness` | Orchestration is a structural pattern; more agents do not by themselves improve reasoning. |

## Wording discipline

- **low_bandwidth_controller** — allowed: _low-bandwidth controller abstraction_ · forbidden: _measured human/PFC bandwidth_
- **intent_vector** — allowed: _compressed control packet / intent-coherence vector_ · forbidden: _neural goal representation_
- **iev_precision_gate** — allowed: _operational precision-gate proxy_ · forbidden: _trained process reward model / free-energy minimization_
- **iev_bandwidth_proxy** — allowed: _operational proxy for validation throughput_ · forbidden: _measured PFC bandwidth_
- **delegated_computational_entropy** — allowed: _delegated computational entropy (proxy)_ · forbidden: _physical/thermodynamic entropy_
- **gnwt_analogy** — allowed: _GNWT-inspired broadcast analogy_ · forbidden: _global workspace proven in the system / consciousness_
- **externalized_active_inference** — allowed: _active-inference-inspired, human-closed loop_ · forbidden: _autonomous active inference agent_
- **cognitive_dimensionality_proxy** — allowed: _effective-dimensionality proxy_ · forbidden: _measured brain dimensionality_
- **cluster_quality_proxy** — allowed: _composite cluster-quality proxy_ · forbidden: _validated cognitive quality measurement_
- **theory_lenses_proxy** — allowed: _deterministic-proxy theory lens_ · forbidden: _implementation of GNWT/IIT/active inference_
- **eiic_speculative** — allowed: _speculative trajectory construct_ · forbidden: _EIIC predicts destiny / true self_
- **category_layer_conceptual_engineering** — allowed: _conceptual-engineering category layer_ · forbidden: _discovers metaphysical / civilizational truth_
- **artifact_stability** — allowed: _verified, regression-safe artifact_ · forbidden: _proven-correct artifact_
- **evidence_bundle_provenance** — allowed: _reproducible evidence bundle with provenance_ · forbidden: _proof of correctness_
- **human_responsibility** — allowed: _human-in-the-loop, human-final-responsibility_ · forbidden: _autonomous decision authority_
- **forbidden_guard** — allowed: _deterministic overclaim guard_ · forbidden: _guarantees no harmful output_
- **externalized_metacognition** — allowed: _externalized metacognition (supports the human's)_ · forbidden: _the system is metacognitive / self-aware_
- **iterative_refinement_loop** — allowed: _critique-and-refine proxy loop_ · forbidden: _self-verifying / guaranteed-correct refinement_
- **agent_orchestration** — allowed: _test-time orchestration pattern_ · forbidden: _more agents = better reasoning_
