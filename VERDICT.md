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
5. **Speculative (S6).** EIIC — a trajectory construct with **no source and no
   validation**; listed in [`docs/UNSUPPORTED_CLAIMS.md`](docs/UNSUPPORTED_CLAIMS.md).
6. **Forbidden (X).** 12 overclaims (AGI, consciousness detection, Φ-as-experience,
   PFC bitrate, judge-as-truth, therapy, diagnosis, destiny, physical entropy,
   brain dimensionality) — each with a safe replacement and a blocking gate
   ([`docs/OVERCLAIM_GUARDRAILS.md`](docs/OVERCLAIM_GUARDRAILS.md)).
7. **Lacking source support.** `eiic_speculative` (S6) and 4 background sources
   (Fleming & Lau, Self-Refine, Reflexion, AutoGen) cited in docs but not yet
   central to a ledger claim — tracked in `docs/UNSUPPORTED_CLAIMS.md`.
8. **Rewrite-if-unsupported rule.** Any claim that cannot be sourced, validated,
   or bounded is marked unsupported or removed; the bibliography gate fails the
   build if a present theory term loses its source mapping.
