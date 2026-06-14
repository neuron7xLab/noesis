# THEORIES — 12 нейрокогнітивних лінз (CME v0.4)

> **ЧЕСНИЙ СТАТУС.** Це **детерміновані текстові ПРОКСІ**, не реалізації теорій.
> Тут нема справжнього Active Inference (немає генеративної моделі й EFE),
> немає Φ з IIT (і жодного claim про свідомість/досвід), немає персистентної
> гомології TDA. Кожна лінза — названий, обмежений оператор над текстом +
> структурою v0.3, із явним сигналом і статусом `deterministic-proxy`. Реалізація:
> `noesis/theories.py`. Заборонені claims гейтуються `noesis/forbidden.py`.

| # | Теорія | Use for | Оператор (проксі) | Software role |
|---|---|---|---|---|
| 1 | **Active Inference** | дія під невизначеністю | політика = дія, що знімає першу невизначеність; EFE-проксі = к-сть невідомих умов | policy selector |
| 2 | **Attention Schema** | модель уваги про увагу | реальний фокус (домінанта) проти наративу; розбіжність якщо є сплячі осі | attention self-model |
| 3 | **Global Neuronal Workspace** | що стає глобально доступним | переможець трансляції = домінантна категорія; придушене = сплячі осі | workspace router |
| 4 | **Integrated Information** | ступінь інтеграції (НЕ свідомість) | φ-проксі = охоплено осей / 3 (зв'язність структури) | integration heuristic |
| 5 | **Thermodynamics of Computation** | втрата на шум | ентропія-проксі = шумові маркери / усі токени | entropy budget |
| 6 | **Topological Data Analysis** | форма простору станів | атрактор = найчастіша лема; цикл; розриви = сплячі осі | morphology scanner |
| 7 | **Switching Dynamical Systems** | зсуви режимів | класифікатор: exploration/defense/planning/execution/collapse | regime classifier |
| 8 | **Hierarchical Predictive Coding** | розбіжність очікування/входу | рівень помилки: sensory/semantic/strategic/identity | prediction-error stack |
| 9 | **Metacognitive Monitoring** | впевненість, корекція | потрібна корекція = (сумнів > впевненість) | monitor-controller loop |
| 10 | **Conceptual Engineering** | концепти, що керують інтерпретацією | переоформити домінантний концепт в операційне визначення | concept refactoring |
| 11 | **Dynamical Systems** | траєкторії, біфуркації | атрактор + біфуркація (маркери вибору) + стабільність | trajectory engine |
| 12 | **Systems Biology of Intelligence** | багатомасштабність | активні шари: bodily/social/technological/neural/molecular | multi-scale coupling |

## Вихідний формат (10 секцій, `noesis neuro`)
intent_mirror · theory_selection · state_space_map · prediction_error_stack ·
workspace_broadcast · active_inference_policy · conceptual_refactor · artifact ·
validation · next_action. Кожна виведена секція тегована провенансом
(observed/inferred/speculative/forbidden); `forbidden`-тег = FAIL.

## DoD (v0.4)
Хаотичне повідомлення → валідований нейрокогнітивний артефакт, що показує: режим
системи · помилку передбачення · сигнал, що контролює workspace · дію, що мінімізує
невизначеність · концепт під ремонт · failure mode під наглядом. Доведено на 12
прикладах (`tests/test_cme_v4.py`).

---

# EIIC v0.1 — Extrapolated Intentional Cognitive Core

`noesis eiic` витягає **термінальний вектор** системи: куди вона структурно прямує,
коли прибрати шум, страх, ресурсні обмеження й фрагментоване виконання — НЕ опис
поточної поведінки. 10 полів, кожне тегує провенанс:
current_state · latent_intent · noise_layer · constraint_layer · **extrapolated_core
(speculative)** · attractor_state · **peak_architecture (speculative)** · failure_mode ·
first_missing_condition · next_action.

**Гарантія чесності (валідатор):** `extrapolated_core` і `peak_architecture`
ОБОВ'ЯЗКОВО тегуються `speculative` — екстраполяція не видається за спостережене.
Заборонено: містицизм, мова долі, діагноз, AGI. Гейтується.
