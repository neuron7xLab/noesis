"""Наскрізна труба: сирий намір → дзеркало наміру → артефакт → перевірка.

Це доказ, що труба несе воду: пропускає сире повідомлення крізь два промпти
(finalizer_mirror → artifact_builder) і прогоняє результати крізь детерміновані
валідатори (finalizer100 + artifact_checker).
"""

from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass, field

from tools.artifact_checker import REQUIRED_SECTIONS, check_artifact
from tools.finalizer100 import validate_finalizer
from tools.llm_adapter import complete, load_prompt


def parse_sections(text: str) -> dict[str, str]:
    """Парсить вивід artifact_builder (7 рядків `key: value`) у dict."""
    out: dict[str, str] = {}
    for line in text.splitlines():
        stripped = line.strip()
        for section in REQUIRED_SECTIONS:
            prefix = f"{section}:"
            if stripped.lower().startswith(prefix):
                out[section] = stripped[len(prefix) :].strip()
    return out


@dataclass
class PipelineResult:
    raw_intent: str
    mirror: str
    mirror_words: int
    mirror_ok: bool
    artifact_text: str
    artifact_problems: list[str] = field(default_factory=list)

    @property
    def artifact_ok(self) -> bool:
        return not self.artifact_problems


def run_pipeline(raw_intent: str, *, backend: str = "auto") -> PipelineResult:
    mirror = complete(load_prompt("finalizer_mirror.md"), raw_intent, backend=backend)
    finalizer = validate_finalizer(mirror)

    artifact_text = complete(load_prompt("artifact_builder.md"), mirror, backend=backend)
    artifact = parse_sections(artifact_text)
    problems = check_artifact(artifact)

    return PipelineResult(
        raw_intent=raw_intent,
        mirror=mirror,
        mirror_words=finalizer.word_count,
        mirror_ok=finalizer.ok,
        artifact_text=artifact_text,
        artifact_problems=problems,
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="cmm-pipeline",
        description="Наскрізна труба: сирий намір → дзеркало → артефакт → перевірка.",
    )
    parser.add_argument("intent", nargs="?", help="сирий намір; stdin якщо не вказано")
    parser.add_argument("--backend", default="auto", choices=["auto", "sdk", "cli"])
    args = parser.parse_args(argv)

    raw_intent = args.intent if args.intent else sys.stdin.read().strip()
    if not raw_intent:
        parser.error("порожній намір")

    result = run_pipeline(raw_intent, backend=args.backend)

    print("=" * 60)
    print("СИРИЙ НАМІР:\n" + result.raw_intent)
    print("=" * 60)
    print(f"ДЗЕРКАЛО НАМІРУ ({result.mirror_words} слів, finalizer={'OK' if result.mirror_ok else 'FAIL'}):")
    print(result.mirror)
    print("=" * 60)
    status = "OK" if result.artifact_ok else "FAIL"
    print(f"АРТЕФАКТ (artifact_checker={status}):")
    print(result.artifact_text)
    if result.artifact_problems:
        print("\nпроблеми артефакту: " + "; ".join(result.artifact_problems))
    print("=" * 60)
    # Труба «несе воду», якщо обидва кінці дали непорожній структурований вихід.
    carried = bool(result.mirror) and result.artifact_ok
    print(f"ТРУБА НЕСЕ ВОДУ: {carried}")
    return 0 if carried else 1


if __name__ == "__main__":
    raise SystemExit(main())
