# Changelog

Формат — [Keep a Changelog](https://keepachangelog.com/), версіонування —
[SemVer](https://semver.org/). Чесні вердикти по кожному шару — у
[`VERDICT.md`](VERDICT.md) та [`docs/VERDICT_V6.md`](docs/VERDICT_V6.md).

## [0.8.0] — 2026-06-14

### Змінено
- **Бренд та пакет.** Проєкт перейменовано на **Noesis**; importable-пакет —
  `noesis`, console-команда — `noesis` (раніше `cme`). `import noesis` працює,
  додано `noesis --version`.
- Назва тепер іменує ноетичний **акт** (νόησις), а гейт θ — його внутрішній
  момент; етимологія в [`docs/NAME.md`](docs/NAME.md).

### Додано
- `py.typed` — пакет позначено як типізований (PEP 561).
- Контрактний smoke-тест по **всіх** підкомандах CLI (`tests/test_cli.py`):
  список команд береться з парсера, тож нові команди покриваються автоматично.
- Coverage-gate `--cov-fail-under=90` у CI та локальному прогоні.

### Виправлено
- `mypy --strict` падав на опціональному `anthropic` (extra `[llm]`) — додано
  `ignore_missing_imports` override; гейт зелений і без LLM-залежності.
- Прибрано дубль `roadmap.md`, узгоджено версію в `__init__` та `pyproject`.

### Метрики
- 199 pytest · покриття 93% · `mypy --strict` (63 файли) · `ruff` — усе зелене.

## [0.1–0.8] — еволюція ядра
- **0.1–0.2** — 7 brain-inspired методів + детермінована підлога + LLM-підсилення.
- **0.3** — цивілізаційний рушій: 30 категорій → reality maps → synthesis.
- **0.4 + EIIC** — 12 нейрокогнітивних лінз (проксі) + термінальний вектор.
- **0.5** — 10 валідаційних гейтів + claim governance + 100-input benchmark.
- **0.6** — причинні категорії, адаптивне стиснення, theory contribution.
- **0.7** — розподілений когнітивний граф + IEV precision-gate + dimensionality.
- **0.8** — latency-aware IEV optimization: cluster_quality, node-scaling крива.
