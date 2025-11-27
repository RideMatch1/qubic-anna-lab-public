#!/usr/bin/env python3
"""
Final Contract Trigger - Hypothesis 2: With Time Code (Tick-Gap 1649)

Payload Format: [Block_ID, Layer_Index, Tick_Gap]
Example: '1,2,1649', '2,2,1649', ... '8,2,1649'

This adds the known tick gap (1649) between Layer 1 and Layer 2 as the third element.
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
AMOUNT_QU = 1 # Reduced to 1 QU to minimize costs
TARGET_TICK_OFFSET = 25
PAYLOAD_CONFIG_FILE = Path("outputs/derived/final_payload_configs.json")
ASSET_CHECK_DELAY = 20 # Increased wait time
TICK_GAP = 1649 # Known tick gap between Layer 1 and Layer 2

@dataclass
class TxResult:
 block_id: int
 label: str
 identity: str
 payload: str
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
 """
 Build transaction with payload - Payload is included BEFORE signing.
 """
 seed_bytes = bytes(seed, 'utf-8')
 subseed = get_subseed_from_seed(seed_bytes)
 private_key = get_private_key_from_subseed(subseed)
 source_pubkey = get_public_key_from_private_key(private_key)
 dest_pubkey = get_public_key_from_identity(dest_identity)
 
 built_data = bytearray()
 offset = 0

 # 1. Source Public Key (32 bytes)
 built_data.extend(source_pubkey)
 offset += len(source_pubkey)

 # 2. Destination Public Key (32 bytes)
 built_data.extend(dest_pubkey)
 offset += len(dest_pubkey)

 # 3. Amount (8 bytes)
 built_data.extend(amount.to_bytes(8, byteorder='little'))
 offset += 8

 # 4. Target Tick (4 bytes)
 built_data.extend(target_tick.to_bytes(4, byteorder='little'))
 offset += 4

 # 5. Input Type (2 bytes) - always 0 for simple transfers
 input_type = 0
 built_data.extend(input_type.to_bytes(2, byteorder='little'))
 offset += 2

 # 6. Input Size (2 bytes) - size of the payload
 payload_bytes = payload.encode('utf-8')
 input_size = len(payload_bytes)
 built_data.extend(input_size.to_bytes(2, byteorder='little'))
 offset += 2

 # 7. Payload (N bytes) - inserted BEFORE signing
 built_data.extend(payload_bytes)
 offset += len(payload_bytes)
 
 # Sign the transaction digest (which now includes the payload)
 tx_digest = kangaroo_twelve(built_data, offset, 32)
 signature = sign(subseed, source_pubkey, tx_digest)

 # 8. Signature (64 bytes)
 built_data.extend(signature)
 offset += len(signature)

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
 """Get a snapshot of current assets (owned and possessed)."""
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
 
 # Compare owned assets
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
 
 # Compare possessed assets
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

def load_payloads() -> List[Dict[str, Any]]:
 """Load payloads for Hypothesis 2 (with Time Code)."""
 if not PAYLOAD_CONFIG_FILE.exists():
 print(f"❌ Error: Payload config file not found: {PAYLOAD_CONFIG_FILE}")
 return []

 with PAYLOAD_CONFIG_FILE.open("r", encoding="utf-8") as f:
 config = json.load(f)

 # Get Hypothesis 1 payloads and add Time Code
 hypo1 = next((h for h in config["hypotheses"] if h["name"] == "Simple Index Tuple"), None)
 
 if not hypo1:
 print("❌ Error: Hypothesis 1 not found in config.")
 return []
 
 # Transform to Hypothesis 2 format: add tick gap
 hypo2_payloads = []
 for item in hypo1["payloads"]:
 block_id = item["payload"][0]
 layer_index = item["payload"][1]
 payload_string = f"{block_id},{layer_index},{TICK_GAP}"
 
 hypo2_payloads.append({
 "label": item["label"],
 "seed": item["seed"],
 "identity": item["identity"],
 "payload": [block_id, layer_index, TICK_GAP],
 "payload_string": payload_string,
 })
 
 return hypo2_payloads

def main() -> int:
 print("=" * 80)
 print("🚀 FINAL CONTRACT TRIGGER - HYPOTHESIS 2")
 print("=" * 80)
 print()
 print("Payload Format: [Block_ID, Layer_Index, Tick_Gap]")
 print(f"Example: '1,2,{TICK_GAP}', '2,2,{TICK_GAP}', ... '8,2,{TICK_GAP}'")
 print()
 print("This adds the known tick gap (1649) between Layer 1 and Layer 2")
 print("as the third element - the 'Proof of Time'.")
 print()
 
 payloads = load_payloads()
 if not payloads:
 return 1

 print(f"✅ Loaded {len(payloads)} payloads for Hypothesis 2")
 print(f" Contract: {CONTRACT_ID}")
 print(f" Amount per transaction: {AMOUNT_QU} QU (minimized for testing)")
 print()
 
 rpc = rpc_client.QubiPy_RPC()
 current_tick = rpc.get_latest_tick()
 target_tick = current_tick + TARGET_TICK_OFFSET
 
 print(f"Current tick: {current_tick}")
 print(f"Target tick for all transactions: {target_tick}")
 print(f"Time window: ~{TARGET_TICK_OFFSET * 0.6:.1f} seconds\n")
 
 print("=" * 80)
 print("STEP 1: CAPTURING BASELINE ASSETS (Before Transactions)")
 print("=" * 80)
 print()
 
 # Capture baseline assets BEFORE sending transactions
 baseline_assets = {}
 for item in payloads:
 identity = item["identity"]
 baseline_assets[identity] = get_assets_snapshot(rpc, identity)
 owned_count = len(baseline_assets[identity]["owned_assets"])
 possessed_count = len(baseline_assets[identity]["possessed_assets"])
 print(f" {item['label']}: {owned_count} owned, {possessed_count} possessed (baseline)")
 
 print()
 print("=" * 80)
 print("STEP 2: SENDING 8 COORDINATED TRANSACTIONS...")
 print("=" * 80)
 print()
 
 tx_results: List[TxResult] = []
 start_time = time.time()
 
 # Send all 8 transactions
 for item in payloads:
 label = item["label"]
 seed = item["seed"]
 identity = item["identity"]
 payload_string = item["payload_string"]
 block_id = item["payload"][0]
 
 print(f"▶️ Block #{block_id} | {label}")
 print(f" Payload: '{payload_string}'")
 
 try:
 tx_id = send_transaction_with_payload(rpc, seed, identity, payload_string)
 tx_results.append(TxResult(
 block_id=block_id,
 label=label,
 identity=identity,
 payload=payload_string,
 tx_id=tx_id,
 status="SENT",
 assets_before=baseline_assets[identity]
 ))
 print(f" ✅ TX sent: {tx_id}")
 except Exception as e:
 tx_results.append(TxResult(
 block_id=block_id,
 label=label,
 identity=identity,
 payload=payload_string,
 tx_id=None,
 status="ERROR",
 error=str(e),
 assets_before=baseline_assets.get(identity, {"owned_assets": [], "possessed_assets": []})
 ))
 print(f" ❌ ERROR: {e}")
 
 time.sleep(0.1) # Small delay between transactions
 
 end_time = time.time()
 print()
 print("=" * 80)
 print(f"All transactions sent in {end_time - start_time:.2f} seconds")
 print(f"Successful: {len([r for r in tx_results if r.status == 'SENT'])}/{len(tx_results)}")
 print()
 
 # Wait for contract response
 print("=" * 80)
 print(f"⏳ WAITING {ASSET_CHECK_DELAY} seconds for contract payout...")
 print("=" * 80)
 time.sleep(ASSET_CHECK_DELAY)
 
 print()
 print("=" * 80)
 print("STEP 3: CHECKING FOR NEW ASSETS (Proof of Payout)...")
 print("=" * 80)
 print()
 
 asset_found_count = 0
 for result in tx_results:
 if result.status != "SENT":
 continue
 
 # Get assets AFTER transaction
 assets_after = get_assets_snapshot(rpc, result.identity)
 result.assets_after = assets_after
 
 # Detect NEW assets (not present in baseline)
 new_assets = detect_new_assets(result.assets_before, assets_after)
 
 owned_new = len(new_assets["owned_assets"])
 possessed_new = len(new_assets["possessed_assets"])
 
 if owned_new > 0 or possessed_new > 0:
 print(f"🎉 **PAYOUT SUCCESS!** | Block #{result.block_id} ({result.payload})")
 print(f" NEW Owned Assets: {owned_new}")
 print(f" NEW Possessed Assets: {possessed_new}")
 if new_assets["owned_assets"]:
 for asset in new_assets["owned_assets"]:
 asset_name = asset.get("data", {}).get("issuedAsset", {}).get("name", "Unknown")
 units = asset.get("data", {}).get("numberOfUnits", "0")
 print(f" → {asset_name}: {units} units")
 if new_assets["possessed_assets"]:
 for asset in new_assets["possessed_assets"]:
 asset_name = asset.get("data", {}).get("ownedAsset", {}).get("issuedAsset", {}).get("name", "Unknown")
 units = asset.get("data", {}).get("numberOfUnits", "0")
 print(f" → {asset_name}: {units} units")
 asset_found_count += 1
 else:
 print(f" [Check] Block #{result.block_id} ({result.payload}) | No NEW assets detected")
 print(f" Baseline: {len(result.assets_before.get('owned_assets', []))} owned, {len(result.assets_before.get('possessed_assets', []))} possessed")
 print(f" Current: {len(assets_after.get('owned_assets', []))} owned, {len(assets_after.get('possessed_assets', []))} possessed")
 
 print()
 print("=" * 80)
 print("FINAL RESULT")
 print("=" * 80)
 print()
 
 if asset_found_count == len(tx_results):
 print(f"✅ **COMPLETE SUCCESS!** The Smart Contract paid out all {len(tx_results)} slots.")
 print(" Hypothesis 2 was CORRECT - the Time Code (Tick-Gap 1649) was the missing piece!")
 elif asset_found_count > 0:
 print(f"⚠️ **PARTIAL SUCCESS!** {asset_found_count} of {len(tx_results)} slots were paid out.")
 print(" The Time Code may be partially correct, or there may be other conditions.")
 else:
 print("😔 **NO NEW PAYOUT.** Hypothesis 2 did not trigger the contract payout.")
 print(" ➡️ Next step: Analyze tick patterns more deeply or test other payload formats.")
 
 print()
 print("=" * 80)
 print("TRANSACTION SUMMARY")
 print("=" * 80)
 for result in tx_results:
 status_icon = "✅" if result.status == "SENT" else "❌"
 print(f"{status_icon} Block #{result.block_id} ({result.payload}): {result.tx_id or result.error}")
 
 return 0

if __name__ == "__main__":
 raise SystemExit(main())

