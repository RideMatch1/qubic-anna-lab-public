#!/usr/bin/env python3
"""
Smart Contract Test mit korrigierten Payloads (Gemini's Vorschlag)

Korrekturen:
- Layer-Index = 1 (nicht 2) - wir senden von Layer 1
- Payload: "[Block-ID, 1, Tick-Gap]"
- Brute-Force Tick-Gap um 1649 (1600-1700)
- Verwende Layer-1 Seeds (die 8 Wallets mit Balance)
"""

from __future__ import annotations

import json
import time
from pathlib import Path
from qubipy.rpc import rpc_client
from qubipy.tx.utils import (
 get_public_key_from_identity,
 get_subseed_from_seed,
 get_private_key_from_subseed,
 get_public_key_from_private_key,
)
from qubipy.crypto.utils import sign, kangaroo_twelve

CONTRACT_ID = "POCCZYCKTRQGHFIPWGSBLJTEQFDDVVBMNUHNCKMRACBGQOPBLURNRCBAFOBD"
AMOUNT_QU = 1
TARGET_TICK_OFFSET = 25

# Die 8 korrekten Layer-1 Seeds → Layer-2 Identities
# WICHTIG: Layer-1 Seeds sind Private Keys for Layer-2 Identities (nicht Layer-1)!
CORRECT_LAYER1_TO_LAYER2 = [
 {"label": "Diagonal #1", "block_id": 1, "seed": "aqiosqqmacybpqxqsjniuaylmxxiwqoxqmeqyxbbtbonsjjrcwpxxdd", "layer2_identity": "OBWIIPWFPOWIQCHGJHKFZNMSSYOBYNNDLUEXAELXKEROIUKIXEUXMLZBICUD"},
 {"label": "Diagonal #2", "block_id": 2, "seed": "gwuxommmmfmtbwfzsngmukwbiltxqdknmmmnypeftamronjmablhtrr", "layer2_identity": "OQOOMLAQLGOJFFAYGXALSTDVDGQDWKWGDQJRMNZSODHMWWWNSLSQZZAHOAZE"},
 {"label": "Diagonal #3", "block_id": 3, "seed": "acgjgqqyilbpxdrborfgwfzbbbnlqnghddelvlxxxlbnnnfbllpbnnn", "layer2_identity": "WEZPWOMKYYQYGDZJDUEPIOTTUKCCQVBYEMYHQUTWGAMHFVJJVRCQLMVGYDGG"},
 {"label": "Diagonal #4", "block_id": 4, "seed": "giuvfgawcbbffkvbmfjeslhbbfbfwzwnnxcbqbbjrvfbnvjltjbbbht", "layer2_identity": "BUICAHKIBLQWQAIONARLYROQGMRAYEAOECSZCPMTEHUIFXLKGTMAPJFDCHQI"},
 {"label": "Vortex #1", "block_id": 5, "seed": "uufeemuubiyxyxduxzcfbihabaysacqswsgabobknxbzciclyokobml", "layer2_identity": "FAEEIVWNINMPFAAWUUYMCJXMSFCAGDJNFDRCEHBFPGFCCEKUWTMCBHXBNSVL"},
 {"label": "Vortex #2", "block_id": 6, "seed": "hjbrfbhtbzjlvrbxtdrforbwnacahaqmsbunbonhtrhnjkxkknkhwcb", "layer2_identity": "PRUATXFVEFFWAEHUADBSBKOFEQTCYOXPSJHWPUSUKCHBXGMRQQEWITAELCNI"},
 {"label": "Vortex #3", "block_id": 7, "seed": "jklmnoipdqorwsictwwuiyvmofiqcqsykmkacmokqyccmcogocqcscw", "layer2_identity": "RIOIMZKDJPHCFFGVYMWSFOKVBNXAYCKUXOLHLHHCPCQDULIITMFGZQUFIMKN"},
 {"label": "Vortex #4", "block_id": 8, "seed": "xyzqaubquuqbqbyqayeiyaqymmemqqqmmqsqeqazsmogwoxkirmjxmc", "layer2_identity": "DZGTELPKNEITGBRUPCWRNZGLTMBCRPLRPERUFBZHDFDTFYTJXOUDYLSBKRRB"},
]

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
 
 # 1. Source Public Key (32 bytes)
 built_data.extend(source_pubkey)
 offset += len(source_pubkey)
 
 # 2. Destination Public Key (32 bytes)
 built_data.extend(dest_pubkey)
 offset += len(dest_pubkey)
 
 # 3. Amount (8 bytes)
 amount_qubic = int(amount * 1_000_000) # Convert to microQU
 built_data.extend(amount_qubic.to_bytes(8, byteorder='little'))
 offset += 8
 
 # 4. Target Tick (4 bytes)
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

def check_assets(rpc, identity: str) -> dict:
 """Check assets of an identity."""
 try:
 info = rpc.get_identity_info(identity)
 assets = info.get("assets", {})
 genesis_count = assets.get("POCCZYCKTRQGHFIPWGSBLJTEQFDDVVBMNUHNCKMRACBGQOPBLURNRCBAFOBD", {}).get("amount", 0)
 return {
 "total_assets": len(assets),
 "genesis_count": genesis_count,
 "all_assets": assets,
 }
 except Exception as e:
 return {"error": str(e)}

def main():
 print("=" * 80)
 print("SMART CONTRACT TEST - KORRIGIERTE PAYLOADS")
 print("=" * 80)
 print()
 print("Korrekturen (Gemini's Vorschlag):")
 print(" - Layer-Index = 1 (nicht 2)")
 print(" - Payload: '[Block-ID, 1, Tick-Gap]'")
 print(" - Brute-Force Tick-Gap: 1600-1700")
 print(" - Verwende ORIGINAL Layer-1 Seeds (mit Balance)")
 print()
 
 rpc = rpc_client.QubiPy_RPC()
 
 # Teste zuerst mit bekanntem Tick-Gap (1649)
 print("=" * 80)
 print("PHASE 1: Test mit Tick-Gap = 1649")
 print("=" * 80)
 print()
 
 current_tick = rpc.get_latest_tick()
 target_tick = current_tick + TARGET_TICK_OFFSET
 
 print(f"Current tick: {current_tick}")
 print(f"Target tick: {target_tick}")
 print()
 
 # Check Assets vorher (for Layer-2 Identities)
 print("Checking assets BEFORE transactions...")
 assets_before = {}
 for entry in CORRECT_LAYER1_TO_LAYER2:
 identity = entry["layer2_identity"]
 assets = check_assets(rpc, identity)
 assets_before[identity] = assets
 print(f" {entry['label']}: {assets.get('genesis_count', 0)} GENESIS")
 print()
 
 # Sende Transaktionen mit korrigierten Payloads
 # WICHTIG: Verwende Layer-1 Seeds (die sind Private Keys for Layer-2 Identities)
 print("Sending transactions with corrected payloads...")
 print("Using Layer-1 Seeds (Private Keys for Layer-2 Identities)")
 print()
 
 tx_results = []
 for entry in CORRECT_LAYER1_TO_LAYER2:
 label = entry["label"]
 seed = entry["seed"] # Layer-1 Seed (Private Key for Layer-2 Identity)
 block_id = entry["block_id"]
 layer2_identity = entry["layer2_identity"]
 
 # Korrigierter Payload: [Block-ID, 1, Tick-Gap]
 payload = f"{block_id},1,1649"
 
 try:
 tx_bytes = build_tx_with_payload(
 seed=seed,
 dest_identity=CONTRACT_ID,
 amount=AMOUNT_QU,
 target_tick=target_tick,
 payload=payload,
 )
 response = rpc.broadcast_transaction(tx_bytes)
 tx_id = response.get("txId") or response.get("transactionHash") or "UNKNOWN"
 
 tx_results.append({
 "label": label,
 "block_id": block_id,
 "layer2_identity": layer2_identity,
 "seed": seed,
 "payload": payload,
 "tx_id": tx_id,
 "status": "sent",
 })
 
 print(f"✅ {label} (Block {block_id}): TX {tx_id[:20]}... | Payload: {payload}")
 except Exception as e:
 print(f"❌ {label} (Block {block_id}): Error - {e}")
 tx_results.append({
 "label": label,
 "block_id": block_id,
 "layer2_identity": layer2_identity,
 "seed": seed,
 "payload": payload,
 "status": "error",
 "error": str(e),
 })
 
 time.sleep(0.5) # Small delay between transactions
 
 print()
 print("Waiting 30 seconds for transactions to process...")
 time.sleep(30)
 
 # Check Assets nachher
 print()
 print("Checking assets AFTER transactions...")
 assets_after = {}
 for entry in CORRECT_LAYER1_TO_LAYER2:
 identity = entry["layer2_identity"]
 assets = check_assets(rpc, identity)
 assets_after[identity] = assets
 before_count = assets_before.get(identity, {}).get("genesis_count", 0)
 after_count = assets.get("genesis_count", 0)
 diff = after_count - before_count
 
 if diff > 0:
 print(f" ✅ {entry['label']}: {before_count} → {after_count} GENESIS (+{diff})")
 else:
 print(f" ⚠️ {entry['label']}: {before_count} → {after_count} GENESIS (no change)")
 
 print()
 print("=" * 80)
 print("PHASE 1 COMPLETE")
 print("=" * 80)
 print()
 
 # Speichere Ergebnisse
 OUTPUT_DIR = Path("outputs/derived")
 OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
 
 results = {
 "phase": 1,
 "tick_gap": 1649,
 "payload_format": "[Block-ID, 1, Tick-Gap]",
 "transactions": tx_results,
 "assets_before": assets_before,
 "assets_after": assets_after,
 }
 
 with (OUTPUT_DIR / "smart_contract_test_corrected.json").open("w") as f:
 json.dump(results, f, indent=2)
 
 print(f"💾 Results saved to: {OUTPUT_DIR / 'smart_contract_test_corrected.json'}")
 print()
 
 # Wenn Phase 1 nicht funktioniert, starte Brute-Force
 any_success = any(
 assets_after.get(entry["layer2_identity"], {}).get("genesis_count", 0) > 
 assets_before.get(entry["layer2_identity"], {}).get("genesis_count", 0)
 for entry in CORRECT_LAYER1_TO_LAYER2
 )
 
 if not any_success:
 print("=" * 80)
 print("PHASE 2: Brute-Force Tick-Gap (1600-1700)")
 print("=" * 80)
 print()
 print("Tick-Gap 1649 didn't work. Starting brute-force...")
 print("This will test Tick-Gap values from 1600 to 1700")
 print()
 
 # Teste nur mit Block 1 zuerst (um Zeit zu sparen)
 test_entry = CORRECT_LAYER1_TO_LAYER2[0]
 print(f"Testing with {test_entry['label']} (Block {test_entry['block_id']})...")
 print()
 
 for tick_gap in range(1600, 1701):
 payload = f"{test_entry['block_id']},1,{tick_gap}"
 
 try:
 tx_bytes = build_tx_with_payload(
 seed=test_entry["seed"], # Layer-1 Seed (Private Key for Layer-2)
 dest_identity=CONTRACT_ID,
 amount=AMOUNT_QU,
 target_tick=current_tick + TARGET_TICK_OFFSET,
 payload=payload,
 )
 response = rpc.broadcast_transaction(tx_bytes)
 tx_id = response.get("txId") or "UNKNOWN"
 
 print(f" Testing Tick-Gap {tick_gap}: TX {tx_id[:20]}...")
 
 time.sleep(5) # Wait for transaction
 
 # Check assets (for Layer-2 Identity)
 assets = check_assets(rpc, test_entry["layer2_identity"])
 genesis_count = assets.get("genesis_count", 0)
 before_count = assets_before.get(test_entry["layer2_identity"], {}).get("genesis_count", 0)
 
 if genesis_count > before_count:
 print(f" ✅ SUCCESS! Tick-Gap {tick_gap} worked! (+{genesis_count - before_count} GENESIS)")
 print()
 print(f" 🎯 CORRECT TICK-GAP: {tick_gap}")
 print(f" 📤 Now testing all 8 blocks with Tick-Gap {tick_gap}...")
 print()
 
 # Teste alle 8 Blocks mit gefundenem Tick-Gap
 for entry in CORRECT_LAYER1_TO_LAYER2:
 payload_all = f"{entry['block_id']},1,{tick_gap}"
 try:
 tx_bytes = build_tx_with_payload(
 seed=entry["seed"], # Layer-1 Seed
 dest_identity=CONTRACT_ID,
 amount=AMOUNT_QU,
 target_tick=rpc.get_latest_tick() + TARGET_TICK_OFFSET,
 payload=payload_all,
 )
 rpc.broadcast_transaction(tx_bytes)
 print(f" ✅ {entry['label']}: Sent with Tick-Gap {tick_gap}")
 time.sleep(0.5)
 except Exception as e:
 print(f" ❌ {entry['label']}: Error - {e}")
 
 break
 else:
 print(f" ⚠️ Tick-Gap {tick_gap}: No change")
 
 except Exception as e:
 print(f" ❌ Tick-Gap {tick_gap}: Error - {e}")
 
 time.sleep(2) # Delay between tests
 
 print()
 print("=" * 80)
 print("TEST COMPLETE")
 print("=" * 80)

if __name__ == "__main__":
 main()

