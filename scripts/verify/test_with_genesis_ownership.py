#!/usr/bin/env python3
"""
Test With GENESIS Ownership: Maybe the contract requires holding GENESIS before triggering.

Since GENESIS is a tradeable asset, maybe the contract checks if the sender owns GENESIS
before processing the trigger.
"""

from __future__ import annotations

import time
from qubipy.rpc import rpc_client
from qubipy.tx.utils import create_tx

CONTRACT_ID = "POCCZYCKTRQGHFIPWGSBLJTEQFDDVVBMNUHNCKMRACBGQOPBLURNRCBAFOBD"
AMOUNT_QU = 1
TARGET_TICK_OFFSET = 25

# Layer-2 identities (we know they have 50 GENESIS each)
LAYER2_IDENTITIES = [
 {"label": "Diagonal #1", "block_id": 1, "seed": "aqiosqqmacybpqxqsjniuaylmxxiwqoxqmeqyxbbtbonsjjrcwpxxdd", "identity": "OBWIIPWFPOWIQCHGJHKFZNMSSYOBYNNDLUEXAELXKEROIUKIXEUXMLZBICUD"},
 {"label": "Diagonal #2", "block_id": 2, "seed": "gwuxommmmfmtbwfzsngmukwbiltxqdknmmmnypeftamronjmablhtrr", "identity": "OQOOMLAQLGOJFFAYGXALSTDVDGQDWKWGDQJRMNZSODHMWWWNSLSQZZAHOAZE"},
 {"label": "Diagonal #3", "block_id": 3, "seed": "acgjgqqyilbpxdrborfgwfzbbbnlqnghddelvlxxxlbnnnfbllpbnnn", "identity": "WEZPWOMKYYQYGDZJDUEPIOTTUKCCQVBYEMYHQUTWGAMHFVJJVRCQLMVGYDGG"},
 {"label": "Diagonal #4", "block_id": 4, "seed": "giuvfgawcbbffkvbmfjeslhbbfbfwzwnnxcbqbbjrvfbnvjltjbbbht", "identity": "BUICAHKIBLQWQAIONARLYROQGMRAYEAOECSZCPMTEHUIFXLKGTMAPJFDCHQI"},
 {"label": "Vortex #1", "block_id": 5, "seed": "uufeemuubiyxyxduxzcfbihabaysacqswsgabobknxbzciclyokobml", "identity": "FAEEIVWNINMPFAAWUUYMCJXMSFCAGDJNFDRCEHBFPGFCCEKUWTMCBHXBNSVL"},
 {"label": "Vortex #2", "block_id": 6, "seed": "hjbrfbhtbzjlvrbxtdrforbwnacahaqmsbunbonhtrhnjkxkknkhwcb", "identity": "PRUATXFVEFFWAEHUADBSBKOFEQTCYOXPSJHWPUSUKCHBXGMRQQEWITAELCNI"},
 {"label": "Vortex #3", "block_id": 7, "seed": "jklmnoipdqorwsictwwuiyvmofiqcqsykmkacmokqyccmcogocqcscw", "identity": "RIOIMZKDJPHCFFGVYMWSFOKVBNXAYCKUXOLHLHHCPCQDULIITMFGZQUFIMKN"},
 {"label": "Vortex #4", "block_id": 8, "seed": "xyzqaubquuqbqbyqayeiyaqymmemqqqmmqsqeqazsmogwoxkirmjxmc", "identity": "DZGTELPKNEITGBRUPCWRNZGLTMBCRPLRPERUFBZHDFDTFYTJXOUDYLSBKRRB"},
]

def check_genesis_ownership(rpc: rpc_client.QubiPy_RPC, identity: str) -> bool:
 """Check if identity owns GENESIS asset."""
 try:
 owned = rpc.get_owned_assets(identity)
 if isinstance(owned, list):
 for asset in owned:
 name = asset.get("data", {}).get("issuedAsset", {}).get("name", "")
 if name == "GENESIS":
 units = asset.get("data", {}).get("numberOfUnits", "0")
 print(f" ✅ Owns {units} GENESIS")
 return True
 return False
 except Exception as e:
 print(f" ⚠️ Error checking assets: {e}")
 return False

def main():
 print("=" * 80)
 print("TEST: WITH GENESIS OWNERSHIP")
 print("=" * 80)
 print()
 print("Hypothesis: Contract requires GENESIS ownership before triggering")
 print("Strategy: Send synchronized transactions from identities that own GENESIS")
 print()
 
 rpc = rpc_client.QubiPy_RPC()
 current_tick = rpc.get_latest_tick()
 target_tick = current_tick + TARGET_TICK_OFFSET
 
 print(f"Current tick: {current_tick}")
 print(f"Target tick: {target_tick}")
 print()
 
 # Check GENESIS ownership
 print("Checking GENESIS ownership...")
 identities_with_genesis = []
 for entry in LAYER2_IDENTITIES:
 label = entry["label"]
 identity = entry["identity"]
 print(f" {label}: ", end="")
 if check_genesis_ownership(rpc, identity):
 identities_with_genesis.append(entry)
 else:
 print(f" ❌ No GENESIS")
 print()
 
 if not identities_with_genesis:
 print("❌ No identities own GENESIS. Cannot test this hypothesis.")
 return 1
 
 print(f"✅ {len(identities_with_genesis)} identities own GENESIS")
 print()
 print("Sending synchronized transactions (no payload)...")
 print()
 
 tx_ids = []
 for entry in identities_with_genesis:
 label = entry["label"]
 seed = entry["seed"]
 
 try:
 tx_bytes, _, _, tx_hash = create_tx(
 seed=seed,
 dest_id=CONTRACT_ID,
 amount=AMOUNT_QU,
 target_tick=target_tick,
 )
 response = rpc.broadcast_transaction(tx_bytes)
 tx_id = response.get("txId", tx_hash)
 tx_ids.append(tx_id)
 print(f"✅ {label}: TX {tx_id[:20]}...")
 except Exception as e:
 print(f"❌ {label}: Error - {e}")
 tx_ids.append(None)
 
 time.sleep(0.01)
 
 print()
 print("=" * 80)
 print("TRANSACTIONS SENT")
 print("=" * 80)
 print()
 print("Check wallets in 20-30 seconds for new assets")
 print("If this doesn't work, we need to try other approaches")

if __name__ == "__main__":
 raise SystemExit(main())

