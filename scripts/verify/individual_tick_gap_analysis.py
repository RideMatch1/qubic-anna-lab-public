#!/usr/bin/env python3
"""
Individual Tick Gap Analysis: Calculate the exact tick gap for each of the 8 identities.

For each identity:
 - Get validForTick for Layer 1 identity
 - Get validForTick for Layer 2 identity (derived from Layer 1 seed)
 - Calculate: Individual Tick Gap = Layer2.validForTick - Layer1.validForTick

This will give us 8 individual tick gap values to use in the payload.
"""

from __future__ import annotations

import json
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List

from qubipy.rpc import rpc_client

OUTPUT_DIR = Path("outputs/derived")
OUTPUT_JSON = OUTPUT_DIR / "individual_tick_gaps.json"

# Layer 1 identities (from matrix extraction)
LAYER1_IDENTITIES = [
 {
 "label": "Diagonal #1",
 "identity": "AQIOSQQMACYBPQXQSJNIUAYLMXXIWQOXQMEQYXBBTBONSJJRCWPXXDDRDWOR",
 "seed_candidate": "aqiosqqmacybpqxqsjniuaylmxxiwqoxqmeqyxbbtbonsjjrcwpxxdd",
 },
 {
 "label": "Diagonal #2",
 "identity": "GWUXOMMMMFMTBWFZSNGMUKWBILTXQDKNMMMNYPEFTAMRONJMABLHTRRROHXZ",
 "seed_candidate": "gwuxommmmfmtbwfzsngmukwbiltxqdknmmmnypeftamronjmablhtrr",
 },
 {
 "label": "Diagonal #3",
 "identity": "ACGJGQQYILBPXDRBORFGWFZBBBNLQNGHDDELVLXXXLBNNNFBLLPBNNNLJIFV",
 "seed_candidate": "acgjgqqyilbpxdrborfgwfzbbbnlqnghddelvlxxxlbnnnfbllpbnnn",
 },
 {
 "label": "Diagonal #4",
 "identity": "GIUVFGAWCBBFFKVBMFJESLHBBFBFWZWNNXCBQBBJRVFBNVJLTJBBBHTHKLDC",
 "seed_candidate": "giuvfgawcbbffkvbmfjeslhbbfbfwzwnnxcbqbbjrvfbnvjltjbbbht",
 },
 {
 "label": "Vortex #1",
 "identity": "UUFEEMUUBIYXYXDUXZCFBIHABAYSACQSWSGABOBKNXBZCICLYOKOBMLKMUAF",
 "seed_candidate": "uufeemuubiyxyxduxzcfbihabaysacqswsgabobknxbzciclyokobml",
 },
 {
 "label": "Vortex #2",
 "identity": "HJBRFBHTBZJLVRBXTDRFORBWNACAHAQMSBUNBONHTRHNJKXKKNKHWCBNAXLD",
 "seed_candidate": "hjbrfbhtbzjlvrbxtdrforbwnacahaqmsbunbonhtrhnjkxkknkhwcb",
 },
 {
 "label": "Vortex #3",
 "identity": "JKLMNOIPDQORWSICTWWUIYVMOFIQCQSYKMKACMOKQYCCMCOGOCQCSCWCDQFL",
 "seed_candidate": "jklmnoipdqorwsictwwuiyvmofiqcqsykmkacmokqyccmcogocqcscw",
 },
 {
 "label": "Vortex #4",
 "identity": "XYZQAUBQUUQBQBYQAYEIYAQYMMEMQQQMMQSQEQAZSMOGWOXKIRMJXMCLFAVK",
 "seed_candidate": "xyzqaubquuqbqbyqayeiyaqymmemqqqmmqsqeqazsmogwoxkirmjxmc",
 },
]

# Layer 2 identities (derived from Layer 1 seeds)
LAYER2_IDENTITIES = [
 {
 "label": "Diagonal #1 • Layer-2",
 "identity": "OBWIIPWFPOWIQCHGJHKFZNMSSYOBYNNDLUEXAELXKEROIUKIXEUXMLZBICUD",
 "seed": "aqiosqqmacybpqxqsjniuaylmxxiwqoxqmeqyxbbtbonsjjrcwpxxdd",
 },
 {
 "label": "Diagonal #2 • Layer-2",
 "identity": "OQOOMLAQLGOJFFAYGXALSTDVDGQDWKWGDQJRMNZSODHMWWWNSLSQZZAHOAZE",
 "seed": "gwuxommmmfmtbwfzsngmukwbiltxqdknmmmnypeftamronjmablhtrr",
 },
 {
 "label": "Diagonal #3 • Layer-2",
 "identity": "WEZPWOMKYYQYGDZJDUEPIOTTUKCCQVBYEMYHQUTWGAMHFVJJVRCQLMVGYDGG",
 "seed": "acgjgqqyilbpxdrborfgwfzbbbnlqnghddelvlxxxlbnnnfbllpbnnn",
 },
 {
 "label": "Diagonal #4 • Layer-2",
 "identity": "BUICAHKIBLQWQAIONARLYROQGMRAYEAOECSZCPMTEHUIFXLKGTMAPJFDCHQI",
 "seed": "giuvfgawcbbffkvbmfjeslhbbfbfwzwnnxcbqbbjrvfbnvjltjbbbht",
 },
 {
 "label": "Vortex #1 • Layer-2",
 "identity": "FAEEIVWNINMPFAAWUUYMCJXMSFCAGDJNFDRCEHBFPGFCCEKUWTMCBHXBNSVL",
 "seed": "uufeemuubiyxyxduxzcfbihabaysacqswsgabobknxbzciclyokobml",
 },
 {
 "label": "Vortex #2 • Layer-2",
 "identity": "PRUATXFVEFFWAEHUADBSBKOFEQTCYOXPSJHWPUSUKCHBXGMRQQEWITAELCNI",
 "seed": "hjbrfbhtbzjlvrbxtdrforbwnacahaqmsbunbonhtrhnjkxkknkhwcb",
 },
 {
 "label": "Vortex #3 • Layer-2",
 "identity": "RIOIMZKDJPHCFFGVYMWSFOKVBNXAYCKUXOLHLHHCPCQDULIITMFGZQUFIMKN",
 "seed": "jklmnoipdqorwsictwwuiyvmofiqcqsykmkacmokqyccmcogocqcscw",
 },
 {
 "label": "Vortex #4 • Layer-2",
 "identity": "DZGTELPKNEITGBRUPCWRNZGLTMBCRPLRPERUFBZHDFDTFYTJXOUDYLSBKRRB",
 "seed": "xyzqaubquuqbqbyqayeiyaqymmemqqqmmqsqeqazsmogwoxkirmjxmc",
 },
]

@dataclass
class TickGapRecord:
 label: str
 layer1_identity: str
 layer2_identity: str
 layer1_tick: int | None
 layer2_tick: int | None
 tick_gap: int | None
 error: str | None = None

def get_identity_tick(rpc: rpc_client.QubiPy_RPC, identity: str) -> int | None:
 """Get validForTick for an identity."""
 try:
 time.sleep(0.3) # Rate limiting
 balance = rpc.get_balance(identity)
 if balance:
 return balance.get("validForTick")
 except Exception as e:
 print(f" Error getting tick for {identity[:20]}...: {e}")
 return None

def calculate_individual_tick_gaps(rpc: rpc_client.QubiPy_RPC) -> List[TickGapRecord]:
 """Calculate individual tick gaps for all 8 identities."""
 records: List[TickGapRecord] = []
 
 print("=" * 80)
 print("COLLECTING TICKS FOR LAYER 1 IDENTITIES")
 print("=" * 80)
 print()
 
 layer1_ticks = {}
 for item in LAYER1_IDENTITIES:
 label = item["label"]
 identity = item["identity"]
 print(f"▶️ {label}: {identity[:30]}...")
 tick = get_identity_tick(rpc, identity)
 layer1_ticks[label] = tick
 if tick:
 print(f" ✅ Tick: {tick}")
 else:
 print(f" ❌ Failed to get tick")
 print()
 
 print("=" * 80)
 print("COLLECTING TICKS FOR LAYER 2 IDENTITIES")
 print("=" * 80)
 print()
 
 layer2_ticks = {}
 for item in LAYER2_IDENTITIES:
 label = item["label"]
 identity = item["identity"]
 print(f"▶️ {label}: {identity[:30]}...")
 tick = get_identity_tick(rpc, identity)
 layer2_ticks[label] = tick
 if tick:
 print(f" ✅ Tick: {tick}")
 else:
 print(f" ❌ Failed to get tick")
 print()
 
 print("=" * 80)
 print("CALCULATING INDIVIDUAL TICK GAPS")
 print("=" * 80)
 print()
 
 for i, layer1_item in enumerate(LAYER1_IDENTITIES):
 layer2_item = LAYER2_IDENTITIES[i]
 
 label = layer1_item["label"]
 layer1_identity = layer1_item["identity"]
 layer2_identity = layer2_item["identity"]
 
 layer1_tick = layer1_ticks.get(label)
 layer2_tick = layer2_ticks.get(layer2_item["label"])
 
 tick_gap = None
 error = None
 
 if layer1_tick is None:
 error = "Failed to get Layer 1 tick"
 elif layer2_tick is None:
 error = "Failed to get Layer 2 tick"
 else:
 tick_gap = layer2_tick - layer1_tick
 
 record = TickGapRecord(
 label=label,
 layer1_identity=layer1_identity,
 layer2_identity=layer2_identity,
 layer1_tick=layer1_tick,
 layer2_tick=layer2_tick,
 tick_gap=tick_gap,
 error=error,
 )
 records.append(record)
 
 if tick_gap is not None:
 print(f"✅ {label}:")
 print(f" Layer 1 Tick: {layer1_tick}")
 print(f" Layer 2 Tick: {layer2_tick}")
 print(f" Individual Tick Gap: {tick_gap}")
 else:
 print(f"❌ {label}: {error}")
 print()
 
 return records

def main() -> int:
 OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
 
 print("=" * 80)
 print("INDIVIDUAL TICK GAP ANALYSIS")
 print("=" * 80)
 print()
 print("Goal: Calculate the exact tick gap for each of the 8 identities")
 print(" to use in the Smart Contract payload.")
 print()
 print("Formula: Individual Tick Gap = Layer2.validForTick - Layer1.validForTick")
 print()
 
 rpc = rpc_client.QubiPy_RPC()
 
 records = calculate_individual_tick_gaps(rpc)
 
 # Summary
 print("=" * 80)
 print("SUMMARY")
 print("=" * 80)
 print()
 
 successful = [r for r in records if r.tick_gap is not None]
 failed = [r for r in records if r.tick_gap is None]
 
 print(f"Successful: {len(successful)}/{len(records)}")
 print(f"Failed: {len(failed)}/{len(records)}")
 print()
 
 if successful:
 print("Individual Tick Gaps:")
 for record in successful:
 print(f" {record.label}: {record.tick_gap}")
 
 gaps = [r.tick_gap for r in successful]
 avg_gap = sum(gaps) / len(gaps)
 min_gap = min(gaps)
 max_gap = max(gaps)
 
 print()
 print(f"Average Gap: {avg_gap:.1f}")
 print(f"Min Gap: {min_gap}")
 print(f"Max Gap: {max_gap}")
 print(f"Range: {max_gap - min_gap}")
 
 if failed:
 print()
 print("Failed Records:")
 for record in failed:
 print(f" {record.label}: {record.error}")
 
 # Save results
 output_data = {
 "records": [
 {
 "label": r.label,
 "layer1_identity": r.layer1_identity,
 "layer2_identity": r.layer2_identity,
 "layer1_tick": r.layer1_tick,
 "layer2_tick": r.layer2_tick,
 "tick_gap": r.tick_gap,
 "error": r.error,
 }
 for r in records
 ],
 "summary": {
 "total": len(records),
 "successful": len(successful),
 "failed": len(failed),
 "average_gap": sum(r.tick_gap for r in successful) / len(successful) if successful else None,
 "min_gap": min(r.tick_gap for r in successful) if successful else None,
 "max_gap": max(r.tick_gap for r in successful) if successful else None,
 },
 }
 
 with OUTPUT_JSON.open("w", encoding="utf-8") as f:
 json.dump(output_data, f, indent=2)
 
 print()
 print("=" * 80)
 print(f"Report saved to: {OUTPUT_JSON}")
 print("=" * 80)
 print()
 
 if successful:
 print("✅ Ready to test Hypothesis 2 with individual tick gaps!")
 print(" Next: Run final_contract_trigger_hypothesis2_individual.py")
 else:
 print("❌ Failed to collect tick data. Check RPC connection.")
 
 return 0

if __name__ == "__main__":
 raise SystemExit(main())

