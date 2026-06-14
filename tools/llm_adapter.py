"""LLM adapter — реальний інтелект у трубі.

Два бекенди, бо вода має текти і з ключем, і без нього:
- "sdk": офіційний Anthropic SDK (потребує ANTHROPIC_API_KEY або ant-профіль).
- "cli": локальний `claude -p` (працює через наявну авторизацію Claude Code).
backend="auto": SDK якщо є ключ у середовищі, інакше CLI.

Канонічна модель — claude-opus-4-8.
"""

from __future__ import annotations

import os
import re
import shutil
import subprocess
from pathlib import Path

DEFAULT_MODEL = "claude-opus-4-8"
PROMPTS_DIR = Path(__file__).resolve().parent.parent / "prompts"

_FENCE_RE = re.compile(r"```(?:\w+)?\n(.*?)```", re.DOTALL)


def load_prompt(name: str) -> str:
    """Завантажує системний промпт; повертає перший fenced-блок або весь файл."""
    text = (PROMPTS_DIR / name).read_text(encoding="utf-8")
    match = _FENCE_RE.search(text)
    return match.group(1).strip() if match else text.strip()


def _complete_sdk(system: str, user: str, model: str) -> str:
    import anthropic

    client = anthropic.Anthropic()
    response = client.messages.create(
        model=model,
        max_tokens=2000,
        system=system,
        messages=[{"role": "user", "content": user}],
    )
    parts = [
        getattr(block, "text", "")
        for block in response.content
        if getattr(block, "type", None) == "text"
    ]
    return "".join(parts).strip()


def _complete_cli(system: str, user: str, model: str) -> str:
    binary = shutil.which("claude")
    if binary is None:
        raise RuntimeError("немає ANTHROPIC_API_KEY і не знайдено `claude` CLI")
    prompt = f"{system}\n\n---\n\n{user}"
    result = subprocess.run(
        [binary, "-p", prompt],
        capture_output=True,
        text=True,
        timeout=180,
        check=False,
    )
    if result.returncode != 0:
        raise RuntimeError(f"`claude` CLI помилка ({result.returncode}): {result.stderr.strip()}")
    return result.stdout.strip()


def complete(
    system: str,
    user: str,
    *,
    model: str = DEFAULT_MODEL,
    backend: str = "auto",
) -> str:
    """Повертає лише текст відповіді моделі."""
    if backend == "auto":
        backend = "sdk" if os.environ.get("ANTHROPIC_API_KEY") else "cli"
    if backend == "sdk":
        return _complete_sdk(system, user, model)
    if backend == "cli":
        return _complete_cli(system, user, model)
    raise ValueError(f"невідомий backend: {backend!r}")
