#!/usr/bin/env python3
"""
Sendet Transaktionen von den ECHTEN Layer-2 Identities (mit 50 GENESIS) an die Master Identity

Die echten Layer-2 Identities sind die, die aus den Seeds abgeleitet wurden
und die 50 GENESIS Assets haben.
"""

import sys
sys.path.insert(0, "venv-tx/lib/python3.11/site-packages")

from qubipy.rpc import rpc_client
try:
 from qubipy.tx.utils import (
 get_public_key_from_identity,
 get_subseed_from_seed,
 get_private_key_from_subseed,
 get_public_key_from_private_key,
 )
 from qubipy.crypto.utils import sign, kangaroo_twelve
except:
 # Fallback for Docker
 from qubipy.crypto.utils import (
 get_public_key_from_identity,
 get_subseed_from_seed,
 get_private_key_from_subseed,
 get_public_key_from_private_key,
 sign,
 kangaroo_twelve,
 )
import time
import json
from pathlib import Path
from typing import Dict, Optional

OUTPUT_DIR = Path("outputs/derived")
OUTPUT_JSON = OUTPUT_DIR / "real_layer2_to_master_transactions.json"

# Master Identity
MASTER_IDENTITY = "BZBQFLLBNCXEMGLOBHUVFTLUPLVCPQUASSILFABOFFBCADQSSUPNWLZBQEXK"

# Die ECHTEN Layer-2 Identities (aus verschiedenen Quellen - die mit 50 GENESIS)
# Es gibt zwei Sets - lass uns beide checkn
LAYER2_SET1 = [
 {"label": "Diagonal #1", "seed": "aqiosqqmacybpqxqsjniuaylmxxiwqoxqmeqyxbbtbonsjjrcwpxxdd", "identity": "CYTORJWZCJFCYXAHJPLPPCWPVOXTDZBWQYVWANQDYQCCIORJTVMPBIXBKIVP"},
 {"label": "Diagonal #2", "seed": "gwuxommmmfmtbwfzsngmukwbiltxqdknmmmnypeftamronjmablhtrr", "identity": "FPEXLMCOGJNYAAELTBSEDHAZCCNAGXJRPRFNBEXUKPDHFTVAHETKPANQCMLM"},
 {"label": "Diagonal #3", "seed": "acgjgqqyilbpxdrborfgwfzbbbnlqnghddelvlxxxlbnnnfbllpbnnn", "identity": "ABCXUAPWHTDRJDASQEZSNCDAMXNJAXDTNESWQLNWPZBBUXDGNJLGYXETNGHN"},
 {"label": "Diagonal #4", "seed": "giuvfgawcbbffkvbmfjeslhbbfbfwzwnnxcbqbbjrvfbnvjltjbbbht", "identity": "AGTIRJYQVZXUEFAUCPEBEYHDAFXZFMFOARDSUKLHHBETDIVPWVZMOORUOXSD"},
 {"label": "Vortex #1", "seed": "uufeemuubiyxyxduxzcfbihabaysacqswsgabobknxbzciclyokobml", "identity": "GNMLDHIPZJHJDNCCCRFHVDDPEIHJEWOPVVAXQRFIBYDZBNDHTELZIANUDAWB"},
 {"label": "Vortex #2", "seed": "hjbrfbhtbzjlvrbxtdrforbwnacahaqmsbunbonhtrhnjkxkknkhwcb", "identity": "ADVDNZIGNSCXAODGDMEXMKICVHFOHBROQQMVZOGAMVASHQURDBPDNJRJJQRM"},
 {"label": "Vortex #3", "seed": "jklmnoipdqorwsictwwuiyvmofiqcqsykmkacmokqyccmcogocqcscw", "identity": "HFVFDNEHUVRRBIESYPSSRPNJSVVSDBIPNAXAHIKISLAKYZFKMWNJXVVUEUQJ"},
 {"label": "Vortex #4", "seed": "xyzqaubquuqbqbyqayeiyaqymmemqqqmmqsqeqazsmogwoxkirmjxmc", "identity": "BIARJWYAYURJYJBXXEDMQOKGSJXBFNWCDSHXZILITIDHCMJYUMPPXQZQAXNR"},
]

# Alternative Set (aus test_with_genesis_ownership.py)
LAYER2_SET2 = [
 {"label": "Diagonal #1", "seed": "aqiosqqmacybpqxqsjniuaylmxxiwqoxqmeqyxbbtbonsjjrcwpxxdd", "identity": "OBWIIPWFPOWIQCHGJHKFZNMSSYOBYNNDLUEXAELXKEROIUKIXEUXMLZBICUD"},
 {"label": "Diagonal #2", "seed": "gwuxommmmfmtbwfzsngmukwbiltxqdknmmmnypeftamronjmablhtrr", "identity": "OQOOMLAQLGOJFFAYGXALSTDVDGQDWKWGDQJRMNZSODHMWWWNSLSQZZAHOAZE"},
 {"label": "Diagonal #3", "seed": "acgjgqqyilbpxdrborfgwfzbbbnlqnghddelvlxxxlbnnnfbllpbnnn", "identity": "WEZPWOMKYYQYGDZJDUEPIOTTUKCCQVBYEMYHQUTWGAMHFVJJVRCQLMVGYDGG"},
 {"label": "Diagonal #4", "seed": "giuvfgawcbbffkvbmfjeslhbbfbfwzwnnxcbqbbjrvfbnvjltjbbbht", "identity": "BUICAHKIBLQWQAIONARLYROQGMRAYEAOECSZCPMTEHUIFXLKGTMAPJFDCHQI"},
 {"label": "Vortex #1", "seed": "uufeemuubiyxyxduxzcfbihabaysacqswsgabobknxbzciclyokobml", "identity": "FAEEIVWNINMPFAAWUUYMCJXMSFCAGDJNFDRCEHBFPGFCCEKUWTMCBHXBNSVL"},
 {"label": "Vortex #2", "seed": "hjbrfbhtbzjlvrbxtdrforbwnacahaqmsbunbonhtrhnjkxkknkhwcb", "identity": "PRUATXFVEFFWAEHUADBSBKOFEQTCYOXPSJHWPUSUKCHBXGMRQQEWITAELCNI"},
 {"label": "Vortex #3", "seed": "jklmnoipdqorwsictwwuiyvmofiqcqsykmkacmokqyccmcogocqcscw", "identity": "RIOIMZKDJPHCFFGVYMWSFOKVBNXAYCKUXOLHLHHCPCQDULIITMFGZQUFIMKN"},
 {"label": "Vortex #4", "seed": "xyzqaubquuqbqbyqayeiyaqymmemqqqmmqsqeqazsmogwoxkirmjxmc", "identity": "DZGTELPKNEITGBRUPCWRNZGLTMBCRPLRPERUFBZHDFDTFYTJXOUDYLSBKRRB"},
]

# Payloads
PAYLOADS = ["MASTER", "ZERO", "PROOF", "ACTIVATE", ""]

def build_tx_with_payload(seed: str, dest_identity: str, amount: int, target_tick: int, payload: str) -> bytes:
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
 
 payload_bytes = payload.encode('utf-8') if payload else b''
 built_data.extend(len(payload_bytes).to_bytes(2, byteorder='little'))
 offset += 2
 if payload_bytes:
 built_data.extend(payload_bytes)
 offset += len(payload_bytes)
 
 tx_digest = kangaroo_twelve(built_data, offset, 32)
 signature = sign(subseed, source_pubkey, tx_digest)
 built_data.extend(signature)
 
 return bytes(built_data)

def check_balance_and_assets(rpc, identity: str) -> Dict:
 """Check balance and assets of an identity."""
 result = {"balance": 0, "genesis_count": 0, "total_assets": 0}
 
 try:
 time.sleep(2.0)
 balance_data = rpc.get_balance(identity)
 if balance_data:
 result["balance"] = int(balance_data.get("balance", 0))
 
 try:
 time.sleep(2.0)
 assets = rpc.get_owned_assets(identity)
 if assets:
 result["total_assets"] = len(assets)
 for asset in assets:
 asset_data = asset.get("data", {})
 issued_asset = asset_data.get("issuedAsset", {})
 if issued_asset.get("name") == "GENESIS":
 result["genesis_count"] = int(asset_data.get("numberOfUnits", 0))
 except:
 pass
 except:
 pass
 
 return result

def main():
 print("=" * 80)
 print("SEND FROM REAL LAYER-2 TO MASTER IDENTITY")
 print("=" * 80)
 print()
 print(f"Master Identity: {MASTER_IDENTITY}")
 print()
 
 rpc = rpc_client.QubiPy_RPC()
 
 # Teste beide Sets
 all_sets = [
 ("Set 1 (CORRECT_LAYER2_MASTER_DATA)", LAYER2_SET1),
 ("Set 2 (test_with_genesis_ownership)", LAYER2_SET2),
 ]
 
 results = []
 
 for set_name, layer2_set in all_sets:
 print("=" * 80)
 print(f"TESTING: {set_name}")
 print("=" * 80)
 print()
 
 # Check Balance und Assets
 print("Checking balances and assets...")
 print()
 
 for item in layer2_set:
 label = item["label"]
 identity = item["identity"]
 
 info = check_balance_and_assets(rpc, identity)
 balance_qubic = info["balance"] / 1_000_000
 
 print(f"{label}: {balance_qubic:.2f} QUBIC, {info['genesis_count']} GENESIS, {info['total_assets']} assets")
 
 # Wenn Balance vorhanden, sende Transaktion
 if info["balance"] >= 1_000_000: # Mindestens 1 QUBIC
 print(f" ✅ Has balance - will send transaction")
 
 # Sende mit verschiedenen Payloads
 for payload in PAYLOADS[:1]: # Nur ersten Payload testen
 try:
 latest_tick = rpc.get_latest_tick()
 target_tick = latest_tick + 25
 
 tx_bytes = build_tx_with_payload(
 seed=item["seed"],
 dest_identity=MASTER_IDENTITY,
 amount=1, # 1 QUBIC
 target_tick=target_tick,
 payload=payload,
 )
 
 response = rpc.broadcast_transaction(tx_bytes)
 tx_id = response.get("txId") or response.get("transactionHash") or "UNKNOWN"
 
 print(f" 📤 Sent {payload or 'empty'} payload: {tx_id}")
 
 results.append({
 "set": set_name,
 "label": label,
 "seed": item["seed"],
 "identity": identity,
 "payload": payload,
 "tx_id": tx_id,
 "status": "sent",
 })
 
 time.sleep(3.0)
 except Exception as e:
 print(f" ❌ Error: {e}")
 else:
 print(f" ⚠️ No balance")
 
 print()
 
 time.sleep(5.0)
 
 # Speichere Ergebnisse
 OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
 with OUTPUT_JSON.open("w") as f:
 json.dump(results, f, indent=2)
 
 print("=" * 80)
 print("✅ COMPLETE")
 print("=" * 80)
 print()
 print(f"💾 Results saved to: {OUTPUT_JSON}")
 print(f"✅ {len(results)} transaction(s) sent")

if __name__ == "__main__":
 main()

