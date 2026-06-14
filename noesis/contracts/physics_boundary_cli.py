"""CLI for the physics-boundary contract gate.

    python -m noesis.contracts.physics_boundary_cli validate

Also wired into the single Noesis CLI as ``noesis physics-boundary validate``.
Exits 0 only when the contract PASSES; exits 1 on any FAIL (unblocked forbidden
claim, schema failure, absent trajectory fields, missing Role 3 handoff, ...).
"""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

from noesis.contracts.physics_boundary_validator import contract_path, repo_root, write_contract


def _summary(contract: dict[str, Any], root: Path) -> str:
    status = contract["contract_status"]
    hard = contract.get("hard_failures", [])
    lines = [
        f"PHYSICS CONTRACT: {status}",
        f"score: {contract.get('score', 0)}/100",
        f"state variables checked: {len(contract['state_variables_checked'])}",
        f"operators checked: {len(contract['operators_checked'])}",
        f"invariants checked: {len(contract['invariants_checked'])}",
        f"trajectory checked: {contract['trajectory_checked'].get('status', 'UNKNOWN')}",
        f"metrics checked: {len(contract['metrics_checked'])}",
        f"forbidden claims checked: {len(contract['claim_status_checked'])}",
        f"first failing gate: {hard[0] if hard else 'none'}",
        f"report: {contract_path(root)}",
    ]
    return "\n".join(lines)


def run(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="noesis-physics-boundary",
        description="Validate the physics-boundary contract for the repository.",
    )
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("validate", help="enforce the physics-boundary contract")
    args = parser.parse_args(argv)

    if args.command == "validate":
        root = repo_root()
        contract = write_contract(root)
        print(_summary(contract, root))
        return 0 if contract["contract_status"] == "PASS" else 1
    return 1  # pragma: no cover - argparse 'required=True' forbids reaching here


def main(argv: list[str] | None = None) -> int:
    return run(argv)


if __name__ == "__main__":
    raise SystemExit(main())
