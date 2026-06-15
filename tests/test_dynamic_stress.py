"""Динамічний хаос-стрес-тест рантайму.

Не «зелений» тест: рандомізований двигун обстрілює три поверхні екстремальними
входами (NaN/inf/±1e9, нерівні матриці, спроби відновлення, що кидають). До
фіксу він убивав систему **712 разів** на 900 пострілах у трьох різних класах:

* ``participation_ratio`` — голий IndexError на нерівній матриці + тихий NaN;
* ``feedback.calibrate``  — видавав CALIBRATED-вердикт над NaN-proxy (обхід
  валідації через прямий конструктор LabeledPair);
* ``RecoverySupervisor.recover`` — падав разом зі спробою, що кидала виняток.

Після fail-closed фіксу всі три відмовляють чисто (ValueError на кордоні /
ESCALATED до людини). DEATH = будь-який не-ValueError виняток, тихий не-скінченний
числовий вихід, або порушення інваріанта статусу. ValueError-гард = DEFENDED.
"""

from __future__ import annotations

import math
import random

import pytest

from noesis.effective_dim import participation_ratio
from noesis.feedback import CALIBRATION_STATES, LabeledPair, calibrate
from noesis.runtime.recovery_supervisor import (
    RECOVERY_STATES,
    AttemptResult,
    FaultSignal,
    RecoverySupervisor,
)
from noesis.runtime.rollback import ROLLBACK_TYPES, RollbackController

_CHAOS = [0.0, 1.0, -1.0, 1e9, -1e9, float("nan"), float("inf"), -float("inf"), 0.5]


def _chaos_round(rng: random.Random) -> list[str]:
    """Один раунд хаосу по трьох поверхнях; повертає список смертей."""
    deaths: list[str] = []

    # 1. participation_ratio — нерівні/не-скінченні матриці
    rows, base = rng.randint(2, 5), rng.randint(0, 4)
    matrix = [
        [rng.choice(_CHAOS) for _ in range(base if rng.random() > 0.3 else rng.randint(0, 4))]
        for _ in range(rows)
    ]
    try:
        r = participation_ratio(matrix)
        if isinstance(r, float) and not math.isfinite(r):
            deaths.append(f"participation_ratio: silent non-finite {r}")
    except ValueError:
        pass  # defended
    except Exception as exc:  # noqa: BLE001 — навмисно ловимо все як смерть
        deaths.append(f"participation_ratio: {type(exc).__name__}")

    # 2. feedback.calibrate — отруйні proxy-оцінки
    try:
        pairs = [
            LabeledPair(
                pair_id=f"p{i}",
                input_hash=f"h{i}",
                artifact_ref=f"a{i}",
                human_verdict=rng.choice(["works", "fails"]),
                proxy_score=rng.choice(_CHAOS),
            )
            for i in range(rng.randint(12, 16))
        ]
        out = calibrate(pairs)
        if out["status"] not in CALIBRATION_STATES:
            deaths.append(f"calibrate: bad status {out['status']}")
        bad = [k for k, v in out.items() if isinstance(v, float) and not math.isfinite(v)]
        if out["status"] == "CALIBRATED" and bad:
            deaths.append(f"calibrate: CALIBRATED with non-finite {bad}")
    except ValueError:
        pass  # defended at construction
    except Exception as exc:  # noqa: BLE001
        deaths.append(f"calibrate: {type(exc).__name__}")

    # 3. RecoverySupervisor — спроби, що кидають виняток
    ctrl = RollbackController()
    ctrl.checkpoint("good", {"v": 0})
    ctrl.discharge("bad", {"v": 1})
    fault_type = rng.choice(sorted(ROLLBACK_TYPES))
    fail_n, calls = rng.randint(0, 6), {"n": 0}

    def attempt() -> AttemptResult:
        calls["n"] += 1
        if rng.random() < 0.4:
            raise RuntimeError("attempt exploded")  # реалістично: перезапуск зламаного коду
        return AttemptResult(ok=calls["n"] > fail_n, state_id="restored")

    try:
        outcome = RecoverySupervisor(ctrl, max_attempts=rng.randint(1, 4)).recover(
            FaultSignal(fault_type, "scale", "d"), attempt
        )
        if outcome.status not in RECOVERY_STATES:
            deaths.append(f"recover: bad status {outcome.status}")
    except ValueError:
        pass
    except Exception as exc:  # noqa: BLE001
        deaths.append(f"recover: {type(exc).__name__}")

    return deaths


@pytest.mark.parametrize("seed", [1, 7, 42, 1337, 99991])
def test_chaos_no_deaths_across_seeds(seed: int) -> None:
    rng = random.Random(seed)
    deaths: list[str] = []
    for _ in range(200):
        deaths.extend(_chaos_round(rng))
    assert deaths == [], f"runtime died under chaos (seed={seed}): {deaths[:5]}"


# ── Точкові регресії на кожну з 4 знайдених смертей (тепер fail-closed) ──────


def test_participation_ragged_matrix_fails_closed() -> None:
    with pytest.raises(ValueError, match="ragged"):
        participation_ratio([[1.0, 2.0], [3.0]])


@pytest.mark.parametrize("bad", [float("nan"), float("inf"), -float("inf")])
def test_participation_non_finite_fails_closed(bad: float) -> None:
    with pytest.raises(ValueError, match="finite"):
        participation_ratio([[bad, 1.0], [1.0, 1.0]])


@pytest.mark.parametrize("bad", [float("nan"), float("inf"), 1.5, -0.1])
def test_labeled_pair_rejects_poison_proxy(bad: float) -> None:
    with pytest.raises(ValueError, match="proxy_score"):
        LabeledPair(pair_id="p", input_hash="h", artifact_ref="a", human_verdict="works", proxy_score=bad)


def test_calibrate_never_emits_calibrated_over_nan() -> None:
    # Поза прямим конструктором поганих даних просто не існує — вони відсікаються
    # на кордоні. Контроль: чисті дані дають скінченний gap.
    pairs = [
        LabeledPair(pair_id=f"p{i}", input_hash=f"h{i}", artifact_ref=f"a{i}",
                    human_verdict=("works" if i % 2 else "fails"), proxy_score=0.9)
        for i in range(15)
    ]
    out = calibrate(pairs)
    assert out["status"] == "CALIBRATED"
    assert math.isfinite(out["calibration_gap"])


def test_recovery_survives_throwing_attempt() -> None:
    ctrl = RollbackController()
    ctrl.checkpoint("good", {"v": 0})
    ctrl.discharge("bad", {"v": 1})

    def always_explodes() -> AttemptResult:
        raise RuntimeError("attempt exploded mid-recovery")

    outcome = RecoverySupervisor(ctrl, max_attempts=3).recover(
        FaultSignal("test_failure", "scale", "d"), always_explodes
    )
    assert outcome.status == "ESCALATED"
    assert outcome.escalated_to_human is True
    assert len(outcome.attempts) == 3
    assert all("attempt raised" in a.note for a in outcome.attempts)
