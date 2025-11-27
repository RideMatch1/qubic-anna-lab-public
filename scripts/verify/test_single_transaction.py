#!/usr/bin/env python3
"""
Test Single Transaction: Simple test to see if RPC 500 is a general issue or specific to our tests.

Send ONE simple transaction to check if the problem is:
- General RPC issue
- Our transaction format
- Our identities/seeds
"""

from __future__ import annotations

from qubipy.rpc import rpc_client
from qubipy.tx.utils import create_tx

CONTRACT_ID = "POCCZYCKTRQGHFIPWGSBLJTEQFDDVVBMNUHNCKMRACBGQOPBLURNRCBAFOBD"

# Test with one identity
TEST_SEED = "aqiosqqmacybpqxqsjniuaylmxxiwqoxqmeqyxbbtbonsjjrcwpxxdd"
TEST_IDENTITY = "OBWIIPWFPOWIQCHGJHKFZNMSSYOBYNNDLUEXAELXKEROIUKIXEUXMLZBICUD"

def main():
 print("=" * 80)
 print("TEST: SINGLE TRANSACTION")
 print("=" * 80)
 print()
 print("Goal: Check if RPC 500 is a general issue or specific to our tests")
 print()
 
 rpc = rpc_client.QubiPy_RPC()
 
 # Check balance first
 print("1. Checking balance...")
 try:
 balance_data = rpc.get_balance(TEST_IDENTITY)
 if balance_data:
 balance = balance_data.get("balance", "0")
 print(f" Balance: {balance} QU")
 if int(balance) < 1:
 print(" ❌ Insufficient balance!")
 return 1
 else:
 print(" ⚠️ Could not get balance")
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
 
 # Try to create transaction
 print("3. Creating transaction...")
 try:
 tx_bytes, _, _, tx_hash = create_tx(
 seed=TEST_SEED,
 dest_id=CONTRACT_ID,
 amount=1,
 target_tick=target_tick,
 )
 print(f" ✅ Transaction created: {tx_hash[:20]}...")
 except Exception as e:
 print(f" ❌ Error creating transaction: {e}")
 import traceback
 traceback.print_exc()
 return 1
 
 print()
 
 # Try to broadcast
 print("4. Broadcasting transaction...")
 try:
 response = rpc.broadcast_transaction(tx_bytes)
 tx_id = response.get("txId", tx_hash)
 print(f" ✅ Transaction broadcasted: {tx_id}")
 print(f" Response: {response}")
 return 0
 except Exception as e:
 print(f" ❌ Error broadcasting: {e}")
 import traceback
 traceback.print_exc()
 return 1

if __name__ == "__main__":
 raise SystemExit(main())

