#!/usr/bin/env python3
"""
Analyze Seed-Position 54 Anomalie
- Seed 'o' an Position 54 hat 31.7% Stabilität (höchste Rate!)
- Warum ist Seed-Position 54 (letzte Position) so wichtig?
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

def identity_to_seed(identity: str) -> str:
 """Konvertiere Identity zu Seed."""
 return identity.lower()[:55]

def analyze_seed_position54() -> Dict:
 """Analyze Seed-Position 54 im Detail."""
 
 print("📂 Load Daten...")
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
 if l3_id and l4_id:
 layer4_map[l3_id] = l4_id
 
 pairs = []
 for l3_entry in layer3_results:
 l3_id = l3_entry.get("layer3_identity", "")
 l4_id = layer4_map.get(l3_id)
 if l3_id and l4_id and len(l3_id) == 60 and len(l4_id) == 60:
 pairs.append({"layer3": l3_id, "layer4": l4_id})
 
 print(f"✅ {len(pairs)} Paare geloadn")
 print()
 
 # Analyze Seed-Position 54 for verschiedene Identity-Positionen
 print("🔍 Analyze Seed-Position 54...")
 
 # Teste verschiedene Identity-Positionen
 identity_positions_to_test = [0, 4, 13, 27, 30, 41, 55, 59]
 
 seed54_analysis = {}
 
 for identity_pos in identity_positions_to_test:
 seed_char_to_stability = defaultdict(lambda: {"stable": 0, "changing": 0})
 
 for pair in pairs:
 l3_id = pair["layer3"]
 l4_id = pair["layer4"]
 seed = identity_to_seed(l3_id)
 
 if len(seed) >= 55 and len(l3_id) > identity_pos and len(l4_id) > identity_pos:
 seed_char_54 = seed[54].lower() # Letzte Position im Seed
 stable = l3_id[identity_pos].upper() == l4_id[identity_pos].upper()
 
 if stable:
 seed_char_to_stability[seed_char_54]["stable"] += 1
 else:
 seed_char_to_stability[seed_char_54]["changing"] += 1
 
 # Berechne Raten
 char_rates = {}
 for char, stats in seed_char_to_stability.items():
 total = stats["stable"] + stats["changing"]
 if total >= 10:
 rate = stats["stable"] / total
 char_rates[char] = {
 "rate": rate,
 "stable": stats["stable"],
 "changing": stats["changing"],
 "total": total
 }
 
 seed54_analysis[identity_pos] = dict(sorted(char_rates.items(), key=lambda x: x[1]["rate"], reverse=True))
 
 # Spezielle Analyse: Seed-Position 54 'o' for Identity-Position 27
 seed_o_pos27 = {
 "stable": 0,
 "changing": 0,
 "examples": []
 }
 
 for pair in pairs:
 l3_id = pair["layer3"]
 l4_id = pair["layer4"]
 seed = identity_to_seed(l3_id)
 
 if len(seed) >= 55 and len(l3_id) > 27 and len(l4_id) > 27:
 if seed[54].lower() == 'o':
 stable = l3_id[27].upper() == l4_id[27].upper()
 if stable:
 seed_o_pos27["stable"] += 1
 if len(seed_o_pos27["examples"]) < 10:
 seed_o_pos27["examples"].append({
 "seed": seed,
 "l3_id": l3_id,
 "l4_id": l4_id,
 "pos27_l3": l3_id[27],
 "pos27_l4": l4_id[27]
 })
 else:
 seed_o_pos27["changing"] += 1
 
 return {
 "seed54_by_identity_position": seed54_analysis,
 "seed_o_position27": seed_o_pos27
 }

def main():
 """Hauptfunktion."""
 print("=" * 80)
 print("SEED-POSITION 54 ANALYSE (Anomalie: Seed 'o' = 31.7%)")
 print("=" * 80)
 print()
 
 # Analyze
 analysis = analyze_seed_position54()
 print()
 
 # Zeige Ergebnisse
 print("=" * 80)
 print("ERGEBNISSE")
 print("=" * 80)
 print()
 
 # Seed-Position 54 for verschiedene Identity-Positionen
 seed54_by_pos = analysis.get("seed54_by_identity_position", {})
 if seed54_by_pos:
 print("📊 Seed-Position 54 (letzte Position) for verschiedene Identity-Positionen:")
 for identity_pos in [0, 4, 13, 27, 30, 41, 55, 59]:
 if identity_pos in seed54_by_pos:
 char_rates = seed54_by_pos[identity_pos]
 if char_rates:
 print(f"\n Identity-Position {identity_pos}:")
 for char, stats in list(char_rates.items())[:5]:
 rate = stats["rate"] * 100
 marker = "⭐" if char == 'o' and rate > 30 else " "
 print(f" {marker} Seed 'o': {rate:.1f}% stabil ({stats['stable']}/{stats['total']})")
 print()
 
 # Seed 'o' Position 27 Spezial-Analyse
 seed_o = analysis.get("seed_o_position27", {})
 if seed_o:
 total = seed_o["stable"] + seed_o["changing"]
 if total > 0:
 rate = seed_o["stable"] / total * 100
 print("📊 Seed 'o' an Position 54 → Identity-Position 27:")
 print(f" Stabilität: {rate:.1f}% ({seed_o['stable']}/{total})")
 print()
 
 if seed_o["examples"]:
 print(" Beispiele (stabile Fälle):")
 for i, ex in enumerate(seed_o["examples"][:5], 1):
 print(f" {i}. Seed: {ex['seed'][:20]}...{ex['seed'][50:]} (pos54='o')")
 print(f" L3: {ex['l3_id'][:30]}... (pos27={ex['pos27_l3']})")
 print(f" L4: {ex['l4_id'][:30]}... (pos27={ex['pos27_l4']})")
 print()
 
 # Speichere Ergebnisse
 output_data = {
 "timestamp": datetime.now().isoformat(),
 "analysis": analysis
 }
 
 output_file = OUTPUT_DIR / "seed_position54_analysis.json"
 with output_file.open("w") as f:
 json.dump(output_data, f, indent=2)
 print(f"💾 Results saved to: {output_file}")
 
 # Erstelle Report
 report_lines = [
 "# Seed-Position 54 Analyse (Anomalie: Seed 'o' = 31.7%)",
 "",
 f"**Generated**: {datetime.now().isoformat()}",
 "",
 "## Seed-Position 54 for verschiedene Identity-Positionen",
 ""
 ]
 
 if seed54_by_pos:
 for identity_pos in [0, 4, 13, 27, 30, 41, 55, 59]:
 if identity_pos in seed54_by_pos:
 char_rates = seed54_by_pos[identity_pos]
 if char_rates:
 report_lines.append(f"### Identity-Position {identity_pos}:")
 for char, stats in list(char_rates.items())[:5]:
 rate = stats["rate"] * 100
 report_lines.append(f"- **Seed '{char}'**: {rate:.1f}% stabil ({stats['stable']}/{stats['total']})")
 report_lines.append("")
 
 report_file = REPORTS_DIR / "seed_position54_analysis_report.md"
 with report_file.open("w") as f:
 f.write("\n".join(report_lines) + "\n")
 print(f"📝 Report gespeichert: {report_file}")

if __name__ == "__main__":
 main()

