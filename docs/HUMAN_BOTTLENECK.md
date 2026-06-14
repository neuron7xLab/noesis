# HUMAN_BOTTLENECK

Ступінь, до якого фінальний прогрес залежить від ручного IEV (`noesis/bottleneck_plan.py`).
benchmark (100): human_bottleneck_score_mean=0.5; вузьке місце — людська IEV-bandwidth,
не кількість вузлів.

Рекомендації: автоматизувати schema/forbidden/first-pass-compression; ЛИШИТИ людським
intent vector, moral responsibility, final acceptance, life-risk decisions. Видалити
редундантні теоретичні вузли (10/12 декоративні з v0.6). Ризик: auto-гейт стає хибним
авторитетом; verifier лише штампує.
