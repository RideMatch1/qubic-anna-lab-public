#!/usr/bin/env python3
"""
Test Different Amounts: The contract might require specific amounts.

Average incoming: 20,879,778 QU (but that might be old IPO transactions)
Test with various amounts to find the minimum or pattern.
"""

from __future__ import annotations

import time
from qubipy.rpc import rpc_client
from qubipy.tx.utils import create_tx

CONTRACT_ID = "POCCZYCKTRQGHFIPWGSBLJTEQFDDVVBMNUHNCKMRACBGQOPBLURNRCBAFOBD"
TARGET_TICK_OFFSET = 25

# Test amounts (focus on small amounts, not millions)
# Note: High average (20M QU) is from normal GENESIS purchases, not triggers
TEST_AMOUNTS = [
 1, # Minimal
 10, # Small
 26, # Special number (CFB's "26")
 50, # Medium-small
 100, # Medium
 128, # Matrix size (128x128)
 256, # Power of 2
]

# Test with Block #1 (one identity, multiple amounts)
TEST_IDENTITY = {
 "label": "Diagonal #1",
 "seed": "aqiosqqmacybpqxqsjniuaylmxxiwqoxqmeqyxbbtbonsjjrcwpxxdd",
 "identity": "OBWIIPWFPOWIQCHGJHKFZNMSSYOBYNNDLUEXAELXKEROIUKIXEUXMLZBICUD",
}

def get_baseline_assets(rpc: rpc_client.QubiPy_RPC, identity: str) -> set:
 """Get baseline asset IDs."""
 asset_ids = set()
 try:
 owned = rpc.get_owned_assets(identity)
 if isinstance(owned, list):
 for asset in owned:
 issuance = asset.get("data", {}).get("issuanceIndex")
 name = asset.get("data", {}).get("issuedAsset", {}).get("name")
 if issuance and name:
 asset_ids.add((issuance, name))
 except:
 pass
 return asset_ids

def main():
 print("=" * 80)
 print("TEST: DIFFERENT AMOUNTS")
 print("=" * 80)
 print()
 print("Hypothesis: Contract might require specific minimum amounts")
 print(f"Testing with: {TEST_AMOUNTS}")
 print()
 
 rpc = rpc_client.QubiPy_RPC()
 
 # Get baseline
 print("Getting baseline assets...")
 baseline = get_baseline_assets(rpc, TEST_IDENTITY["identity"])
 print(f"Baseline: {len(baseline)} assets")
 print()
 
 results = []
 
 for amount in TEST_AMOUNTS:
 print(f"▶️ Testing amount: {amount} QU")
 
 try:
 current_tick = rpc.get_latest_tick()
 target_tick = current_tick + TARGET_TICK_OFFSET
 
 tx_bytes, _, _, tx_hash = create_tx(
 seed=TEST_IDENTITY["seed"],
 dest_id=CONTRACT_ID,
 amount=amount,
 target_tick=target_tick,
 )
 response = rpc.broadcast_transaction(tx_bytes)
 tx_id = response.get("txId", tx_hash)
 print(f" ✅ TX sent: {tx_id[:20]}...")
 
 # Wait and check
 print(f" ⏳ Waiting 20 seconds...")
 time.sleep(20)
 
 current_assets = get_baseline_assets(rpc, TEST_IDENTITY["identity"])
 new_assets = current_assets - baseline
 
 if new_assets:
 print(f" 🎉 SUCCESS! {len(new_assets)} new assets with amount {amount} QU!")
 results.append({"amount": amount, "success": True, "new_assets": len(new_assets)})
 break # Stop if we find a working amount
 else:
 print(f" ❌ No new assets with amount {amount} QU")
 results.append({"amount": amount, "success": False})
 
 except Exception as e:
 print(f" ❌ Error: {e}")
 results.append({"amount": amount, "success": False, "error": str(e)})
 
 print()
 time.sleep(2) # Delay between tests
 
 print("=" * 80)
 print("RESULTS")
 print("=" * 80)
 print()
 
 successful = [r for r in results if r.get("success")]
 if successful:
 print(f"✅ Found working amount: {successful[0]['amount']} QU")
 else:
 print("❌ No working amount found in tested range")
 print(" Might need higher amounts or different approach")
 
 return 0

if __name__ == "__main__":
 raise SystemExit(main())

