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
import time
from pathlib import Path

import pytest

from formal.metrics import goodman_kruskal_gamma
from formal.verify import verify_reflection
from noesis.cli import main as cli_main
from noesis.effective_dim import participation_ratio
from noesis.evidence_integral import build_bundle, bundle_metrics, replay, validate_bundle
from noesis.feedback import CALIBRATION_STATES, LabeledPair, calibrate
from noesis.runtime.recovery_supervisor import (
    RECOVERY_STATES,
    AttemptResult,
    FaultSignal,
    RecoverySupervisor,
)
from noesis.runtime.rollback import ROLLBACK_TYPES, RollbackController
from noesis.verdict import render_verdict_md

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


# ── Round 2: evidence bundle / verdict / CLI surfaces ───────────────────────

_BUNDLE_CHAOS = [
    1, "x", None, [], {}, 5.0, float("nan"), float("inf"), True, [1, 2], [{}, {}],
    {"transition_index": "bad"}, {"verifier_index": "y"}, {"transition_index": 0}, "abc", -3,
]
_BUNDLE_KEYS = [
    "transitions", "artifacts", "decisions", "state_transition_hashes", "artifact_hashes",
    "verifier_outputs", "final_manifest_hash", "run_id", "gates_failed",
    "deterministic_modules", "pipeline_version", "overall_status", "gates_passed",
]


@pytest.mark.parametrize("seed", [3, 11, 2024, 55555])
def test_evidence_and_verdict_never_crash_under_chaos(seed: int) -> None:
    rng = random.Random(seed)
    for _ in range(500):
        bundle = {
            k: rng.choice(_BUNDLE_CHAOS)
            for k in rng.sample(_BUNDLE_KEYS, k=rng.randint(0, 7))
        }
        # None of these may raise on an arbitrary dict; validators report, not crash.
        problems = validate_bundle(bundle)
        assert isinstance(problems, list)
        metrics = bundle_metrics(bundle)
        assert all(math.isfinite(v) for v in metrics.values())
        assert isinstance(replay(bundle), bool)
        assert "VERDICT" in render_verdict_md(bundle)


def test_validate_bundle_reports_malformed_instead_of_crashing() -> None:
    problems = validate_bundle({"transitions": [1, 2], "artifacts": [7]})
    assert any("TRANSITION_MALFORMED" in p for p in problems)
    assert any("ARTIFACT_MALFORMED" in p for p in problems)


def test_replay_on_non_list_transitions_is_false_not_crash() -> None:
    assert replay({"transitions": 1}) is False
    assert replay({"transitions": "abc"}) is False


def test_render_verdict_md_degrades_on_partial_manifest() -> None:
    out = render_verdict_md({})
    assert "VERDICT" in out and "—" in out


@pytest.mark.parametrize(
    "argv",
    [
        ["pipeline", "/nonexistent/cme_stress_file.txt"],
        ["verdict", "/nonexistent/cme_stress_dir"],
        ["neuro", "/nonexistent/cme_stress_neuro"],
    ],
)
def test_cli_missing_path_fails_closed(argv: list[str], capsys: pytest.CaptureFixture[str]) -> None:
    assert cli_main(argv) == 1
    assert "file not found" in capsys.readouterr().err


def test_cli_corrupt_json_fails_closed(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    (tmp_path / "manifest.json").write_text("{not valid json", encoding="utf-8")
    assert cli_main(["verdict", str(tmp_path)]) == 1
    assert "invalid JSON" in capsys.readouterr().err


# ── Round 3: formal verifier must fail-closed on NaN, never PASS over poison ──


@pytest.mark.parametrize("bad", [float("nan"), float("inf"), -float("inf")])
def test_gamma_rejects_non_finite_confidence(bad: float) -> None:
    with pytest.raises(ValueError, match="скінченн"):
        goodman_kruskal_gamma([(bad, True), (2.0, False)])


@pytest.mark.parametrize("bad", [float("nan"), float("inf")])
def test_verify_reflection_fails_closed_on_nan(bad: float) -> None:
    # A NaN judgment silently produced a PASSING verdict — the worst place for
    # silent poison (a verifier). It must fail closed.
    verdict = verify_reflection([(bad, True), (2.0, False), (0.5, True)])
    assert verdict.passed is False


def test_verify_reflection_still_passes_clean_calibration() -> None:
    verdict = verify_reflection([(0.9, True), (0.2, False), (0.7, True)])
    assert verdict.passed is True


@pytest.mark.parametrize("seed", [13, 808, 31337])
def test_gamma_never_returns_non_finite(seed: int) -> None:
    rng = random.Random(seed)
    scores = [0.0, 0.5, 1.0, -1.0, 1e9, float("nan"), float("inf")]
    for _ in range(400):
        pairs = [(rng.choice(scores), rng.random() > 0.5) for _ in range(rng.randint(0, 6))]
        try:
            g = goodman_kruskal_gamma(pairs)
        except ValueError:
            continue  # defended (no informative pairs / non-finite)
        assert math.isfinite(g) and -1.0 <= g <= 1.0


# ── Round 4: extrapolated dynamic vulnerabilities (scale / portability / types) ──


def test_participation_ratio_scales_linearly_not_quadratically() -> None:
    # O(n²) was a DoS axis: n=1600 took ~1.2 s. The covariance form is O(n·d²);
    # 2000 vectors must finish well under a generous bound a quadratic would blow.
    rng = random.Random(0)
    vectors = [[rng.random() for _ in range(5)] for _ in range(2000)]
    start = time.perf_counter()
    result = participation_ratio(vectors)
    assert math.isfinite(result)
    assert time.perf_counter() - start < 0.5  # quadratic would need ~2-3 s here


def test_participation_ratio_covariance_form_matches_reference() -> None:
    # Lock the algebraic identity D_eff = tr(Σ)²/tr(Σ²): N identical vectors → 1.0,
    # N near-orthogonal → close to N−1 (centring removes one dof).
    assert participation_ratio([[1.0, 0.0], [1.0, 0.0], [1.0, 0.0]]) == 1.0
    ortho = participation_ratio([[1.0, 0.0, 0.0], [0.0, 1.0, 0.0], [0.0, 0.0, 1.0]])
    assert ortho == pytest.approx(2.0)


@pytest.mark.parametrize("bad", [float("inf"), float("nan"), -float("inf")])
def test_evidence_bundle_fails_closed_on_non_portable_floats(bad: float) -> None:
    # NaN/inf serialise to non-standard JSON tokens → unportable hash chain.
    with pytest.raises(ValueError, match="JSON-portable"):
        build_bundle(
            run_id="r", input_text="i",
            transitions=[{"i": 0, "state": bad}],
            artifacts=[], decisions=[], verifier_outputs=[], rollback_points=[],
        )


def test_replay_returns_false_on_non_portable_bundle() -> None:
    bad = {
        "transitions": [{"x": float("inf")}],
        "state_transition_hashes": ["deadbeef"],
        "final_manifest_hash": "x",
    }
    assert replay(bad) is False


def test_bool_is_not_a_valid_evidence_index() -> None:
    # isinstance(True, int) is True — a bool must not pass as a transition index.
    problems = validate_bundle(
        {
            "transitions": [{"verifier_index": True}],
            "verifier_outputs": [{}, {}],
            "state_transition_hashes": [],
            "artifact_hashes": [],
        }
    )
    assert any("VERIFIER_NOT_LINKED" in p for p in problems)
