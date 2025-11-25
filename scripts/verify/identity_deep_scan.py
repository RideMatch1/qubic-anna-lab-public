#!/usr/bin/env python3
"""
Deep scan for all Anna Matrix derived identities (Layer 1 + Layer 2).

For each identity we collect:
- RPC status, balance, incoming/outgoing amounts, valid tick
- Owned and possessed assets (IPOs, contracts, etc.)
- Seed information for Layer 2 identities (body-derived seeds)

This scans both the original 8 identities from the matrix (Layer-1) and the
8 identities derived from their seeds (Layer-2). That's 16 identities total.

Usage:
    python scripts/verify/identity_deep_scan.py
    
    Or with Docker:
    docker run --rm -v "$PWD":/workspace -w /workspace qubic-proof python scripts/verify/identity_deep_scan.py

Outputs:
- outputs/derived/identity_deep_scan.json  # full data dump
- outputs/derived/identity_deep_scan.md     # human-readable table
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

from qubipy.rpc import rpc_client

from scripts.core.identity_constants import DIAGONAL_IDENTITIES, VORTEX_IDENTITIES
from scripts.core.seed_candidate_scan import derive_identity_from_seed

OUTPUT_DIR = Path("outputs/derived")
OUTPUT_JSON = OUTPUT_DIR / "identity_deep_scan.json"
OUTPUT_MD = OUTPUT_DIR / "identity_deep_scan.md"

import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(project_root))

from analysis.utils.identity_tools import IDENTITY_BODY_LENGTH
from scripts.core.identity_constants import SEED_LENGTH

def seed_from_identity(identity: str) -> Optional[str]:
    """Return lowercase seed candidate from the identity body.
    
    Takes the first IDENTITY_BODY_LENGTH chars (the body), lowercases it, then takes first SEED_LENGTH.
    That's the formula: identity.lower()[:SEED_LENGTH] = seed
    """
    body = identity[:IDENTITY_BODY_LENGTH]
    if len(body) < SEED_LENGTH:
        return None
    candidate = body.lower()[:SEED_LENGTH]
    return candidate if len(candidate) == SEED_LENGTH else None

@dataclass
class DeepIdentityRecord:
    label: str
    layer: str
    source: str
    identity: str
    seed: Optional[str]
    rpc_status: Optional[str]
    balance: Optional[str]
    incoming_amount: Optional[str]
    outgoing_amount: Optional[str]
    valid_for_tick: Optional[int]
    owned_assets: List[Any]
    possessed_assets: List[Any]
    notes: str = ""

def query_identity(rpc, label: str, layer: str, identity: str, seed: Optional[str], source: str) -> DeepIdentityRecord:
    rpc_status = None
    balance = None
    incoming = None
    outgoing = None
    valid_tick = None
    notes: List[str] = []

    try:
        balance_data = rpc.get_balance(identity)
        if balance_data:
            rpc_status = "exists"
            balance = balance_data.get("balance", "0")
            incoming = balance_data.get("incomingAmount", "0")
            outgoing = balance_data.get("outgoingAmount", "0")
            valid_tick = balance_data.get("validForTick")
        else:
            rpc_status = "not_found"
    except Exception as exc:  # pragma: no cover - network errors
        rpc_status = "error"
        notes.append(f"balance_error={exc}")

    def safe_call(method_name: str) -> List[Any]:
        try:
            method = getattr(rpc, method_name)
            return method(identity) or []
        except Exception as exc:  # pragma: no cover - network errors
            notes.append(f"{method_name}_error={exc}")
            return []

    owned_assets = safe_call("get_owned_assets")
    possessed_assets = safe_call("get_possessed_assets")

    return DeepIdentityRecord(
        label=label,
        layer=layer,
        source=source,
        identity=identity,
        seed=seed,
        rpc_status=rpc_status,
        balance=balance,
        incoming_amount=incoming,
        outgoing_amount=outgoing,
        valid_for_tick=valid_tick,
        owned_assets=owned_assets,
        possessed_assets=possessed_assets,
        notes="; ".join(notes),
    )

def build_identity_sets() -> List[Dict[str, Any]]:
    """Build list of all identities to scan (Layer-1 + Layer-2).
    
    For each Layer-1 identity, we derive its seed (first 55 chars of body, lowercased)
    and then derive the Layer-2 identity from that seed.
    """
    identities: List[Dict[str, Any]] = []

    for idx, identity in enumerate(DIAGONAL_IDENTITIES, 1):
        identities.append(
            {
                "label": f"Diagonal #{idx}",
                "layer": "layer1",
                "source": "matrix-diagonal",
                "identity": identity,
                "seed": None,
            }
        )
        seed = seed_from_identity(identity)
        if seed:
            derived = derive_identity_from_seed(seed)
            if derived:
                identities.append(
                    {
                        "label": f"Diagonal #{idx} • Seed-Derived",
                        "layer": "layer2",
                        "source": "seed-derivation",
                        "identity": derived,
                        "seed": seed,
                    }
                )

    for idx, identity in enumerate(VORTEX_IDENTITIES, 1):
        identities.append(
            {
                "label": f"Vortex #{idx}",
                "layer": "layer1",
                "source": "matrix-vortex",
                "identity": identity,
                "seed": None,
            }
        )
        seed = seed_from_identity(identity)
        if seed:
            derived = derive_identity_from_seed(seed)
            if derived:
                identities.append(
                    {
                        "label": f"Vortex #{idx} • Seed-Derived",
                        "layer": "layer2",
                        "source": "seed-derivation",
                        "identity": derived,
                        "seed": seed,
                    }
                )

    return identities

def write_outputs(records: List[DeepIdentityRecord], latest_tick: Any) -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    payload = {
        "latest_tick": latest_tick,
        "total_identities": len(records),
        "records": [asdict(record) for record in records],
    }
    OUTPUT_JSON.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    lines = [
        "# Identity Deep Scan",
        "",
        f"- Latest tick: `{latest_tick}`",
        f"- Total identities scanned: {len(records)}",
        "",
        "| Label | Layer | Balance | Valid Tick | Owned Assets | Possessed Assets | Notes |",
        "| --- | --- | --- | --- | --- | --- | --- |",
    ]
    for record in records:
        balance = record.balance or "0"
        vtick = record.valid_for_tick or "–"
        owned = len(record.owned_assets)
        possessed = len(record.possessed_assets)
        note = record.notes or ""
        lines.append(
            f"| {record.label} | {record.layer} | {balance} | {vtick} | {owned} | {possessed} | {note} |"
        )

    lines.extend(
        [
            "",
            "## Seed Inventory",
            "",
            "| Layer-2 Label | Seed | Identity |",
            "| --- | --- | --- |",
        ]
    )

    for record in records:
        if record.layer != "layer2":
            continue
        seed = record.seed or "n/a"
        lines.append(f"| {record.label} | `{seed}` | `{record.identity}` |")

    OUTPUT_MD.write_text("\n".join(lines), encoding="utf-8")

def main() -> None:
    """Main scanning routine."""
    print("[identity-deep-scan] Building identity sets (Layer-1 + Layer-2)...")
    identities = build_identity_sets()
    print(f"[identity-deep-scan] Found {len(identities)} identities to scan")
    
    print("[identity-deep-scan] Connecting to Qubic RPC...")
    rpc = rpc_client.QubiPy_RPC()
    latest_tick = rpc.get_latest_tick()
    print(f"[identity-deep-scan] Latest tick: {latest_tick}")

    print("[identity-deep-scan] Querying identities...")
    records: List[DeepIdentityRecord] = []
    for i, entry in enumerate(identities, 1):
        print(f"  [{i}/{len(identities)}] {entry['label']}...", end="\r")
        record = query_identity(
            rpc=rpc,
            label=entry["label"],
            layer=entry["layer"],
            identity=entry["identity"],
            seed=entry["seed"],
            source=entry["source"],
        )
        records.append(record)
    print()  # newline after progress

    write_outputs(records, latest_tick)
    print(f"[identity-deep-scan] ✓ json -> {OUTPUT_JSON}")
    print(f"[identity-deep-scan] ✓ markdown -> {OUTPUT_MD}")
    
    # Quick summary
    exists = sum(1 for r in records if r.rpc_status == "exists")
    print(f"[identity-deep-scan] Summary: {exists}/{len(records)} identities exist on-chain")

if __name__ == "__main__":
    main()

