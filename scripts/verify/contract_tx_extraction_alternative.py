#!/usr/bin/env python3
"""
Contract TX Extraction (Alternative Method)

Since get_transaction_history() doesn't work (pruned?), we use alternative methods:
1. Block-by-Block Scanning: Scan recent ticks systematically
2. Contract Balance History: Use numberOfIncomingTransfers as validation
3. Passive Monitoring: Monitor live ticks for new transactions

This script extracts all transactions to/from the contract and matches them with our identities.
"""

from __future__ import annotations

import json
import time
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Set, Optional, Tuple

try:
 from qubipy.rpc import rpc_client
 HAS_QUBIPY = True
except ImportError:
 HAS_QUBIPY = False
 print("⚠️ QubiPy nicht verfügbar - verwende Docker")

CONTRACT_ID = "POCCZYCKTRQGHFIPWGSBLJTEQFDDVVBMNUHNCKMRACBGQOPBLURNRCBAFOBD"
OUTPUT_DIR = Path("outputs/derived")
OUTPUT_JSON = OUTPUT_DIR / "contract_tx_extraction.json"
OUTPUT_MD = OUTPUT_DIR / "contract_tx_extraction.md"

@dataclass
class ContractTransaction:
 """Represents a transaction involving the contract."""
 tx_id: str
 source_id: str
 dest_id: str
 amount: int
 tick: int
 is_incoming: bool # True if contract is destination
 is_outgoing: bool # True if contract is source
 payload: Optional[str] = None

def load_our_identities() -> Set[str]:
 """Load all our verified identities."""
 our_identities = set()
 
 # Load from verification file
 path = Path("outputs/derived/all_identities_rpc_verification.json")
 if path.exists():
 with path.open() as f:
 data = json.load(f)
 our_identities.update(data.get("verified_identities", []))
 
 # Also load from identity_deep_scan.json
 path2 = Path("outputs/derived/identity_deep_scan.json")
 if path2.exists():
 with path2.open() as f:
 data2 = json.load(f)
 if "records" in data2:
 for record in data2["records"]:
 identity = record.get("identity")
 if identity:
 our_identities.add(identity)
 
 return our_identities

def get_contract_balance_info(rpc) -> Dict:
 """Get contract balance and transfer counts."""
 max_retries = 3
 for attempt in range(max_retries):
 try:
 time.sleep(1.0) # Rate limiting
 balance_data = rpc.get_balance(CONTRACT_ID)
 if balance_data:
 return {
 "balance": balance_data.get("balance", "0"),
 "incoming_transfers": balance_data.get("numberOfIncomingTransfers", 0),
 "outgoing_transfers": balance_data.get("numberOfOutgoingTransfers", 0),
 "valid_for_tick": balance_data.get("validForTick"),
 }
 except Exception as e:
 error_msg = str(e)
 if "429" in error_msg or "Too Many Requests" in error_msg:
 if attempt < max_retries - 1:
 wait_time = (attempt + 1) * 5 # Exponential backoff
 print(f" ⚠️ Rate limit hit, waiting {wait_time}s before retry {attempt + 1}/{max_retries}...")
 time.sleep(wait_time)
 continue
 return {"error": str(e)}
 return {}

def scan_ticks_for_contract_tx(
 rpc,
 start_tick: int,
 end_tick: int,
 max_transactions: int = 1000,
) -> List[ContractTransaction]:
 """
 Scan ticks for transactions involving the contract.
 
 This is the alternative method when get_transaction_history() doesn't work.
 """
 transactions = []
 our_identities = load_our_identities()
 
 print(f"Scanning ticks {start_tick} to {end_tick} for contract transactions...")
 print(f"Looking for transactions involving: {CONTRACT_ID[:30]}...")
 print()
 
 tick_count = 0
 for tick in range(start_tick, end_tick + 1):
 try:
 # Get transfer transactions for this tick
 tx_data = rpc.get_transfer_transactions_per_tick(tick)
 
 if tx_data and tx_data.get("transactions"):
 for tx in tx_data["transactions"]:
 source = tx.get("sourceId", "")
 dest = tx.get("destinationId", "")
 
 # Check if this involves our contract
 if source == CONTRACT_ID or dest == CONTRACT_ID:
 contract_tx = ContractTransaction(
 tx_id=tx.get("transactionId", ""),
 source_id=source,
 dest_id=dest,
 amount=int(tx.get("amount", 0)),
 tick=tick,
 is_incoming=(dest == CONTRACT_ID),
 is_outgoing=(source == CONTRACT_ID),
 payload=tx.get("payload", None),
 )
 transactions.append(contract_tx)
 
 # Check if source/dest is one of our identities
 is_our_identity = (source in our_identities) or (dest in our_identities)
 
 direction = "→ IN" if contract_tx.is_incoming else "← OUT"
 our_marker = " 🎯 OUR IDENTITY!" if is_our_identity else ""
 
 print(f" Tick {tick}: {direction} {contract_tx.amount} QU{our_marker}")
 if contract_tx.is_incoming:
 print(f" From: {source[:40]}...")
 else:
 print(f" To: {dest[:40]}...")
 
 if len(transactions) >= max_transactions:
 print(f"\n⚠️ Reached max_transactions limit ({max_transactions})")
 return transactions
 
 tick_count += 1
 if tick_count % 100 == 0:
 print(f" Scanned {tick_count} ticks, found {len(transactions)} transactions...")
 
 # Rate limiting
 time.sleep(0.1)
 
 except Exception as e:
 # Skip errors (might be pruned ticks)
 continue
 
 return transactions

def analyze_transactions(
 transactions: List[ContractTransaction],
 our_identities: Set[str],
) -> Dict:
 """Analyze collected transactions for patterns."""
 analysis = {
 "total_transactions": len(transactions),
 "incoming_count": sum(1 for tx in transactions if tx.is_incoming),
 "outgoing_count": sum(1 for tx in transactions if tx.is_outgoing),
 "total_incoming_amount": sum(tx.amount for tx in transactions if tx.is_incoming),
 "total_outgoing_amount": sum(tx.amount for tx in transactions if tx.is_outgoing),
 "our_identity_matches": [],
 "unique_sources": set(),
 "unique_destinations": set(),
 "tick_range": None,
 }
 
 if transactions:
 ticks = [tx.tick for tx in transactions]
 analysis["tick_range"] = (min(ticks), max(ticks))
 
 for tx in transactions:
 if tx.is_incoming:
 analysis["unique_sources"].add(tx.source_id)
 else:
 analysis["unique_destinations"].add(tx.dest_id)
 
 # Check if source/dest is one of our identities
 if tx.source_id in our_identities:
 analysis["our_identity_matches"].append({
 "tx_id": tx.tx_id,
 "tick": tx.tick,
 "direction": "outgoing",
 "amount": tx.amount,
 "our_identity": tx.source_id,
 })
 if tx.dest_id in our_identities:
 analysis["our_identity_matches"].append({
 "tx_id": tx.tx_id,
 "tick": tx.tick,
 "direction": "incoming",
 "amount": tx.amount,
 "our_identity": tx.dest_id,
 })
 
 analysis["unique_sources"] = list(analysis["unique_sources"])
 analysis["unique_destinations"] = list(analysis["unique_destinations"])
 
 return analysis

def main() -> None:
 OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
 
 print("=" * 80)
 print("CONTRACT TX EXTRACTION (ALTERNATIVE METHOD)")
 print("=" * 80)
 print()
 
 if not HAS_QUBIPY:
 print("❌ QubiPy nicht verfügbar")
 print(" Bitte in Docker ausführen:")
 print(" docker run --rm -v \"$PWD\":/workspace -w /workspace -e PYTHONPATH=/workspace qubic-proof \\")
 print(" python3 scripts/verify/contract_tx_extraction_alternative.py")
 return
 
 rpc = rpc_client.QubiPy_RPC()
 
 # Get contract balance info
 print("Getting contract balance info...")
 balance_info = get_contract_balance_info(rpc)
 if "error" in balance_info:
 print(f"❌ Error: {balance_info['error']}")
 return
 
 print(f"Contract Balance: {balance_info.get('balance', '0')} QU")
 print(f"Incoming Transfers: {balance_info.get('incoming_transfers', 0)}")
 print(f"Outgoing Transfers: {balance_info.get('outgoing_transfers', 0)}")
 print()
 
 # Get latest tick
 try:
 latest_tick = rpc.get_latest_tick()
 print(f"Latest Tick: {latest_tick}")
 except Exception as e:
 print(f"❌ Error getting latest tick: {e}")
 return
 
 # Scan recent ticks (last 10,000 ticks = ~4.6 days)
 scan_range = 10000
 start_tick = max(0, latest_tick - scan_range)
 end_tick = latest_tick
 
 print(f"Scanning ticks {start_tick} to {end_tick}...")
 print(f"(This may take a while - scanning {scan_range} ticks)")
 print()
 
 transactions = scan_ticks_for_contract_tx(
 rpc,
 start_tick,
 end_tick,
 max_transactions=5000, # Allow more transactions
 )
 
 print()
 print("=" * 80)
 print("ANALYSIS")
 print("=" * 80)
 print()
 
 our_identities = load_our_identities()
 analysis = analyze_transactions(transactions, our_identities)
 
 print(f"Total Transactions Found: {analysis['total_transactions']}")
 print(f"Incoming: {analysis['incoming_count']}")
 print(f"Outgoing: {analysis['outgoing_count']}")
 print(f"Total Incoming Amount: {analysis['total_incoming_amount']} QU")
 print(f"Total Outgoing Amount: {analysis['total_outgoing_amount']} QU")
 print()
 
 if analysis['tick_range']:
 print(f"Tick Range: {analysis['tick_range'][0]} to {analysis['tick_range'][1]}")
 print()
 
 print(f"Unique Sources: {len(analysis['unique_sources'])}")
 print(f"Unique Destinations: {len(analysis['unique_destinations'])}")
 print()
 
 print(f"🎯 OUR IDENTITY MATCHES: {len(analysis['our_identity_matches'])}")
 if analysis['our_identity_matches']:
 print()
 print("Matches found:")
 for match in analysis['our_identity_matches'][:10]:
 print(f" Tick {match['tick']}: {match['direction']} {match['amount']} QU")
 print(f" Identity: {match['our_identity'][:50]}...")
 if len(analysis['our_identity_matches']) > 10:
 print(f" ... and {len(analysis['our_identity_matches']) - 10} more")
 else:
 print(" No matches with our identities found in scanned range")
 print()
 
 # Save results
 output_data = {
 "contract_id": CONTRACT_ID,
 "balance_info": balance_info,
 "scan_range": {
 "start_tick": start_tick,
 "end_tick": end_tick,
 "ticks_scanned": scan_range,
 },
 "transactions": [
 {
 "tx_id": tx.tx_id,
 "source_id": tx.source_id,
 "dest_id": tx.dest_id,
 "amount": tx.amount,
 "tick": tx.tick,
 "is_incoming": tx.is_incoming,
 "is_outgoing": tx.is_outgoing,
 "payload": tx.payload,
 }
 for tx in transactions
 ],
 "analysis": analysis,
 }
 
 with OUTPUT_JSON.open("w", encoding="utf-8") as f:
 json.dump(output_data, f, indent=2)
 
 # Create markdown report
 with OUTPUT_MD.open("w", encoding="utf-8") as f:
 f.write("# Contract TX Extraction Results\n\n")
 f.write(f"**Contract ID:** `{CONTRACT_ID}`\n\n")
 f.write(f"**Balance:** {balance_info.get('balance', '0')} QU\n")
 f.write(f"**Incoming Transfers:** {balance_info.get('incoming_transfers', 0)}\n")
 f.write(f"**Outgoing Transfers:** {balance_info.get('outgoing_transfers', 0)}\n\n")
 f.write(f"## Scan Results\n\n")
 f.write(f"- **Ticks Scanned:** {scan_range} ({start_tick} to {end_tick})\n")
 f.write(f"- **Transactions Found:** {analysis['total_transactions']}\n")
 f.write(f"- **Incoming:** {analysis['incoming_count']}\n")
 f.write(f"- **Outgoing:** {analysis['outgoing_count']}\n\n")
 f.write(f"## Our Identity Matches\n\n")
 if analysis['our_identity_matches']:
 f.write(f"**Found {len(analysis['our_identity_matches'])} matches!**\n\n")
 for match in analysis['our_identity_matches']:
 f.write(f"- Tick {match['tick']}: {match['direction']} {match['amount']} QU\n")
 f.write(f" - Identity: `{match['our_identity']}`\n")
 else:
 f.write("No matches found in scanned range.\n")
 
 print(f"Results saved:")
 print(f" - {OUTPUT_JSON}")
 print(f" - {OUTPUT_MD}")

if __name__ == "__main__":
 main()

