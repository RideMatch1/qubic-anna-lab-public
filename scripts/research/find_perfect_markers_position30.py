#!/usr/bin/env python3
"""
Find Perfect Markers for Position 30

Findet Perfect Markers (n >= 10) for Position 30 auf größerem Datensatz.
"""

import json
import sys
from pathlib import Path
from typing import Dict, List
from collections import Counter

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

OUTPUT_DIR = project_root / "outputs" / "derived"
REPORTS_DIR = project_root / "outputs" / "reports"

def load_layer3_data() -> Dict:
 """Load Layer-3 Daten."""
 # Versuche zuerst extended (mehr Daten)
 layer3_file = OUTPUT_DIR / "layer3_derivation_extended.json"
 
 if not layer3_file.exists():
 layer3_file = OUTPUT_DIR / "layer3_derivation_complete.json"
 
 if not layer3_file.exists():
 return {}
 
 with layer3_file.open() as f:
 return json.load(f)

def find_perfect_markers(layer3_data: Dict) -> Dict:
 """Finde Perfect Markers for Position 30."""
 results_data = layer3_data.get("results", [])
 
 pos30_onchain = Counter()
 pos30_offchain = Counter()
 
 for result in results_data:
 layer3_id = result.get("layer3_identity", "")
 is_onchain = result.get("layer3_onchain", False)
 
 # Wenn onchain None ist (skip-rpc), verwende vorhandene Daten oder abovespringe
 if is_onchain is None:
 continue
 
 if len(layer3_id) > 30:
 char = layer3_id[30]
 if is_onchain:
 pos30_onchain[char] += 1
 else:
 pos30_offchain[char] += 1
 
 # Analyze Perfect Markers
 perfect_onchain = []
 perfect_offchain = []
 strong_onchain = []
 strong_offchain = []
 
 all_chars = set(list(pos30_onchain.keys()) + list(pos30_offchain.keys()))
 
 for char in all_chars:
 on_count = pos30_onchain.get(char, 0)
 off_count = pos30_offchain.get(char, 0)
 total = on_count + off_count
 
 if total >= 10: # Reliable marker
 rate = (on_count / total * 100) if total > 0 else 0
 
 if rate == 100.0:
 perfect_onchain.append({
 "char": char,
 "count": total,
 "onchain": on_count,
 "offchain": off_count,
 "rate": rate,
 "reliable": True
 })
 elif rate == 0.0:
 perfect_offchain.append({
 "char": char,
 "count": total,
 "onchain": on_count,
 "offchain": off_count,
 "rate": rate,
 "reliable": True
 })
 elif rate >= 70.0:
 strong_onchain.append({
 "char": char,
 "count": total,
 "onchain": on_count,
 "offchain": off_count,
 "rate": rate,
 "reliable": True
 })
 elif rate <= 30.0:
 strong_offchain.append({
 "char": char,
 "count": total,
 "onchain": on_count,
 "offchain": off_count,
 "rate": rate,
 "reliable": True
 })
 
 return {
 "total_analyzed": len([r for r in results_data if r.get("layer3_onchain") is not None]),
 "position30_onchain": dict(pos30_onchain),
 "position30_offchain": dict(pos30_offchain),
 "perfect_onchain_markers": sorted(perfect_onchain, key=lambda x: x["count"], reverse=True),
 "perfect_offchain_markers": sorted(perfect_offchain, key=lambda x: x["count"], reverse=True),
 "strong_onchain_markers": sorted(strong_onchain, key=lambda x: x["rate"], reverse=True),
 "strong_offchain_markers": sorted(strong_offchain, key=lambda x: x["count"], reverse=True)
 }

def main():
 """Hauptfunktion."""
 print("=" * 80)
 print("FIND PERFECT MARKERS FOR POSITION 30")
 print("=" * 80)
 print()
 
 # Load Daten
 print("Loading Layer-3 data...")
 layer3_data = load_layer3_data()
 
 if not layer3_data:
 print("❌ Layer-3 data not found")
 return
 
 print(f"✅ Loaded {len(layer3_data.get('results', []))} entries")
 print()
 
 # Finde Perfect Markers
 print("Analyzing Position 30 for perfect markers...")
 result = find_perfect_markers(layer3_data)
 
 print()
 print("=" * 80)
 print("RESULTS")
 print("=" * 80)
 print()
 
 print(f"Total Analyzed: {result['total_analyzed']}")
 print()
 
 if result['perfect_onchain_markers']:
 print("Perfect On-Chain Markers (100%, n >= 10):")
 for m in result['perfect_onchain_markers']:
 print(f" {m['char']}: {m['count']} cases ({m['onchain']} on-chain, {m['offchain']} off-chain)")
 print()
 else:
 print("No Perfect On-Chain Markers found (n >= 10)")
 print()
 
 if result['perfect_offchain_markers']:
 print("Perfect Off-Chain Markers (0%, n >= 10):")
 for m in result['perfect_offchain_markers']:
 print(f" {m['char']}: {m['count']} cases ({m['onchain']} on-chain, {m['offchain']} off-chain)")
 print()
 else:
 print("No Perfect Off-Chain Markers found (n >= 10)")
 print()
 
 if result['strong_onchain_markers']:
 print("Strong On-Chain Markers (>=70%, n >= 10):")
 for m in result['strong_onchain_markers'][:10]:
 print(f" {m['char']}: {m['rate']:.1f}% ({m['count']} cases)")
 print()
 
 if result['strong_offchain_markers']:
 print("Strong Off-Chain Markers (<=30%, n >= 10):")
 for m in result['strong_offchain_markers'][:10]:
 print(f" {m['char']}: {m['rate']:.1f}% ({m['count']} cases)")
 print()
 
 # Speichere Ergebnisse
 OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
 
 output_json = OUTPUT_DIR / "position30_perfect_markers.json"
 with output_json.open("w") as f:
 json.dump(result, f, indent=2)
 
 # Report
 REPORTS_DIR.mkdir(parents=True, exist_ok=True)
 output_md = REPORTS_DIR / "position30_perfect_markers_report.md"
 
 with output_md.open("w") as f:
 f.write("# Position 30 Perfect Markers Report\n\n")
 f.write("**Generated**: 2025-11-25\n\n")
 f.write("## Summary\n\n")
 f.write(f"Analysis of Position 30 perfect markers on {result['total_analyzed']} identities.\n\n")
 
 if result['perfect_onchain_markers']:
 f.write("## Perfect On-Chain Markers (100%, n >= 10)\n\n")
 f.write("| Char | Count | On-chain | Off-chain | Rate |\n")
 f.write("|------|-------|----------|-----------|------|\n")
 for m in result['perfect_onchain_markers']:
 f.write(f"| {m['char']} | {m['count']} | {m['onchain']} | {m['offchain']} | {m['rate']:.1f}% |\n")
 f.write("\n")
 
 if result['perfect_offchain_markers']:
 f.write("## Perfect Off-Chain Markers (0%, n >= 10)\n\n")
 f.write("| Char | Count | On-chain | Off-chain | Rate |\n")
 f.write("|------|-------|----------|-----------|------|\n")
 for m in result['perfect_offchain_markers']:
 f.write(f"| {m['char']} | {m['count']} | {m['onchain']} | {m['offchain']} | {m['rate']:.1f}% |\n")
 f.write("\n")
 
 if not result['perfect_onchain_markers'] and not result['perfect_offchain_markers']:
 f.write("## No Perfect Markers Found\n\n")
 f.write("No perfect markers with n >= 10 found. This may be because:\n")
 f.write("- Dataset is too small\n")
 f.write("- Position 30 uses all 26 characters (complex pattern)\n")
 f.write("- Need larger dataset for reliable markers\n\n")
 
 if result['strong_onchain_markers']:
 f.write("## Strong On-Chain Markers (>=70%, n >= 10)\n\n")
 f.write("| Char | Rate | Count |\n")
 f.write("|------|------|-------|\n")
 for m in result['strong_onchain_markers'][:10]:
 f.write(f"| {m['char']} | {m['rate']:.1f}% | {m['count']} |\n")
 f.write("\n")
 
 print(f"💾 Results saved to: {output_json}")
 print(f"📄 Report saved to: {output_md}")
 print()

if __name__ == "__main__":
 main()

