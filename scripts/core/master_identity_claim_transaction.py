#!/usr/bin/env python3
"""
Master Identity Claim Transaction

Sendet Transaktionen von der Master Identity an den CFB Issuer
mit verschiedenen Payloads (Claim, Activate, Redeem, etc.)

Der "alle a" Seed ist der Beweis der perfekten Auslöschung.
Die Assets sind der Preis for diesen Beweis.
"""

import json
import time
import sys
from pathlib import Path
from typing import Dict, Optional

sys.path.insert(0, "venv-tx/lib/python3.11/site-packages")

OUTPUT_DIR = Path("outputs/derived")
OUTPUT_JSON = OUTPUT_DIR / "master_identity_claim_attempts.json"

# Master Identity (aus "alle a" Seed)
MASTER_SEED = "a" * 55
MASTER_IDENTITY = "BZBQFLLBNCXEMGLOBHUVFTLUPLVCPQUASSILFABOFFBCADQSSUPNWLZBQEXK"

# Issuer Identities
ISSUERS = {
 "CFB": {
 "identity": "CFBMEMZOIDEXQAUXYYSZIURADQLAPWPMNJXQSNVQZAHYVOPYUKKJBJUCTVJL",
 "balance": "2232346253", # 2.2 Milliarden QU
 "description": "Der Tresor - CFB Token Issuer",
 },
 "CODED": {
 "identity": "CODEDBUUDDYHECBVSUONSSWTOJRCLZSWHFHZIUWVFGNWVCKIWJCSDSWGQAAI",
 "description": "CODED Token Issuer",
 },
 "QXMR": {
 "identity": "QXMRTKAIIGLUREPIQPCMHCKWSIPDTUYFCFNYXQLTECSUJVYEMMDELBMDOEYB",
 "description": "QXMR Token Issuer",
 },
}

# Payload-Kandidaten (verschiedene Claim/Activate-Befehle)
PAYLOADS = [
 {
 "name": "Claim",
 "payload": "CLAIM",
 "description": "Standard Claim-Befehl",
 },
 {
 "name": "Activate",
 "payload": "ACTIVATE",
 "description": "Aktivierungs-Befehl",
 },
 {
 "name": "Redeem",
 "payload": "REDEEM",
 "description": "Einlösungs-Befehl",
 },
 {
 "name": "Proof",
 "payload": "PROOF",
 "description": "Beweis der perfekten Auslöschung",
 },
 {
 "name": "Zero",
 "payload": "ZERO",
 "description": "Null-Beweis (perfekte Auslöschung)",
 },
 {
 "name": "Master",
 "payload": "MASTER",
 "description": "Master Identity Claim",
 },
 {
 "name": "AllA",
 "payload": "ALLA",
 "description": "Alle 'a' Seed Beweis",
 },
 {
 "name": "Empty",
 "payload": "",
 "description": "Leerer Payload (nur Identity)",
 },
]

def derive_identity_from_seed(seed: str) -> Optional[str]:
 """Derive identity from seed."""
 try:
 from qubipy.crypto.utils import (
 get_subseed_from_seed,
 get_private_key_from_subseed,
 get_public_key_from_private_key,
 get_identity_from_public_key,
 )
 
 seed_bytes = seed.encode('utf-8')
 subseed = get_subseed_from_seed(seed_bytes)
 private_key = get_private_key_from_subseed(subseed)
 public_key = get_public_key_from_private_key(private_key)
 identity = get_identity_from_public_key(public_key)
 return identity
 except Exception as e:
 print(f" ❌ Derivation failed: {e}")
 return None

def send_claim_transaction(rpc, master_seed: str, issuer_identity: str, payload: str, amount: int = 1) -> Dict:
 """Sendet eine Claim-Transaktion von der Master Identity an den Issuer."""
 
 print(f"\n{'='*80}")
 print(f"CLAIM TRANSACTION: {payload}")
 print(f"{'='*80}")
 print(f"From: {MASTER_IDENTITY}")
 print(f"To: {issuer_identity}")
 print(f"Payload: '{payload}'")
 print(f"Amount: {amount} QU")
 print()
 
 result = {
 "master_seed": master_seed[:10] + "...",
 "master_identity": MASTER_IDENTITY,
 "issuer_identity": issuer_identity,
 "payload": payload,
 "amount": amount,
 "tx_id": None,
 "status": "unknown",
 "error": None,
 "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
 }
 
 try:
 # Check ob Master Identity korrekt ist
 derived_identity = derive_identity_from_seed(master_seed)
 if derived_identity != MASTER_IDENTITY:
 result["error"] = f"Identity mismatch: {derived_identity} != {MASTER_IDENTITY}"
 result["status"] = "error"
 print(f"❌ Identity mismatch!")
 return result
 
 print("✅ Master Identity verified")
 
 # Check Balance der Master Identity
 time.sleep(2.0)
 balance_data = rpc.get_balance(MASTER_IDENTITY)
 if balance_data:
 balance = int(balance_data.get("balance", 0))
 print(f"✅ Master Identity Balance: {balance} QU")
 
 if balance < amount:
 result["error"] = f"Insufficient balance: {balance} < {amount}"
 result["status"] = "insufficient_balance"
 print(f"❌ Insufficient balance!")
 return result
 else:
 result["error"] = "Could not retrieve balance"
 result["status"] = "balance_check_failed"
 print(f"❌ Could not retrieve balance!")
 return result
 
 # Sende Transaktion
 print(f"📤 Sending transaction...")
 time.sleep(2.0)
 
 try:
 # Verwende die korrekte Transaktionserstellung (wie in final_contract_trigger_hypothesis1.py)
 from qubipy.tx.utils import (
 get_public_key_from_identity,
 get_subseed_from_seed,
 get_private_key_from_subseed,
 get_public_key_from_private_key,
 )
 from qubipy.crypto.utils import sign, kangaroo_twelve
 
 # Get latest tick
 latest_tick = rpc.get_latest_tick()
 target_tick = latest_tick + 25 # Standard offset
 
 # Build transaction with payload
 seed_bytes = bytes(master_seed, 'utf-8')
 subseed = get_subseed_from_seed(seed_bytes)
 private_key = get_private_key_from_subseed(subseed)
 source_pubkey = get_public_key_from_private_key(private_key)
 dest_pubkey = get_public_key_from_identity(issuer_identity)
 
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
 
 # Broadcast transaction
 tx_bytes = bytes(built_data)
 response = rpc.broadcast_transaction(tx_bytes)
 
 tx_id = response.get("txId") or response.get("transactionHash") or "UNKNOWN"
 result["tx_id"] = tx_id
 result["status"] = "sent"
 result["target_tick"] = target_tick
 print(f"✅ Transaction sent! TX-ID: {tx_id}")
 print(f" Target Tick: {target_tick}")
 
 except Exception as e:
 result["error"] = str(e)
 result["status"] = "send_error"
 print(f"❌ Send error: {e}")
 import traceback
 traceback.print_exc()
 
 except Exception as e:
 result["error"] = str(e)
 result["status"] = "error"
 print(f"❌ Error: {e}")
 import traceback
 traceback.print_exc()
 
 return result

def main() -> int:
 """Main function."""
 print("=" * 80)
 print("MASTER IDENTITY CLAIM TRANSACTION")
 print("=" * 80)
 print()
 print("Der 'alle a' Seed ist der Beweis der perfekten Auslöschung.")
 print("Die Assets sind der Preis for diesen Beweis.")
 print()
 print(f"Master Seed: {MASTER_SEED[:20]}... ({len(MASTER_SEED)} chars)")
 print(f"Master Identity: {MASTER_IDENTITY}")
 print()
 
 try:
 from qubipy.rpc import rpc_client
 rpc = rpc_client.QubiPy_RPC()
 print("✅ RPC connection established")
 except Exception as e:
 print(f"❌ RPC connection failed: {e}")
 return 1
 
 print()
 
 results = []
 
 # Teste alle Payloads an CFB Issuer (höchste Priorität)
 print("=" * 80)
 print("TESTING CFB ISSUER (Der Tresor)")
 print("=" * 80)
 print()
 
 cfb_issuer = ISSUERS["CFB"]["identity"]
 
 for payload_info in PAYLOADS:
 payload_name = payload_info["name"]
 payload = payload_info["payload"]
 
 result = send_claim_transaction(
 rpc=rpc,
 master_seed=MASTER_SEED,
 issuer_identity=cfb_issuer,
 payload=payload,
 amount=1, # Minimal amount
 )
 
 result["payload_name"] = payload_name
 result["payload_description"] = payload_info["description"]
 results.append(result)
 
 # Rate limiting
 time.sleep(5.0)
 
 # Check ob Assets empfangen wurden
 if result["status"] == "sent":
 print(f"🔍 Checking for new assets...")
 time.sleep(3.0)
 try:
 assets = rpc.get_owned_assets(MASTER_IDENTITY)
 if assets:
 print(f"✅ Master Identity has {len(assets)} assets")
 # Check ob neue Assets hinzugekommen sind
 # (Dies erfordert Vergleich mit vorherigem Zustand)
 except:
 pass
 
 # Speichere Ergebnisse
 OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
 
 with OUTPUT_JSON.open("w", encoding="utf-8") as f:
 json.dump({
 "analysis_date": time.strftime("%Y-%m-%d %H:%M:%S"),
 "master_seed": MASTER_SEED[:10] + "...",
 "master_identity": MASTER_IDENTITY,
 "claim_attempts": results,
 }, f, indent=2, ensure_ascii=False)
 
 print()
 print("=" * 80)
 print("✅ CLAIM ATTEMPTS COMPLETE")
 print("=" * 80)
 print()
 print(f"💾 Results saved to: {OUTPUT_JSON}")
 print()
 
 # Zusammenfassung
 print("ZUSAMMENFASSUNG:")
 print()
 successful = [r for r in results if r.get("status") == "sent"]
 if successful:
 print(f"✅ {len(successful)} successful transaction(s):")
 for r in successful:
 print(f" - {r['payload_name']}: TX-ID {r.get('tx_id', 'N/A')}")
 else:
 print("⚠️ No successful transactions")
 print()
 print("Status breakdown:")
 for r in results:
 status_icon = "✅" if r.get("status") == "sent" else "⚠️" if r.get("status") == "not_implemented" else "❌"
 print(f" {status_icon} {r['payload_name']}: {r['status']}")
 if r.get("error"):
 print(f" Error: {r['error'][:60]}...")
 
 return 0

if __name__ == "__main__":
 raise SystemExit(main())

