#!/usr/bin/env python3
"""
Analyze Block-Patterns (14-Character-Blocks) in Layer-3 → Layer-4 Transformation
"""

import json
from pathlib import Path
from typing import Dict, List
from collections import Counter, defaultdict
from datetime import datetime

project_root = Path(__file__).parent.parent.parent
LAYER3_FILE = project_root / "outputs" / "derived" / "layer3_derivation_23k_complete.json"
LAYER4_FILE = project_root / "outputs" / "derived" / "layer4_derivation_sample_5000.json"
OUTPUT_DIR = project_root / "outputs" / "derived"
REPORTS_DIR = project_root / "outputs" / "reports"

def load_pairs() -> List[Dict]:
 """Load Layer-3 → Layer-4 Paare."""
 layer3_data = []
 if LAYER3_FILE.exists():
 with LAYER3_FILE.open() as f:
 data = json.load(f)
 layer3_data = data.get("results", [])
 
 layer4_map = {}
 if LAYER4_FILE.exists():
 with LAYER4_FILE.open() as f:
 data = json.load(f)
 for entry in data.get("results", []):
 l3_id = entry.get("layer3_identity", "")
 l4_id = entry.get("layer4_identity", "")
 if l3_id and l4_id:
 layer4_map[l3_id] = l4_id
 
 pairs = []
 for l3_entry in layer3_data:
 l3_id = l3_entry.get("layer3_identity", "")
 l4_id = layer4_map.get(l3_id)
 if l3_id and l4_id and len(l3_id) == 60 and len(l4_id) == 60:
 pairs.append({"layer3": l3_id, "layer4": l4_id})
 
 return pairs

def analyze_block_patterns(pairs: List[Dict]) -> Dict:
 """Analyze Block-Patterns (14-Character-Blocks)."""
 
 # Identity hat 60 Characters = 4 Blocks à 14 Characters + 4 Checksum
 # Blocks: 0-13, 14-27, 28-41, 42-55, 56-59 (Checksum)
 
 block_changes = defaultdict(lambda: {"same": 0, "different": 0, "changes": []})
 block_stability = defaultdict(lambda: {"fully_same": 0, "fully_different": 0, "partial": 0})
 
 # Block-spezifische Character-Änderungen
 block_char_changes = defaultdict(lambda: Counter())
 
 for pair in pairs:
 l3_id = pair["layer3"]
 l4_id = pair["layer4"]
 
 # Analyze 4 Blocks (0-13, 14-27, 28-41, 42-55)
 block_ranges = [(0, 14), (14, 28), (28, 42), (42, 56)]
 
 for block_idx, (start, end) in enumerate(block_ranges):
 l3_block = l3_id[start:end]
 l4_block = l4_id[start:end]
 
 # Zähle Änderungen im Block
 changes_in_block = sum(1 for i in range(len(l3_block)) if l3_block[i] != l4_block[i])
 
 if changes_in_block == 0:
 block_stability[block_idx]["fully_same"] += 1
 elif changes_in_block == len(l3_block):
 block_stability[block_idx]["fully_different"] += 1
 else:
 block_stability[block_idx]["partial"] += 1
 
 # Analyze Character-Änderungen im Block
 for i in range(len(l3_block)):
 if l3_block[i] != l4_block[i]:
 transition = f"{l3_block[i].upper()}->{l4_block[i].upper()}"
 block_char_changes[block_idx][transition] += 1
 
 # Berechne Block-Änderungsraten
 block_change_rates = {}
 for block_idx in range(4):
 if block_idx in block_stability:
 stats = block_stability[block_idx]
 total = stats["fully_same"] + stats["fully_different"] + stats["partial"]
 if total > 0:
 block_change_rates[block_idx] = {
 "fully_same_rate": stats["fully_same"] / total,
 "fully_different_rate": stats["fully_different"] / total,
 "partial_rate": stats["partial"] / total,
 "total": total
 }
 
 return {
 "block_stability": {str(k): dict(v) for k, v in block_stability.items()},
 "block_change_rates": {str(k): v for k, v in block_change_rates.items()},
 "block_char_changes": {
 str(k): dict(Counter(v).most_common(10))
 for k, v in block_char_changes.items()
 }
 }

def analyze_position_in_blocks(pairs: List[Dict]) -> Dict:
 """Analyze wie sich Positionen innerhalb von Blocks verhalten."""
 
 # Position 27 ist in Block 1 (14-27), Position 55 ist in Block 3 (42-55)
 block_analysis = defaultdict(lambda: defaultdict(lambda: {"same": 0, "different": 0}))
 
 for pair in pairs:
 l3_id = pair["layer3"]
 l4_id = pair["layer4"]
 
 # Block 0: 0-13, Block 1: 14-27, Block 2: 28-41, Block 3: 42-55
 block_ranges = [(0, 14), (14, 28), (28, 42), (42, 56)]
 
 for block_idx, (start, end) in enumerate(block_ranges):
 for pos_in_block in range(end - start):
 global_pos = start + pos_in_block
 
 if l3_id[global_pos].upper() == l4_id[global_pos].upper():
 block_analysis[block_idx][pos_in_block]["same"] += 1
 else:
 block_analysis[block_idx][pos_in_block]["different"] += 1
 
 # Berechne Raten
 block_position_rates = {}
 for block_idx in range(4):
 block_position_rates[block_idx] = {}
 for pos_in_block in range(14):
 if pos_in_block in block_analysis[block_idx]:
 stats = block_analysis[block_idx][pos_in_block]
 total = stats["same"] + stats["different"]
 if total > 0:
 block_position_rates[block_idx][pos_in_block] = {
 "same_rate": stats["same"] / total,
 "different_rate": stats["different"] / total
 }
 
 return {
 "block_position_rates": {
 str(k): {str(p): v for p, v in positions.items()}
 for k, positions in block_position_rates.items()
 }
 }

def main():
 """Hauptfunktion."""
 print("=" * 80)
 print("BLOCK-PATTERNS ANALYSE (14-Character-Blocks)")
 print("=" * 80)
 print()
 
 # Load Paare
 print("📂 Load Layer-3 → Layer-4 Paare...")
 pairs = load_pairs()
 print(f"✅ {len(pairs)} Paare geloadn")
 print()
 
 # Analyze Block-Patterns
 print("🔍 Analyze Block-Patterns...")
 block_analysis = analyze_block_patterns(pairs)
 print("✅ Block-Patterns analysiert")
 print()
 
 # Analyze Positionen in Blocks
 print("🔍 Analyze Positionen in Blocks...")
 position_analysis = analyze_position_in_blocks(pairs)
 print("✅ Positionen in Blocks analysiert")
 print()
 
 # Zeige Ergebnisse
 print("=" * 80)
 print("ERGEBNISSE")
 print("=" * 80)
 print()
 
 # Block-Stabilität
 block_rates = block_analysis.get("block_change_rates", {})
 if block_rates:
 print("📊 Block-Stabilität:")
 for block_idx in range(4):
 block_str = str(block_idx)
 if block_str in block_rates:
 rates = block_rates[block_str]
 same_rate = rates.get("fully_same_rate", 0) * 100
 diff_rate = rates.get("fully_different_rate", 0) * 100
 partial_rate = rates.get("partial_rate", 0) * 100
 print(f" Block {block_idx} (Pos {block_idx*14}-{block_idx*14+13}):")
 print(f" Fully Same: {same_rate:.1f}%")
 print(f" Fully Different: {diff_rate:.1f}%")
 print(f" Partial: {partial_rate:.1f}%")
 print()
 
 # Position 27 ist in Block 1 (Position 13 im Block = global Position 27)
 # Position 55 ist in Block 3 (Position 13 im Block = global Position 55)
 block_pos = position_analysis.get("block_position_rates", {})
 if block_pos:
 print("📊 Position 27 (Block 1, Position 13 im Block):")
 if "1" in block_pos and "13" in block_pos["1"]:
 rates = block_pos["1"]["13"]
 same_rate = rates.get("same_rate", 0) * 100
 print(f" Same Rate: {same_rate:.1f}%")
 print()
 
 print("📊 Position 55 (Block 3, Position 13 im Block):")
 if "3" in block_pos and "13" in block_pos["3"]:
 rates = block_pos["3"]["13"]
 same_rate = rates.get("same_rate", 0) * 100
 print(f" Same Rate: {same_rate:.1f}%")
 print()
 
 # Speichere Ergebnisse
 output_data = {
 "timestamp": datetime.now().isoformat(),
 "block_analysis": block_analysis,
 "position_analysis": position_analysis
 }
 
 output_file = OUTPUT_DIR / "block_patterns_analysis.json"
 with output_file.open("w") as f:
 json.dump(output_data, f, indent=2)
 print(f"💾 Results saved to: {output_file}")
 
 # Erstelle Report
 report_lines = [
 "# Block-Patterns Analyse (14-Character-Blocks)",
 "",
 f"**Generated**: {datetime.now().isoformat()}",
 "",
 "## Block-Stabilität",
 ""
 ]
 
 if block_rates:
 for block_idx in range(4):
 block_str = str(block_idx)
 if block_str in block_rates:
 rates = block_rates[block_str]
 report_lines.extend([
 f"### Block {block_idx} (Position {block_idx*14}-{block_idx*14+13}):",
 f"- **Fully Same**: {rates.get('fully_same_rate', 0)*100:.1f}%",
 f"- **Fully Different**: {rates.get('fully_different_rate', 0)*100:.1f}%",
 f"- **Partial**: {rates.get('partial_rate', 0)*100:.1f}%",
 ""
 ])
 
 report_file = REPORTS_DIR / "block_patterns_analysis_report.md"
 with report_file.open("w") as f:
 f.write("\n".join(report_lines) + "\n")
 print(f"📝 Report gespeichert: {report_file}")

if __name__ == "__main__":
 main()

