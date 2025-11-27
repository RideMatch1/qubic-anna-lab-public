#!/usr/bin/env python3
"""
Analyze Character-Distanzen in Layer-3 → Layer-4 Transformation
"""

import json
from pathlib import Path
from typing import Dict, List
from collections import Counter, defaultdict
from datetime import datetime
import statistics

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

def analyze_character_distances(pairs: List[Dict]) -> Dict:
 """Analyze Character-Distanzen."""
 
 # 1. Lineare Distanz (A=0, B=1, ..., Z=25)
 linear_distances = defaultdict(list)
 
 # 2. Circular Distanz (mod 26)
 circular_distances = defaultdict(list)
 
 # 3. Position-spezifische Distanzen
 position_distances = defaultdict(lambda: {"linear": [], "circular": []})
 
 # 4. Distanz-Verteilung pro Position
 distance_distributions = defaultdict(Counter)
 
 # 5. Häufigste Distanzen
 all_distances = []
 
 for pair in pairs:
 l3_id = pair["layer3"]
 l4_id = pair["layer4"]
 
 for pos in range(60):
 l3_char = l3_id[pos].upper()
 l4_char = l4_id[pos].upper()
 
 if l3_char != l4_char:
 l3_val = ord(l3_char) - ord('A')
 l4_val = ord(l4_char) - ord('A')
 
 # Lineare Distanz
 linear_dist = abs(l4_val - l3_val)
 linear_distances[pos].append(linear_dist)
 position_distances[pos]["linear"].append(linear_dist)
 all_distances.append(linear_dist)
 
 # Circular Distanz (mod 26)
 circular_dist = min(
 (l4_val - l3_val) % 26,
 (l3_val - l4_val) % 26
 )
 circular_distances[pos].append(circular_dist)
 position_distances[pos]["circular"].append(circular_dist)
 
 distance_distributions[pos][circular_dist] += 1
 
 # Berechne Statistiken
 distance_stats = {}
 for pos in range(60):
 if pos in linear_distances and linear_distances[pos]:
 linear_dists = linear_distances[pos]
 circular_dists = circular_distances[pos]
 
 distance_stats[pos] = {
 "linear": {
 "mean": statistics.mean(linear_dists),
 "median": statistics.median(linear_dists),
 "stdev": statistics.stdev(linear_dists) if len(linear_dists) > 1 else 0,
 "min": min(linear_dists),
 "max": max(linear_dists),
 "most_common": Counter(linear_dists).most_common(5)
 },
 "circular": {
 "mean": statistics.mean(circular_dists),
 "median": statistics.median(circular_dists),
 "stdev": statistics.stdev(circular_dists) if len(circular_dists) > 1 else 0,
 "min": min(circular_dists),
 "max": max(circular_dists),
 "most_common": Counter(circular_dists).most_common(5)
 },
 "distribution": dict(distance_distributions[pos].most_common(10))
 }
 
 # Gesamt-Statistiken
 overall_stats = {
 "linear": {
 "mean": statistics.mean(all_distances) if all_distances else 0,
 "median": statistics.median(all_distances) if all_distances else 0,
 "stdev": statistics.stdev(all_distances) if len(all_distances) > 1 else 0,
 "distribution": dict(Counter(all_distances).most_common(15))
 }
 }
 
 return {
 "total_changes": len(all_distances),
 "distance_stats": {str(k): v for k, v in distance_stats.items()},
 "overall_stats": overall_stats,
 "key_positions": {
 str(pos): distance_stats.get(pos, {})
 for pos in [27, 55, 30, 4]
 if pos in distance_stats
 }
 }

def main():
 """Hauptfunktion."""
 print("=" * 80)
 print("CHARACTER-DISTANZ ANALYSE")
 print("=" * 80)
 print()
 
 # Load Paare
 print("📂 Load Layer-3 → Layer-4 Paare...")
 pairs = load_pairs()
 print(f"✅ {len(pairs)} Paare geloadn")
 print()
 
 # Analyze Distanzen
 print("🔍 Analyze Character-Distanzen...")
 distance_analysis = analyze_character_distances(pairs)
 print("✅ Character-Distanzen analysiert")
 print()
 
 # Zeige Ergebnisse
 print("=" * 80)
 print("ERGEBNISSE")
 print("=" * 80)
 print()
 
 # Gesamt-Statistiken
 overall = distance_analysis.get("overall_stats", {}).get("linear", {})
 if overall:
 print("📊 Gesamt-Statistiken (Lineare Distanz):")
 print(f" Mean: {overall.get('mean', 0):.2f}")
 print(f" Median: {overall.get('median', 0):.2f}")
 print(f" StDev: {overall.get('stdev', 0):.2f}")
 print()
 
 dist_dist = overall.get("distribution", {})
 if dist_dist:
 print(" Top Distanzen:")
 for dist, count in list(dist_dist.items())[:10]:
 print(f" {dist}: {count} Fälle")
 print()
 
 # Key Positionen
 key_pos = distance_analysis.get("key_positions", {})
 if key_pos:
 print("📊 Key Positionen (Circular Distanz):")
 for pos in [27, 55, 30, 4]:
 pos_str = str(pos)
 if pos_str in key_pos:
 circular = key_pos[pos_str].get("circular", {})
 mean = circular.get("mean", 0)
 median = circular.get("median", 0)
 most_common = circular.get("most_common", [])
 print(f" Position {pos:2d}: Mean={mean:.2f}, Median={median:.1f}", end="")
 if most_common:
 print(f" | Top: {most_common[0][0]} ({most_common[0][1]} Fälle)")
 else:
 print()
 print()
 
 # Speichere Ergebnisse
 output_data = {
 "timestamp": datetime.now().isoformat(),
 "distance_analysis": distance_analysis
 }
 
 output_file = OUTPUT_DIR / "character_distances_analysis.json"
 with output_file.open("w") as f:
 json.dump(output_data, f, indent=2)
 print(f"💾 Results saved to: {output_file}")
 
 # Erstelle Report
 report_lines = [
 "# Character-Distanz Analyse",
 "",
 f"**Generated**: {datetime.now().isoformat()}",
 "",
 "## Gesamt-Statistiken",
 ""
 ]
 
 if overall:
 report_lines.extend([
 f"- **Mean**: {overall.get('mean', 0):.2f}",
 f"- **Median**: {overall.get('median', 0):.2f}",
 f"- **StDev**: {overall.get('stdev', 0):.2f}",
 ""
 ])
 
 report_file = REPORTS_DIR / "character_distances_analysis_report.md"
 with report_file.open("w") as f:
 f.write("\n".join(report_lines) + "\n")
 print(f"📝 Report gespeichert: {report_file}")

if __name__ == "__main__":
 main()

