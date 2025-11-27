#!/usr/bin/env python3
"""
Phase 2: Test contract interaction with all 8 identities holding GENESIS assets.

This script sends coordinated transactions from all 8 identities to the contract
and monitors for responses, new assets, or other changes.
"""

from __future__ import annotations

import time
from dataclasses import dataclass
from typing import List

from qubipy.rpc import rpc_client
from qubipy.tx.utils import create_tx

CONTRACT_ID = "POCCZYCKTRQGHFIPWGSBLJTEQFDDVVBMNUHNCKMRACBGQOPBLURNRCBAFOBD"
AMOUNT_QU = 1 # Small amount to test
TARGET_TICK_OFFSET = 25

SEED_TABLE = [
 {
 "label": "Diagonal #1",
 "seed": "aqiosqqmacybpqxqsjniuaylmxxiwqoxqmeqyxbbtbonsjjrcwpxxdd",
 "identity": "OBWIIPWFPOWIQCHGJHKFZNMSSYOBYNNDLUEXAELXKEROIUKIXEUXMLZBICUD",
 },
 {
 "label": "Diagonal #2",
 "seed": "gwuxommmmfmtbwfzsngmukwbiltxqdknmmmnypeftamronjmablhtrr",
 "identity": "OQOOMLAQLGOJFFAYGXALSTDVDGQDWKWGDQJRMNZSODHMWWWNSLSQZZAHOAZE",
 },
 {
 "label": "Diagonal #3",
 "seed": "acgjgqqyilbpxdrborfgwfzbbbnlqnghddelvlxxxlbnnnfbllpbnnn",
 "identity": "WEZPWOMKYYQYGDZJDUEPIOTTUKCCQVBYEMYHQUTWGAMHFVJJVRCQLMVGYDGG",
 },
 {
 "label": "Diagonal #4",
 "seed": "giuvfgawcbbffkvbmfjeslhbbfbfwzwnnxcbqbbjrvfbnvjltjbbbht",
 "identity": "BUICAHKIBLQWQAIONARLYROQGMRAYEAOECSZCPMTEHUIFXLKGTMAPJFDCHQI",
 },
 {
 "label": "Vortex #1",
 "seed": "uufeemuubiyxyxduxzcfbihabaysacqswsgabobknxbzciclyokobml",
 "identity": "FAEEIVWNINMPFAAWUUYMCJXMSFCAGDJNFDRCEHBFPGFCCEKUWTMCBHXBNSVL",
 },
 {
 "label": "Vortex #2",
 "seed": "hjbrfbhtbzjlvrbxtdrforbwnacahaqmsbunbonhtrhnjkxkknkhwcb",
 "identity": "PRUATXFVEFFWAEHUADBSBKOFEQTCYOXPSJHWPUSUKCHBXGMRQQEWITAELCNI",
 },
 {
 "label": "Vortex #3",
 "seed": "jklmnoipdqorwsictwwuiyvmofiqcqsykmkacmokqyccmcogocqcscw",
 "identity": "RIOIMZKDJPHCFFGVYMWSFOKVBNXAYCKUXOLHLHHCPCQDULIITMFGZQUFIMKN",
 },
 {
 "label": "Vortex #4",
 "seed": "xyzqaubquuqbqbyqayeiyaqymmemqqqmmqsqeqazsmogwoxkirmjxmc",
 "identity": "DZGTELPKNEITGBRUPCWRNZGLTMBCRPLRPERUFBZHDFDTFYTJXOUDYLSBKRRB",
 },
]

@dataclass
class TxResult:
 label: str
 identity: str
 tx_id: str | None
 status: str
 error: str | None = None

def check_assets_before(rpc: rpc_client.QubiPy_RPC, identity: str) -> dict:
 """Get asset snapshot before transaction."""
 try:
 owned = rpc.get_owned_assets(identity)
 possessed = rpc.get_possessed_assets(identity)
 
 owned_list = owned if isinstance(owned, list) else (owned.get('assets', []) if owned else [])
 possessed_list = possessed if isinstance(possessed, list) else (possessed.get('assets', []) if possessed else [])
 
 return {
 'owned_count': len(owned_list),
 'possessed_count': len(possessed_list),
 'owned': owned_list,
 'possessed': possessed_list,
 }
 except:
 return {'owned_count': 0, 'possessed_count': 0, 'owned': [], 'possessed': []}

def main() -> None:
 rpc = rpc_client.QubiPy_RPC()
 results: List[TxResult] = []
 
 print("=== Phase 2: Contract Interaction Test ===\n")
 print("All 8 identities now have 50 GENESIS assets each.")
 print("Testing if contract responds to coordinated transactions.\n")
 
 # Get baseline
 print("1. Baseline Check (before transactions):")
 baselines = {}
 for entry in SEED_TABLE:
 identity = entry["identity"]
 label = entry["label"]
 assets_before = check_assets_before(rpc, identity)
 baselines[identity] = assets_before
 print(f" {label}: {assets_before['owned_count']} owned, {assets_before['possessed_count']} possessed")
 
 # Get contract baseline
 print("\n2. Contract Baseline:")
 try:
 contract_balance_before = rpc.get_balance(CONTRACT_ID)
 print(f" Balance: {contract_balance_before.get('balance')} QU")
 print(f" Incoming: {contract_balance_before.get('numberOfIncomingTransfers')} transfers")
 except Exception as e:
 print(f" Error: {e}")
 contract_balance_before = None
 
 # Send transactions
 print("\n3. Sending Coordinated Transactions:")
 latest_tick = rpc.get_latest_tick()
 target_tick = latest_tick + TARGET_TICK_OFFSET
 
 print(f" Current tick: {latest_tick}")
 print(f" Target tick: {target_tick} (all transactions same tick)\n")
 
 start_time = time.time()
 
 for entry in SEED_TABLE:
 label = entry["label"]
 seed = entry["seed"]
 identity = entry["identity"]
 
 try:
 _, tx_bytes, _, tx_hash = create_tx(
 seed=seed,
 dest_id=CONTRACT_ID,
 amount=AMOUNT_QU,
 target_tick=target_tick,
 )
 
 response = rpc.broadcast_transaction(tx_bytes)
 tx_id = response.get("txId", response.get("transactionHash", tx_hash))
 
 results.append(TxResult(label, identity, tx_id, "SENT"))
 print(f" ✓ {label}: TX sent ({tx_id[:20]}...)")
 except Exception as e:
 results.append(TxResult(label, identity, None, "ERROR", str(e)))
 print(f" ✗ {label}: ERROR - {e}")
 
 elapsed = time.time() - start_time
 print(f"\n All transactions sent in {elapsed:.2f} seconds")
 
 # Wait and check
 print("\n4. Waiting for contract response (15 seconds)...")
 time.sleep(15)
 
 print("\n5. Checking for Changes:")
 
 # Check identities for new assets
 new_assets_found = False
 for entry in SEED_TABLE:
 identity = entry["identity"]
 label = entry["label"]
 
 assets_after = check_assets_before(rpc, identity)
 baseline = baselines[identity]
 
 owned_diff = assets_after['owned_count'] - baseline['owned_count']
 possessed_diff = assets_after['possessed_count'] - baseline['possessed_count']
 
 if owned_diff > 0 or possessed_diff > 0:
 new_assets_found = True
 print(f" 🎉 {label}: NEW ASSETS!")
 print(f" Owned: +{owned_diff}, Possessed: +{possessed_diff}")
 
 # Show new assets
 if owned_diff > 0:
 new_owned = assets_after['owned'][-owned_diff:]
 for asset in new_owned:
 name = asset.get('data', {}).get('issuedAsset', {}).get('name', 'UNKNOWN')
 units = asset.get('data', {}).get('numberOfUnits', '0')
 print(f" NEW OWNED: {name} - {units} units")
 else:
 print(f" - {label}: No new assets")
 
 # Check contract
 print("\n6. Contract Status After:")
 try:
 contract_balance_after = rpc.get_balance(CONTRACT_ID)
 if contract_balance_before:
 balance_before = int(contract_balance_before.get('balance', '0'))
 balance_after = int(contract_balance_after.get('balance', '0'))
 balance_change = balance_after - balance_before
 
 incoming_before = contract_balance_before.get('numberOfIncomingTransfers', 0)
 incoming_after = contract_balance_after.get('numberOfIncomingTransfers', 0)
 incoming_diff = incoming_after - incoming_before
 
 print(f" Balance change: {balance_change} QU")
 print(f" New incoming transfers: {incoming_diff}")
 
 if balance_change > 0:
 print(f" ✓ Contract received {balance_change} QU from transactions")
 else:
 print(f" Balance: {contract_balance_after.get('balance')} QU")
 except Exception as e:
 print(f" Error: {e}")
 
 print("\n=== Summary ===")
 success_count = sum(1 for r in results if r.status == "SENT")
 print(f"Transactions sent: {success_count}/8")
 
 if new_assets_found:
 print("🎉 NEW ASSETS DETECTED! Contract responded!")
 else:
 print("⚠️ No new assets detected yet.")
 print(" - Contract may need more time")
 print(" - Contract may require different trigger")
 print(" - Contract may need all 8 transactions in exact same tick")
 print(" - Or this might not be the next step")

if __name__ == "__main__":
 main()

