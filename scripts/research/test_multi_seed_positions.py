#!/usr/bin/env python3
"""
Teste Multi-Position Models (3+ Seed-Positionen)
- Finde beste Kombinationen for höchste Stabilität
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

def test_multi_seed_positions(pairs: List[Dict], seed_positions: List[int], min_samples: int = 10) -> Dict:
 """Teste Kombinationen von mehreren Seed-Positionen."""
 
 print(f"🔍 Teste Kombinationen von {len(seed_positions)} Seed-Positionen...")
 
 # Erstelle alle möglichen Kombinationen
 # Für Performance: Teste nur Top Characters pro Position
 position_top_chars = {}
 
 # Finde Top Characters for jede Position
 for seed_pos in seed_positions:
 char_counts = Counter()
 for pair in pairs:
 seed = identity_to_seed(pair["layer3"])
 if len(seed) > seed_pos:
 char_counts[seed[seed_pos].lower()] += 1
 # Top 5 Characters pro Position
 position_top_chars[seed_pos] = [char for char, _ in char_counts.most_common(5)]
 
 # Teste Kombinationen
 combination_groups = defaultdict(lambda: {"stable": 0, "changing": 0})
 
 for pair in pairs:
 l3_id = pair["layer3"]
 l4_id = pair["layer4"]
 seed = identity_to_seed(l3_id)
 
 if len(seed) >= 55 and len(l3_id) > 27 and len(l4_id) > 27:
 # Erstelle Kombinations-Key
 combo_chars = []
 valid = True
 for seed_pos in seed_positions:
 if len(seed) > seed_pos:
 char = seed[seed_pos].lower()
 # Nur testen wenn Character in Top 5
 if char in position_top_chars[seed_pos]:
 combo_chars.append(f"{seed_pos}:{char}")
 else:
 valid = False
 break
 else:
 valid = False
 break
 
 if valid:
 combination_key = "_".join(combo_chars)
 stable = l3_id[27].upper() == l4_id[27].upper()
 
 if stable:
 combination_groups[combination_key]["stable"] += 1
 else:
 combination_groups[combination_key]["changing"] += 1
 
 # Berechne Raten
 combination_rates = {}
 for combo, stats in combination_groups.items():
 total = stats["stable"] + stats["changing"]
 if total >= min_samples:
 rate = stats["stable"] / total
 combination_rates[combo] = {
 "rate": rate,
 "stable": stats["stable"],
 "changing": stats["changing"],
 "total": total
 }
 
 # Sortiere nach Rate
 sorted_combinations = sorted(
 combination_rates.items(),
 key=lambda x: x[1]["rate"],
 reverse=True
 )
 
 return {
 "combinations": dict(sorted_combinations[:20]), # Top 20
 "total_combinations": len(combination_rates),
 "seed_positions": seed_positions
 }

def main():
 """Hauptfunktion."""
 print("=" * 80)
 print("MULTI-POSITION MODELS TEST")
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
 
 # Teste verschiedene Kombinationen
 results = {}
 
 # 2-Positionen (bereits bekannt: 27 + 54 = 37.3%)
 print("🔍 Teste 2-Positionen Kombinationen...")
 result_2pos = test_multi_seed_positions(pairs, [27, 54], min_samples=10)
 results["2_positions"] = result_2pos
 print("✅ 2-Positionen getestet")
 print()
 
 # 3-Positionen
 print("🔍 Teste 3-Positionen Kombinationen (27, 54, 13)...")
 result_3pos = test_multi_seed_positions(pairs, [27, 54, 13], min_samples=5)
 results["3_positions"] = result_3pos
 print("✅ 3-Positionen getestet")
 print()
 
 # Zeige Ergebnisse
 print("=" * 80)
 print("ERGEBNISSE")
 print("=" * 80)
 print()
 
 # 2-Positionen
 combo_2pos = results.get("2_positions", {}).get("combinations", {})
 if combo_2pos:
 print("📊 Top 10 - 2-Positionen Kombinationen:")
 for i, (combo, stats) in enumerate(list(combo_2pos.items())[:10], 1):
 rate = stats["rate"] * 100
 marker = "⭐" if rate > 35 else " "
 print(f" {marker} {i:2d}. {combo}: {rate:.1f}% ({stats['stable']}/{stats['total']})")
 print()
 
 # 3-Positionen
 combo_3pos = results.get("3_positions", {}).get("combinations", {})
 if combo_3pos:
 print("📊 Top 10 - 3-Positionen Kombinationen:")
 for i, (combo, stats) in enumerate(list(combo_3pos.items())[:10], 1):
 rate = stats["rate"] * 100
 marker = "⭐" if rate > 40 else " "
 print(f" {marker} {i:2d}. {combo}: {rate:.1f}% ({stats['stable']}/{stats['total']})")
 print()
 
 # Speichere Ergebnisse
 output_data = {
 "timestamp": datetime.now().isoformat(),
 "results": results
 }
 
 output_file = OUTPUT_DIR / "multi_seed_positions_analysis.json"
 with output_file.open("w") as f:
 json.dump(output_data, f, indent=2)
 print(f"💾 Results saved to: {output_file}")
 
 # Erstelle Report
 report_lines = [
 "# Multi-Position Models Test",
 "",
 f"**Generated**: {datetime.now().isoformat()}",
 "",
 "## 2-Positionen Kombinationen",
 ""
 ]
 
 if combo_2pos:
 for i, (combo, stats) in enumerate(list(combo_2pos.items())[:10], 1):
 rate = stats["rate"] * 100
 report_lines.append(f"{i}. **{combo}**: {rate:.1f}% ({stats['stable']}/{stats['total']})")
 report_lines.append("")
 
 if combo_3pos:
 report_lines.extend([
 "## 3-Positionen Kombinationen",
 ""
 ])
 for i, (combo, stats) in enumerate(list(combo_3pos.items())[:10], 1):
 rate = stats["rate"] * 100
 report_lines.append(f"{i}. **{combo}**: {rate:.1f}% ({stats['stable']}/{stats['total']})")
 report_lines.append("")
 
 report_file = REPORTS_DIR / "multi_seed_positions_analysis_report.md"
 with report_file.open("w") as f:
 f.write("\n".join(report_lines) + "\n")
 print(f"📝 Report gespeichert: {report_file}")

if __name__ == "__main__":
 main()

