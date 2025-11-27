#!/usr/bin/env python3
"""
Optimiere Transformation-Vorhersage - Finde beste Kombinationen for höchste Genauigkeit
"""

import json
from pathlib import Path
from typing import Dict, List, Tuple
from collections import Counter, defaultdict
from datetime import datetime
import itertools

project_root = Path(__file__).parent.parent.parent
LAYER3_FILE = project_root / "outputs" / "derived" / "layer3_derivation_23k_complete.json"
LAYER4_FILE = project_root / "outputs" / "derived" / "layer4_derivation_full_23k.json"
OUTPUT_DIR = project_root / "outputs" / "derived"
REPORTS_DIR = project_root / "outputs" / "reports"

def identity_to_seed(identity: str) -> str:
 """Konvertiere Identity zu Seed."""
 return identity.lower()[:55]

def find_best_combinations(pairs: List[Dict], max_positions: int = 4, min_samples: int = 20) -> Dict:
 """Finde beste Kombinationen for höchste Stabilität."""
 
 # Bekannte wichtige Seed-Positionen
 candidate_positions = [0, 4, 13, 27, 30, 54]
 
 best_combinations = []
 
 # Teste 2-Positionen Kombinationen
 print("🔍 Teste 2-Positionen Kombinationen...")
 for pos1, pos2 in itertools.combinations(candidate_positions, 2):
 combo_groups = defaultdict(lambda: {"stable": 0, "changing": 0})
 
 for pair in pairs:
 seed = identity_to_seed(pair["layer3"])
 if len(seed) >= 55 and len(pair["layer3"]) > 27 and len(pair["layer4"]) > 27:
 char1 = seed[pos1].lower()
 char2 = seed[pos2].lower()
 combo = f"{char1}_{char2}"
 
 stable = pair["layer3"][27].upper() == pair["layer4"][27].upper()
 if stable:
 combo_groups[combo]["stable"] += 1
 else:
 combo_groups[combo]["changing"] += 1
 
 # Finde beste Kombination for diese Positionen
 for combo, stats in combo_groups.items():
 total = stats["stable"] + stats["changing"]
 if total >= min_samples:
 rate = stats["stable"] / total
 best_combinations.append({
 "positions": [pos1, pos2],
 "combination": combo,
 "rate": rate,
 "stable": stats["stable"],
 "total": total
 })
 
 # Teste 3-Positionen Kombinationen (nur Top Positionen)
 print("🔍 Teste 3-Positionen Kombinationen (27, 54, 13)...")
 for pos3 in [0, 4, 13, 30]:
 if pos3 in [27, 54]:
 continue
 
 combo_groups = defaultdict(lambda: {"stable": 0, "changing": 0})
 
 for pair in pairs:
 seed = identity_to_seed(pair["layer3"])
 if len(seed) >= 55 and len(pair["layer3"]) > 27 and len(pair["layer4"]) > 27:
 char27 = seed[27].lower()
 char54 = seed[54].lower()
 char3 = seed[pos3].lower()
 combo = f"{char27}_{char54}_{char3}"
 
 stable = pair["layer3"][27].upper() == pair["layer4"][27].upper()
 if stable:
 combo_groups[combo]["stable"] += 1
 else:
 combo_groups[combo]["changing"] += 1
 
 # Finde beste Kombination
 for combo, stats in combo_groups.items():
 total = stats["stable"] + stats["changing"]
 if total >= min_samples:
 rate = stats["stable"] / total
 best_combinations.append({
 "positions": [27, 54, pos3],
 "combination": combo,
 "rate": rate,
 "stable": stats["stable"],
 "total": total
 })
 
 # Sortiere nach Rate
 best_combinations.sort(key=lambda x: x["rate"], reverse=True)
 
 return {
 "best_combinations": best_combinations[:20], # Top 20
 "max_rate": best_combinations[0]["rate"] if best_combinations else 0,
 "total_tested": len(best_combinations)
 }

def analyze_practical_applications(pairs: List[Dict]) -> Dict:
 """Analyze praktische Anwendungen for 37.3% Genauigkeit."""
 
 # Nutze beste Kombination: Seed[27]='a' + Seed[54]='o'
 matching_pairs = []
 
 for pair in pairs:
 seed = identity_to_seed(pair["layer3"])
 if len(seed) >= 55:
 if seed[27].lower() == 'a' and seed[54].lower() == 'o':
 matching_pairs.append(pair)
 
 # Analyze diese Identities
 analysis = {
 "total_matching": len(matching_pairs),
 "stable_count": sum(1 for p in matching_pairs if p["layer3"][27].upper() == p["layer4"][27].upper()),
 "characteristics": {}
 }
 
 if matching_pairs:
 # Character Distribution
 pos27_chars = Counter()
 for pair in matching_pairs:
 pos27_chars[pair["layer3"][27].upper()] += 1
 
 analysis["characteristics"]["position27_distribution"] = dict(pos27_chars.most_common(10))
 
 # Identity Patterns
 identity_patterns = Counter()
 for pair in matching_pairs[:100]: # Sample
 pattern = pair["layer3"][:10] # Erste 10 Characters
 identity_patterns[pattern] += 1
 
 analysis["characteristics"]["identity_patterns"] = dict(identity_patterns.most_common(10))
 
 return analysis

def main():
 """Hauptfunktion."""
 print("=" * 80)
 print("TRANSFORMATION-VORHERSAGE OPTIMIERUNG")
 print("=" * 80)
 print()
 
 # Load Daten
 print("📂 Load Layer-3 und Layer-4 Daten...")
 with LAYER3_FILE.open() as f:
 layer3_data = json.load(f)
 layer3_results = layer3_data.get("results", [])
 
 with LAYER4_FILE.open() as f:
 layer4_data = json.load(f)
 layer4_results = layer4_data.get("results", [])
 
 # Erstelle Paare
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
 
 # Finde beste Kombinationen
 print("🔍 Finde beste Kombinationen for höchste Genauigkeit...")
 optimization_results = find_best_combinations(pairs, max_positions=3, min_samples=20)
 print("✅ Optimierung abgeschlossen")
 print()
 
 # Analyze praktische Anwendungen
 print("🔍 Analyze praktische Anwendungen...")
 practical_analysis = analyze_practical_applications(pairs)
 print("✅ Praktische Analyse abgeschlossen")
 print()
 
 # Zeige Ergebnisse
 print("=" * 80)
 print("ERGEBNISSE")
 print("=" * 80)
 print()
 
 # Beste Kombinationen
 best_combos = optimization_results.get("best_combinations", [])
 if best_combos:
 print("📊 Top 10 Kombinationen for höchste Genauigkeit:")
 for i, combo in enumerate(best_combos[:10], 1):
 rate = combo["rate"] * 100
 positions = combo["positions"]
 marker = "⭐" if rate > 35 else " "
 print(f" {marker} {i:2d}. Positions {positions}: {rate:.1f}% ({combo['stable']}/{combo['total']})")
 print(f" Kombination: {combo['combination']}")
 print()
 
 max_rate = optimization_results.get("max_rate", 0) * 100
 print(f"📊 Höchste erreichte Genauigkeit: {max_rate:.1f}%")
 print()
 
 # Praktische Anwendungen
 matching = practical_analysis.get("total_matching", 0)
 stable = practical_analysis.get("stable_count", 0)
 if matching > 0:
 rate = stable / matching * 100
 print("📊 Praktische Anwendung (Seed[27]='a' + Seed[54]='o'):")
 print(f" Matching Identities: {matching}")
 print(f" Stabile: {stable} ({rate:.1f}%)")
 print()
 
 # Speichere Ergebnisse
 output_data = {
 "timestamp": datetime.now().isoformat(),
 "optimization_results": optimization_results,
 "practical_analysis": practical_analysis
 }
 
 output_file = OUTPUT_DIR / "transformation_prediction_optimization.json"
 with output_file.open("w") as f:
 json.dump(output_data, f, indent=2)
 print(f"💾 Results saved to: {output_file}")
 
 # Erstelle Report
 report_lines = [
 "# Transformation-Vorhersage Optimierung",
 "",
 f"**Generated**: {datetime.now().isoformat()}",
 "",
 "## Top 10 Kombinationen",
 ""
 ]
 
 if best_combos:
 for i, combo in enumerate(best_combos[:10], 1):
 rate = combo["rate"] * 100
 positions = combo["positions"]
 report_lines.append(f"{i}. **Positions {positions}**: {rate:.1f}% ({combo['stable']}/{combo['total']})")
 report_lines.append(f" Kombination: {combo['combination']}")
 report_lines.append("")
 
 report_file = REPORTS_DIR / "transformation_prediction_optimization_report.md"
 with report_file.open("w") as f:
 f.write("\n".join(report_lines) + "\n")
 print(f"📝 Report gespeichert: {report_file}")

if __name__ == "__main__":
 main()

