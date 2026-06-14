<!-- GENERATED from data/*.json by noesis.bibliography — do not edit by hand. -->

# Bibliography

Grouped by domain. Each entry anchors a claim, module, or limitation.


## 1. Working memory / PFC / cognitive control

### `miller_1956_magical_seven` — S2
- **George A. Miller (1956).** *The magical number seven, plus or minus two: Some limits on our capacity for processing information.* Psychological Review [primary]
- supports: bounded information-processing channel of the human controller
- limits: historical estimate, superseded by chunk-based accounts
- used in: `docs/IEV_BANDWIDTH.md`, `docs/HUMAN_BOTTLENECK.md`
- risk if overused: treating '7±2' as a literal bandwidth constant

### `baddeley_hitch_1974_working_memory` — S2
- **Alan D. Baddeley, Graham Hitch (1974).** *Working memory.* The Psychology of Learning and Motivation [primary]
- supports: componential model of working memory used as controller analogy
- limits: model of biological memory, not of a software buffer
- used in: `docs/HUMAN_BOTTLENECK.md`
- risk if overused: mapping software state onto biological subsystems literally

### `nelson_narens_1990_metamemory` — S2
- **Thomas O. Nelson, Louis Narens (1990).** *Metamemory: A theoretical framework and new findings.* The Psychology of Learning and Motivation [primary]
- supports: monitoring/control loop structure for reflection methods
- limits: framework for human metamemory
- used in: `docs/METHODOLOGY.md`, `methods/introspection`
- risk if overused: asserting a literal monitoring/control loop in code

### `cowan_2001_working_memory` — S2
- **Nelson Cowan (2001).** *The magical number 4 in short-term memory: A reconsideration of mental storage capacity.* Behavioral and Brain Sciences [primary]
- supports: limited capacity of controlled working memory; low-bandwidth human controller abstraction
- limits: does not provide a measured PFC bitrate; capacity estimates are task- and chunk-dependent
- used in: `docs/IEV_BANDWIDTH.md`, `docs/HUMAN_BOTTLENECK.md`, `noesis/iev_bandwidth.py`
- risk if overused: pretending Noesis measured biological memory capacity

### `miller_cohen_2001_pfc` — S3
- **Earl K. Miller, Jonathan D. Cohen (2001).** *An integrative theory of prefrontal cortex function.* Annual Review of Neuroscience [review]
- supports: cognitive control via goal representations; top-down biasing as control abstraction
- limits: biological theory; Noesis implements no neural mechanism
- used in: `docs/IEV_PRECISION_GATE.md`, `noesis/intent_vector.py`
- risk if overused: claiming Noesis models PFC

### `badre_2008_hierarchical_control` — S3
- **David Badre (2008).** *Cognitive control, hierarchy, and the rostro-caudal organization of the frontal lobes.* Trends in Cognitive Sciences [review]
- supports: hierarchical cognitive control motivating layered pipeline
- limits: anatomical hierarchy ≠ software pipeline hierarchy
- used in: `docs/ARCHITECTURE.md`, `docs/NOESIS_V06_ARCHITECTURE.md`
- risk if overused: equating module depth with cortical hierarchy

### `fleming_lau_2014_metacognition` — S3 _(background)_
- **Stephen M. Fleming, Hakwan C. Lau (2014).** *How to measure metacognition.* Frontiers in Human Neuroscience [review]
- supports: metacognition and monitoring as a measurable construct; externalized metacognition framing
- limits: measures human metacognitive sensitivity, not a tool's
- used in: `README.md`, `docs/METHODOLOGY.md`, `docs/THEORY.md`
- risk if overused: claiming Noesis has metacognition rather than supporting the user's


## 2. Global Workspace / GNWT

### `baars_1988_global_workspace` — S2
- **Bernard J. Baars (1988).** *A Cognitive Theory of Consciousness.* Cambridge University Press [primary]
- supports: global workspace: broadcast and selective access as analogy
- limits: not a consciousness proof; not a brain-measurement claim
- used in: `docs/GNWT_OPERATIONAL_ANALOGY.md`, `noesis/broadcast.py`
- risk if overused: claiming Noesis instantiates a global workspace

### `dehaene_changeux_2011_conscious_processing` — S3
- **Stanislas Dehaene, Jean-Pierre Changeux (2011).** *Experimental and theoretical approaches to conscious processing.* Neuron [review]
- supports: ignition/broadcast vocabulary for selective access analogy
- limits: about neural consciousness, not software access control
- used in: `docs/GNWT_OPERATIONAL_ANALOGY.md`
- risk if overused: importing 'ignition' as a literal mechanism

### `graziano_2013_attention_schema` — S2
- **Michael S. A. Graziano (2013).** *Consciousness and the Social Brain.* Oxford University Press [primary]
- supports: attention-schema framing for one theory lens
- limits: theory of attention modelling; lens is a deterministic proxy
- used in: `noesis/theories.py`, `docs/THEORIES.md`
- risk if overused: claiming the lens implements an attention schema

### `tononi_2016_iit` — S3
- **Giulio Tononi, Melanie Boly, Marcello Massimini, Christof Koch (2016).** *Integrated information theory: from consciousness to its physical substrate.* Nature Reviews Neuroscience [review]
- supports: origin of the Φ vocabulary used only to bound the proxy
- limits: IIT Φ is a theory of consciousness; the repo Φ-proxy measures no experience
- used in: `docs/OVERCLAIM_GUARDRAILS.md`, `noesis/forbidden.py`
- risk if overused: claiming a Φ-proxy measures integrated information or experience

### `mashour_2020_gnwt_review` — S3
- **George A. Mashour, Pieter Roelfsema, Jean-Pierre Changeux, Stanislas Dehaene (2020).** *Conscious processing and the global neuronal workspace hypothesis.* Neuron [review]
- supports: broadcast/re-entry dynamics as structural analogy
- limits: GNWT is a neuroscientific hypothesis about consciousness; Noesis makes no such claim
- used in: `docs/GNWT_OPERATIONAL_ANALOGY.md`
- risk if overused: using GNWT to imply biological workspace in software


## 3. Active Inference / Free Energy / Predictive Coding

### `friston_2010_free_energy` — S3
- **Karl Friston (2010).** *The free-energy principle: a unified brain theory?.* Nature Reviews Neuroscience [review]
- supports: precision-weighting and prediction-error language; action under uncertainty framing
- limits: Noesis is human-in-the-loop, not an autonomous active-inference agent
- used in: `docs/EXTERNALIZED_ACTIVE_INFERENCE.md`, `docs/PRECISION_WEIGHT_SCHEDULER.md`, `noesis/precision_scheduler.py`
- risk if overused: claiming Noesis minimizes variational free energy

### `clark_2013_predictive_processing` — S2
- **Andy Clark (2013).** *Whatever next? Predictive brains, situated agents, and the future of cognitive science.* Behavioral and Brain Sciences [primary]
- supports: predictive-processing framing of error-driven refinement
- limits: theory of biological cognition
- used in: `docs/EXTERNALIZED_ACTIVE_INFERENCE.md`
- risk if overused: claiming the pipeline is a predictive-coding hierarchy

### `parr_pezzulo_friston_2022_active_inference` — S2
- **Thomas Parr, Giovanni Pezzulo, Karl Friston (2022).** *Active Inference: The Free Energy Principle in Mind, Brain, and Behavior.* MIT Press [primary]
- supports: expected-free-energy vocabulary for action selection analogy
- limits: formal autonomous agent theory; Noesis closes the loop through a human
- used in: `docs/EXTERNALIZED_ACTIVE_INFERENCE.md`, `noesis/precision_gate.py`
- risk if overused: presenting the IEV functional as a literal EFE computation


## 4. Distributed Cognition / Cognitive Offloading

### `hutchins_1995_cognition_in_the_wild` — S2
- **Edwin Hutchins (1995).** *Cognition in the Wild.* MIT Press [primary]
- supports: cognition distributed across people and artifacts; externalized computation justification
- limits: descriptive ethnography, not a performance guarantee
- used in: `docs/DISTRIBUTED_COGNITIVE_GRAPH.md`, `docs/ENTROPY_DELEGATION.md`
- risk if overused: claiming distribution per se improves outcomes

### `clark_chalmers_1998_extended_mind` — S2
- **Andy Clark, David J. Chalmers (1998).** *The extended mind.* Analysis [primary]
- supports: tool-mediated cognition / cognitive extension framing
- limits: philosophical thesis, contested; not an empirical result
- used in: `docs/DISTRIBUTED_COGNITIVE_GRAPH.md`, `README.md`
- risk if overused: treating extension as proven cognitive enhancement

### `risko_gilbert_2016_cognitive_offloading` — S3
- **Evan F. Risko, Sam J. Gilbert (2016).** *Cognitive offloading.* Trends in Cognitive Sciences [review]
- supports: offloading improves immediate task performance; delegated computation framing
- limits: offloading may introduce dependence and skill atrophy
- used in: `docs/ENTROPY_DELEGATION.md`, `noesis/entropy_ledger.py`
- risk if overused: claiming offloading is uniformly beneficial


## 5. Test-time LLM orchestration

### `wang_2023_self_consistency` — S2
- **Xuezhi Wang, Jason Wei, Dale Schuurmans, Quoc Le, Ed Chi, Sharan Narang, Aakanksha Chowdhery, Denny Zhou (2023).** *Self-Consistency Improves Chain of Thought Reasoning in Language Models.* ICLR [primary]
- supports: multi-sample candidate generation and aggregation
- limits: gains are task-dependent; more samples cost compute
- used in: `docs/DISTRIBUTED_COGNITIVE_GRAPH.md`, `noesis/graph.py`
- risk if overused: assuming more samples always improve quality

### `madaan_2023_self_refine` — S2 _(background)_
- **Aman Madaan, Niket Tandon, Prakhar Gupta, et al. (2023).** *Self-Refine: Iterative Refinement with Self-Feedback.* NeurIPS [primary]
- supports: critique-and-refine loop for candidate improvement
- limits: self-feedback can entrench errors without external verification
- used in: `docs/METHODOLOGY.md`, `noesis/vertical_loop.py`
- risk if overused: treating self-critique as ground truth

### `shinn_2023_reflexion` — S2 _(background)_
- **Noah Shinn, Federico Cassano, Edward Berman, Ashwin Gopinath, Karthik Narasimhan, Shunyu Yao (2023).** *Reflexion: Language Agents with Verbal Reinforcement Learning.* NeurIPS [primary]
- supports: verbal self-reflection between passes
- limits: reflection quality bounded by the base model
- used in: `noesis/vertical_loop.py`
- risk if overused: claiming reflection yields reinforcement-learning guarantees

### `du_2023_multiagent_debate` — S2
- **Yilun Du, Shuang Li, Antonio Torralba, Joshua B. Tenenbaum, Igor Mordatch (2023).** *Improving Factuality and Reasoning in Language Models through Multiagent Debate.* arXiv:2305.14325 [primary]
- supports: multi-node disagreement as a diversity signal
- limits: more agents ≠ better reasoning by default
- used in: `docs/NODE_DIVERSITY.md`, `noesis/node_profile.py`
- risk if overused: claiming debate guarantees correctness

### `wu_2023_autogen` — S2 _(background)_
- **Qingyun Wu, Gagan Bansal, Jieyu Zhang, et al. (2023).** *AutoGen: Enabling Next-Gen LLM Applications via Multi-Agent Conversation.* arXiv:2308.08155 [primary]
- supports: agent/tool orchestration patterns
- limits: framework, not evidence of reasoning gains
- used in: `docs/DISTRIBUTED_COGNITIVE_GRAPH.md`
- risk if overused: citing as proof that orchestration improves reasoning


## 6. Verification / Process supervision / LLM-as-judge limits

### `uesato_2022_process_outcome` — S2
- **Jonathan Uesato, Nate Kushman, Ramana Kumar, et al. (2022).** *Solving math word problems with process- and outcome-based feedback.* arXiv:2211.14275 [primary]
- supports: process- vs outcome-based feedback distinction
- limits: domain-specific (math); not a general verifier
- used in: `docs/CLAIM_GOVERNANCE.md`
- risk if overused: generalizing math-verifier results to all claims

### `lightman_2023_process_supervision` — S2
- **Hunter Lightman, Vineet Kosaraju, Yura Burda, et al. (2023).** *Let's Verify Step by Step.* arXiv:2305.20050 [primary]
- supports: process supervision over outcome-only supervision; step-level verification motivating the IEV gate
- limits: process reward models need labeled supervision; Noesis uses a computable proxy
- used in: `docs/IEV_PRECISION_GATE.md`, `docs/CLAIM_GOVERNANCE.md`, `noesis/precision_gate.py`
- risk if overused: presenting the IEV proxy as a trained process reward model

### `zheng_2023_llm_as_judge` — S2
- **Lianmin Zheng, Wei-Lin Chiang, Ying Sheng, et al. (2023).** *Judging LLM-as-a-Judge with MT-Bench and Chatbot Arena.* NeurIPS [primary]
- supports: LLM-as-judge as a usable but biased evaluator
- limits: judge bias (position, verbosity, self-preference); not final truth
- used in: `docs/IEV_PRECISION_GATE.md`, `noesis/precision_gate.py`
- risk if overused: treating an LLM judge as ground truth

### `gu_2024_judge_survey` — S3
- **Jiawei Gu, Xuhui Jiang, Zhichao Shi, et al. (2024).** *A Survey on LLM-as-a-Judge.* arXiv:2411.15594 [review]
- supports: survey of judge reliability and failure modes
- limits: documents limits; does not solve them
- used in: `docs/IEV_PRECISION_GATE.md`, `docs/CLAIM_GOVERNANCE.md`
- risk if overused: citing survey breadth as endorsement of judging


## 7. Software engineering / architecture

### `parnas_1972_modular_decomposition` — S2
- **David L. Parnas (1972).** *On the criteria to be used in decomposing systems into modules.* Communications of the ACM [primary]
- supports: information hiding, modularity, decoupling
- limits: principle, not a correctness proof
- used in: `docs/ARCHITECTURE.md`, `docs/NOESIS_V06_ARCHITECTURE.md`
- risk if overused: citing modularity as evidence of correctness

### `fowler_2018_refactoring` — S3
- **Martin Fowler (2018).** *Refactoring: Improving the Design of Existing Code (2nd ed.).* Addison-Wesley [review]
- supports: regression-safe change, rollback discipline, artifact stability
- limits: engineering practice, not formal verification
- used in: `docs/COLLAPSE_CONTROLLER.md`, `noesis/collapse_controller.py`
- risk if overused: claiming refactoring guarantees behavior preservation

### `wroblewski_2022_jsonschema` — S0
- **JSON Schema Organization (2022).** *JSON Schema Specification (Draft 2020-12).* json-schema.org [primary]
- supports: schema contracts and structural validation
- limits: validates structure, not semantic truth of content
- used in: `schemas/`, `noesis/validators.py`, `docs/SCHEMAS.md`
- risk if overused: treating schema-valid as semantically correct


## 8. Philosophy / conceptual engineering / metaphysics

### `whitehead_1929_process_reality` — S4
- **Alfred North Whitehead (1929).** *Process and Reality.* Macmillan [primary]
- supports: process-over-substance framing as bounded analogy only
- limits: speculative metaphysics; used strictly as analogy, never as mechanism
- used in: `docs/CIVILIZATIONAL_METAPHYSICS.md`, `docs/philosophy.md`
- risk if overused: civilizational essentialism or mystical reading

### `cappelen_2018_conceptual_engineering` — S2
- **Herman Cappelen (2018).** *Fixing Language: An Essay on Conceptual Engineering.* Oxford University Press [primary]
- supports: conceptual engineering: assessing and improving concepts; category/reality-map layer
- limits: philosophy of concepts; no empirical metric
- used in: `docs/CAUSAL_CATEGORY_LAYER.md`, `docs/ONTOLOGY.md`, `noesis/ontology.py`
- risk if overused: claiming category refactoring discovers metaphysical truth

### `chalmers_2020_conceptual_engineering` — S3
- **David J. Chalmers (2020).** *What is conceptual engineering and what should it be?.* Inquiry [review]
- supports: framework for conceptual refactoring of terms
- limits: meta-philosophical; bounds, not validates, the category layer
- used in: `docs/CAUSAL_CATEGORY_LAYER.md`
- risk if overused: over-reading category outputs as conceptual truth

