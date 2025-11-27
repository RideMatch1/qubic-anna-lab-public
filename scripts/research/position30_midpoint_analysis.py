#!/usr/bin/env python3
"""
Position 30 Midpoint Analysis

Analysiert warum Position 30 (genau am Mittelpunkt) so gut funktioniert:
- Midpoint-Hypothese testen
- Zusammenhang mit Checksum checkn
- Strukturelle Bedeutung verstehen
"""

import json
import sys
from pathlib import Path
from typing import Dict, List, Tuple
from collections import defaultdict, Counter

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

OUTPUT_DIR = project_root / "outputs" / "derived"
REPORTS_DIR = project_root / "outputs" / "reports"

def load_layer3_data() -> Dict:
 """Load Layer-3 Daten."""
 layer3_file = OUTPUT_DIR / "layer3_derivation_complete.json"
 
 if not layer3_file.exists():
 return {}
 
 with layer3_file.open() as f:
 return json.load(f)

def analyze_midpoint_structure(layer3_data: Dict) -> Dict:
 """Analyze strukturelle Bedeutung des Mittelpunkts."""
 results_data = layer3_data.get("results", [])
 
 # Position 30 ist genau am Mittelpunkt (30/60 = 50%)
 # Analyze symmetrische Positionen
 
 midpoint = 30
 checksum_start = 56
 
 # Analyze Position 30 vs Position 29 und 31 (um Mittelpunkt)
 pos29_chars = defaultdict(lambda: {"onchain": 0, "offchain": 0})
 pos30_chars = defaultdict(lambda: {"onchain": 0, "offchain": 0})
 pos31_chars = defaultdict(lambda: {"onchain": 0, "offchain": 0})
 
 # Analyze Distanz zu Checksum
 distance_to_checksum = defaultdict(lambda: {"onchain": 0, "offchain": 0})
 
 for result in results_data:
 layer3_id = result.get("layer3_identity", "")
 is_onchain = result.get("layer3_onchain", False)
 
 if len(layer3_id) < 60:
 continue
 
 # Position 29, 30, 31
 if len(layer3_id) > 29:
 char29 = layer3_id[29]
 if is_onchain:
 pos29_chars[char29]["onchain"] += 1
 else:
 pos29_chars[char29]["offchain"] += 1
 
 if len(layer3_id) > 30:
 char30 = layer3_id[30]
 if is_onchain:
 pos30_chars[char30]["onchain"] += 1
 else:
 pos30_chars[char30]["offchain"] += 1
 
 if len(layer3_id) > 31:
 char31 = layer3_id[31]
 if is_onchain:
 pos31_chars[char31]["onchain"] += 1
 else:
 pos31_chars[char31]["offchain"] += 1
 
 # Distanz zu Checksum
 dist = checksum_start - midpoint # 26 positions
 if is_onchain:
 distance_to_checksum[dist]["onchain"] += 1
 else:
 distance_to_checksum[dist]["offchain"] += 1
 
 return {
 "midpoint_position": midpoint,
 "checksum_start": checksum_start,
 "distance_to_checksum": dict(distance_to_checksum),
 "position29": {k: dict(v) for k, v in pos29_chars.items()},
 "position30": {k: dict(v) for k, v in pos30_chars.items()},
 "position31": {k: dict(v) for k, v in pos31_chars.items()}
 }

def analyze_symmetry(layer3_data: Dict) -> Dict:
 """Analyze Symmetrie um Mittelpunkt."""
 results_data = layer3_data.get("results", [])
 
 midpoint = 30
 symmetry_pairs = []
 
 # Teste symmetrische Positionen: (midpoint - i, midpoint + i)
 for i in range(1, 16): # Bis zu 15 Positionen vom Mittelpunkt
 pos_before = midpoint - i
 pos_after = midpoint + i
 
 if pos_before < 0 or pos_after >= 60:
 continue
 
 before_chars = defaultdict(lambda: {"onchain": 0, "offchain": 0})
 after_chars = defaultdict(lambda: {"onchain": 0, "offchain": 0})
 
 for result in results_data:
 layer3_id = result.get("layer3_identity", "")
 is_onchain = result.get("layer3_onchain", False)
 
 if len(layer3_id) <= max(pos_before, pos_after):
 continue
 
 char_before = layer3_id[pos_before]
 char_after = layer3_id[pos_after]
 
 if is_onchain:
 before_chars[char_before]["onchain"] += 1
 after_chars[char_after]["onchain"] += 1
 else:
 before_chars[char_before]["offchain"] += 1
 after_chars[char_after]["offchain"] += 1
 
 symmetry_pairs.append({
 "distance": i,
 "position_before": pos_before,
 "position_after": pos_after,
 "before_chars": {k: dict(v) for k, v in before_chars.items()},
 "after_chars": {k: dict(v) for k, v in after_chars.items()}
 })
 
 return {
 "midpoint": midpoint,
 "symmetry_pairs": symmetry_pairs
 }

def analyze_checksum_relationship(layer3_data: Dict) -> Dict:
 """Analyze Zusammenhang zwischen Position 30 und Checksum."""
 results_data = layer3_data.get("results", [])
 
 # Checksum ist Positionen 56-59 (letzte 4 Zeichen)
 pos30_to_checksum = defaultdict(lambda: {"onchain": 0, "offchain": 0})
 
 for result in results_data:
 layer3_id = result.get("layer3_identity", "")
 is_onchain = result.get("layer3_onchain", False)
 
 if len(layer3_id) < 60:
 continue
 
 pos30_char = layer3_id[30]
 checksum = layer3_id[56:60] # Letzte 4 Zeichen
 
 key = f"{pos30_char}_{checksum}"
 
 if is_onchain:
 pos30_to_checksum[key]["onchain"] += 1
 else:
 pos30_to_checksum[key]["offchain"] += 1
 
 return {
 "pos30_checksum_combinations": {k: dict(v) for k, v in pos30_to_checksum.items()}
 }

def main():
 """Hauptfunktion."""
 print("=" * 80)
 print("POSITION 30 MIDPOINT ANALYSIS")
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
 
 # 1. Midpoint Structure
 print("=" * 80)
 print("1. MIDPOINT STRUCTURE ANALYSIS")
 print("=" * 80)
 print()
 
 structure_result = analyze_midpoint_structure(layer3_data)
 
 print(f"Midpoint Position: {structure_result['midpoint_position']}/60 (50%)")
 print(f"Checksum Start: Position {structure_result['checksum_start']}")
 print(f"Distance to Checksum: {structure_result['checksum_start'] - structure_result['midpoint_position']} positions")
 print()
 
 print("Position 30 Character Distribution:")
 pos30_total = sum(sum(v.values()) for v in structure_result['position30'].values())
 print(f" Total: {pos30_total}")
 print(f" Unique characters: {len(structure_result['position30'])}")
 print()
 
 # 2. Symmetry Analysis
 print("=" * 80)
 print("2. SYMMETRY ANALYSIS")
 print("=" * 80)
 print()
 
 symmetry_result = analyze_symmetry(layer3_data)
 
 print(f"Midpoint: Position {symmetry_result['midpoint']}")
 print(f"Symmetry pairs tested: {len(symmetry_result['symmetry_pairs'])}")
 print()
 
 # Sample symmetry pairs
 for pair in symmetry_result['symmetry_pairs'][:5]:
 print(f"Distance {pair['distance']}: Position {pair['position_before']} ↔ Position {pair['position_after']}")
 print(f" Before: {len(pair['before_chars'])} unique chars")
 print(f" After: {len(pair['after_chars'])} unique chars")
 print()
 
 # 3. Checksum Relationship
 print("=" * 80)
 print("3. CHECKSUM RELATIONSHIP ANALYSIS")
 print("=" * 80)
 print()
 
 checksum_result = analyze_checksum_relationship(layer3_data)
 
 print(f"Position 30 + Checksum combinations: {len(checksum_result['pos30_checksum_combinations'])}")
 print()
 
 # Top combinations
 top_combos = sorted(
 checksum_result['pos30_checksum_combinations'].items(),
 key=lambda x: sum(x[1].values()),
 reverse=True
 )[:10]
 
 print("Top 10 Position 30 + Checksum Combinations:")
 for combo, counts in top_combos:
 total = sum(counts.values())
 onchain = counts.get("onchain", 0)
 onchain_pct = (onchain / total * 100) if total > 0 else 0
 print(f" {combo}: {onchain}/{total} on-chain ({onchain_pct:.1f}%)")
 print()
 
 # Speichere Ergebnisse
 OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
 
 results = {
 "midpoint_structure": structure_result,
 "symmetry": symmetry_result,
 "checksum_relationship": checksum_result
 }
 
 output_json = OUTPUT_DIR / "position30_midpoint_analysis.json"
 with output_json.open("w") as f:
 json.dump(results, f, indent=2)
 
 # Report
 REPORTS_DIR.mkdir(parents=True, exist_ok=True)
 output_md = REPORTS_DIR / "position30_midpoint_analysis_report.md"
 
 with output_md.open("w") as f:
 f.write("# Position 30 Midpoint Analysis Report\n\n")
 f.write("**Generated**: 2025-11-25\n\n")
 f.write("## Summary\n\n")
 f.write("Analysis of why Position 30 (exactly at midpoint) works so well.\n\n")
 
 f.write("## Key Findings\n\n")
 f.write(f"### Midpoint Position\n\n")
 f.write(f"- **Position**: {structure_result['midpoint_position']}/60 (50% through identity)\n")
 f.write(f"- **Checksum Start**: Position {structure_result['checksum_start']}\n")
 f.write(f"- **Distance to Checksum**: {structure_result['checksum_start'] - structure_result['midpoint_position']} positions\n\n")
 
 f.write(f"### Character Distribution\n\n")
 f.write(f"- **Position 30**: {len(structure_result['position30'])} unique characters\n")
 f.write(f"- **Position 29**: {len(structure_result['position29'])} unique characters\n")
 f.write(f"- **Position 31**: {len(structure_result['position31'])} unique characters\n\n")
 
 f.write("### Symmetry Analysis\n\n")
 f.write(f"- **Symmetry pairs tested**: {len(symmetry_result['symmetry_pairs'])}\n")
 f.write(f"- **Midpoint**: Position {symmetry_result['midpoint']}\n\n")
 
 f.write("### Checksum Relationship\n\n")
 f.write(f"- **Combinations tested**: {len(checksum_result['pos30_checksum_combinations'])}\n\n")
 
 f.write("## Hypotheses\n\n")
 f.write("### Hypothesis 1: Structural Midpoint\n\n")
 f.write("Position 30 is exactly at the midpoint (50% through identity). This may be:\n")
 f.write("- A structural checkpoint\n")
 f.write("- A validation point\n")
 f.write("- A transition marker\n\n")
 
 f.write("### Hypothesis 2: Checksum Preparation\n\n")
 f.write("Position 30 is 26 positions before checksum (positions 56-59). This may:\n")
 f.write("- Prepare for checksum calculation\n")
 f.write("- Be part of checksum algorithm\n")
 f.write("- Validate identity structure\n\n")
 
 f.write("### Hypothesis 3: Symmetry Point\n\n")
 f.write("Position 30 may be a symmetry point in the identity structure.\n\n")
 
 f.write("## Conclusion\n\n")
 f.write("Position 30's effectiveness may be due to:\n")
 f.write("1. **Midpoint structure**: Exactly 50% through identity\n")
 f.write("2. **Checksum relationship**: 26 positions before checksum\n")
 f.write("3. **Structural significance**: May be a validation/transition point\n\n")
 
 print(f"💾 Results saved to: {output_json}")
 print(f"📄 Report saved to: {output_md}")
 print()
 
 return results

if __name__ == "__main__":
 main()

