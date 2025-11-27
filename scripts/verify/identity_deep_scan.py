#!/usr/bin/env python3
"""
Deep scan for all Anna Matrix derived identities (Layer 1 + Layer 2).

For each identity we collect:
- RPC status, balance, incoming/outgoing amounts, valid tick
- Owned and possessed assets (IPOs, contracts, etc.)
- Seed information for Layer 2 identities (body-derived seeds)

Outputs:
- outputs/derived/identity_deep_scan.json
- outputs/derived/identity_deep_scan.md
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

from qubipy.rpc import rpc_client

from scripts.core.seed_candidate_scan import (
 DIAGONAL_IDENTITIES,
 VORTEX_IDENTITIES,
 derive_identity_from_seed,
)

OUTPUT_DIR = Path("outputs/derived")
OUTPUT_JSON = OUTPUT_DIR / "identity_deep_scan.json"
OUTPUT_MD = OUTPUT_DIR / "identity_deep_scan.md"

IDENTITY_BODY_LENGTH = 56
SEED_LENGTH = 55

def seed_from_identity(identity: str) -> Optional[str]:
 """Return lowercase 55-char seed candidate from the 56-char body."""
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
 except Exception as exc: # pragma: no cover - network errors
 rpc_status = "error"
 notes.append(f"balance_error={exc}")

 def safe_call(method_name: str) -> List[Any]:
 try:
 method = getattr(rpc, method_name)
 return method(identity) or []
 except Exception as exc: # pragma: no cover - network errors
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
 """Return list of dictionaries describing both layers."""
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
 identities = build_identity_sets()
 rpc = rpc_client.QubiPy_RPC()
 latest_tick = rpc.get_latest_tick()

 records: List[DeepIdentityRecord] = []
 for entry in identities:
 record = query_identity(
 rpc=rpc,
 label=entry["label"],
 layer=entry["layer"],
 identity=entry["identity"],
 seed=entry["seed"],
 source=entry["source"],
 )
 records.append(record)

 write_outputs(records, latest_tick)
 print(f"[identity-deep-scan] ✓ json -> {OUTPUT_JSON}")
 print(f"[identity-deep-scan] ✓ markdown -> {OUTPUT_MD}")

if __name__ == "__main__":
 main()

