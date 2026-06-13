# VERDICT_V6 — чесний, із реальними числами

Усі числа — детермінований **proxy_eval** на 100 входах (`cme benchmark`). НЕ людська оцінка.

## 10 обов'язкових відповідей

**1. Чи виправило adaptive compression проблему padding?**
ТАК — частково й чесно. Фіксований 90–110 контракт прибрано; довжина = режим складності
(micro/brief/standard/deep/protocol). Бенчмарк: `compression_status_distribution =
{structured_not_compressed: 100}` — на коротких/середніх входах вихід **структурований, не
стиснутий** (чесно позначено, не видається за стиснення). `compressed` зʼявляється лише на
довгих входах; `expanded_by_request` лише за явного запиту deep/protocol (live: in14→out103).
**Залишок:** реального стиснення на коротких входах не буває за визначенням — тепер це чесний
тег, а не padding-брехня.

**2. Чи category_layer тепер впливає на дію?**
ТАК. `category_causality_rate = 1.0`; `next_action_change_rate_under_ablation = 1.0`.
Домінантна категорія причинно модифікує `selected_action` (ablation `without_category_layer`
→ дія змінюється → verdict keep). Acceptance #2 (≥60%) виконано на 100%.

**3. Які теорії корисні / слабкі / декоративні?**
`decorative_theory_rate = 0.833`, `theory_contribution_mean = 0.358`,
`theory_layer_status = overloaded`. Корисні (wired): **switching** (score 4 коли режим=collapse,
змінює дію), **conceptual_engineering** (score 3, змінює валідацію). Декоративні (score 0):
решта 10 лінз — лише термінологія. Система **рекомендує їх вимкнути**.

**4. EIIC покращує стратегію чи додає спекулятивний шум?**
Нейтрально-до-керованого. EIIC дає `first_missing_condition` (входить у дію як вплив) і
дисципліну (Gate 7 примушує speculative). Ablation: `without_eiic → modify` (ламає лише власний
gate7, дію не змінює). Тобто EIIC = governance-цінність, не action-цінність.

**5. Які модулі видалити, якщо людська оцінка не підтримає?**
Кандидати на remove (ablation, ai_system_design): **theory_layer**, **adaptive_compression**
(для довгих входів), — змінюють 0 гейтів і 0 дії. `reality_maps`, `eiic`, `claim_governance` →
modify (лише власний гейт). **category_layer, artifact_validation → keep.**

**6. Що лишається proxy-only?**
Усі benchmark-оцінки; 12 теоретичних лінз; hallucination-евристика; domain="general"
(детектор домену не реалізовано).

**7. Що валідоване тестами?**
123 pytest, mypy --strict (41 файл), ruff. Adaptive (no-pad), causal-category-changes-action,
theory-decorative-flagging, ablation keep/modify/remove, human-eval-no-fake-scores,
15-файловий bundle, 12 гейтів.

**8. Що потребує людського судження?**
Чи вихід суб'єктивно ясніший/корисніший за baseline; чи category-bias дійсно покращує дію, а
не просто змінює її; чи EIIC-проєкція стратегічно корисна. → HumanEvalPacket (status=pending).

**9. Які claims заборонені?**
AGI, свідомість (детекція/вимір), IIT-досвід, діагноз, доля/карма/містика, мозок без даних,
universal truth. `claim_safety_rate = 1.0`.

**10. Наступне інженерне вузьке місце?**
Відокремити «category змінює дію» від «category ПОКРАЩУЄ дію» — зараз доведено лише перше
(diff), не друге (потребує людської оцінки). Без неї category-causality = механічний, не якісний.

## Підсумок: real / proxy / speculative / decorative
- **real:** adaptive-no-pad, causal-category-effect (diff-доведено), 12 гейтів, 15-файл bundle.
- **proxy:** усі бенчмарк-числа, 12 лінз, domain-детектор.
- **speculative:** EIIC extrapolated_core / peak_architecture.
- **decorative (чесно названо):** 10/12 теорій (score 0), theory_layer overloaded.
