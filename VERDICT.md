# Tasks 3–9 — Action-Potential Runtime

The runtime that stops treating agent output as action and starts treating action
as a verified threshold-crossing with trace, hash, rollback, artifact, metric, and
release verdict. All deterministic, fail-closed, gate-bound.

| Task | Module | Core |
|---|---|---|
| 3 Action-Potential Trace | `noesis/runtime/action_potential_trace.py` | `state_t→gate_score→decision→artifact_delta→state_t+1`; invalid without threshold/score/artifact/rollback |
| 4 Discharge Gate | `noesis/gates/discharge_gate.py` | `w=αR+βV+γP−δK`; PASS/BELOW_THRESHOLD/FAIL/REROUTE/HUMAN_REVIEW; PASS impossible below θ |
| 5 Residual Promotion | `noesis/gates/residual_promotion.py` | no verifier → no mechanism; proxy↛measurement; unsupported→human |
| 6 Evidence Integral | `noesis/evidence_integral.py` | sha256 hash-chain; replayable; artifact↔trace↔verifier linked |
| 7 Rollback Physics | `noesis/runtime/rollback.py` | every invalid discharge reversible; failed benchmark never releases |
| 8 Fractal Gate Consistency | `noesis/evaluation/fractal_gate_consistency.py` | one gate, 7 scales; release can't PASS when a lower scale fails |
| 9 Failure-Weighted Benchmark | `noesis/evaluation/failure_weighted_benchmark.py` | quality = verified − unsupported − rollback debt − human overload |

**Release verdict (live):** `assemble_from_repo` pulls the open `trajectory` hard
failure from `data/physics_boundary_contract.json` → **release_verdict = FAIL**.
The runtime refuses to release while Role 3's trajectory trace is unbuilt. Failure
signal outweighs simulated success, by construction.

**Verification:** 324 pytest @ 93.13% coverage gate · ruff clean · mypy --strict
(78 files). Per-task suites:
`tests/test_{discharge_gate,action_potential_trace,residual_promotion,evidence_integral,rollback,fractal_gate_consistency,failure_weighted_benchmark}.py`.

---

# Role 2 — Physics Contract Implementer

**contract_status: FAIL (by design) — score 95/100.** The contract LAYER is fully
implemented and its tests pass; the FAIL is the gate correctly rejecting an
incomplete repository (no per-operator trajectory trace). Report:
[`data/physics_boundary_contract.json`](data/physics_boundary_contract.json) ·
[`docs/PHYSICS_CONTRACT.md`](docs/PHYSICS_CONTRACT.md).

- **hard_failures:** `["trajectory"]` — `rollback_condition_t`, `state_t_plus_1`,
  `score_t`, `decision_t` are not persisted per operator.
- **files created:** `noesis/contracts/{__init__,physics_boundary,physics_boundary_validator,physics_boundary_cli}.py`,
  `schemas/{physics_boundary_contract,operator_contract,claim_status_contract,trajectory_contract}.schema.json`,
  `data/physics_boundary_contract.json`,
  `tests/test_{physics_boundary_contract,operator_contract,claim_status_contract,trajectory_contract}.py`,
  `docs/PHYSICS_CONTRACT.md`.
- **files modified:** `noesis/cli.py` (add `physics-boundary validate`),
  `noesis/bibliography.py` (exclude contract meta-doc from scan), `tests/test_cli.py`.
- **validation commands:**
  `python -m pytest tests/test_physics_boundary_contract.py tests/test_operator_contract.py tests/test_claim_status_contract.py tests/test_trajectory_contract.py -q` ·
  `python -m pytest -q` · `ruff check .` · `mypy` ·
  `python -m noesis.contracts.physics_boundary_cli validate` (exit 1 by design).
- **test results:** 255 pytest pass @ 92.79% coverage gate; ruff clean; mypy --strict (68 files); the 4 contract suites (32 tests) pass.
- **first failing gate:** `trajectory`.
- **Role 3:** TRAJECTORY TRACE IMPLEMENTER — `schemas/trajectory_trace.schema.json`,
  `noesis/trajectory.py`, `tests/test_trajectory_trace.py`; modify `noesis/pipeline_v8.py`,
  `noesis/evidence.py`, `noesis/cli.py`. Gate passes when the CLI exits 0.
- **honest verdict:** The physics boundary is now machine-verifiable and the gate
  bites: it refuses to call the repo green while the trajectory/rollback layer is
  absent. Role 2's deliverable is complete; the contract it enforces is not yet
  satisfied — that is the point, and it is handed to Role 3.

---

# VERDICT — Physics Boundary Audit (Role 1, First-Principles Physics Auditor)

**Verdict: PASS — 75/90.** Full report: [`data/physics_boundary_report.json`](data/physics_boundary_report.json)
· [`docs/PHYSICS_BOUNDARY_AUDIT.md`](docs/PHYSICS_BOUNDARY_AUDIT.md)
· verifier [`tests/test_physics_boundary_report_schema.py`](tests/test_physics_boundary_report_schema.py).

## Verifier run (this audit)

| Command | Status |
|---|---|
| `python -m pytest tests/test_physics_boundary_report_schema.py -q` | PASS (7) |
| `python -m pytest -q` | PASS (215, coverage 92.61% ≥ 90% gate) |
| `ruff check .` | PASS |
| `mypy` | PASS (64 files, strict) |
| `python -m noesis.cli bibliography validate` | PASS (exit 0, Gate 13 runtime guard) |
| `python -m noesis.cli verdict out/` (after a pipeline run) | PASS |

> Role 1 spec referenced `cme.cli`; canonical package is `noesis`. `verdict` needs a
> bundle dir argument (`out/`), not `.`.

## First missing condition

No unified machine-readable **per-operator trajectory trace** (`score_t`,
`decision_t`, `rollback_condition_t`, explicit `state_t → state_t+1`). The Evidence
Bundle is auditable by artifact but not replayable by step.

## Next role

**Role 2 = TRAJECTORY TRACE IMPLEMENTER** — create
`schemas/trajectory_trace.schema.json`, `noesis/trajectory.py`,
`tests/test_trajectory_trace.py`; modify `noesis/pipeline_v8.py`,
`noesis/evidence.py`, `noesis/cli.py`. Pass/fail criteria in the JSON `role_2_handoff`.

---

# VERDICT — Noesis v0.5 (чесно настільки, щоб боліло)

## Що працює
10-гейтова труба, claim governance, 10-файловий Evidence Bundle, `noesis verdict`,
100-input proxy benchmark + ablation. **114/114 pytest, mypy --strict (35 файлів), ruff.**

## Що детерміноване
Усі 4 страти, 10 гейтів, провенанс-теги, baseline-порівняння, benchmark, ablation,
evidence. Працює офлайн, відтворювано (sha256 input_hash).

## Що потребує LLM
Лише якість прози фіналайзера (опційно). Решта — детермінована.

## Що валідоване (числом)
claim_safety_rate=**1.0**, artifact_validity_rate=**1.0**, failure_mode_rate=**1.0**
на 100 входах. 10 гейтів проходять на full_pipeline.

## Що спекулятивне
`extrapolated_core` і `peak_architecture` EIIC — примусово `speculative` (Gate 8).

## Що ФЕЙКОВЕ, якщо перебільшити (болить)
1. **compression=1.0/5** — фіналайзер на коротких входах НЕ стискає, а ДОПОВНЮЄ до
   90–110 слів. Називати це «стисненням» — брехня; чесно — «структурує».
2. **category_layer декоративний для валідації** — ablation: його видалення ламає
   НУЛЬ гейтів. Він додає інтерпретацію, але жоден гейт від нього не залежить.
3. **12 теорій — текстові проксі, не реалізації** (нема EFE/Φ/гомології). benchmark
   не відокремлює внесок теорій від артефакту → RQ3 поки не доведено.
4. **proxy_eval ≠ якість.** Рейти 1.0 означають структурну консистентність, НЕ що
   вихід суб'єктивно кращий. Без людської оцінки це не доведено.

## Що треба збудувати далі (3 кроки)
1. **Дати category_layer власну гейт-залежність** (interpretation_bias впливає на
   вибір дії) — або видалити як декор. Ablation мусить його штрафувати.
2. **Стиснення для коротких входів** — або зняти 90–110 контракт із коротких, або
   ввести adaptive-rate; зараз compression-метрика чесно провалена.
3. **Людська оцінка (Phase 3)** на ablation-парах — відокремити структурну
   консистентність від реальної корисності; без неї benchmark лишається проксі.

---

# VERDICT — Noesis v0.4 + EIIC v0.1

## v0.4 / EIIC — нейрокогнітивний шар (короткий вердикт)
- **Детерміноване:** 12 теоретичних лінз (`noesis/theories.py`) — текстові проксі;
  10-секційний `noesis neuro`; EIIC `noesis eiic`; уся валідація + провенанс-теги.
- **Що чесно метафоричне/проксі:** жодна лінза не є реалізацією теорії — нема
  EFE/Φ/персистентної гомології. Це названі оператори над текстом. Явно позначено
  у кожному `operator_output` і в `docs/THEORIES.md`.
- **Валідоване:** forbidden-шар ловить claims про свідомість/досвід(IIT)/AGI/долю/
  містику/діагноз; EIIC примусово тегує екстраполяцію `speculative` (не observed).
- **Спекулятивне:** усе `extrapolated_core`/`peak_architecture` — інженерна
  екстраполяція, не передбачення; теги це фіксують.
- **78→106 тестів** включно з 12 прикладами через `neuro` і `eiic`.

Нижче — повний вердикт ядра v0.3.

---

# VERDICT — Noesis v0.3

Чесний аудит. Сепарація сигналу від шуму застосована до самого продукту.

## Definition of Done — виконано
> Хаотичне людське повідомлення стає в **одну команду** валідованим когнітивним
> артефактом, що показує: яка карта реальності активна · яка категорія керує
> інтерпретацією · яка перша відсутня умова блокує · яка наступна дія · який
> failure mode тримати під наглядом.

```bash
python -m noesis.cli pipeline examples/problems/05_career_path.txt --evidence out/
# → domain china (Ци), refuse: "адаптація без конфронтації", PASS, Evidence Bundle×8
```
**78/78 pytest, mypy --strict (28 файлів), ruff.** 12 реальних прикладів проходять
end-to-end; кожен видає валідований артефакт (`tests/test_cme_v3.py`).

## Що детерміноване (підлога, офлайн, завжди валідне)
- Category Extractor (лексикон 30 категорій), Reality Map Builder, Synthesis Axis,
  Reverse Inference (goal regression), Artifact Builder, **уся валідація**, Evidence Bundle.
- Працює без мережі; результат відтворюваний (sha256-id маніфесту).

## Що потребує LLM (підсилення якості, не коректності)
- Природна якість фіналайзера дзеркала (`--backend cli|sdk|llm`).
- LLM пропонує — детермінований контракт розпоряджається; при невідповідності
  падаємо на детерміновану підлогу. Продукт ЗАВЖДИ видає валідований артефакт.

## Що академічно обґрунтоване
- Формальні інваріанти 7 методів ізоморфні рецензованим конструктам
  (`docs/THEORY.md`): метакогніція (Nelson 1984), STRIPS-регресія (Fikes & Nilsson
  1971), інформаційне вузьке місце (Tishby 1999), демаркація (Popper 1959).
- Цивілізаційна матриця 30 категорій спирається на першоджерела
  (`docs/CIVILIZATIONAL_METAPHYSICS.md`).

## Що метафоричне (і чесно позначене)
- Самі цивілізаційні «осі реальності» — **граматика лінз**, не онтологічна істина.
- AI-product-аналогії категорій — дидактичні мости, не тотожності.
- «Brain-inspired» — ізоморфізм операцій, не нейрофізіологічне твердження.

## Що валідоване (числом, не словом)
- Контракт фіналайзера (90–110 слів + 6 якорів), 7 секцій + виконуваний фальсифікатор,
  forbidden=0, hallucination≠high, goal-regression soundness, повнота категорій/синтезу.

## Що лишається спекулятивним / дослідженням
- Чи активна карта реальності справді відповідає тому, як людина мислить проблему
  (конструктна валідність екстрактора — зараз евристика на сигнал-маркерах).
- Чи блокуюче припущення правильне (виводиться з домінантної осі, не доводиться).
- Семантична глибина дзеркала без LLM (детермінований шаблон ≠ розуміння).
- Чи вихід «менш емоційно шумний» — потрібна афективна метрика, зараз без числа.

## Що чесно слабке (не приховую)
- Екстрактор — підрядкове співпадіння, не класифікатор; чутливий до формулювання.
- Дефолтна категорія «Дія» маскує випадок «жоден маркер не спрацював».
- Reverse plan і synthesis виводяться з осі детерміновано — корисна евристика, не доказ.

## Наступні 3 інженерні кроки
1. **Адверсивний набір** (~30 входів, що цілять у хибну осьову класифікацію,
   anchor-евейжн, прихований forbidden/overclaim); гейти мусять ловити, інакше — посилити.
2. **Афективно-навантажувальна метрика** (лексикон + дельта вхід/вихід) для кількісного
   доказу тези «менш емоційно шумний».
3. **LLM-екстрактор категорій із детермінованим фолбеком** — підняти конструктну
   валідність класифікації, лишивши детерміновану підлогу як гарант.

---

## Bibliographic status

Claim-to-source evidence graph (canonical data in `data/*.json`, validator
`noesis bibliography verdict`, gate `tests/test_bibliography_coverage.py`).
Live numbers: `noesis bibliography verdict`; full tables in
[`docs/BIBLIOGRAPHIC_EVIDENCE_GRAPH.md`](docs/BIBLIOGRAPHIC_EVIDENCE_GRAPH.md).

1. **Repo-verified (S0–S1).** Evidence Bundle / provenance, artifact stability,
   the deterministic forbidden guard — present in code and machine-checked.
2. **Literature-grounded (S2–S3).** Working memory (Cowan, Miller, Baddeley),
   cognitive control (Miller & Cohen, Badre), metacognition (Fleming & Lau),
   global workspace (Baars, Mashour/Dehaene), free energy / active inference
   (Friston, Parr et al., Clark), distributed cognition & offloading (Hutchins,
   Clark & Chalmers, Risko & Gilbert), LLM orchestration (self-consistency,
   Self-Refine, Reflexion, debate, AutoGen), verification (process supervision,
   LLM-as-judge survey), conceptual engineering (Cappelen, Chalmers).
3. **Analogy (S4).** GNWT broadcast, externalized active inference, the
   low-bandwidth controller, the conceptual-engineering category layer — borrowed
   structure, not biological/metaphysical identity.
4. **Proxy (S5).** IEV precision gate, IEV bandwidth, delegated computational
   entropy, cognitive dimensionality, cluster quality, theory lenses — heuristics
   that say *proxy*, never *measurement* (Gate 8).
5. **Speculative (S6).** EIIC — a trajectory construct framed by possible-selves
   (Markus & Nurius 1986) and narrative-identity (McAdams 2001) psychology, but
   with **no predictive validation**; listed in [`docs/UNSUPPORTED_CLAIMS.md`](docs/UNSUPPORTED_CLAIMS.md).
6. **Forbidden (X).** 12 overclaims (AGI, consciousness detection, Φ-as-experience,
   PFC bitrate, judge-as-truth, therapy, diagnosis, destiny, physical entropy,
   brain dimensionality) — each with a safe replacement and a blocking gate
   ([`docs/OVERCLAIM_GUARDRAILS.md`](docs/OVERCLAIM_GUARDRAILS.md)).
7. **Lacking source support.** None. Every claim is now anchored to ≥1 source
   (Gate 11) and every source anchors ≥1 claim (Gate 6/7) — zero
   `claims_without_sources`, zero `sources_without_claims`. EIIC remains S6 by
   honesty, not by missing sources. First-principle framing:
   [`docs/FIRST_PRINCIPLES.md`](docs/FIRST_PRINCIPLES.md).
8. **Rewrite-if-unsupported rule.** Any claim that cannot be sourced, validated,
   or bounded is marked unsupported or removed; the bibliography gate fails the
   build if a present theory term loses its source mapping (13 gates, incl.
   hierarchy type↔status and a runtime guard verifying the forbidden data
   against `noesis/forbidden.py`).
