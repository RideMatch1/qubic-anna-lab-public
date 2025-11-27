#!/usr/bin/env python3
"""
Analyze Layer-4 Patterns auf vollständigem Datensatz (alle 23.765 Identities)
"""

import json
from pathlib import Path
from typing import Dict, List
from collections import Counter, defaultdict
from datetime import datetime

project_root = Path(__file__).parent.parent.parent
LAYER3_FILE = project_root / "outputs" / "derived" / "layer3_derivation_23k_complete.json"
LAYER4_FILE = project_root / "outputs" / "derived" / "layer4_derivation_full_23k.json"
OUTPUT_DIR = project_root / "outputs" / "derived"
REPORTS_DIR = project_root / "outputs" / "reports"

def analyze_layer4_patterns() -> Dict:
 """Analyze Layer-4 Patterns."""
 
 print("📂 Load Layer-3 und Layer-4 Daten...")
 with LAYER3_FILE.open() as f:
 layer3_data = json.load(f)
 layer3_results = layer3_data.get("results", [])
 
 with LAYER4_FILE.open() as f:
 layer4_data = json.load(f)
 layer4_results = layer4_data.get("results", [])
 
 # Erstelle Mapping
 layer4_map = {}
 for entry in layer4_results:
 l3_id = entry.get("layer3_identity", "")
 l4_id = entry.get("layer4_identity", "")
 if l3_id and l4_id and len(l3_id) == 60 and len(l4_id) == 60:
 layer4_map[l3_id] = l4_id
 
 pairs = []
 for l3_entry in layer3_results:
 l3_id = l3_entry.get("layer3_identity", "")
 l4_id = layer4_map.get(l3_id)
 if l3_id and l4_id:
 pairs.append({"layer3": l3_id, "layer4": l4_id})
 
 print(f"✅ {len(pairs)} Paare geloadn")
 print()
 
 # Analyze verschiedene Patterns
 analyses = {}
 
 # 1. Character Distribution
 print("🔍 Analyze Character Distribution...")
 l3_chars_all = Counter()
 l4_chars_all = Counter()
 
 for pair in pairs:
 l3_id = pair["layer3"]
 l4_id = pair["layer4"]
 for i in range(60):
 l3_chars_all[l3_id[i].upper()] += 1
 l4_chars_all[l4_id[i].upper()] += 1
 
 analyses["character_distribution"] = {
 "layer3": dict(l3_chars_all.most_common(26)),
 "layer4": dict(l4_chars_all.most_common(26))
 }
 print("✅ Character Distribution analysiert")
 
 # 2. Position-spezifische Patterns
 print("🔍 Analyze Position-spezifische Patterns...")
 position_stability = {}
 position_changes = {}
 
 for pos in range(60):
 same_count = 0
 different_count = 0
 char_changes = Counter()
 
 for pair in pairs:
 l3_id = pair["layer3"]
 l4_id = pair["layer4"]
 
 if l3_id[pos].upper() == l4_id[pos].upper():
 same_count += 1
 else:
 different_count += 1
 change = f"{l3_id[pos].upper()}->{l4_id[pos].upper()}"
 char_changes[change] += 1
 
 total = same_count + different_count
 stability_rate = same_count / total if total > 0 else 0
 
 position_stability[pos] = {
 "stability_rate": stability_rate,
 "same_count": same_count,
 "different_count": different_count
 }
 
 position_changes[pos] = dict(char_changes.most_common(10))
 
 analyses["position_stability"] = position_stability
 analyses["position_changes"] = position_changes
 print("✅ Position-spezifische Patterns analysiert")
 
 # 3. Block-Patterns
 print("🔍 Analyze Block-Patterns...")
 block_stability = {}
 block_ranges = [(0, 14), (14, 28), (28, 42), (42, 56)]
 
 for block_idx, (start, end) in enumerate(block_ranges):
 same_count = 0
 different_count = 0
 
 for pair in pairs:
 l3_id = pair["layer3"]
 l4_id = pair["layer4"]
 
 for pos in range(start, end):
 if l3_id[pos].upper() == l4_id[pos].upper():
 same_count += 1
 else:
 different_count += 1
 
 total = same_count + different_count
 stability_rate = same_count / total if total > 0 else 0
 
 block_stability[block_idx] = {
 "stability_rate": stability_rate,
 "same_count": same_count,
 "different_count": different_count
 }
 
 analyses["block_stability"] = block_stability
 print("✅ Block-Patterns analysiert")
 
 # 4. Spezielle Positionen (27, 30, 4, 55)
 print("🔍 Analyze spezielle Positionen...")
 special_positions = [4, 13, 27, 30, 41, 55]
 special_analysis = {}
 
 for pos in special_positions:
 if pos in position_stability:
 special_analysis[pos] = position_stability[pos]
 
 analyses["special_positions"] = special_analysis
 print("✅ Spezielle Positionen analysiert")
 
 return analyses

def main():
 """Hauptfunktion."""
 print("=" * 80)
 print("LAYER-4 PATTERNS ANALYSE (Alle 23.765 Identities)")
 print("=" * 80)
 print()
 
 # Analyze Patterns
 analyses = analyze_layer4_patterns()
 print()
 
 # Zeige Ergebnisse
 print("=" * 80)
 print("ERGEBNISSE")
 print("=" * 80)
 print()
 
 # Position Stability (Top 10)
 position_stability = analyses.get("position_stability", {})
 if position_stability:
 sorted_positions = sorted(
 position_stability.items(),
 key=lambda x: x[1]["stability_rate"],
 reverse=True
 )
 print("📊 Top 10 stabilste Positionen:")
 for pos, stats in sorted_positions[:10]:
 rate = stats["stability_rate"] * 100
 marker = "⭐" if pos in [4, 13, 27, 30, 41, 55] else " "
 print(f" {marker} Position {pos:2d}: {rate:5.1f}% ({stats['same_count']}/{stats['same_count']+stats['different_count']})")
 print()
 
 # Block Stability
 block_stability = analyses.get("block_stability", {})
 if block_stability:
 print("📊 Block-Stabilität:")
 for block_idx in range(4):
 if block_idx in block_stability:
 stats = block_stability[block_idx]
 rate = stats["stability_rate"] * 100
 print(f" Block {block_idx}: {rate:.1f}% stabil")
 print()
 
 # Spezielle Positionen
 special_positions = analyses.get("special_positions", {})
 if special_positions:
 print("📊 Spezielle Positionen:")
 for pos in [4, 13, 27, 30, 41, 55]:
 if pos in special_positions:
 stats = special_positions[pos]
 rate = stats["stability_rate"] * 100
 print(f" Position {pos:2d}: {rate:5.1f}% stabil")
 print()
 
 # Speichere Ergebnisse
 output_data = {
 "timestamp": datetime.now().isoformat(),
 "analyses": analyses
 }
 
 output_file = OUTPUT_DIR / "layer4_patterns_full_analysis.json"
 with output_file.open("w") as f:
 json.dump(output_data, f, indent=2)
 print(f"💾 Results saved to: {output_file}")
 
 # Erstelle Report
 report_lines = [
 "# Layer-4 Patterns Analyse (Alle 23.765 Identities)",
 "",
 f"**Generated**: {datetime.now().isoformat()}",
 "",
 "## Top 10 stabilste Positionen",
 ""
 ]
 
 if position_stability:
 sorted_positions = sorted(
 position_stability.items(),
 key=lambda x: x[1]["stability_rate"],
 reverse=True
 )
 for pos, stats in sorted_positions[:10]:
 rate = stats["stability_rate"] * 100
 report_lines.append(f"- **Position {pos}**: {rate:.1f}% stabil")
 report_lines.append("")
 
 report_file = REPORTS_DIR / "layer4_patterns_full_analysis_report.md"
 with report_file.open("w") as f:
 f.write("\n".join(report_lines) + "\n")
 print(f"📝 Report gespeichert: {report_file}")

if __name__ == "__main__":
 main()

