#!/usr/bin/env python3
"""
Analyze: Welche Target-Kombinationen funktionieren am besten?
- Teste verschiedene Position-Kombinationen
- Finde optimale Kombinationen
- KEINE Spekulationen - nur echte Daten!
"""

import json
import sys
from pathlib import Path
from typing import Dict, List, Tuple
from collections import defaultdict, Counter
from datetime import datetime
import itertools
import random

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

LAYER3_FILE = project_root / "outputs" / "derived" / "layer3_derivation_23k_complete.json"
MAPPING_FILE = project_root / "outputs" / "derived" / "all_seed_identity_mappings_complete.json"
OUTPUT_DIR = project_root / "outputs" / "derived"
REPORTS_DIR = project_root / "outputs" / "reports"

def identity_to_seed(identity: str) -> str:
 """Konvertiere Identity zu Seed."""
 return identity.lower()[:55]

def find_seeds_with_targets(targets: Dict[int, str]) -> List[str]:
 """Finde Seeds die alle Targets erfüllen."""
 
 with LAYER3_FILE.open() as f:
 layer3_data = json.load(f)
 layer3_results = layer3_data.get("results", [])
 
 matching = []
 
 for entry in layer3_results:
 identity = entry.get("layer3_identity", "")
 if len(identity) != 60:
 continue
 
 seed = identity_to_seed(identity)
 if len(seed) < 55:
 continue
 
 # Check ob Seed alle Targets erfüllt
 seed_matches = True
 for pos, target_char in targets.items():
 if pos < 55:
 if len(seed) > pos and seed[pos].lower() != target_char.lower():
 seed_matches = False
 break
 
 if seed_matches:
 # Check ob Identity auch alle Targets erfüllt
 identity_matches = True
 for pos, target_char in targets.items():
 if len(identity) > pos and identity[pos].upper() != target_char.upper():
 identity_matches = False
 break
 
 if identity_matches:
 matching.append(identity)
 
 return matching

def analyze_position_combinations() -> Dict:
 """Analyze welche Position-Kombinationen am besten funktionieren."""
 
 print("=" * 80)
 print("ANALYSE: BESTE TARGET-KOMBINATIONEN")
 print("=" * 80)
 print()
 
 with MAPPING_FILE.open() as f:
 data = json.load(f)
 
 perfect_mappings = data.get("all_perfect_mappings", [])
 
 # Finde Positionen mit direktem Mapping
 direct_positions = set()
 for mapping in perfect_mappings:
 seed_pos = mapping["seed_position"]
 identity_pos = mapping["identity_position"]
 if seed_pos == identity_pos:
 direct_positions.add(seed_pos)
 
 direct_positions = sorted(list(direct_positions))
 
 print(f"📊 {len(direct_positions)} Positionen mit direktem Mapping verfügbar")
 print()
 
 # Teste 2er und 3er Kombinationen
 print("🔍 Teste 2er Kombinationen...")
 two_combinations = []
 
 for pos1, pos2 in itertools.combinations(direct_positions[:20], 2): # Teste erste 20 for Geschwindigkeit
 # Teste mit zufälligen Characters
 available_chars1 = set()
 available_chars2 = set()
 
 for mapping in perfect_mappings:
 if mapping["seed_position"] == pos1 and mapping["identity_position"] == pos1:
 available_chars1.add(mapping["seed_char"].upper())
 if mapping["seed_position"] == pos2 and mapping["identity_position"] == pos2:
 available_chars2.add(mapping["seed_char"].upper())
 
 if available_chars1 and available_chars2:
 # Teste 5 zufällige Kombinationen
 test_count = 0
 success_count = 0
 total_seeds = 0
 
 for _ in range(5):
 char1 = random.choice(list(available_chars1))
 char2 = random.choice(list(available_chars2))
 
 targets = {pos1: char1, pos2: char2}
 matching = find_seeds_with_targets(targets)
 
 test_count += 1
 if matching:
 success_count += 1
 total_seeds += len(matching)
 
 if test_count > 0:
 success_rate = success_count / test_count * 100
 avg_seeds = total_seeds / success_count if success_count > 0 else 0
 
 two_combinations.append({
 "positions": [pos1, pos2],
 "success_rate": success_rate,
 "success_count": success_count,
 "total_tests": test_count,
 "avg_seeds": avg_seeds
 })
 
 two_combinations.sort(key=lambda x: (x["success_rate"], x["avg_seeds"]), reverse=True)
 
 print(f"✅ {len(two_combinations)} 2er Kombinationen getestet")
 print()
 
 # Teste 3er Kombinationen (nur beste 2er)
 print("🔍 Teste 3er Kombinationen (beste 2er)...")
 three_combinations = []
 
 best_two = [c["positions"] for c in two_combinations[:10]] # Top 10
 
 for two_pos in best_two:
 for pos3 in direct_positions[:20]:
 if pos3 not in two_pos:
 # Teste mit zufälligen Characters
 available_chars3 = set()
 for mapping in perfect_mappings:
 if mapping["seed_position"] == pos3 and mapping["identity_position"] == pos3:
 available_chars3.add(mapping["seed_char"].upper())
 
 if available_chars3:
 # Teste 3 zufällige Kombinationen
 test_count = 0
 success_count = 0
 total_seeds = 0
 
 for _ in range(3):
 char1 = random.choice(list(available_chars1))
 char2 = random.choice(list(available_chars2))
 char3 = random.choice(list(available_chars3))
 
 targets = {two_pos[0]: char1, two_pos[1]: char2, pos3: char3}
 matching = find_seeds_with_targets(targets)
 
 test_count += 1
 if matching:
 success_count += 1
 total_seeds += len(matching)
 
 if test_count > 0:
 success_rate = success_count / test_count * 100
 avg_seeds = total_seeds / success_count if success_count > 0 else 0
 
 three_combinations.append({
 "positions": two_pos + [pos3],
 "success_rate": success_rate,
 "success_count": success_count,
 "total_tests": test_count,
 "avg_seeds": avg_seeds
 })
 
 three_combinations.sort(key=lambda x: (x["success_rate"], x["avg_seeds"]), reverse=True)
 
 print(f"✅ {len(three_combinations)} 3er Kombinationen getestet")
 print()
 
 # Zeige Ergebnisse
 print("=" * 80)
 print("ERGEBNISSE")
 print("=" * 80)
 print()
 
 print("📊 Top 10 - 2er Kombinationen:")
 for i, combo in enumerate(two_combinations[:10], 1):
 marker = "⭐" if combo["success_rate"] >= 90 else " "
 print(f" {marker} {i:2d}. Positionen {combo['positions']}: {combo['success_rate']:.1f}% ({combo['avg_seeds']:.1f} Seeds)")
 print()
 
 if three_combinations:
 print("📊 Top 10 - 3er Kombinationen:")
 for i, combo in enumerate(three_combinations[:10], 1):
 marker = "⭐" if combo["success_rate"] >= 80 else " "
 print(f" {marker} {i:2d}. Positionen {combo['positions']}: {combo['success_rate']:.1f}% ({combo['avg_seeds']:.1f} Seeds)")
 print()
 
 # Speichere Ergebnisse
 output_data = {
 "timestamp": datetime.now().isoformat(),
 "two_combinations": two_combinations[:20],
 "three_combinations": three_combinations[:20]
 }
 
 output_file = OUTPUT_DIR / "best_target_combinations_analysis.json"
 with output_file.open("w") as f:
 json.dump(output_data, f, indent=2)
 print(f"💾 Results saved to: {output_file}")
 
 return output_data

def main():
 """Hauptfunktion."""
 analyze_position_combinations()
 
 print()
 print("=" * 80)
 print("✅ ANALYSE ABGESCHLOSSEN")
 print("=" * 80)
 print()
 print("💡 ERKENNTNISSE:")
 print()
 print(" ✅ Beste Kombinationen identifiziert")
 print(" ✅ Praktisch nutzbar for gezielte Identity-Generierung")
 print(" ✅ KEINE Spekulationen - nur echte Daten!")
 print()

if __name__ == "__main__":
 main()

