#!/usr/bin/env python3
"""
Test Manual TX Building: Use the same method as final_contract_trigger.py
to see if manual building works while create_tx doesn't.
"""

from __future__ import annotations

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

def build_tx_manual(
 seed: str,
 dest_identity: str,
 amount: int,
 target_tick: int,
 payload: bytes = b"",
) -> bytes:
 """Build transaction manually (same as final_contract_trigger.py)."""
 seed_bytes = bytes(seed, 'utf-8')
 subseed = get_subseed_from_seed(seed_bytes)
 private_key = get_private_key_from_subseed(subseed)
 public_key = get_public_key_from_private_key(private_key)
 dest_pubkey = get_public_key_from_identity(dest_identity)
 
 # Build transaction data (same structure as final_contract_trigger.py)
 built_data = bytearray()
 
 # 1. Source Public Key (32 bytes)
 built_data.extend(public_key)
 
 # 2. Destination Public Key (32 bytes)
 built_data.extend(dest_pubkey)
 
 # 3. Amount (8 bytes, little-endian)
 built_data.extend(amount.to_bytes(8, byteorder='little'))
 
 # 4. Target Tick (4 bytes, little-endian)
 built_data.extend(target_tick.to_bytes(4, byteorder='little'))
 
 # 5. Input Type (2 bytes) - 0 for simple transfers
 built_data.extend((0).to_bytes(2, byteorder='little'))
 
 # 6. Input Size (2 bytes) - size of payload
 payload_len = len(payload) if payload else 0
 built_data.extend(payload_len.to_bytes(2, byteorder='little'))
 
 # 7. Payload (if any)
 if payload_len > 0:
 built_data.extend(payload)
 
 # Sign transaction
 offset = len(built_data)
 tx_digest = kangaroo_twelve(built_data, offset, 32)
 signature = sign(subseed, public_key, tx_digest)
 
 # 8. Signature (64 bytes)
 built_data.extend(signature)
 
 return bytes(built_data)

def main():
 print("=" * 80)
 print("TEST: MANUAL TX BUILDING")
 print("=" * 80)
 print()
 print("Goal: Test if manual TX building works (like final_contract_trigger.py)")
 print()
 
 rpc = rpc_client.QubiPy_RPC()
 
 # Test identity
 test_seed = "aqiosqqmacybpqxqsjniuaylmxxiwqoxqmeqyxbbtbonsjjrcwpxxdd"
 test_identity = "OBWIIPWFPOWIQCHGJHKFZNMSSYOBYNNDLUEXAELXKEROIUKIXEUXMLZBICUD"
 
 # Check balance
 print("1. Checking balance...")
 try:
 balance_data = rpc.get_balance(test_identity)
 if balance_data:
 balance = int(balance_data.get("balance", "0"))
 print(f" Balance: {balance} QU")
 if balance < AMOUNT_QU:
 print(" ❌ Insufficient balance!")
 return 1
 except Exception as e:
 print(f" ❌ Error: {e}")
 return 1
 
 print()
 
 # Get latest tick
 print("2. Getting latest tick...")
 try:
 current_tick = rpc.get_latest_tick()
 target_tick = current_tick + 25
 print(f" Current: {current_tick}")
 print(f" Target: {target_tick}")
 except Exception as e:
 print(f" ❌ Error: {e}")
 return 1
 
 print()
 
 # Build transaction manually
 print("3. Building transaction manually...")
 try:
 tx_bytes = build_tx_manual(
 seed=test_seed,
 dest_identity=CONTRACT_ID,
 amount=AMOUNT_QU,
 target_tick=target_tick,
 payload=b"", # No payload
 )
 print(f" ✅ Transaction built: {len(tx_bytes)} bytes")
 except Exception as e:
 print(f" ❌ Error: {e}")
 import traceback
 traceback.print_exc()
 return 1
 
 print()
 
 # Broadcast
 print("4. Broadcasting transaction...")
 try:
 response = rpc.broadcast_transaction(tx_bytes)
 tx_id = response.get("txId", "unknown")
 print(f" ✅ SUCCESS: {tx_id}")
 print(f" Response: {response}")
 return 0
 except Exception as e:
 print(f" ❌ Error: {e}")
 import traceback
 traceback.print_exc()
 return 1

if __name__ == "__main__":
 raise SystemExit(main())

