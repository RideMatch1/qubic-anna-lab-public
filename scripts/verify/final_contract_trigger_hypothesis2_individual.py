#!/usr/bin/env python3
"""
Final Contract Trigger - Hypothesis 2 with Individual Tick Gaps

Uses the exact individual tick gap for each identity (calculated from validForTick values)
instead of the average value (1649).

Payload Format: [Block_ID, Layer_Index, Individual_Tick_Gap]
Example: '1,2,9', '2,2,9', '3,2,13', ... '8,2,12'
"""

from __future__ import annotations

import json
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List

from qubipy.rpc import rpc_client
from qubipy.tx.utils import (
 get_public_key_from_identity,
 get_subseed_from_seed,
 get_private_key_from_subseed,
 get_public_key_from_private_key,
)
from qubipy.crypto.utils import sign, kangaroo_twelve

# --- CONSTANTS ---
CONTRACT_ID = "POCCZYCKTRQGHFIPWGSBLJTEQFDDVVBMNUHNCKMRACBGQOPBLURNRCBAFOBD"
AMOUNT_QU = 1 # Minimized for testing
TARGET_TICK_OFFSET = 25
TICK_GAPS_FILE = Path("outputs/derived/individual_tick_gaps.json")
ASSET_CHECK_DELAY = 20

@dataclass
class TxResult:
 block_id: int
 label: str
 identity: str
 payload: str
 tick_gap: int
 tx_id: str | None
 status: str
 error: str | None = None
 assets_before: Dict[str, Any] = None
 assets_after: Dict[str, Any] = None

def build_tx_with_payload(
 seed: str,
 dest_identity: str,
 amount: int,
 target_tick: int,
 payload: str,
) -> bytes:
 """Build transaction with payload."""
 seed_bytes = bytes(seed, 'utf-8')
 subseed = get_subseed_from_seed(seed_bytes)
 private_key = get_private_key_from_subseed(subseed)
 source_pubkey = get_public_key_from_private_key(private_key)
 dest_pubkey = get_public_key_from_identity(dest_identity)
 
 built_data = bytearray()
 offset = 0

 built_data.extend(source_pubkey)
 offset += len(source_pubkey)
 built_data.extend(dest_pubkey)
 offset += len(dest_pubkey)
 built_data.extend(amount.to_bytes(8, byteorder='little'))
 offset += 8
 built_data.extend(target_tick.to_bytes(4, byteorder='little'))
 offset += 4
 built_data.extend((0).to_bytes(2, byteorder='little'))
 offset += 2
 
 payload_bytes = payload.encode('utf-8')
 built_data.extend(len(payload_bytes).to_bytes(2, byteorder='little'))
 offset += 2
 built_data.extend(payload_bytes)
 offset += len(payload_bytes)
 
 tx_digest = kangaroo_twelve(built_data, offset, 32)
 signature = sign(subseed, source_pubkey, tx_digest)
 built_data.extend(signature)
 
 return bytes(built_data)

def send_transaction_with_payload(
 rpc: rpc_client.QubiPy_RPC,
 seed: str,
 identity: str,
 payload: str,
) -> str:
 """Send transaction with payload to contract."""
 latest_tick = rpc.get_latest_tick()
 target_tick = latest_tick + TARGET_TICK_OFFSET
 
 tx_bytes = build_tx_with_payload(
 seed=seed,
 dest_identity=CONTRACT_ID,
 amount=AMOUNT_QU,
 target_tick=target_tick,
 payload=payload,
 )
 
 response = rpc.broadcast_transaction(tx_bytes)
 return response.get("txId", response.get("transactionHash", "UNKNOWN"))

def get_assets_snapshot(rpc: rpc_client.QubiPy_RPC, identity: str) -> Dict[str, Any]:
 """Get a snapshot of current assets."""
 assets = {"owned_assets": [], "possessed_assets": []}
 try:
 owned = rpc.get_owned_assets(identity)
 if isinstance(owned, list):
 assets["owned_assets"] = owned
 elif isinstance(owned, dict) and owned.get("assets"):
 assets["owned_assets"] = owned["assets"]
 
 possessed = rpc.get_possessed_assets(identity)
 if isinstance(possessed, list):
 assets["possessed_assets"] = possessed
 elif isinstance(possessed, dict) and possessed.get("assets"):
 assets["possessed_assets"] = possessed["assets"]
 except Exception as e:
 print(f" Error getting assets snapshot: {e}")
 return assets

def detect_new_assets(before: Dict[str, Any], after: Dict[str, Any]) -> Dict[str, Any]:
 """Detect new assets that appeared after the transaction."""
 new_assets = {"owned_assets": [], "possessed_assets": []}
 
 before_owned_ids = {
 (a.get("data", {}).get("issuanceIndex"), a.get("data", {}).get("issuedAsset", {}).get("name"))
 for a in before.get("owned_assets", [])
 }
 for asset in after.get("owned_assets", []):
 asset_id = (
 asset.get("data", {}).get("issuanceIndex"),
 asset.get("data", {}).get("issuedAsset", {}).get("name")
 )
 if asset_id not in before_owned_ids:
 new_assets["owned_assets"].append(asset)
 
 before_possessed_ids = {
 (a.get("data", {}).get("issuanceIndex"), a.get("data", {}).get("ownedAsset", {}).get("issuedAsset", {}).get("name"))
 for a in before.get("possessed_assets", [])
 }
 for asset in after.get("possessed_assets", []):
 asset_id = (
 asset.get("data", {}).get("issuanceIndex"),
 asset.get("data", {}).get("ownedAsset", {}).get("issuedAsset", {}).get("name")
 )
 if asset_id not in before_possessed_ids:
 new_assets["possessed_assets"].append(asset)
 
 return new_assets

def load_tick_gaps() -> Dict[str, int]:
 """Load individual tick gaps from analysis."""
 if not TICK_GAPS_FILE.exists():
 print(f"❌ Error: Tick gaps file not found: {TICK_GAPS_FILE}")
 return {}
 
 with TICK_GAPS_FILE.open("r", encoding="utf-8") as f:
 data = json.load(f)
 
 gaps = {}
 for record in data.get("records", []):
 if record.get("tick_gap") is not None:
 gaps[record["label"]] = record["tick_gap"]
 
 return gaps

def main() -> int:
 print("=" * 80)
 print("🚀 FINAL CONTRACT TRIGGER - HYPOTHESIS 2 (INDIVIDUAL TICK GAPS)")
 print("=" * 80)
 print()
 print("Using exact individual tick gaps for each identity")
 print("instead of the average value (1649).")
 print()
 
 # Load tick gaps
 tick_gaps = load_tick_gaps()
 if not tick_gaps:
 print("❌ Failed to load tick gaps. Run individual_tick_gap_analysis.py first.")
 return 1
 
 print(f"✅ Loaded {len(tick_gaps)} individual tick gaps")
 print()
 
 # Load payload config for seeds and identities
 payload_config_file = Path("outputs/derived/final_payload_configs.json")
 if not payload_config_file.exists():
 print(f"❌ Error: Payload config file not found")
 return 1
 
 with payload_config_file.open("r", encoding="utf-8") as f:
 config = json.load(f)
 
 hypo1 = next((h for h in config["hypotheses"] if h["name"] == "Simple Index Tuple"), None)
 if not hypo1:
 print("❌ Error: Hypothesis 1 not found in config.")
 return 1
 
 # Create payloads with individual tick gaps
 payloads = []
 for item in hypo1["payloads"]:
 label = item["label"]
 block_id = item["payload"][0]
 layer_index = item["payload"][1]
 
 # Get individual tick gap for this identity
 tick_gap = tick_gaps.get(label)
 if tick_gap is None:
 print(f"⚠️ Warning: No tick gap found for {label}, skipping")
 continue
 
 payload_string = f"{block_id},{layer_index},{tick_gap}"
 
 payloads.append({
 "label": label,
 "seed": item["seed"],
 "identity": item["identity"],
 "block_id": block_id,
 "tick_gap": tick_gap,
 "payload_string": payload_string,
 })
 
 if not payloads:
 print("❌ No valid payloads created")
 return 1
 
 print(f"✅ Created {len(payloads)} payloads with individual tick gaps")
 print()
 for p in payloads:
 print(f" {p['label']}: Payload '{p['payload_string']}' (Tick Gap: {p['tick_gap']})")
 print()
 
 rpc = rpc_client.QubiPy_RPC()
 current_tick = rpc.get_latest_tick()
 target_tick = current_tick + TARGET_TICK_OFFSET
 
 print(f"Contract: {CONTRACT_ID}")
 print(f"Amount per transaction: {AMOUNT_QU} QU")
 print(f"Current tick: {current_tick}")
 print(f"Target tick: {target_tick}")
 print()
 
 print("=" * 80)
 print("STEP 1: CAPTURING BASELINE ASSETS")
 print("=" * 80)
 print()
 
 baseline_assets = {}
 for item in payloads:
 identity = item["identity"]
 baseline_assets[identity] = get_assets_snapshot(rpc, identity)
 owned_count = len(baseline_assets[identity]["owned_assets"])
 possessed_count = len(baseline_assets[identity]["possessed_assets"])
 print(f" {item['label']}: {owned_count} owned, {possessed_count} possessed")
 
 print()
 print("=" * 80)
 print("STEP 2: SENDING TRANSACTIONS...")
 print("=" * 80)
 print()
 
 tx_results: List[TxResult] = []
 start_time = time.time()
 
 for item in payloads:
 print(f"▶️ Block #{item['block_id']} | {item['label']}")
 print(f" Payload: '{item['payload_string']}' (Tick Gap: {item['tick_gap']})")
 
 try:
 tx_id = send_transaction_with_payload(rpc, item["seed"], item["identity"], item["payload_string"])
 tx_results.append(TxResult(
 block_id=item["block_id"],
 label=item["label"],
 identity=item["identity"],
 payload=item["payload_string"],
 tick_gap=item["tick_gap"],
 tx_id=tx_id,
 status="SENT",
 assets_before=baseline_assets[item["identity"]]
 ))
 print(f" ✅ TX sent: {tx_id}")
 except Exception as e:
 tx_results.append(TxResult(
 block_id=item["block_id"],
 label=item["label"],
 identity=item["identity"],
 payload=item["payload_string"],
 tick_gap=item["tick_gap"],
 tx_id=None,
 status="ERROR",
 error=str(e),
 assets_before=baseline_assets.get(item["identity"], {"owned_assets": [], "possessed_assets": []})
 ))
 print(f" ❌ ERROR: {e}")
 
 time.sleep(0.1)
 
 end_time = time.time()
 print()
 print(f"All transactions sent in {end_time - start_time:.2f} seconds")
 print(f"Successful: {len([r for r in tx_results if r.status == 'SENT'])}/{len(tx_results)}")
 print()
 
 print("=" * 80)
 print(f"⏳ WAITING {ASSET_CHECK_DELAY} seconds for contract payout...")
 print("=" * 80)
 time.sleep(ASSET_CHECK_DELAY)
 
 print()
 print("=" * 80)
 print("STEP 3: CHECKING FOR NEW ASSETS")
 print("=" * 80)
 print()
 
 asset_found_count = 0
 for result in tx_results:
 if result.status != "SENT":
 continue
 
 assets_after = get_assets_snapshot(rpc, result.identity)
 result.assets_after = assets_after
 
 new_assets = detect_new_assets(result.assets_before, assets_after)
 
 owned_new = len(new_assets["owned_assets"])
 possessed_new = len(new_assets["possessed_assets"])
 
 if owned_new > 0 or possessed_new > 0:
 print(f"🎉 **PAYOUT SUCCESS!** | Block #{result.block_id} ({result.payload})")
 print(f" NEW Assets: {owned_new} owned, {possessed_new} possessed")
 asset_found_count += 1
 else:
 print(f" [Check] Block #{result.block_id} ({result.payload}) | No NEW assets")
 
 print()
 print("=" * 80)
 print("FINAL RESULT")
 print("=" * 80)
 print()
 
 if asset_found_count == len(tx_results):
 print(f"✅ **COMPLETE SUCCESS!** All {len(tx_results)} slots paid out!")
 print(" Individual tick gaps were the correct approach!")
 elif asset_found_count > 0:
 print(f"⚠️ **PARTIAL SUCCESS!** {asset_found_count}/{len(tx_results)} slots paid out.")
 else:
 print("😔 **NO PAYOUT.** Individual tick gaps did not trigger the contract.")
 print(" ➡️ May need to use original creation ticks, not current validForTick values.")
 
 return 0

if __name__ == "__main__":
 raise SystemExit(main())

