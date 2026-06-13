# ENTROPY_EXPANSION_COLLAPSE

Обчислювальна ентропія = розмірність простору гіпотез до collapse у рішення/артефакт.
LLM-вузли НЕ зменшують ентропію — вони розгортають її ширше. IEV-гейт зменшує її
відбором/відкиданням/стисненням (`cme/entropy_budget.py`, `cme/collapse_controller.py`).

Collapse Controller вирішує, коли спинити розширення: enough_signal / artifact_ready /
entropy_too_high / human_review_required / further_expansion_needed. Collapse у рівно
один артефакт/дію, окрім human_review. Невизначеність зберігається, не ховається.
