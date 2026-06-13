# PRECISION_WEIGHT_SCHEDULER

Коли довіряти/стискати/відхиляти/перенаправляти (`cme/precision_scheduler.py`).
Рішення: pass/fail/compress/reroute_{creator,critic,auditor,verifier}/human_review.
Кожен precision_weight має reason; жоден гладкий вихід не отримує pass автоматично;
novelty ≠ validity.
