#!/usr/bin/env python3
"""
Continuous monitoring for assets on Layer-2 identities after contract trigger.

Checks every N seconds for:
- New assets (owned/possessed)
- Balance changes
- Transaction confirmations
- Contract responses

Run this after executing contract_trigger.py to watch for the Genesis Token.
"""

from __future__ import annotations

import json
import time
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from qubipy.rpc import rpc_client

CONTRACT_ID = "POCCZYCKTRQGHFIPWGSBLJTEQFDDVVBMNUHNCKMRACBGQOPBLURNRCBAFOBD"

SEED_TABLE = [
 {
 "label": "Diagonal #1 • Layer-2",
 "seed": "aqiosqqmacybpqxqsjniuaylmxxiwqoxqmeqyxbbtbonsjjrcwpxxdd",
 "identity": "CYTORJWZCJFCYXAHJPLPPCWPVOXTDZBWQYVWANQDYQCCIORJTVMPBIXBKIVP",
 "payload": 1,
 },
 {
 "label": "Diagonal #2 • Layer-2",
 "seed": "gwuxommmmfmtbwfzsngmukwbiltxqdknmmmnypeftamronjmablhtrr",
 "identity": "FPEXLMCOGJNYAAELTBSEDHAZCCNAGXJRPRFNBEXUKPDHFTVAHETKPANQCMLM",
 "payload": 2,
 },
 {
 "label": "Diagonal #3 • Layer-2",
 "seed": "acgjgqqyilbpxdrborfgwfzbbbnlqnghddelvlxxxlbnnnfbllpbnnn",
 "identity": "ABCXUAPWHTDRJDASQEZSNCDAMXNJAXDTNESWQLNWPZBBUXDGNJLGYXETNGHN",
 "payload": 3,
 },
 {
 "label": "Diagonal #4 • Layer-2",
 "seed": "giuvfgawcbbffkvbmfjeslhbbfbfwzwnnxcbqbbjrvfbnvjltjbbbht",
 "identity": "AGTIRJYQVZXUEFAUCPEBEYHDAFXZFMFOARDSUKLHHBETDIVPWVZMOORUOXSD",
 "payload": 4,
 },
 {
 "label": "Vortex #1 • Layer-2",
 "seed": "uufeemuubiyxyxduxzcfbihabaysacqswsgabobknxbzciclyokobml",
 "identity": "GNMLDHIPZJHJDNCCCRFHVDDPEIHJEWOPVVAXQRFIBYDZBNDHTELZIANUDAWB",
 "payload": 5,
 },
 {
 "label": "Vortex #2 • Layer-2",
 "seed": "hjbrfbhtbzjlvrbxtdrforbwnacahaqmsbunbonhtrhnjkxkknkhwcb",
 "identity": "ADVDNZIGNSCXAODGDMEXMKICVHFOHBROQQMVZOGAMVASHQURDBPDNJRJJQRM",
 "payload": 6,
 },
 {
 "label": "Vortex #3 • Layer-2",
 "seed": "jklmnoipdqorwsictwwuiyvmofiqcqsykmkacmokqyccmcogocqcscw",
 "identity": "HFVFDNEHUVRRBIESYPSSRPNJSVVSDBIPNAXAHIKISLAKYZFKMWNJXVVUEUQJ",
 "payload": 7,
 },
 {
 "label": "Vortex #4 • Layer-2",
 "seed": "xyzqaubquuqbqbyqayeiyaqymmemqqqmmqsqeqazsmogwoxkirmjxmc",
 "identity": "BIARJWYAYURJYJBXXEDMQOKGSJXBFNWCDSHXZILITIDHCMJYUMPPXQZQAXNR",
 "payload": 8,
 },
]

OUTPUT_DIR = Path("outputs/derived")
OUTPUT_JSON = OUTPUT_DIR / "asset_monitor.json"
OUTPUT_LOG = OUTPUT_DIR / "asset_monitor.log"

CHECK_INTERVAL = 30
MAX_CHECKS = 120

@dataclass
class AssetSnapshot:
 timestamp: str
 tick: int
 label: str
 identity: str
 balance: str
 owned_assets: List[Dict[str, Any]]
 possessed_assets: List[Dict[str, Any]]
 owned_count: int
 possessed_count: int
 notes: str = ""

 def to_dict(self) -> dict:
 return asdict(self)

def scan_identity(rpc: rpc_client.QubiPy_RPC, entry: Dict[str, Any]) -> AssetSnapshot:
 label = entry["label"]
 identity = entry["identity"]
 
 try:
 latest_tick = rpc.get_latest_tick()
 balance_data = rpc.get_balance(identity)
 balance = balance_data.get("balance", "0") if balance_data else "0"
 
 owned_assets = rpc.get_owned_assets(identity)
 owned_list = owned_assets.get("assets", []) if owned_assets else []
 
 possessed_assets = rpc.get_possessed_assets(identity)
 possessed_list = possessed_assets.get("assets", []) if possessed_assets else []
 
 notes = ""
 if owned_list:
 notes += f"OWNED: {len(owned_list)} assets. "
 if possessed_list:
 notes += f"POSSESSED: {len(possessed_list)} assets. "
 
 return AssetSnapshot(
 timestamp=datetime.utcnow().isoformat() + "Z",
 tick=latest_tick,
 label=label,
 identity=identity,
 balance=balance,
 owned_assets=owned_list,
 possessed_assets=possessed_list,
 owned_count=len(owned_list),
 possessed_count=len(possessed_list),
 notes=notes.strip(),
 )
 except Exception as e:
 return AssetSnapshot(
 timestamp=datetime.utcnow().isoformat() + "Z",
 tick=0,
 label=label,
 identity=identity,
 balance="ERROR",
 owned_assets=[],
 possessed_assets=[],
 owned_count=0,
 possessed_count=0,
 notes=f"RPC Error: {e}",
 )

def compare_snapshots(old: Optional[AssetSnapshot], new: AssetSnapshot) -> List[str]:
 changes = []
 if old is None:
 return ["Initial scan"]
 
 if old.balance != new.balance:
 changes.append(f"Balance: {old.balance} → {new.balance}")
 
 if old.owned_count != new.owned_count:
 changes.append(f"Owned assets: {old.owned_count} → {new.owned_count}")
 if new.owned_assets:
 changes.append(f" New owned: {json.dumps(new.owned_assets, indent=2)}")
 
 if old.possessed_count != new.possessed_count:
 changes.append(f"Possessed assets: {old.possessed_count} → {new.possessed_count}")
 if new.possessed_assets:
 changes.append(f" New possessed: {json.dumps(new.possessed_assets, indent=2)}")
 
 return changes

def log_message(msg: str, level: str = "INFO") -> None:
 timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
 log_line = f"[{timestamp}] [{level}] {msg}"
 print(log_line)
 OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
 with OUTPUT_LOG.open("a", encoding="utf-8") as f:
 f.write(log_line + "\n")

def main() -> None:
 rpc = rpc_client.QubiPy_RPC()
 
 OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
 
 snapshots_history: Dict[str, List[AssetSnapshot]] = {
 entry["identity"]: [] for entry in SEED_TABLE
 }
 
 previous_snapshots: Dict[str, Optional[AssetSnapshot]] = {
 entry["identity"]: None for entry in SEED_TABLE
 }
 
 log_message("=== Asset Monitor Started ===")
 log_message(f"Monitoring {len(SEED_TABLE)} Layer-2 identities")
 log_message(f"Check interval: {CHECK_INTERVAL} seconds")
 log_message(f"Max checks: {MAX_CHECKS}")
 log_message("")
 
 check_count = 0
 
 try:
 while check_count < MAX_CHECKS:
 check_count += 1
 log_message(f"--- Check #{check_count}/{MAX_CHECKS} ---")
 
 for entry in SEED_TABLE:
 identity = entry["identity"]
 label = entry["label"]
 
 snapshot = scan_identity(rpc, entry)
 snapshots_history[identity].append(snapshot)
 previous = previous_snapshots[identity]
 
 changes = compare_snapshots(previous, snapshot)
 
 if changes:
 log_message(f"{label}:")
 for change in changes:
 log_message(f" → {change}")
 
 if snapshot.owned_count > 0 or snapshot.possessed_count > 0:
 log_message(f" ⚠️ ASSETS DETECTED!", level="ALERT")
 
 previous_snapshots[identity] = snapshot
 
 all_data = {
 "monitor_start": datetime.utcnow().isoformat() + "Z",
 "check_count": check_count,
 "snapshots": {
 identity: [s.to_dict() for s in snapshots]
 for identity, snapshots in snapshots_history.items()
 },
 }
 
 with OUTPUT_JSON.open("w", encoding="utf-8") as f:
 json.dump(all_data, f, indent=2)
 
 if check_count < MAX_CHECKS:
 log_message(f"Waiting {CHECK_INTERVAL} seconds...")
 time.sleep(CHECK_INTERVAL)
 
 except KeyboardInterrupt:
 log_message("Monitor stopped by user", level="INFO")
 except Exception as e:
 log_message(f"Monitor error: {e}", level="ERROR")
 
 log_message("=== Asset Monitor Finished ===")
 
 total_assets = sum(
 len(snapshots_history[entry["identity"]][-1].owned_assets) +
 len(snapshots_history[entry["identity"]][-1].possessed_assets)
 for entry in SEED_TABLE
 if snapshots_history[entry["identity"]]
 )
 
 log_message(f"Final status: {total_assets} total assets across all identities")
 log_message(f"Full history saved to: {OUTPUT_JSON}")
 log_message(f"Log file: {OUTPUT_LOG}")

if __name__ == "__main__":
 main()

