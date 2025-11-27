#!/usr/bin/env python3
"""
Block Sniffer: Passive Intelligence - Monitor recent ticks for contract interactions.

Instead of sending transactions, we LISTEN and OBSERVE what others are doing
with the contract. This is forensic analysis, not brute-force.

Strategy:
1. Scan the last 100-1000 ticks for transactions TO the contract
2. If we find any, analyze their payload, amount, source identity
3. Copy successful patterns instead of guessing
"""

from __future__ import annotations

import json
import time
from collections import defaultdict
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import List, Optional

from qubipy.rpc import rpc_client

CONTRACT_ID = "POCCZYCKTRQGHFIPWGSBLJTEQFDDVVBMNUHNCKMRACBGQOPBLURNRCBAFOBD"
OUTPUT_DIR = Path("outputs/derived")
OUTPUT_JSON = OUTPUT_DIR / "block_sniffer_results.json"

@dataclass
class ContractTransaction:
 """Represents a transaction to/from the contract."""
 tx_id: str
 source_id: str
 dest_id: str
 amount: int
 tick: int
 payload: Optional[bytes] = None
 payload_str: Optional[str] = None
 is_incoming: bool = False
 is_outgoing: bool = False

def scan_recent_ticks(
 rpc: rpc_client.QubiPy_RPC,
 num_ticks: int = 1000,
 max_transactions: int = 100,
) -> List[ContractTransaction]:
 """
 Scan recent ticks for transactions involving the contract.
 
 Args:
 rpc: QubiPy RPC client
 num_ticks: Number of recent ticks to scan
 max_transactions: Maximum transactions to collect
 
 Returns:
 List of ContractTransaction objects
 """
 print(f"Scanning last {num_ticks} ticks for contract interactions...")
 print()
 
 latest_tick = rpc.get_latest_tick()
 start_tick = max(0, latest_tick - num_ticks)
 
 print(f"Latest tick: {latest_tick}")
 print(f"Scanning range: {start_tick} to {latest_tick}")
 print()
 
 transactions = []
 
 # Try to get transaction history
 try:
 tx_data = rpc.get_transfer_transactions_per_tick(
 identity=CONTRACT_ID,
 start_tick=start_tick,
 end_tick=latest_tick,
 )
 
 if tx_data and tx_data.get("transactions"):
 raw_txs = tx_data["transactions"]
 print(f"Found {len(raw_txs)} transactions in history")
 
 for tx in raw_txs[:max_transactions]:
 source = tx.get("sourceId", "")
 dest = tx.get("destinationId", "")
 amount = int(tx.get("amount", 0))
 tick = tx.get("tickNumber", 0)
 tx_id = tx.get("transactionId", "")
 
 # Check if this involves our contract
 if source == CONTRACT_ID or dest == CONTRACT_ID:
 contract_tx = ContractTransaction(
 tx_id=tx_id,
 source_id=source,
 dest_id=dest,
 amount=amount,
 tick=tick,
 is_incoming=(dest == CONTRACT_ID),
 is_outgoing=(source == CONTRACT_ID),
 )
 transactions.append(contract_tx)
 
 direction = "→ IN" if contract_tx.is_incoming else "← OUT"
 print(f" Tick {tick}: {direction} {amount} QU")
 if contract_tx.is_incoming:
 print(f" From: {source[:30]}...")
 else:
 print(f" To: {dest[:30]}...")
 else:
 print("⚠️ No transactions found in history (might be pruned)")
 
 except Exception as e:
 print(f"❌ Error scanning ticks: {e}")
 import traceback
 traceback.print_exc()
 
 return transactions

def analyze_transactions(transactions: List[ContractTransaction]) -> dict:
 """Analyze collected transactions for patterns."""
 
 analysis = {
 "total_found": len(transactions),
 "incoming": len([t for t in transactions if t.is_incoming]),
 "outgoing": len([t for t in transactions if t.is_outgoing]),
 "amount_stats": {},
 "tick_stats": {},
 "unique_sources": set(),
 "unique_destinations": set(),
 }
 
 if not transactions:
 return analysis
 
 # Amount statistics
 amounts = [t.amount for t in transactions if t.amount > 0]
 if amounts:
 analysis["amount_stats"] = {
 "min": min(amounts),
 "max": max(amounts),
 "average": sum(amounts) / len(amounts),
 "median": sorted(amounts)[len(amounts) // 2],
 }
 
 # Tick statistics
 ticks = [t.tick for t in transactions]
 if ticks:
 analysis["tick_stats"] = {
 "oldest": min(ticks),
 "newest": max(ticks),
 "range": max(ticks) - min(ticks),
 "latest_age_ticks": max(ticks) - ticks[-1] if ticks else 0,
 }
 
 # Unique identities
 for tx in transactions:
 if tx.is_incoming:
 analysis["unique_sources"].add(tx.source_id)
 if tx.is_outgoing:
 analysis["unique_destinations"].add(tx.dest_id)
 
 analysis["unique_sources"] = list(analysis["unique_sources"])
 analysis["unique_destinations"] = list(analysis["unique_destinations"])
 
 return analysis

def monitor_live(rpc: rpc_client.QubiPy_RPC, duration_seconds: int = 300) -> List[ContractTransaction]:
 """
 Monitor live for new contract transactions.
 
 Args:
 rpc: QubiPy RPC client
 duration_seconds: How long to monitor (default 5 minutes)
 
 Returns:
 List of new ContractTransaction objects found
 """
 print(f"Monitoring live for {duration_seconds} seconds...")
 print("Press Ctrl+C to stop early")
 print()
 
 start_tick = rpc.get_latest_tick()
 seen_tx_ids = set()
 new_transactions = []
 
 try:
 start_time = time.time()
 check_interval = 10 # Check every 10 seconds
 
 while time.time() - start_time < duration_seconds:
 current_tick = rpc.get_latest_tick()
 
 # Scan last 50 ticks for new transactions
 scan_start = max(start_tick, current_tick - 50)
 
 try:
 tx_data = rpc.get_transfer_transactions_per_tick(
 identity=CONTRACT_ID,
 start_tick=scan_start,
 end_tick=current_tick,
 )
 
 if tx_data and tx_data.get("transactions"):
 for tx in tx_data["transactions"]:
 tx_id = tx.get("transactionId", "")
 
 if tx_id and tx_id not in seen_tx_ids:
 seen_tx_ids.add(tx_id)
 
 source = tx.get("sourceId", "")
 dest = tx.get("destinationId", "")
 
 if source == CONTRACT_ID or dest == CONTRACT_ID:
 contract_tx = ContractTransaction(
 tx_id=tx_id,
 source_id=source,
 dest_id=dest,
 amount=int(tx.get("amount", 0)),
 tick=tx.get("tickNumber", 0),
 is_incoming=(dest == CONTRACT_ID),
 is_outgoing=(source == CONTRACT_ID),
 )
 new_transactions.append(contract_tx)
 
 direction = "→ IN" if contract_tx.is_incoming else "← OUT"
 print(f"🆕 NEW: Tick {contract_tx.tick}: {direction} {contract_tx.amount} QU")
 if contract_tx.is_incoming:
 print(f" From: {source[:40]}...")
 else:
 print(f" To: {dest[:40]}...")
 print()
 
 except Exception as e:
 print(f"⚠️ Error during monitoring: {e}")
 
 time.sleep(check_interval)
 print(f"⏳ Still monitoring... (Tick {current_tick})")
 
 except KeyboardInterrupt:
 print("\n⚠️ Monitoring stopped by user")
 
 return new_transactions

def main() -> int:
 OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
 
 print("=" * 80)
 print("🔍 BLOCK SNIFFER - PASSIVE INTELLIGENCE")
 print("=" * 80)
 print()
 print("Strategy: LISTEN and OBSERVE, don't send")
 print("Goal: Find what successful transactions look like")
 print()
 
 rpc = rpc_client.QubiPy_RPC()
 
 # Step 1: Scan recent history
 print("STEP 1: Scanning recent transaction history...")
 print()
 recent_txs = scan_recent_ticks(rpc, num_ticks=1000, max_transactions=100)
 
 print()
 print("=" * 80)
 print("ANALYSIS")
 print("=" * 80)
 print()
 
 analysis = analyze_transactions(recent_txs)
 
 print(f"Total transactions found: {analysis['total_found']}")
 print(f" Incoming: {analysis['incoming']}")
 print(f" Outgoing: {analysis['outgoing']}")
 print()
 
 if analysis["amount_stats"]:
 amt = analysis["amount_stats"]
 print("Amount Statistics:")
 print(f" Min: {amt['min']} QU")
 print(f" Max: {amt['max']} QU")
 print(f" Average: {amt['average']:.0f} QU")
 print(f" Median: {amt['median']} QU")
 print()
 
 if analysis["tick_stats"]:
 tick = analysis["tick_stats"]
 print("Tick Statistics:")
 print(f" Oldest: {tick['oldest']}")
 print(f" Newest: {tick['newest']}")
 if tick["latest_age_ticks"]:
 age_minutes = tick["latest_age_ticks"] * 0.6 / 60
 print(f" Latest activity: {age_minutes:.1f} minutes ago")
 print()
 
 print(f"Unique sources: {len(analysis['unique_sources'])}")
 print(f"Unique destinations: {len(analysis['unique_destinations'])}")
 print()
 
 # Save results
 output_data = {
 "contract_id": CONTRACT_ID,
 "scan_timestamp": time.time(),
 "transactions": [asdict(tx) for tx in recent_txs],
 "analysis": {k: v for k, v in analysis.items() if k not in ["unique_sources", "unique_destinations"]},
 "unique_sources": analysis["unique_sources"],
 "unique_destinations": analysis["unique_destinations"],
 }
 
 with OUTPUT_JSON.open("w", encoding="utf-8") as f:
 json.dump(output_data, f, indent=2, default=str)
 
 print("=" * 80)
 print(f"✅ Results saved to: {OUTPUT_JSON}")
 print("=" * 80)
 print()
 
 # Step 2: Try live monitoring (short duration)
 if recent_txs:
 print("✅ Found transactions in history!")
 print(" Analyze the results above to see patterns")
 else:
 print("⚠️ No transactions found in recent history (likely pruned)")
 print()
 print("Attempting short live monitoring (60 seconds)...")
 print()
 
 try:
 live_txs = monitor_live(rpc, duration_seconds=60)
 
 if live_txs:
 print()
 print(f"✅ Found {len(live_txs)} new transactions during monitoring!")
 # Append to results
 output_data["live_transactions"] = [asdict(tx) for tx in live_txs]
 with OUTPUT_JSON.open("w", encoding="utf-8") as f:
 json.dump(output_data, f, indent=2, default=str)
 else:
 print()
 print("❌ No new transactions detected during monitoring")
 print(" Contract might be inactive or waiting")
 except KeyboardInterrupt:
 print("\n⚠️ Monitoring interrupted")
 
 return 0

if __name__ == "__main__":
 raise SystemExit(main())

