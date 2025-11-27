#!/usr/bin/env python3
"""
Fetch Creation Ticks: Attempts to find the ORIGINAL creation tick for Layer 1 and Layer 2 identities
by analyzing transaction history, rather than current validForTick.

Goal: Calculate the TRUE creation tick gap.
"""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

from qubipy.rpc import rpc_client

OUTPUT_DIR = Path("outputs/derived")
OUTPUT_JSON = OUTPUT_DIR / "original_creation_gaps.json"

# Layer 1 & 2 Pairs (CORRECTED identities)
IDENTITY_PAIRS = [
 {
 "label": "Diagonal #1",
 "block_id": 1,
 "l1": "AQIOSQQMACYBPQXQSJNIUAYLMXXIWQOXQMEQYXBBTBONSJJRCWPXXDDRDWOR",
 "l2": "OBWIIPWFPOWIQCHGJHKFZNMSSYOBYNNDLUEXAELXKEROIUKIXEUXMLZBICUD"
 },
 {
 "label": "Diagonal #2",
 "block_id": 2,
 "l1": "GWUXOMMMMFMTBWFZSNGMUKWBILTXQDKNMMMNYPEFTAMRONJMABLHTRRROHXZ",
 "l2": "OQOOMLAQLGOJFFAYGXALSTDVDGQDWKWGDQJRMNZSODHMWWWNSLSQZZAHOAZE"
 },
 {
 "label": "Diagonal #3",
 "block_id": 3,
 "l1": "ACGJGQQYILBPXDRBORFGWFZBBBNLQNGHDDELVLXXXLBNNNFBLLPBNNNLJIFV",
 "l2": "WEZPWOMKYYQYGDZJDUEPIOTTUKCCQVBYEMYHQUTWGAMHFVJJVRCQLMVGYDGG"
 },
 {
 "label": "Diagonal #4",
 "block_id": 4,
 "l1": "GIUVFGAWCBBFFKVBMFJESLHBBFBFWZWNNXCBQBBJRVFBNVJLTJBBBHTHKLDC",
 "l2": "BUICAHKIBLQWQAIONARLYROQGMRAYEAOECSZCPMTEHUIFXLKGTMAPJFDCHQI"
 },
 {
 "label": "Vortex #1",
 "block_id": 5,
 "l1": "UUFEEMUUBIYXYXDUXZCFBIHABAYSACQSWSGABOBKNXBZCICLYOKOBMLKMUAF",
 "l2": "FAEEIVWNINMPFAAWUUYMCJXMSFCAGDJNFDRCEHBFPGFCCEKUWTMCBHXBNSVL"
 },
 {
 "label": "Vortex #2",
 "block_id": 6,
 "l1": "HJBRFBHTBZJLVRBXTDRFORBWNACAHAQMSBUNBONHTRHNJKXKKNKHWCBNAXLD",
 "l2": "PRUATXFVEFFWAEHUADBSBKOFEQTCYOXPSJHWPUSUKCHBXGMRQQEWITAELCNI"
 },
 {
 "label": "Vortex #3",
 "block_id": 7,
 "l1": "JKLMNOIPDQORWSICTWWUIYVMOFIQCQSYKMKACMOKQYCCMCOGOCQCSCWCDQFL",
 "l2": "RIOIMZKDJPHCFFGVYMWSFOKVBNXAYCKUXOLHLHHCPCQDULIITMFGZQUFIMKN"
 },
 {
 "label": "Vortex #4",
 "block_id": 8,
 "l1": "XYZQAUBQUUQBQBYQAYEIYAQYMMEMQQQMMQSQEQAZSMOGWOXKIRMJXMCLFAVK",
 "l2": "DZGTELPKNEITGBRUPCWRNZGLTMBCRPLRPERUFBZHDFDTFYTJXOUDYLSBKRRB"
 },
]

def get_earliest_tick_from_balance(rpc: rpc_client.QubiPy_RPC, identity: str) -> Optional[int]:
 """
 Attempts to get the creation tick from balance data.
 Some RPC implementations might include creation tick in balance response.
 """
 try:
 balance = rpc.get_balance(identity)
 if balance:
 # Check various possible fields
 creation_tick = balance.get("creationTick") or balance.get("firstTick") or balance.get("birthTick")
 if creation_tick:
 return creation_tick
 except Exception as e:
 print(f" ⚠️ Error getting balance for {identity[:20]}...: {e}")
 return None

def get_earliest_tick_from_transactions(rpc: rpc_client.QubiPy_RPC, identity: str, max_ticks_back: int = 100000) -> Optional[int]:
 """
 Fetches transaction history and returns the tick of the earliest transaction.
 
 Tries multiple RPC methods:
 1. get_transfer_transactions_per_tick (if available)
 2. get_transaction_history (if available)
 3. get_identity_info (if available)
 """
 try:
 latest_tick = rpc.get_latest_tick()
 start_tick = max(0, latest_tick - max_ticks_back)
 
 # Try get_transfer_transactions_per_tick
 try:
 tx_data = rpc.get_transfer_transactions_per_tick(
 identity=identity,
 start_tick=start_tick,
 end_tick=latest_tick
 )
 
 if tx_data and tx_data.get("transactions"):
 transactions = tx_data["transactions"]
 if transactions:
 # Find minimum tick
 ticks = [tx.get("tickNumber") or tx.get("tick") for tx in transactions if tx.get("tickNumber") or tx.get("tick")]
 if ticks:
 return min(ticks)
 except Exception as e:
 print(f" ⚠️ get_transfer_transactions_per_tick failed: {e}")
 
 # Try get_identity_info (if available)
 try:
 # Some RPC implementations might have this
 identity_info = rpc.get_identity_info(identity)
 if identity_info:
 creation_tick = identity_info.get("creationTick") or identity_info.get("firstTick")
 if creation_tick:
 return creation_tick
 except Exception:
 pass # Method might not exist
 
 except Exception as e:
 print(f" ❌ Error fetching transaction history for {identity[:20]}...: {e}")
 
 return None

def get_earliest_tick(rpc: rpc_client.QubiPy_RPC, identity: str) -> Optional[int]:
 """
 Attempts to find the earliest tick for an identity using multiple methods.
 """
 # Method 1: Try balance data
 tick = get_earliest_tick_from_balance(rpc, identity)
 if tick:
 return tick
 
 # Method 2: Try transaction history
 tick = get_earliest_tick_from_transactions(rpc, identity)
 if tick:
 return tick
 
 return None

def main() -> int:
 OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
 
 print("=" * 80)
 print("🔍 ORIGINAL TICK GAP DISCOVERY")
 print("=" * 80)
 print()
 print("Goal: Find the ORIGINAL creation ticks for Layer 1 and Layer 2 identities")
 print(" by analyzing transaction history, not current validForTick values.")
 print()
 
 rpc = rpc_client.QubiPy_RPC()
 results: List[Dict[str, Any]] = []
 
 print("=" * 80)
 print("FETCHING CREATION TICKS")
 print("=" * 80)
 print()
 print(f"{'Block':<10} | {'Label':<15} | {'Layer 1 Tick':<15} | {'Layer 2 Tick':<15} | {'Gap':<10} | {'Status':<10}")
 print("-" * 90)
 
 for pair in IDENTITY_PAIRS:
 label = pair["label"]
 block_id = pair["block_id"]
 l1_identity = pair["l1"]
 l2_identity = pair["l2"]
 
 print(f"▶️ {label} (Block #{block_id})")
 
 # Get Layer 1 creation tick
 print(f" Fetching Layer 1 tick...")
 l1_tick = get_earliest_tick(rpc, l1_identity)
 time.sleep(0.5) # Rate limiting
 
 # Get Layer 2 creation tick
 print(f" Fetching Layer 2 tick...")
 l2_tick = get_earliest_tick(rpc, l2_identity)
 time.sleep(0.5) # Rate limiting
 
 gap = None
 status = "UNKNOWN"
 
 if l1_tick and l2_tick:
 gap = l2_tick - l1_tick
 status = "FOUND"
 print(f" ✅ Layer 1: {l1_tick}, Layer 2: {l2_tick}, Gap: {gap}")
 elif l1_tick:
 status = "PARTIAL_L1"
 print(f" ⚠️ Layer 1: {l1_tick}, Layer 2: Not found")
 elif l2_tick:
 status = "PARTIAL_L2"
 print(f" ⚠️ Layer 1: Not found, Layer 2: {l2_tick}")
 else:
 status = "NOT_FOUND"
 print(f" ❌ Both ticks not found")
 
 # Special note for Block #7
 if block_id == 7 and gap is None:
 print(f" (Note: Block #7 is known to work with gap 1649)")
 
 print()
 
 results.append({
 "block_id": block_id,
 "label": label,
 "l1_identity": l1_identity,
 "l2_identity": l2_identity,
 "l1_creation_tick": l1_tick,
 "l2_creation_tick": l2_tick,
 "original_gap": gap,
 "status": status
 })
 
 # Summary
 print("=" * 80)
 print("SUMMARY")
 print("=" * 80)
 print()
 
 found_gaps = [r["original_gap"] for r in results if r["original_gap"] is not None]
 
 if found_gaps:
 print(f"✅ Found {len(found_gaps)}/{len(results)} original gaps")
 print()
 print("Original Tick Gaps:")
 for result in results:
 if result["original_gap"] is not None:
 print(f" {result['label']} (Block #{result['block_id']}): {result['original_gap']}")
 
 avg_gap = sum(found_gaps) / len(found_gaps)
 min_gap = min(found_gaps)
 max_gap = max(found_gaps)
 
 print()
 print(f"Average Gap: {avg_gap:.2f}")
 print(f"Min Gap: {min_gap}")
 print(f"Max Gap: {max_gap}")
 print(f"Range: {max_gap - min_gap}")
 
 if 1649 in found_gaps:
 print()
 print("🎯 Target 1649 confirmed in history data!")
 else:
 print("⚠️ No creation ticks found in transaction history")
 print(" Possible reasons:")
 print(" - Node has pruned old transaction data")
 print(" - RPC method doesn't support historical queries")
 print(" - Identities were created before transaction tracking")
 print()
 print("📋 Recommended Strategy:")
 print(" - Use known value 1649 for all blocks (Block #7 worked with this)")
 print(" - Or test with 1649 +/- 10 ticks for remaining blocks")
 
 # Save results
 output_data = {
 "records": results,
 "summary": {
 "total": len(results),
 "found": len(found_gaps),
 "average_gap": sum(found_gaps) / len(found_gaps) if found_gaps else None,
 "min_gap": min(found_gaps) if found_gaps else None,
 "max_gap": max(found_gaps) if found_gaps else None,
 }
 }
 
 with OUTPUT_JSON.open("w", encoding="utf-8") as f:
 json.dump(output_data, f, indent=2)
 
 print()
 print("=" * 80)
 print(f"✅ Analysis saved to: {OUTPUT_JSON}")
 print("=" * 80)
 
 return 0

if __name__ == "__main__":
 raise SystemExit(main())

