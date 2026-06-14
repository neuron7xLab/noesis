# Внесок у Noesis

Noesis тримається на одному інваріанті: **тримати ноему ∧ гейтувати ентропію**.
Кожна зміна теж проходить через гейт — нижче його пороги.

## Налаштування
```bash
git clone https://github.com/neuron7xLab/noesis
cd noesis
make dev        # python -m pip install -e ".[dev,serve]"
make test       # 199 pytest
```

## Гейти якості (мусять бути зелені перед PR)
```bash
make lint       # ruff check .
make type       # mypy --strict (63 файли)
make test       # pytest + coverage --cov-fail-under=90
```
CI ([`.github/workflows/ci.yml`](.github/workflows/ci.yml)) ганяє ті самі три гейти
на Python 3.10–3.12. PR не мерджиться, поки всі три не зелені.

## Принцип чесності (обовʼязковий)
Жоден шар не виживає, якщо не впливає на **дію / валідацію / ризик / failure-mode /
стиснення / людську преференцію / benchmark-delta / якість evidence**. Якщо твоя
зміна додає шар — додай і вимірюваний внесок. Інакше шар позначається `decorative`
і пропонується до видалення. Жодних claim без чисел: див. [`docs/CLAIM_GOVERNANCE.md`](docs/CLAIM_GOVERNANCE.md).

## Контракти
- **Метод** має повний контракт: `definition · input · method · output · validation ·
  example · failure_modes` (див. `methods/`).
- **Нова CLI-команда** автоматично потрапляє під `tests/test_cli.py` — переконайся,
  що вона виконується на детермінованому backend без винятку.
- **Типи** — пиши анотованим з самого початку (`mypy --strict`, пакет має `py.typed`).

## Стиль коміту
Імперативний заголовок, тіло пояснює *чому*. Один логічний крок = один коміт.
