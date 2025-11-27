#!/usr/bin/env python3
"""
Tick Sequence Analyzer: Collect creation ticks (validForTick) for all identities
to find patterns in batch creation, sequential creation, or AI generator patterns.
"""

from __future__ import annotations

import json
import time
from collections import Counter
from pathlib import Path
from typing import Dict, List

from qubipy.rpc import rpc_client

OUTPUT_DIR = Path("outputs/derived")
SCAN_FILE = OUTPUT_DIR / "comprehensive_matrix_scan.json"
OUTPUT_JSON = OUTPUT_DIR / "tick_sequence_analysis.json"

KNOWN_8 = [
 "AQIOSQQMACYBPQXQSJNIUAYLMXXIWQOXQMEQYXBBTBONSJJRCWPXXDDRDWOR",
 "GWUXOMMMMFMTBWFZSNGMUKWBILTXQDKNMMMNYPEFTAMRONJMABLHTRRROHXZ",
 "ACGJGQQYILBPXDRBORFGWFZBBBNLQNGHDDELVLXXXLBNNNFBLLPBNNNLJIFV",
 "GIUVFGAWCBBFFKVBMFJESLHBBFBFWZWNNXCBQBBJRVFBNVJLTJBBBHTHKLDC",
 "UUFEEMUUBIYXYXDUXZCFBIHABAYSACQSWSGABOBKNXBZCICLYOKOBMLKMUAF",
 "HJBRFBHTBZJLVRBXTDRFORBWNACAHAQMSBUNBONHTRHNJKXKKNKHWCBNAXLD",
 "JKLMNOIPDQORWSICTWWUIYVMOFIQCQSYKMKACMOKQYCCMCOGOCQCSCWCDQFL",
 "XYZQAUBQUUQBQBYQAYEIYAQYMMEMQQQMMQSQEQAZSMOGWOXKIRMJXMCLFAVK",
]

def get_identity_tick(rpc: rpc_client.QubiPy_RPC, identity: str) -> int | None:
 """Get validForTick for an identity."""
 try:
 time.sleep(0.3)
 balance_data = rpc.get_balance(identity)
 if balance_data:
 return balance_data.get("validForTick")
 except:
 pass
 return None

def analyze_tick_sequence(ticks: List[int]) -> Dict:
 """Analyze tick sequence for patterns."""
 if not ticks:
 return {}
 
 sorted_ticks = sorted(ticks)
 differences = [sorted_ticks[i+1] - sorted_ticks[i] for i in range(len(sorted_ticks)-1)]
 
 diff_counter = Counter(differences)
 
 return {
 "total_identities": len(ticks),
 "min_tick": min(ticks),
 "max_tick": max(ticks),
 "tick_range": max(ticks) - min(ticks),
 "sorted_ticks": sorted_ticks,
 "tick_differences": differences,
 "most_common_differences": diff_counter.most_common(10),
 "average_difference": sum(differences) / len(differences) if differences else 0,
 }

def main() -> None:
 rpc = rpc_client.QubiPy_RPC()
 OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
 
 print("=== Tick Sequence Analyzer ===\n")
 print("Collecting creation ticks for all identities...\n")
 
 # Load all identities
 with SCAN_FILE.open("r", encoding="utf-8") as f:
 scan_data = json.load(f)
 
 all_identities = set()
 for result in scan_data.get("results", []):
 for identity in result.get("on_chain_identities", []):
 all_identities.add(identity)
 
 new_identities = list(all_identities - set(KNOWN_8))
 
 print(f"Total identities to check: {len(KNOWN_8)} known + {len(new_identities)} new")
 print(f"Checking first 50 new identities (to avoid rate limiting)...\n")
 
 # Collect ticks
 identity_ticks: Dict[str, int] = {}
 
 print("Checking known 8...")
 for identity in KNOWN_8:
 tick = get_identity_tick(rpc, identity)
 if tick:
 identity_ticks[identity] = tick
 print(f" {identity[:30]}... → Tick {tick}")
 
 print(f"\nChecking new identities (first 50)...")
 for i, identity in enumerate(new_identities[:50], 1):
 tick = get_identity_tick(rpc, identity)
 if tick:
 identity_ticks[identity] = tick
 if i % 10 == 0:
 print(f" Checked {i}/50...")
 
 print(f"\n=== Analysis ===")
 print(f"Total identities with ticks: {len(identity_ticks)}")
 
 # Analyze all ticks
 all_ticks = list(identity_ticks.values())
 analysis = analyze_tick_sequence(all_ticks)
 
 print(f"Tick range: {analysis['min_tick']} → {analysis['max_tick']} (span: {analysis['tick_range']})")
 print(f"Average difference: {analysis['average_difference']:.1f} ticks")
 
 print(f"\nMost common tick differences:")
 for diff, count in analysis["most_common_differences"]:
 print(f" {diff} ticks: {count} occurrences")
 if diff == 1649:
 print(f" ⚠️ This is the known Layer-1 → Layer-2 gap!")
 
 # Group by pattern
 print(f"\n=== Pattern Detection ===")
 
 # Check for batch creation (same tick)
 tick_groups = {}
 for identity, tick in identity_ticks.items():
 if tick not in tick_groups:
 tick_groups[tick] = []
 tick_groups[tick].append(identity)
 
 batches = {tick: ids for tick, ids in tick_groups.items() if len(ids) > 1}
 if batches:
 print(f"Found {len(batches)} ticks with multiple identities (batch creation):")
 for tick, ids in sorted(batches.items())[:10]:
 print(f" Tick {tick}: {len(ids)} identities")
 
 # Save results
 output = {
 "total_identities_checked": len(identity_ticks),
 "identity_ticks": identity_ticks,
 "tick_analysis": analysis,
 "batch_groups": {str(k): len(v) for k, v in batches.items()},
 }
 
 with OUTPUT_JSON.open("w", encoding="utf-8") as f:
 json.dump(output, f, indent=2)
 
 print(f"\nReport saved to: {OUTPUT_JSON}")

if __name__ == "__main__":
 main()

