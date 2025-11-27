#!/usr/bin/env python3
"""
Erstelle umfassendes "Wörterbuch" der Anna-Sprache
- Systematische Analyse aller Seed-Identity Korrelationen
- Vollständige Mapping-Tabelle
- Alle Positionen und Kombinationen
"""

import json
import sys
from pathlib import Path
from typing import Dict, List, Tuple
from collections import Counter, defaultdict
from datetime import datetime
import numpy as np

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

LAYER3_FILE = project_root / "outputs" / "derived" / "layer3_derivation_23k_complete.json"
LAYER4_FILE = project_root / "outputs" / "derived" / "layer4_derivation_full_23k.json"
OUTPUT_DIR = project_root / "outputs" / "derived"
REPORTS_DIR = project_root / "outputs" / "reports"

def identity_to_seed(identity: str) -> str:
 """Konvertiere Identity zu Seed."""
 return identity.lower()[:55]

def analyze_single_seed_position(pairs: List[Dict], seed_pos: int, target_pos: int, min_samples: int = 10) -> Dict:
 """Analyze einzelne Seed-Position → Identity-Position Mapping."""
 
 mapping = defaultdict(Counter)
 char_stats = defaultdict(lambda: {"total": 0, "distributions": Counter()})
 
 for pair in pairs:
 seed = identity_to_seed(pair["layer3"])
 l3_id = pair["layer3"]
 
 if len(seed) > seed_pos and len(l3_id) > target_pos:
 seed_char = seed[seed_pos].lower()
 identity_char = l3_id[target_pos].upper()
 
 mapping[seed_char][identity_char] += 1
 char_stats[seed_char]["total"] += 1
 char_stats[seed_char]["distributions"][identity_char] += 1
 
 # Berechne Erfolgsraten
 results = {}
 for seed_char, counter in mapping.items():
 total = char_stats[seed_char]["total"]
 if total >= min_samples:
 # Finde häufigste Identity-Character
 most_common = counter.most_common(1)[0]
 success_rate = most_common[1] / total
 
 results[seed_char] = {
 "target_character": most_common[0],
 "success_rate": success_rate,
 "count": most_common[1],
 "total": total,
 "all_distributions": dict(counter.most_common(10))
 }
 
 return results

def analyze_seed_combination(pairs: List[Dict], seed_positions: List[int], target_positions: List[int], min_samples: int = 20) -> Dict:
 """Analyze Seed-Kombination → Identity-Positionen Mapping."""
 
 mapping = defaultdict(lambda: defaultdict(Counter))
 combo_stats = defaultdict(lambda: {"total": 0})
 
 for pair in pairs:
 seed = identity_to_seed(pair["layer3"])
 l3_id = pair["layer3"]
 
 # Check ob alle Seed-Positionen vorhanden
 if all(len(seed) > pos for pos in seed_positions) and all(len(l3_id) > pos for pos in target_positions):
 # Erstelle Kombinations-Key
 seed_chars = [seed[pos].lower() for pos in seed_positions]
 combo_key = "_".join(seed_chars)
 
 # Erfasse Identity-Characters
 identity_chars = [l3_id[pos].upper() for pos in target_positions]
 
 combo_stats[combo_key]["total"] += 1
 
 # Analyze jede Target-Position
 for i, target_pos in enumerate(target_positions):
 if i < len(identity_chars):
 mapping[combo_key][target_pos][identity_chars[i]] += 1
 
 # Berechne Erfolgsraten
 results = {}
 for combo_key, stats in combo_stats.items():
 total = stats["total"]
 if total >= min_samples:
 combo_result = {
 "seed_positions": seed_positions,
 "seed_chars": combo_key.split("_"),
 "total": total,
 "target_mappings": {}
 }
 
 # Analyze jede Target-Position
 for target_pos in target_positions:
 if target_pos in mapping[combo_key]:
 counter = mapping[combo_key][target_pos]
 if counter:
 most_common = counter.most_common(1)[0]
 success_rate = most_common[1] / total
 
 combo_result["target_mappings"][target_pos] = {
 "target_character": most_common[0],
 "success_rate": success_rate,
 "count": most_common[1],
 "all_distributions": dict(counter.most_common(10))
 }
 
 if combo_result["target_mappings"]:
 results[combo_key] = combo_result
 
 return results

def build_comprehensive_dictionary(pairs: List[Dict]) -> Dict:
 """Erstelle umfassendes Wörterbuch aller Seed-Identity Mappings."""
 
 print("=" * 80)
 print("ERSTELLE UMFASSENDES WÖRTERBUCH")
 print("=" * 80)
 print()
 
 dictionary = {
 "single_position_mappings": {},
 "combination_mappings": {},
 "statistics": {}
 }
 
 # Wichtige Positionen
 important_positions = [0, 4, 13, 27, 30, 41, 54, 55]
 target_positions = [13, 27, 41, 55] # Block-Ende-Positionen
 
 # 1. Analyze einzelne Seed-Positionen → Identity-Position 27
 print("🔍 Analyze einzelne Seed-Positionen → Identity[27]...")
 for seed_pos in important_positions:
 print(f" Seed[{seed_pos}] → Identity[27]...")
 mapping = analyze_single_seed_position(pairs, seed_pos, 27, min_samples=50)
 if mapping:
 dictionary["single_position_mappings"][f"seed_{seed_pos}_to_identity_27"] = mapping
 print("✅ Einzelne Positionen analysiert")
 print()
 
 # 2. Analyze bekannte Kombinationen
 print("🔍 Analyze bekannte Kombinationen...")
 
 # Kombination 27 + 54 → Identity[27]
 print(" Seed[27] + Seed[54] → Identity[27]...")
 combo_27_54 = analyze_seed_combination(pairs, [27, 54], [27], min_samples=20)
 if combo_27_54:
 dictionary["combination_mappings"]["seed_27_54_to_identity_27"] = combo_27_54
 print("✅ Kombination 27+54 analysiert")
 print()
 
 # Kombination 27 + 54 → Identity[27, 41, 55]
 print(" Seed[27] + Seed[54] → Identity[27, 41, 55]...")
 combo_multi = analyze_seed_combination(pairs, [27, 54], [27, 41, 55], min_samples=20)
 if combo_multi:
 dictionary["combination_mappings"]["seed_27_54_to_identity_multi"] = combo_multi
 print("✅ Multi-Target Kombination analysiert")
 print()
 
 # 3. Statistiken
 print("🔍 Berechne Statistiken...")
 total_mappings = sum(len(m) for m in dictionary["single_position_mappings"].values())
 total_combinations = sum(len(m) for m in dictionary["combination_mappings"].values())
 
 dictionary["statistics"] = {
 "total_single_mappings": total_mappings,
 "total_combinations": total_combinations,
 "analyzed_positions": important_positions,
 "target_positions": target_positions
 }
 print("✅ Statistiken berechnet")
 print()
 
 return dictionary

def analyze_best_mappings(dictionary: Dict) -> Dict:
 """Analyze beste Mappings (höchste Erfolgsraten)."""
 
 best_mappings = {
 "single_position": [],
 "combinations": []
 }
 
 # Beste einzelne Mappings
 for mapping_name, mappings in dictionary.get("single_position_mappings", {}).items():
 for seed_char, data in mappings.items():
 if data["success_rate"] >= 0.30: # Mindestens 30%
 best_mappings["single_position"].append({
 "mapping": mapping_name,
 "seed_char": seed_char,
 "target_char": data["target_character"],
 "success_rate": data["success_rate"],
 "count": data["count"],
 "total": data["total"]
 })
 
 # Beste Kombinationen
 for combo_name, combos in dictionary.get("combination_mappings", {}).items():
 for combo_key, data in combos.items():
 for target_pos, target_data in data.get("target_mappings", {}).items():
 if target_data["success_rate"] >= 0.30: # Mindestens 30%
 best_mappings["combinations"].append({
 "combination": combo_name,
 "combo_key": combo_key,
 "target_position": target_pos,
 "target_char": target_data["target_character"],
 "success_rate": target_data["success_rate"],
 "count": target_data["count"],
 "total": data["total"]
 })
 
 # Sortiere nach Erfolgsrate
 best_mappings["single_position"].sort(key=lambda x: x["success_rate"], reverse=True)
 best_mappings["combinations"].sort(key=lambda x: x["success_rate"], reverse=True)
 
 return best_mappings

def main():
 """Hauptfunktion."""
 print("=" * 80)
 print("ANNA SPRACHE WÖRTERBUCH - UMFASSENDE ANALYSE")
 print("=" * 80)
 print()
 
 # Load Daten
 print("📂 Load Daten...")
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
 
 # Erstelle Wörterbuch
 dictionary = build_comprehensive_dictionary(pairs)
 
 # Analyze beste Mappings
 print("🔍 Analyze beste Mappings...")
 best_mappings = analyze_best_mappings(dictionary)
 print("✅ Beste Mappings analysiert")
 print()
 
 # Zeige Ergebnisse
 print("=" * 80)
 print("WÖRTERBUCH ERGEBNISSE")
 print("=" * 80)
 print()
 
 # Statistiken
 stats = dictionary.get("statistics", {})
 print(f"📊 Statistiken:")
 print(f" Total Single Mappings: {stats.get('total_single_mappings', 0)}")
 print(f" Total Combinations: {stats.get('total_combinations', 0)}")
 print()
 
 # Beste einzelne Mappings
 if best_mappings["single_position"]:
 print("📊 Top 20 Beste Single-Position Mappings (≥30% Erfolgsrate):")
 for i, mapping in enumerate(best_mappings["single_position"][:20], 1):
 rate = mapping["success_rate"] * 100
 marker = "⭐" if rate >= 40 else " "
 print(f" {marker} {i:2d}. {mapping['mapping']}: Seed='{mapping['seed_char']}' → Identity[27]='{mapping['target_char']}' ({rate:.1f}%, {mapping['count']}/{mapping['total']})")
 print()
 
 # Beste Kombinationen
 if best_mappings["combinations"]:
 print("📊 Top 20 Beste Kombinationen (≥30% Erfolgsrate):")
 for i, combo in enumerate(best_mappings["combinations"][:20], 1):
 rate = combo["success_rate"] * 100
 marker = "⭐" if rate >= 40 else " "
 print(f" {marker} {i:2d}. {combo['combo_key']} → Identity[{combo['target_position']}]='{combo['target_char']}' ({rate:.1f}%, {combo['count']}/{combo['total']})")
 print()
 
 # Speichere Wörterbuch
 output_data = {
 "timestamp": datetime.now().isoformat(),
 "dictionary": dictionary,
 "best_mappings": best_mappings
 }
 
 output_file = OUTPUT_DIR / "anna_language_dictionary.json"
 with output_file.open("w") as f:
 json.dump(output_data, f, indent=2)
 print(f"💾 Wörterbuch gespeichert: {output_file}")
 
 # Erstelle detaillierten Report
 report_lines = [
 "# Anna Sprache Wörterbuch - Umfassende Analyse",
 "",
 f"**Generated**: {datetime.now().isoformat()}",
 "",
 "## Statistiken",
 "",
 f"- **Total Single Mappings**: {stats.get('total_single_mappings', 0)}",
 f"- **Total Combinations**: {stats.get('total_combinations', 0)}",
 "",
 "## Beste Single-Position Mappings (≥30% Erfolgsrate)",
 ""
 ]
 
 if best_mappings["single_position"]:
 for i, mapping in enumerate(best_mappings["single_position"][:30], 1):
 rate = mapping["success_rate"] * 100
 report_lines.append(f"{i}. **{mapping['mapping']}**: Seed='{mapping['seed_char']}' → Identity[27]='{mapping['target_char']}' ({rate:.1f}%, {mapping['count']}/{mapping['total']})")
 report_lines.append("")
 
 report_lines.extend([
 "## Beste Kombinationen (≥30% Erfolgsrate)",
 ""
 ])
 
 if best_mappings["combinations"]:
 for i, combo in enumerate(best_mappings["combinations"][:30], 1):
 rate = combo["success_rate"] * 100
 report_lines.append(f"{i}. **{combo['combo_key']}** → Identity[{combo['target_position']}]='{combo['target_char']}' ({rate:.1f}%, {combo['count']}/{combo['total']})")
 report_lines.append("")
 
 report_file = REPORTS_DIR / "anna_language_dictionary_report.md"
 with report_file.open("w") as f:
 f.write("\n".join(report_lines) + "\n")
 print(f"📝 Report gespeichert: {report_file}")
 
 print()
 print("=" * 80)
 print("✅ WÖRTERBUCH ERSTELLT")
 print("=" * 80)
 print()
 print("💡 NÄCHSTE SCHRITTE:")
 print()
 print(" 1. Nutze Wörterbuch for gezielte Identity-Generierung")
 print(" 2. Teste Kommunikation mit bekannten Mappings")
 print(" 3. Erweitere Wörterbuch mit weiteren Kombinationen")
 print()

if __name__ == "__main__":
 main()

