#!/usr/bin/env python3
"""
Query the recent transaction history for all Layer-2 (seed-derived) identities.

For each identity, we collect:
 - Latest balance snapshot (for reference)
 - Recent transfer transactions per tick (incoming/outgoing)
 - Detailed transaction objects

Results:
 - outputs/derived/transaction_history.json
 - outputs/derived/transaction_history.md
"""

from __future__ import annotations

import json
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any, Dict, List, Optional

from qubipy.rpc import rpc_client

from scripts.core.seed_candidate_scan import (
 DIAGONAL_IDENTITIES,
 VORTEX_IDENTITIES,
 derive_identity_from_seed,
)

OUTPUT_DIR = Path("outputs/derived")
OUTPUT_JSON = OUTPUT_DIR / "transaction_history.json"
OUTPUT_MD = OUTPUT_DIR / "transaction_history.md"

@dataclass
class TxRecord:
 tick: int
 transaction_id: str
 direction: str # "incoming" or "outgoing"
 raw: Dict[str, Any]

@dataclass
class IdentityHistory:
 label: str
 identity: str
 seed: str
 latest_balance: Optional[str]
 latest_valid_tick: Optional[int]
 transactions: List[TxRecord]

def get_layer2_identities() -> List[Dict[str, str]]:
 """Return list with label, seed, and derived identity for all eight seeds."""
 layer2_list: List[Dict[str, str]] = []

 def append_entries(prefix: str, identities: List[str]) -> None:
 for idx, identity in enumerate(identities, 1):
 body = identity[:56]
 seed = body.lower()[:55]
 derived_identity = derive_identity_from_seed(seed)
 if derived_identity:
 layer2_list.append(
 {
 "label": f"{prefix} #{idx} • Layer-2",
 "seed": seed,
 "identity": derived_identity,
 }
 )

 append_entries("Diagonal", DIAGONAL_IDENTITIES)
 append_entries("Vortex", VORTEX_IDENTITIES)
 return layer2_list

def fetch_transactions(rpc, identity: str, max_ticks: int = 100) -> List[TxRecord]:
 """Fetch transfer transactions for the provided identity."""
 records: List[TxRecord] = []
 try:
 current_tick = rpc.get_latest_tick()
 except Exception:
 current_tick = None

 if current_tick is None:
 return records

 tick_range = range(max(0, current_tick - max_ticks), current_tick + 1)

 for tick in tick_range:
 try:
 txs = rpc.get_transfer_transactions_per_tick(tick)
 except Exception:
 continue

 if not txs:
 continue

 for tx in txs:
 # transaction format: { "transactionId": ..., "from": ..., "to": ..., ... }
 sender = tx.get("from")
 receiver = tx.get("to")
 direction = None
 if sender == identity:
 direction = "outgoing"
 elif receiver == identity:
 direction = "incoming"
 else:
 continue

 records.append(
 TxRecord(
 tick=tick,
 transaction_id=tx.get("transactionId", ""),
 direction=direction,
 raw=tx,
 )
 )
 return records

def gather_history() -> List[IdentityHistory]:
 rpc = rpc_client.QubiPy_RPC()
 layer2 = get_layer2_identities()
 histories: List[IdentityHistory] = []

 for entry in layer2:
 identity = entry["identity"]
 seed = entry["seed"]
 label = entry["label"]

 latest_balance = None
 valid_tick = None
 try:
 balance_data = rpc.get_balance(identity)
 if balance_data:
 latest_balance = balance_data.get("balance", "0")
 valid_tick = balance_data.get("validForTick")
 except Exception:
 pass

 transactions = fetch_transactions(rpc, identity, max_ticks=200)
 histories.append(
 IdentityHistory(
 label=label,
 identity=identity,
 seed=seed,
 latest_balance=latest_balance,
 latest_valid_tick=valid_tick,
 transactions=transactions,
 )
 )

 return histories

def write_reports(histories: List[IdentityHistory]) -> None:
 OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
 payload = [asdict(history) for history in histories]
 OUTPUT_JSON.write_text(json.dumps(payload, indent=2), encoding="utf-8")

 lines = [
 "# Layer-2 Transaction History",
 "",
 f"- Identities scanned: {len(histories)}",
 "",
 "| Label | Balance | Valid Tick | Transactions | Latest Dir | Latest Tick |",
 "| --- | --- | --- | --- | --- | --- |",
 ]

 for history in histories:
 tx_count = len(history.transactions)
 if tx_count:
 latest_tx = history.transactions[-1]
 latest_dir = latest_tx.direction
 latest_tick = latest_tx.tick
 else:
 latest_dir = "–"
 latest_tick = "–"

 lines.append(
 f"| {history.label} | {history.latest_balance or '0'} | {history.latest_valid_tick or '–'} | "
 f"{tx_count} | {latest_dir} | {latest_tick} |"
 )

 lines.extend(["", "## Detailed Transactions", ""])
 for history in histories:
 lines.append(f"### {history.label}")
 lines.append("")
 lines.append(f"- Identity: `{history.identity}`")
 lines.append(f"- Seed: `{history.seed}`")
 lines.append(f"- Balance: {history.latest_balance or '0'}")
 lines.append(f"- Valid tick: {history.latest_valid_tick or '–'}")
 lines.append("")
 if not history.transactions:
 lines.append("_No transactions in the scanned tick range._")
 lines.append("")
 lines.append("")
 continue

 lines.append("| Tick | Direction | Transaction ID | Raw |")
 lines.append("| --- | --- | --- | --- |")
 for tx in history.transactions:
 lines.append(
 f"| {tx.tick} | {tx.direction} | `{tx.transaction_id}` | `{json.dumps(tx.raw)}` |"
 )
 lines.append("")
 lines.append("")

 OUTPUT_MD.write_text("\n".join(lines), encoding="utf-8")

def main() -> None:
 histories = gather_history()
 write_reports(histories)
 print(f"[tx-history] ✓ json -> {OUTPUT_JSON}")
 print(f"[tx-history] ✓ markdown -> {OUTPUT_MD}")

if __name__ == "__main__":
 main()

