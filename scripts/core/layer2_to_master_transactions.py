#!/usr/bin/env python3
"""
Layer-2 to Master Identity Transactions

Sendet Transaktionen von allen 8 Layer-2 Identities an die Master Identity
mit verschiedenen Payloads, um zu sehen, was passiert.
"""

import json
import time
import sys
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass

sys.path.insert(0, "venv-tx/lib/python3.11/site-packages")

OUTPUT_DIR = Path("outputs/derived")
OUTPUT_JSON = OUTPUT_DIR / "layer2_to_master_transactions.json"

# Master Identity
MASTER_IDENTITY = "BZBQFLLBNCXEMGLOBHUVFTLUPLVCPQUASSILFABOFFBCADQSSUPNWLZBQEXK"

# Layer-2 Identities mit Seeds
LAYER2_IDENTITIES = [
 {
 "label": "Diagonal #1",
 "seed": "aqiosqqmacybpqxqsjniuaylmxxiwqoxqmeqyxbbtbonsjjrcwpxxdd",
 "identity": "CYTORJWZCJFCYXAHJPLPPCWPVOXTDZBWQYVWANQDYQCCIORJTVMPBIXBKIVP",
 },
 {
 "label": "Diagonal #2",
 "seed": "gwuxommmmfmtbwfzsngmukwbiltxqdknmmmnypeftamronjmablhtrr",
 "identity": "FPEXLMCOGJNYAAELTBSEDHAZCCNAGXJRPRFNBEXUKPDHFTVAHETKPANQCMLM",
 },
 {
 "label": "Diagonal #3",
 "seed": "acgjgqqyilbpxdrborfgwfzbbbnlqnghddelvlxxxlbnnnfbllpbnnn",
 "identity": "ABCXUAPWHTDRJDASQEZSNCDAMXNJAXDTNESWQLNWPZBBUXDGNJLGYXETNGHN",
 },
 {
 "label": "Diagonal #4",
 "seed": "giuvfgawcbbffkvbmfjeslhbbfbfwzwnnxcbqbbjrvfbnvjltjbbbht",
 "identity": "AGTIRJYQVZXUEFAUCPEBEYHDAFXZFMFOARDSUKLHHBETDIVPWVZMOORUOXSD",
 },
 {
 "label": "Vortex #1",
 "seed": "uufeemuubiyxyxduxzcfbihabaysacqswsgabobknxbzciclyokobml",
 "identity": "GNMLDHIPZJHJDNCCCRFHVDDPEIHJEWOPVVAXQRFIBYDZBNDHTELZIANUDAWB",
 },
 {
 "label": "Vortex #2",
 "seed": "hjbrfbhtbzjlvrbxtdrforbwnacahaqmsbunbonhtrhnjkxkknkhwcb",
 "identity": "ADVDNZIGNSCXAODGDMEXMKICVHFOHBROQQMVZOGAMVASHQURDBPDNJRJJQRM",
 },
 {
 "label": "Vortex #3",
 "seed": "jklmnoipdqorwsictwwuiyvmofiqcqsykmkacmokqyccmcogocqcscw",
 "identity": "HFVFDNEHUVRRBIESYPSSRPNJSVVSDBIPNAXAHIKISLAKYZFKMWNJXVVUEUQJ",
 },
 {
 "label": "Vortex #4",
 "seed": "xyzqaubquuqbqbyqayeiyaqymmemqqqmmqsqeqazsmogwoxkirmjxmc",
 "identity": "BIARJWYAYURJYJBXXEDMQOKGSJXBFNWCDSHXZILITIDHCMJYUMPPXQZQAXNR",
 },
]

# Payload-Kandidaten
PAYLOADS = [
 {
 "name": "Master",
 "payload": "MASTER",
 "description": "Master Identity Claim",
 },
 {
 "name": "Zero",
 "payload": "ZERO",
 "description": "Null-Beweis (perfekte Auslöschung)",
 },
 {
 "name": "Proof",
 "payload": "PROOF",
 "description": "Beweis der perfekten Auslöschung",
 },
 {
 "name": "Activate",
 "payload": "ACTIVATE",
 "description": "Aktivierungs-Befehl",
 },
 {
 "name": "Empty",
 "payload": "",
 "description": "Leerer Payload (nur Identity)",
 },
]

@dataclass
class TxResult:
 label: str
 identity: str
 payload: str
 amount: int
 tx_id: Optional[str]
 status: str
 error: Optional[str] = None
 target_tick: Optional[int] = None

def build_tx_with_payload(
 seed: str,
 dest_identity: str,
 amount: int,
 target_tick: int,
 payload: str,
) -> bytes:
 """Build transaction with payload."""
 from qubipy.tx.utils import (
 get_public_key_from_identity,
 get_subseed_from_seed,
 get_private_key_from_subseed,
 get_public_key_from_private_key,
 )
 from qubipy.crypto.utils import sign, kangaroo_twelve
 
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

def send_transaction(
 rpc,
 seed: str,
 identity: str,
 dest_identity: str,
 payload: str,
 amount: int = 1,
) -> TxResult:
 """Send transaction from Layer-2 Identity to Master Identity."""
 
 print(f" 📤 Sending {amount} QU with payload '{payload}'...")
 
 result = TxResult(
 label="",
 identity=identity,
 payload=payload,
 amount=amount,
 tx_id=None,
 status="unknown",
 )
 
 try:
 # Get latest tick
 latest_tick = rpc.get_latest_tick()
 target_tick = latest_tick + 25 # Standard offset
 result.target_tick = target_tick
 
 # Build transaction
 tx_bytes = build_tx_with_payload(
 seed=seed,
 dest_identity=dest_identity,
 amount=amount,
 target_tick=target_tick,
 payload=payload,
 )
 
 # Broadcast transaction
 response = rpc.broadcast_transaction(tx_bytes)
 
 tx_id = response.get("txId") or response.get("transactionHash") or "UNKNOWN"
 result.tx_id = tx_id
 result.status = "sent"
 
 print(f" ✅ TX-ID: {tx_id}")
 
 except Exception as e:
 result.error = str(e)
 result.status = "error"
 print(f" ❌ Error: {e}")
 import traceback
 traceback.print_exc()
 
 return result

def check_balance(rpc, identity: str) -> int:
 """Check balance of an identity."""
 try:
 time.sleep(1.0)
 balance_data = rpc.get_balance(identity)
 if balance_data:
 return int(balance_data.get("balance", 0))
 except:
 pass
 return 0

def main() -> int:
 """Main function."""
 print("=" * 80)
 print("LAYER-2 TO MASTER IDENTITY TRANSACTIONS")
 print("=" * 80)
 print()
 print(f"Master Identity: {MASTER_IDENTITY}")
 print(f"Layer-2 Identities: {len(LAYER2_IDENTITIES)}")
 print()
 
 try:
 from qubipy.rpc import rpc_client
 rpc = rpc_client.QubiPy_RPC()
 print("✅ RPC connection established")
 except Exception as e:
 print(f"❌ RPC connection failed: {e}")
 return 1
 
 print()
 
 # Check Balances aller Layer-2 Identities
 print("=" * 80)
 print("BALANCE CHECK: Layer-2 Identities")
 print("=" * 80)
 print()
 
 layer2_balances = {}
 for item in LAYER2_IDENTITIES:
 identity = item["identity"]
 balance = check_balance(rpc, identity)
 balance_qubic = balance / 1_000_000
 layer2_balances[identity] = balance
 
 print(f"{item['label']}: {balance_qubic:.2f} QUBIC ({balance} QU)")
 
 print()
 
 # Check Master Identity Balance und Assets VORHER
 print("=" * 80)
 print("MASTER IDENTITY: BEFORE")
 print("=" * 80)
 print()
 
 master_balance_before = check_balance(rpc, MASTER_IDENTITY)
 master_assets_before = []
 try:
 time.sleep(2.0)
 master_assets_before = rpc.get_owned_assets(MASTER_IDENTITY) or []
 except:
 pass
 
 print(f"Balance: {master_balance_before / 1_000_000:.2f} QUBIC ({master_balance_before} QU)")
 print(f"Assets: {len(master_assets_before)}")
 print()
 
 # Sende Transaktionen
 print("=" * 80)
 print("SENDING TRANSACTIONS")
 print("=" * 80)
 print()
 
 all_results = []
 
 # Teste jeden Payload mit allen 8 Identities
 for payload_info in PAYLOADS:
 payload_name = payload_info["name"]
 payload = payload_info["payload"]
 
 print(f"Payload: '{payload}' ({payload_info['description']})")
 print()
 
 payload_results = []
 
 for item in LAYER2_IDENTITIES:
 label = item["label"]
 seed = item["seed"]
 identity = item["identity"]
 balance = layer2_balances.get(identity, 0)
 
 print(f" {label}:")
 
 # Check ob genug Balance vorhanden
 if balance < 1_000_000: # Mindestens 1 QUBIC
 print(f" ⚠️ Insufficient balance: {balance / 1_000_000:.2f} QUBIC")
 result = TxResult(
 label=label,
 identity=identity,
 payload=payload,
 amount=1,
 tx_id=None,
 status="insufficient_balance",
 error=f"Insufficient balance: {balance} QU",
 )
 payload_results.append(result)
 continue
 
 # Sende Transaktion
 result = send_transaction(
 rpc=rpc,
 seed=seed,
 identity=identity,
 dest_identity=MASTER_IDENTITY,
 payload=payload,
 amount=1, # 1 QUBIC pro Transaktion
 )
 
 result.label = label
 payload_results.append(result)
 all_results.append(result)
 
 # Rate limiting
 time.sleep(3.0)
 
 print()
 time.sleep(5.0) # Pause zwischen Payloads
 
 # Check Master Identity Balance und Assets NACHHER
 print("=" * 80)
 print("MASTER IDENTITY: AFTER")
 print("=" * 80)
 print()
 
 time.sleep(10.0) # Warte auf Bestätigung
 
 master_balance_after = check_balance(rpc, MASTER_IDENTITY)
 master_assets_after = []
 try:
 time.sleep(2.0)
 master_assets_after = rpc.get_owned_assets(MASTER_IDENTITY) or []
 except:
 pass
 
 print(f"Balance: {master_balance_after / 1_000_000:.2f} QUBIC ({master_balance_after} QU)")
 print(f"Assets: {len(master_assets_after)}")
 print()
 
 balance_change = master_balance_after - master_balance_before
 assets_change = len(master_assets_after) - len(master_assets_before)
 
 print(f"Balance Change: {balance_change / 1_000_000:.2f} QUBIC")
 print(f"Assets Change: {assets_change}")
 print()
 
 # Speichere Ergebnisse
 OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
 
 results_data = {
 "analysis_date": time.strftime("%Y-%m-%d %H:%M:%S"),
 "master_identity": MASTER_IDENTITY,
 "master_balance_before": master_balance_before,
 "master_balance_after": master_balance_after,
 "master_balance_change": balance_change,
 "master_assets_before": len(master_assets_before),
 "master_assets_after": len(master_assets_after),
 "master_assets_change": assets_change,
 "transactions": [
 {
 "label": r.label,
 "identity": r.identity,
 "payload": r.payload,
 "amount": r.amount,
 "tx_id": r.tx_id,
 "status": r.status,
 "error": r.error,
 "target_tick": r.target_tick,
 }
 for r in all_results
 ],
 }
 
 with OUTPUT_JSON.open("w", encoding="utf-8") as f:
 json.dump(results_data, f, indent=2, ensure_ascii=False)
 
 print("=" * 80)
 print("✅ TRANSACTIONS COMPLETE")
 print("=" * 80)
 print()
 print(f"💾 Results saved to: {OUTPUT_JSON}")
 print()
 
 # Zusammenfassung
 successful = [r for r in all_results if r.status == "sent"]
 print(f"✅ {len(successful)} successful transaction(s)")
 print(f"❌ {len(all_results) - len(successful)} failed transaction(s)")
 print()
 
 if balance_change > 0:
 print(f"🎉 Master Identity received {balance_change / 1_000_000:.2f} QUBIC!")
 if assets_change > 0:
 print(f"🎉 Master Identity received {assets_change} new asset(s)!")
 
 return 0

if __name__ == "__main__":
 raise SystemExit(main())

