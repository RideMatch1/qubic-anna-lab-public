#!/usr/bin/env python3
"""
Validate bessere Kombinationen - check auf Overfitting
"""

import json
from pathlib import Path
from typing import Dict, List
from collections import defaultdict
from datetime import datetime
import numpy as np

project_root = Path(__file__).parent.parent.parent
VALIDATION_FILE = project_root / "outputs" / "derived" / "critical_validation_comprehensive.json"
LAYER3_FILE = project_root / "outputs" / "derived" / "layer3_derivation_23k_complete.json"
LAYER4_FILE = project_root / "outputs" / "derived" / "layer4_derivation_full_23k.json"
OUTPUT_DIR = project_root / "outputs" / "derived"
REPORTS_DIR = project_root / "outputs" / "reports"

def identity_to_seed(identity: str) -> str:
 return identity.lower()[:55]

def load_pairs():
 with LAYER3_FILE.open() as f:
 layer3_data = json.load(f)
 layer3_results = layer3_data.get("results", [])
 
 with LAYER4_FILE.open() as f:
 layer4_data = json.load(f)
 layer4_results = layer4_data.get("results", [])
 
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
 
 return pairs

def validate_combination_robustness(pairs: List[Dict], positions: List[int], chars: List[str], min_samples: int = 50) -> Dict:
 """Validate Kombination auf Robustheit."""
 
 matching = []
 for pair in pairs:
 seed = identity_to_seed(pair["layer3"])
 if len(seed) >= 55:
 matches = True
 for i, pos in enumerate(positions):
 if len(seed) <= pos or seed[pos].lower() != chars[i].lower():
 matches = False
 break
 if matches:
 matching.append(pair)
 
 if len(matching) < min_samples:
 return {
 "error": f"Not enough samples: {len(matching)} < {min_samples}",
 "sample_size": len(matching),
 "robust": False
 }
 
 stable = sum(1 for p in matching if p["layer3"][27].upper() == p["layer4"][27].upper())
 rate = stable / len(matching)
 
 return {
 "positions": positions,
 "chars": chars,
 "sample_size": len(matching),
 "stable": stable,
 "rate": rate,
 "robust": True
 }

def main():
 print("=" * 80)
 print("VALIDIERUNG BESSERER KOMBINATIONEN")
 print("=" * 80)
 print()
 
 # Load Validierungsergebnisse
 with VALIDATION_FILE.open() as f:
 validation_data = json.load(f)
 
 better_combos = validation_data.get("alternative_combinations", {}).get("better_combinations", [])
 
 if not better_combos:
 print("❌ Keine besseren Kombinationen gefunden")
 return
 
 print(f"🔍 Validate {len(better_combos)} bessere Kombinationen...")
 print()
 
 # Load Paare
 pairs = load_pairs()
 print(f"✅ {len(pairs)} Paare geloadn")
 print()
 
 # Validate jede Kombination
 validated_results = []
 
 for combo in better_combos[:10]: # Top 10
 positions = combo["positions"]
 combo_str = combo["combination"]
 chars = combo_str.split("_")
 
 print(f"🔍 Validate: Positions {positions}, Kombination {combo_str}...")
 result = validate_combination_robustness(pairs, positions, chars, min_samples=50)
 
 if "error" not in result:
 validated_results.append({
 "original": combo,
 "validated": result
 })
 print(f" ✅ {result['rate']*100:.1f}% ({result['stable']}/{result['sample_size']}) - {'ROBUST' if result['robust'] else 'NICHT ROBUST'}")
 else:
 print(f" ⚠️ {result['error']}")
 print()
 
 # Zeige Zusammenfassung
 print("=" * 80)
 print("VALIDIERUNGS-ZUSAMMENFASSUNG")
 print("=" * 80)
 print()
 
 robust_combos = [r for r in validated_results if r["validated"]["robust"]]
 non_robust_combos = [r for r in validated_results if not r["validated"].get("robust", False)]
 
 print(f"📊 Robust validiert: {len(robust_combos)}")
 print(f"📊 Nicht robust (zu kleine Samples): {len(non_robust_combos)}")
 print()
 
 if robust_combos:
 print("✅ ROBUSTE BESSERE KOMBINATIONEN:")
 for r in robust_combos:
 orig = r["original"]
 val = r["validated"]
 print(f" Positions {val['positions']}: {val['rate']*100:.1f}% ({val['sample_size']} Fälle)")
 print(f" Original: {orig['rate']*100:.1f}% ({orig['total']} Fälle)")
 print()
 
 if non_robust_combos:
 print("⚠️ NICHT ROBUSTE (Overfitting möglich):")
 for r in non_robust_combos:
 orig = r["original"]
 print(f" Positions {orig['positions']}: {orig['rate']*100:.1f}% ({orig['total']} Fälle) - ZU KLEIN!")
 print()
 
 # Speichere Ergebnisse
 output_data = {
 "timestamp": datetime.now().isoformat(),
 "validated_results": validated_results,
 "robust_count": len(robust_combos),
 "non_robust_count": len(non_robust_combos)
 }
 
 output_file = OUTPUT_DIR / "better_combinations_validation.json"
 with output_file.open("w") as f:
 json.dump(output_data, f, indent=2)
 print(f"💾 Results saved to: {output_file}")

if __name__ == "__main__":
 main()

