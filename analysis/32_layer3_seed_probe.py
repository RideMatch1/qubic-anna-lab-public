#!/usr/bin/env python3
"""
Layer-3 Seed Probe
------------------

Starting from the four diagonal and four vortex identities (Layer 1),
derive Layer 2 (by interpreting the 56-letter body as a 55-letter seed)
and continue the derivation recursively to search for Layer 3 + N.

For each identity in the chain we log:
- parent label
- seed that produced it (if any)
- next seed candidate (if any)
- RPC status / balance / valid tick
- tick delta to the parent (if available)

Outputs:
  - outputs/derived/layer3_seed_probe.json
  - outputs/derived/layer3_seed_probe.md
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import List, Optional

from qubipy.rpc import rpc_client

from scripts.core.identity_constants import DIAGONAL_IDENTITIES, VORTEX_IDENTITIES
from scripts.core.seed_candidate_scan import derive_identity_from_seed

OUTPUT_DIR = Path("outputs/derived")
OUTPUT_JSON = OUTPUT_DIR / "layer3_seed_probe.json"
OUTPUT_MD = OUTPUT_DIR / "layer3_seed_probe.md"

from analysis.utils.identity_tools import IDENTITY_BODY_LENGTH
from scripts.core.identity_constants import SEED_LENGTH

IDENTITY_BODY_LEN = IDENTITY_BODY_LENGTH
SEED_LEN = SEED_LENGTH

def seed_from_identity(identity: str) -> Optional[str]:
    """Return 55-letter lowercase seed candidate from a 60-char identity."""
    if len(identity) < IDENTITY_BODY_LENGTH:
        return None
    body = identity[:IDENTITY_BODY_LENGTH]
    candidate = body.lower()[:SEED_LENGTH]
    if len(candidate) != SEED_LENGTH or not candidate.isalpha():
        return None
    return candidate

@dataclass
class ChainNode:
    label: str
    level: int
    identity: str
    parent_label: Optional[str]
    seed_from_parent: Optional[str]
    next_seed_candidate: Optional[str]
    rpc_status: Optional[str]
    balance: Optional[str]
    valid_tick: Optional[int]
    tick_delta_from_parent: Optional[int]

def rpc_snapshot(rpc, identity: str) -> tuple[Optional[str], Optional[str], Optional[int]]:
    status = None
    balance = None
    tick = None
    try:
        data = rpc.get_balance(identity)
        if data:
            status = "exists"
            balance = data.get("balance", "0")
            tick = data.get("validForTick")
        else:
            status = "not_found"
    except Exception as exc:  # pragma: no cover - network issues
        status = "error"
        balance = str(exc)
    return status, balance, tick

def build_chain(rpc, label_prefix: str, base_identity: str) -> List[ChainNode]:
    chain: List[ChainNode] = []
    current_identity = base_identity
    parent_label = None
    parent_tick = None
    parent_seed = None
    level = 1

    while True:
        status, balance, tick = rpc_snapshot(rpc, current_identity)
        seed_candidate = seed_from_identity(current_identity)
        tick_delta = None
        if parent_tick is not None and tick is not None:
            tick_delta = tick - parent_tick

        label = f"{label_prefix} L{level}"
        chain.append(
            ChainNode(
                label=label,
                level=level,
                identity=current_identity,
                parent_label=parent_label,
                seed_from_parent=parent_seed,
                next_seed_candidate=seed_candidate,
                rpc_status=status,
                balance=balance,
                valid_tick=tick,
                tick_delta_from_parent=tick_delta,
            )
        )

        if not seed_candidate:
            break
        next_identity = derive_identity_from_seed(seed_candidate)
        if not next_identity or next_identity == current_identity:
            break

        parent_label = label
        parent_tick = tick
        parent_seed = seed_candidate
        current_identity = next_identity
        level += 1

    return chain

def main() -> None:
    rpc = rpc_client.QubiPy_RPC()
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    all_chains: List[ChainNode] = []

    for idx, identity in enumerate(DIAGONAL_IDENTITIES, 1):
        all_chains.extend(build_chain(rpc, f"Diagonal #{idx}", identity))

    for idx, identity in enumerate(VORTEX_IDENTITIES, 1):
        all_chains.extend(build_chain(rpc, f"Vortex #{idx}", identity))

    OUTPUT_JSON.write_text(json.dumps([asdict(node) for node in all_chains], indent=2), encoding="utf-8")

    lines = [
        "# Layer-3 Seed Probe",
        "",
        f"- Total nodes recorded: {len(all_chains)}",
        "",
        "| Label | Level | Parent | RPC Status | Balance | Tick | Δ Tick | Next Seed Candidate |",
        "| --- | --- | --- | --- | --- | --- | --- | --- |",
    ]

    for node in all_chains:
        lines.append(
            f"| {node.label} | {node.level} | {node.parent_label or '–'} | {node.rpc_status or 'n/a'} | "
            f"{node.balance or 'n/a'} | {node.valid_tick or '–'} | {node.tick_delta_from_parent or '–'} | "
            f"`{node.next_seed_candidate or 'n/a'}` |"
        )

    lines.extend(["", "## Chain Details", ""])

    for node in all_chains:
        lines.extend(
            [
                f"### {node.label}",
                "",
                f"- Identity: `{node.identity}`",
                f"- Parent: {node.parent_label or 'None'}",
                f"- Seed used (from parent): `{node.seed_from_parent or 'n/a'}`",
                f"- Next seed candidate: `{node.next_seed_candidate or 'n/a'}`",
                f"- RPC status: {node.rpc_status or 'n/a'}",
                f"- Balance: {node.balance or 'n/a'}",
                f"- Valid tick: {node.valid_tick or 'n/a'}",
                f"- Tick delta from parent: {node.tick_delta_from_parent or 'n/a'}",
                "",
            ]
        )

    OUTPUT_MD.write_text("\n".join(lines), encoding="utf-8")
    print(f"[layer3-seed-probe] ✓ json -> {OUTPUT_JSON}")
    print(f"[layer3-seed-probe] ✓ markdown -> {OUTPUT_MD}")

if __name__ == "__main__":
    main()

