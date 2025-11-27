#!/usr/bin/env python3
"""
Sendet Transaktionen von den ECHTEN Layer-2 Identities (mit 50 GENESIS und QUBIC) 
an die Master Identity

Die echten Layer-2 Identities sind die, die der Benutzer bestätigt hat.
"""

import sys
sys.path.insert(0, "venv-tx/lib/python3.11/site-packages")

from qubipy.rpc import rpc_client
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

OUTPUT_DIR = Path("outputs/derived")
OUTPUT_JSON = OUTPUT_DIR / "real_layer2_to_master_final.json"

# Master Identity
MASTER_IDENTITY = "BZBQFLLBNCXEMGLOBHUVFTLUPLVCPQUASSILFABOFFBCADQSSUPNWLZBQEXK"

# Die ECHTEN Layer-2 Identities (vom Benutzer bestätigt)
# Mapping: Seed -> Identity (aus test_with_genesis_ownership.py)
LAYER2_IDENTITIES = [
 {"label": "Diagonal #1", "seed": "aqiosqqmacybpqxqsjniuaylmxxiwqoxqmeqyxbbtbonsjjrcwpxxdd", "identity": "OBWIIPWFPOWIQCHGJHKFZNMSSYOBYNNDLUEXAELXKEROIUKIXEUXMLZBICUD"},
 {"label": "Diagonal #2", "seed": "gwuxommmmfmtbwfzsngmukwbiltxqdknmmmnypeftamronjmablhtrr", "identity": "OQOOMLAQLGOJFFAYGXALSTDVDGQDWKWGDQJRMNZSODHMWWWNSLSQZZAHOAZE"},
 {"label": "Diagonal #3", "seed": "acgjgqqyilbpxdrborfgwfzbbbnlqnghddelvlxxxlbnnnfbllpbnnn", "identity": "WEZPWOMKYYQYGDZJDUEPIOTTUKCCQVBYEMYHQUTWGAMHFVJJVRCQLMVGYDGG"},
 {"label": "Diagonal #4", "seed": "giuvfgawcbbffkvbmfjeslhbbfbfwzwnnxcbqbbjrvfbnvjltjbbbht", "identity": "BUICAHKIBLQWQAIONARLYROQGMRAYEAOECSZCPMTEHUIFXLKGTMAPJFDCHQI"},
 {"label": "Vortex #1", "seed": "uufeemuubiyxyxduxzcfbihabaysacqswsgabobknxbzciclyokobml", "identity": "FAEEIVWNINMPFAAWUUYMCJXMSFCAGDJNFDRCEHBFPGFCCEKUWTMCBHXBNSVL"},
 {"label": "Vortex #2", "seed": "hjbrfbhtbzjlvrbxtdrforbwnacahaqmsbunbonhtrhnjkxkknkhwcb", "identity": "PRUATXFVEFFWAEHUADBSBKOFEQTCYOXPSJHWPUSUKCHBXGMRQQEWITAELCNI"},
 {"label": "Vortex #3", "seed": "jklmnoipdqorwsictwwuiyvmofiqcqsykmkacmokqyccmcogocqcscw", "identity": "RIOIMZKDJPHCFFGVYMWSFOKVBNXAYCKUXOLHLHHCPCQDULIITMFGZQUFIMKN"},
 {"label": "Vortex #4", "seed": "xyzqaubquuqbqbyqayeiyaqymmemqqqmmqsqeqazsmogwoxkirmjxmc", "identity": "DZGTELPKNEITGBRUPCWRNZGLTMBCRPLRPERUFBZHDFDTFYTJXOUDYLSBKRRB"},
]

# Payloads zum Testen
PAYLOADS = [
 {"name": "MASTER", "payload": "MASTER"},
 {"name": "ZERO", "payload": "ZERO"},
 {"name": "PROOF", "payload": "PROOF"},
 {"name": "ACTIVATE", "payload": "ACTIVATE"},
 {"name": "Empty", "payload": ""},
]

def build_tx_with_payload(seed: str, dest_identity: str, amount: int, target_tick: int, payload: str) -> bytes:
 """Build transaction with payload."""
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
 
 # 3. Amount (8 bytes, little-endian)
 amount_qubic = int(amount * 1_000_000) # Convert to microQU
 built_data.extend(amount_qubic.to_bytes(8, byteorder='little'))
 offset += 8
 
 # 4. Target Tick (4 bytes, little-endian)
 built_data.extend(target_tick.to_bytes(4, byteorder='little'))
 offset += 4
 
 # 5. Input Type (2 bytes) - always 0 for simple transfers
 input_type = 0
 built_data.extend(input_type.to_bytes(2, byteorder='little'))
 offset += 2
 
 # 6. Input Size (2 bytes) - size of the payload
 payload_bytes = payload.encode('utf-8') if payload else b''
 input_size = len(payload_bytes)
 built_data.extend(input_size.to_bytes(2, byteorder='little'))
 offset += 2
 
 # 7. Payload (N bytes) - inserted BEFORE signing
 if payload_bytes:
 built_data.extend(payload_bytes)
 offset += len(payload_bytes)
 
 # Sign the transaction digest (which now includes the payload)
 tx_digest = kangaroo_twelve(built_data, offset, 32)
 signature = sign(subseed, source_pubkey, tx_digest)
 
 # 8. Signature (64 bytes)
 built_data.extend(signature)
 
 return bytes(built_data)

def check_balance_and_assets(rpc, identity: str) -> dict:
 """Check balance and assets of an identity."""
 result = {"balance": 0, "genesis_count": 0, "total_assets": 0, "error": None}
 
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
 except Exception as e:
 result["error"] = f"Assets error: {e}"
 except Exception as e:
 result["error"] = f"Balance error: {e}"
 
 return result

def main():
 print("=" * 80)
 print("SEND FROM REAL LAYER-2 TO MASTER IDENTITY")
 print("=" * 80)
 print()
 print(f"Master Identity: {MASTER_IDENTITY}")
 print(f"Layer-2 Identities: {len(LAYER2_IDENTITIES)}")
 print()
 
 rpc = rpc_client.QubiPy_RPC()
 
 # Check Master Identity VORHER
 print("=" * 80)
 print("MASTER IDENTITY: BEFORE")
 print("=" * 80)
 print()
 
 master_before = check_balance_and_assets(rpc, MASTER_IDENTITY)
 print(f"Balance: {master_before['balance'] / 1_000_000:.2f} QUBIC")
 print(f"Assets: {master_before['total_assets']}")
 print()
 
 # Check alle Layer-2 Identities
 print("=" * 80)
 print("LAYER-2 IDENTITIES CHECK")
 print("=" * 80)
 print()
 
 layer2_info = []
 for item in LAYER2_IDENTITIES:
 label = item["label"]
 identity = item["identity"]
 seed = item["seed"]
 
 print(f"{label}:")
 print(f" Identity: {identity}")
 
 info = check_balance_and_assets(rpc, identity)
 balance_qubic = info["balance"] / 1_000_000
 
 print(f" Balance: {balance_qubic:.2f} QUBIC ({info['balance']} QU)")
 print(f" GENESIS: {info['genesis_count']}")
 print(f" Total Assets: {info['total_assets']}")
 if info.get("error"):
 print(f" ⚠️ Error: {info['error']}")
 print()
 
 layer2_info.append({
 "label": label,
 "seed": seed,
 "identity": identity,
 "balance": info["balance"],
 "genesis_count": info["genesis_count"],
 "total_assets": info["total_assets"],
 })
 
 # Sende Transaktionen von Identities mit Balance
 print("=" * 80)
 print("SENDING TRANSACTIONS")
 print("=" * 80)
 print()
 
 results = []
 
 for item in LAYER2_IDENTITIES:
 label = item["label"]
 seed = item["seed"]
 identity = item["identity"]
 
 # Finde Info
 info = next((i for i in layer2_info if i["identity"] == identity), None)
 if not info:
 continue
 
 balance = info["balance"]
 
 if balance < 1_000_000: # Mindestens 1 QUBIC
 print(f"{label}: ⚠️ Insufficient balance ({balance / 1_000_000:.2f} QUBIC)")
 continue
 
 print(f"{label}: ✅ Has balance ({balance / 1_000_000:.2f} QUBIC)")
 
 # Sende mit verschiedenen Payloads
 for payload_info in PAYLOADS:
 payload_name = payload_info["name"]
 payload = payload_info["payload"]
 
 try:
 latest_tick = rpc.get_latest_tick()
 target_tick = latest_tick + 25
 
 tx_bytes = build_tx_with_payload(
 seed=seed,
 dest_identity=MASTER_IDENTITY,
 amount=1, # 1 QUBIC
 target_tick=target_tick,
 payload=payload,
 )
 
 response = rpc.broadcast_transaction(tx_bytes)
 tx_id = response.get("txId") or response.get("transactionHash") or "UNKNOWN"
 
 print(f" 📤 {payload_name}: {tx_id}")
 
 results.append({
 "label": label,
 "seed": seed[:20] + "...",
 "identity": identity,
 "payload": payload,
 "payload_name": payload_name,
 "tx_id": tx_id,
 "target_tick": target_tick,
 "status": "sent",
 })
 
 time.sleep(3.0) # Rate limiting
 except Exception as e:
 print(f" ❌ {payload_name}: Error - {e}")
 results.append({
 "label": label,
 "seed": seed[:20] + "...",
 "identity": identity,
 "payload": payload,
 "payload_name": payload_name,
 "status": "error",
 "error": str(e),
 })
 
 print()
 time.sleep(5.0) # Pause zwischen Identities
 
 # Check Master Identity NACHHER
 print("=" * 80)
 print("MASTER IDENTITY: AFTER")
 print("=" * 80)
 print()
 
 time.sleep(10.0) # Warte auf Bestätigung
 
 master_after = check_balance_and_assets(rpc, MASTER_IDENTITY)
 print(f"Balance: {master_after['balance'] / 1_000_000:.2f} QUBIC")
 print(f"Assets: {master_after['total_assets']}")
 print()
 
 balance_change = master_after["balance"] - master_before["balance"]
 assets_change = master_after["total_assets"] - master_before["total_assets"]
 
 print(f"Balance Change: {balance_change / 1_000_000:.2f} QUBIC")
 print(f"Assets Change: {assets_change}")
 print()
 
 # Speichere Ergebnisse
 OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
 
 final_results = {
 "analysis_date": time.strftime("%Y-%m-%d %H:%M:%S"),
 "master_identity": MASTER_IDENTITY,
 "master_before": {
 "balance": master_before["balance"],
 "total_assets": master_before["total_assets"],
 },
 "master_after": {
 "balance": master_after["balance"],
 "total_assets": master_after["total_assets"],
 },
 "master_changes": {
 "balance_change": balance_change,
 "assets_change": assets_change,
 },
 "layer2_info": layer2_info,
 "transactions": results,
 }
 
 with OUTPUT_JSON.open("w", encoding="utf-8") as f:
 json.dump(final_results, f, indent=2, ensure_ascii=False)
 
 print("=" * 80)
 print("✅ COMPLETE")
 print("=" * 80)
 print()
 print(f"💾 Results saved to: {OUTPUT_JSON}")
 
 successful = [r for r in results if r.get("status") == "sent"]
 print(f"✅ {len(successful)} successful transaction(s)")
 
 if balance_change > 0:
 print(f"🎉 Master Identity received {balance_change / 1_000_000:.2f} QUBIC!")
 if assets_change > 0:
 print(f"🎉 Master Identity received {assets_change} new asset(s)!")

if __name__ == "__main__":
 main()

