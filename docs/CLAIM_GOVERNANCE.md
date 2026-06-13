# CLAIM_GOVERNANCE — модель провенансу

Кожне високорівневе твердження тегується рівно одним статусом
(`cme/provenance.py`). Це формальний центр чесності CME.

| Тег | Значення |
|---|---|
| **observed** | прямо присутнє у вході або вироблене детерміновано |
| **inferred** | виведене з тексту правилами/LLM, правдоподібне але не гарантоване |
| **speculative** | проєкція/екстраполяція/майбутня траєкторія (вихід EIIC) |
| **forbidden** | claim, який НЕ можна емітити як валідний вихід |

## Заборонена таксономія (детектори в `cme/forbidden.py`)
AGI achieved · consciousness detected/measured · IIT proves experience ·
therapy/medical diagnosis · destiny/karma/mysticism · unmeasured brain claim ·
validated neuroscience without data · universal truth claim.

## Жорсткі правила EIIC
- `latent_intent` — мусить бути `inferred`.
- `extrapolated_core` — мусить бути `speculative`.
- `peak_architecture` — мусить бути `speculative`.
Порушення → Gate 8 FAIL. Тест: `tests/test_cme_v4.py::test_eiic_terminal_vector`.

## Як це гейтується
Gate 2 (provenance) — кожен claim протеговано валідним статусом.
Gate 3 (forbidden) — жоден заборонений claim не проходить.
Gate 8 (EIIC discipline) — екстраполяція не видається за спостережене.
