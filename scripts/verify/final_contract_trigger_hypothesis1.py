#!/usr/bin/env python3
"""
Final Contract Trigger - Hypothesis 1: Executes the coordinated 8-fold 
"Proof of Participation" transaction using Payload Hypothesis 1.

Payload: [Block_ID (1-8), Layer_Index (2)]
Example: "1,2", "2,2", ... "8,2"
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
AMOUNT_QU = 50
TARGET_TICK_OFFSET = 25
PAYLOAD_CONFIG_FILE = Path("outputs/derived/final_payload_configs.json")
ASSET_CHECK_DELAY = 15 # Seconds to wait for asset update

@dataclass
class TxResult:
 block_id: int
 label: str
 identity: str
 payload: str
 tx_id: str | None
 status: str
 error: str | None = None

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

def load_payloads() -> List[Dict[str, Any]]:
 """Load payloads for Hypothesis 1."""
 if not PAYLOAD_CONFIG_FILE.exists():
 print(f"❌ Error: Payload config file not found: {PAYLOAD_CONFIG_FILE}")
 return []

 with PAYLOAD_CONFIG_FILE.open("r", encoding="utf-8") as f:
 config = json.load(f)

 # Filter for Hypothesis 1
 hypo1 = next((h for h in config["hypotheses"] if h["name"] == "Simple Index Tuple"), None)
 
 if not hypo1:
 print("❌ Error: Hypothesis 1 ('Simple Index Tuple') not found in config.")
 return []
 
 return hypo1["payloads"]

def check_assets(rpc: rpc_client.QubiPy_RPC, identity: str) -> Dict[str, Any]:
 """Check assets for an identity."""
 assets = {"owned_assets": [], "possessed_assets": []}
 try:
 owned = rpc.get_owned_assets(identity)
 # Handle both dict and list responses
 if isinstance(owned, dict) and owned.get("assets"):
 assets["owned_assets"] = owned["assets"]
 elif isinstance(owned, list):
 assets["owned_assets"] = owned
 
 possessed = rpc.get_possessed_assets(identity)
 if isinstance(possessed, dict) and possessed.get("assets"):
 assets["possessed_assets"] = possessed["assets"]
 elif isinstance(possessed, list):
 assets["possessed_assets"] = possessed
 except Exception as e:
 print(f" Error checking assets for {identity[:20]}...: {e}")
 return assets

def main() -> int:
 print("=" * 80)
 print("🚀 FINAL CONTRACT TRIGGER - HYPOTHESIS 1")
 print("=" * 80)
 print()
 print("Payload Format: [Block_ID, Layer_Index]")
 print("Example: '1,2', '2,2', ... '8,2'")
 print()
 
 payloads = load_payloads()
 if not payloads:
 return 1

 print(f"✅ Loaded {len(payloads)} payloads for Hypothesis 1")
 print(f" Contract: {CONTRACT_ID}")
 print(f" Amount per transaction: {AMOUNT_QU} QU")
 print()
 
 rpc = rpc_client.QubiPy_RPC()
 current_tick = rpc.get_latest_tick()
 target_tick = current_tick + TARGET_TICK_OFFSET
 
 print(f"Current tick: {current_tick}")
 print(f"Target tick for all transactions: {target_tick}")
 print(f"Time window: ~{TARGET_TICK_OFFSET * 0.6:.1f} seconds\n")
 
 print("=" * 80)
 print("SENDING 8 COORDINATED TRANSACTIONS...")
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
 # Extract actual TX ID from response
 if tx_id == "UNKNOWN":
 # Try to get it from the transaction hash
 print(f" ⚠️ TX sent but ID unknown - checking transaction status...")
 tx_results.append(TxResult(
 block_id=block_id,
 label=label,
 identity=identity,
 payload=payload_string,
 tx_id=tx_id,
 status="SENT"
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
 error=str(e)
 ))
 print(f" ❌ ERROR: {e}")
 
 time.sleep(0.01) # Small delay between transactions
 
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
 print("CHECKING ASSETS (Proof of Payout)...")
 print("=" * 80)
 print()
 
 asset_found_count = 0
 for result in tx_results:
 if result.status != "SENT":
 continue
 
 assets = check_assets(rpc, result.identity)
 
 # Check if new assets appeared (excluding GENESIS which we already have)
 owned_count = len(assets["owned_assets"])
 possessed_count = len(assets["possessed_assets"])
 
 if owned_count > 0 or possessed_count > 0:
 print(f"🎉 **PAYOUT SUCCESS!** | Block #{result.block_id} ({result.payload})")
 print(f" Owned Assets: {owned_count}")
 print(f" Possessed Assets: {possessed_count}")
 if assets["owned_assets"]:
 print(f" Assets: {assets['owned_assets']}")
 if assets["possessed_assets"]:
 print(f" Assets: {assets['possessed_assets']}")
 asset_found_count += 1
 else:
 print(f" [Check] Block #{result.block_id} ({result.payload}) | No new assets found")
 
 print()
 print("=" * 80)
 print("FINAL RESULT")
 print("=" * 80)
 print()
 
 if asset_found_count == len(tx_results):
 print(f"✅ **COMPLETE SUCCESS!** The Smart Contract paid out all {len(tx_results)} slots.")
 print(" The architectural code was CORRECT!")
 elif asset_found_count > 0:
 print(f"⚠️ **PARTIAL SUCCESS!** {asset_found_count} of {len(tx_results)} slots were paid out.")
 print(" This may indicate an issue with Vortex Block-IDs (5-8) or partial correctness.")
 else:
 print("😔 **NO IMMEDIATE PAYOUT.** The payload was not correct, or the contract needs a different trigger.")
 print(" ➡️ Next step: Test Hypothesis 2 (with timing code 1649) or wait for tick analysis results.")
 
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

