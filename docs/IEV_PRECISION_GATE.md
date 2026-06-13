# IEV_PRECISION_GATE

Intentional-Evidential-Validation gate. Рішення: pass | fail | compress | reroute |
human_review, з precision_weight∈[0,1] і обов'язковим поясненням (`cme/precision_gate.py`).

## Компоненти ваги
intent_match · evidence_strength · claim_safety · artifact_validity · (1−noise_risk).

## Правила
- **fail** — forbidden claim / немає артефакту.
- **human_review** — високі ставки (стосунки/медицина/право/фінанси/ідентичність).
- **compress** — корисний сигнал є, але noise_risk>0.6.
- **reroute** — intent_match<0.7 → critic/auditor.
- **pass** — намір збігається, claim чистий, артефакт валідний, дія ясна.

Жодного авто-pass за «гладкий» вихід. Бенчмарк (100): рішення = `compress` 100% —
сирий вихід графа завжди занадто шумний, потребує стиснення перед прийняттям.
