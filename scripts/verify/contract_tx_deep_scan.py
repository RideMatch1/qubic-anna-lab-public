#!/usr/bin/env python3
"""
Contract TX Deep Scan: Scan much further back in history.

Since the first scan found 0 transactions in the last 10k ticks,
we need to scan much further back or use alternative methods.
"""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import List, Dict

try:
 from qubipy.rpc import rpc_client
 HAS_QUBIPY = True
except ImportError:
 HAS_QUBIPY = False

CONTRACT_ID = "POCCZYCKTRQGHFIPWGSBLJTEQFDDVVBMNUHNCKMRACBGQOPBLURNRCBAFOBD"
OUTPUT_DIR = Path("outputs/derived")
OUTPUT_JSON = OUTPUT_DIR / "contract_tx_deep_scan.json"

def get_contract_balance(rpc) -> Dict:
 """Get contract balance with retries."""
 max_retries = 5
 for attempt in range(max_retries):
 try:
 time.sleep(2.0) # Longer delay
 balance_data = rpc.get_balance(CONTRACT_ID)
 if balance_data:
 return balance_data
 except Exception as e:
 if "429" in str(e) and attempt < max_retries - 1:
 wait = (attempt + 1) * 10
 print(f" Rate limit, waiting {wait}s...")
 time.sleep(wait)
 else:
 raise
 return {}

def scan_ticks_in_chunks(rpc, start_tick: int, end_tick: int, chunk_size: int = 1000) -> List[Dict]:
 """Scan ticks in chunks to avoid rate limiting."""
 transactions = []
 our_identities = load_our_identities()
 
 total_ticks = end_tick - start_tick + 1
 num_chunks = (total_ticks + chunk_size - 1) // chunk_size
 
 print(f"Scanning {total_ticks} ticks in {num_chunks} chunks of {chunk_size}...")
 print()
 
 for chunk_num in range(num_chunks):
 chunk_start = start_tick + chunk_num * chunk_size
 chunk_end = min(chunk_start + chunk_size - 1, end_tick)
 
 print(f"Chunk {chunk_num + 1}/{num_chunks}: Ticks {chunk_start} to {chunk_end}...")
 
 chunk_txs = []
 for tick in range(chunk_start, chunk_end + 1):
 try:
 tx_data = rpc.get_transfer_transactions_per_tick(tick)
 if tx_data and tx_data.get("transactions"):
 for tx in tx_data["transactions"]:
 source = tx.get("sourceId", "")
 dest = tx.get("destinationId", "")
 
 if source == CONTRACT_ID or dest == CONTRACT_ID:
 is_our = (source in our_identities) or (dest in our_identities)
 chunk_txs.append({
 "tick": tick,
 "tx_id": tx.get("transactionId", ""),
 "source": source,
 "dest": dest,
 "amount": int(tx.get("amount", 0)),
 "is_incoming": (dest == CONTRACT_ID),
 "is_our_identity": is_our,
 })
 
 time.sleep(0.2) # Rate limiting
 except Exception:
 continue
 
 if chunk_txs:
 print(f" ✅ Found {len(chunk_txs)} transactions in this chunk")
 transactions.extend(chunk_txs)
 else:
 print(f" - No transactions")
 
 # Longer pause between chunks
 if chunk_num < num_chunks - 1:
 time.sleep(5.0)
 
 return transactions

def load_our_identities() -> set:
 """Load our verified identities."""
 our_identities = set()
 path = Path("outputs/derived/all_identities_rpc_verification.json")
 if path.exists():
 with path.open() as f:
 data = json.load(f)
 our_identities.update(data.get("verified_identities", []))
 return our_identities

def main() -> None:
 OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
 
 print("=" * 80)
 print("CONTRACT TX DEEP SCAN")
 print("=" * 80)
 print()
 
 if not HAS_QUBIPY:
 print("❌ QubiPy nicht verfügbar")
 return
 
 rpc = rpc_client.QubiPy_RPC()
 
 # Get latest tick
 try:
 latest_tick = rpc.get_latest_tick()
 print(f"Latest Tick: {latest_tick}")
 except Exception as e:
 print(f"❌ Error: {e}")
 return
 
 # Get contract balance info
 print("Getting contract balance...")
 balance_data = get_contract_balance(rpc)
 if balance_data:
 print(f" Balance: {balance_data.get('balance', '0')} QU")
 print(f" Incoming: {balance_data.get('numberOfIncomingTransfers', 0)}")
 print(f" Outgoing: {balance_data.get('numberOfOutgoingTransfers', 0)}")
 print()
 
 # Scan much further back (100k ticks = ~46 days)
 scan_range = 100000
 start_tick = max(0, latest_tick - scan_range)
 end_tick = latest_tick
 
 print(f"Scanning {scan_range} ticks ({start_tick} to {end_tick})...")
 print("(This will take a while - scanning in chunks)")
 print()
 
 transactions = scan_ticks_in_chunks(rpc, start_tick, end_tick, chunk_size=1000)
 
 print()
 print("=" * 80)
 print("RESULTS")
 print("=" * 80)
 print()
 print(f"Total Transactions Found: {len(transactions)}")
 
 our_matches = [tx for tx in transactions if tx.get("is_our_identity")]
 print(f"🎯 Our Identity Matches: {len(our_matches)}")
 
 if our_matches:
 print()
 print("Matches found:")
 for match in our_matches[:10]:
 print(f" Tick {match['tick']}: {match['amount']} QU")
 print(f" {'IN' if match['is_incoming'] else 'OUT'}")
 
 # Save results
 output = {
 "scan_range": {"start": start_tick, "end": end_tick, "ticks": scan_range},
 "contract_balance": balance_data,
 "transactions": transactions,
 "our_matches": our_matches,
 }
 
 with OUTPUT_JSON.open("w", encoding="utf-8") as f:
 json.dump(output, f, indent=2)
 
 print()
 print(f"Results saved to: {OUTPUT_JSON}")

if __name__ == "__main__":
 main()

