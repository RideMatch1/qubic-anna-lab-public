#!/usr/bin/env python3
"""
Vergleiche Layer-3 und Layer-4 Patterns und Charakteristika
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

def load_layer_data(file_path: Path) -> List[Dict]:
 """Load Layer-Daten."""
 if not file_path.exists():
 return []
 
 with file_path.open() as f:
 data = json.load(f)
 
 return data.get("results", [])

def analyze_character_distribution(identities: List[str], layer_name: str) -> Dict:
 """Analyze Character Distribution for eine Layer."""
 if not identities:
 return {}
 
 # Position-spezifische Distribution
 position_distributions = defaultdict(Counter)
 
 # Gesamt Distribution
 total_chars = Counter()
 
 for identity in identities:
 if len(identity) != 60:
 continue
 
 for pos in range(60):
 char = identity[pos].upper()
 position_distributions[pos][char] += 1
 total_chars[char] += 1
 
 # Top Characters pro Position
 top_per_position = {}
 for pos in range(60):
 if pos in position_distributions:
 top_per_position[pos] = dict(position_distributions[pos].most_common(5))
 
 return {
 "total_identities": len(identities),
 "total_chars": dict(total_chars),
 "position_distributions": {str(k): dict(v) for k, v in position_distributions.items()},
 "top_per_position": {str(k): v for k, v in top_per_position.items()}
 }

def analyze_position_patterns(layer3_data: List[Dict], layer4_data: List[Dict]) -> Dict:
 """Analyze Position-Patterns zwischen Layer-3 und Layer-4."""
 
 # Extrahiere Identities
 layer3_identities = [r.get("layer3_identity", "") for r in layer3_data if r.get("layer3_identity")]
 layer4_identities = [r.get("layer4_identity", "") for r in layer4_data if r.get("layer4_identity")]
 
 # Analyze Character Distribution
 layer3_dist = analyze_character_distribution(layer3_identities, "Layer-3")
 layer4_dist = analyze_character_distribution(layer4_identities, "Layer-4")
 
 # Vergleiche Position 30 und 4
 pos30_comparison = {}
 pos4_comparison = {}
 
 if "position_distributions" in layer3_dist and "position_distributions" in layer4_dist:
 l3_pos30 = layer3_dist["position_distributions"].get("30", {})
 l4_pos30 = layer4_dist["position_distributions"].get("30", {})
 pos30_comparison = {
 "layer3": l3_pos30,
 "layer4": l4_pos30,
 "common_chars": list(set(l3_pos30.keys()) & set(l4_pos30.keys()))
 }
 
 l3_pos4 = layer3_dist["position_distributions"].get("4", {})
 l4_pos4 = layer4_dist["position_distributions"].get("4", {})
 pos4_comparison = {
 "layer3": l3_pos4,
 "layer4": l4_pos4,
 "common_chars": list(set(l3_pos4.keys()) & set(l4_pos4.keys()))
 }
 
 return {
 "layer3": layer3_dist,
 "layer4": layer4_dist,
 "position30_comparison": pos30_comparison,
 "position4_comparison": pos4_comparison
 }

def analyze_evolution_patterns(layer3_data: List[Dict], layer4_data: List[Dict]) -> Dict:
 """Analyze Evolution-Patterns von Layer-3 zu Layer-4."""
 
 # Finde Paare (Layer-3 -> Layer-4)
 pairs = []
 layer4_map = {r.get("layer3_identity"): r.get("layer4_identity") 
 for r in layer4_data 
 if r.get("layer3_identity") and r.get("layer4_identity")}
 
 for l3_entry in layer3_data:
 l3_id = l3_entry.get("layer3_identity", "")
 l4_id = layer4_map.get(l3_id)
 if l3_id and l4_id:
 pairs.append({
 "layer3": l3_id,
 "layer4": l4_id
 })
 
 # Analyze Character-Änderungen
 position_changes = defaultdict(lambda: {"same": 0, "different": 0})
 
 for pair in pairs:
 l3_id = pair["layer3"]
 l4_id = pair["layer4"]
 if len(l3_id) == 60 and len(l4_id) == 60:
 for pos in range(60):
 if l3_id[pos].upper() == l4_id[pos].upper():
 position_changes[pos]["same"] += 1
 else:
 position_changes[pos]["different"] += 1
 
 # Berechne Änderungsraten
 change_rates = {}
 for pos in range(60):
 if pos in position_changes:
 total = position_changes[pos]["same"] + position_changes[pos]["different"]
 if total > 0:
 change_rates[pos] = {
 "same_rate": position_changes[pos]["same"] / total,
 "different_rate": position_changes[pos]["different"] / total,
 "total": total
 }
 
 return {
 "total_pairs": len(pairs),
 "position_changes": {str(k): v for k, v in position_changes.items()},
 "change_rates": {str(k): v for k, v in change_rates.items()}
 }

def main():
 """Hauptfunktion."""
 print("=" * 80)
 print("LAYER-3 vs. LAYER-4 PATTERNS ANALYSE")
 print("=" * 80)
 print()
 
 # Load Daten
 print("📂 Load Daten...")
 layer3_data = load_layer_data(LAYER3_FILE)
 layer4_data = load_layer_data(LAYER4_FILE)
 
 print(f"✅ Layer-3: {len(layer3_data)} Identities")
 print(f"✅ Layer-4: {len(layer4_data)} Identities")
 print()
 
 if not layer3_data or not layer4_data:
 print("❌ Nicht genug Daten for Analyse!")
 return
 
 # Analyze Position Patterns
 print("🔍 Analyze Position Patterns...")
 pattern_analysis = analyze_position_patterns(layer3_data, layer4_data)
 print("✅ Position Patterns analysiert")
 print()
 
 # Analyze Evolution Patterns
 print("🔍 Analyze Evolution Patterns...")
 evolution_analysis = analyze_evolution_patterns(layer3_data, layer4_data)
 print(f"✅ Evolution Patterns analysiert ({evolution_analysis['total_pairs']} Paare)")
 print()
 
 # Speichere Ergebnisse
 output_data = {
 "timestamp": datetime.now().isoformat(),
 "layer3_count": len(layer3_data),
 "layer4_count": len(layer4_data),
 "pattern_analysis": pattern_analysis,
 "evolution_analysis": evolution_analysis
 }
 
 output_file = OUTPUT_DIR / "layer3_layer4_patterns_comparison.json"
 with output_file.open("w") as f:
 json.dump(output_data, f, indent=2)
 print(f"💾 Results saved to: {output_file}")
 
 # Erstelle Report
 report_lines = [
 "# Layer-3 vs. Layer-4 Patterns Analyse",
 "",
 f"**Generated**: {datetime.now().isoformat()}",
 "",
 "## Zusammenfassung",
 "",
 f"- **Layer-3 Identities**: {len(layer3_data)}",
 f"- **Layer-4 Identities**: {len(layer4_data)}",
 f"- **Analysierte Paare**: {evolution_analysis['total_pairs']}",
 "",
 "## Position 30 Vergleich",
 ""
 ]
 
 if pattern_analysis.get("position30_comparison"):
 pos30 = pattern_analysis["position30_comparison"]
 report_lines.append("### Layer-3 (Top 10):")
 for char, count in sorted(pos30.get("layer3", {}).items(), key=lambda x: x[1], reverse=True)[:10]:
 report_lines.append(f"- **{char}**: {count}")
 report_lines.append("")
 report_lines.append("### Layer-4 (Top 10):")
 for char, count in sorted(pos30.get("layer4", {}).items(), key=lambda x: x[1], reverse=True)[:10]:
 report_lines.append(f"- **{char}**: {count}")
 report_lines.append("")
 
 report_lines.extend([
 "## Position 4 Vergleich",
 ""
 ])
 
 if pattern_analysis.get("position4_comparison"):
 pos4 = pattern_analysis["position4_comparison"]
 report_lines.append("### Layer-3 (Top 10):")
 for char, count in sorted(pos4.get("layer3", {}).items(), key=lambda x: x[1], reverse=True)[:10]:
 report_lines.append(f"- **{char}**: {count}")
 report_lines.append("")
 report_lines.append("### Layer-4 (Top 10):")
 for char, count in sorted(pos4.get("layer4", {}).items(), key=lambda x: x[1], reverse=True)[:10]:
 report_lines.append(f"- **{char}**: {count}")
 report_lines.append("")
 
 report_lines.extend([
 "## Evolution Patterns (Layer-3 → Layer-4)",
 "",
 "### Character-Änderungen pro Position:",
 ""
 ])
 
 # Zeige Positionen mit höchster/lowester Änderungsrate
 change_rates = evolution_analysis.get("change_rates", {})
 if change_rates:
 sorted_by_change = sorted(
 change_rates.items(),
 key=lambda x: x[1].get("different_rate", 0),
 reverse=True
 )
 
 report_lines.append("**Top 10 Positionen mit höchster Änderungsrate:**")
 for pos, rates in sorted_by_change[:10]:
 diff_rate = rates.get("different_rate", 0) * 100
 report_lines.append(f"- Position {pos}: {diff_rate:.1f}% ändern sich")
 report_lines.append("")
 
 sorted_by_same = sorted(
 change_rates.items(),
 key=lambda x: x[1].get("same_rate", 0),
 reverse=True
 )
 
 report_lines.append("**Top 10 Positionen mit höchster Übereinstimmung:**")
 for pos, rates in sorted_by_same[:10]:
 same_rate = rates.get("same_rate", 0) * 100
 report_lines.append(f"- Position {pos}: {same_rate:.1f}% bleiben gleich")
 report_lines.append("")
 
 report_file = REPORTS_DIR / "layer3_layer4_patterns_comparison_report.md"
 with report_file.open("w") as f:
 f.write("\n".join(report_lines) + "\n")
 print(f"📝 Report gespeichert: {report_file}")

if __name__ == "__main__":
 main()

