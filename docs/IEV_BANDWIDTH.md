# IEV_BANDWIDTH

Скільки якісних валідаційних/collapse-рішень контролер робить за задачу без втрати
когерентності наміру (`cme/iev_bandwidth.py`). Це СКАРБНИЙ ресурс кластера.

human_gate_capacity ≈ 3 (робоча память Miller&Cohen / McNab&Klingberg). Якщо
required_gate_decisions > capacity → стиснути перед людським review. Автоматизовні:
schema/forbidden/compression гейти. Не автоматизовні: high-risk фінальні гейти.
