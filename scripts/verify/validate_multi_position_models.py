#!/usr/bin/env python3
"""
Validate Multi-Position Models auf größerem Sample
- Check ob 3-Positionen Model robust ist
"""

import json
from pathlib import Path
from typing import Dict, List
from collections import Counter, defaultdict
from datetime import datetime
import random

project_root = Path(__file__).parent.parent.parent
LAYER3_FILE = project_root / "outputs" / "derived" / "layer3_derivation_23k_complete.json"
LAYER4_FILE = project_root / "outputs" / "derived" / "layer4_derivation_full_23k.json"
OUTPUT_DIR = project_root / "outputs" / "derived"
REPORTS_DIR = project_root / "outputs" / "reports"

def identity_to_seed(identity: str) -> str:
 """Konvertiere Identity zu Seed."""
 return identity.lower()[:55]

def validate_combination(pairs: List[Dict], seed_positions: List[int], seed_chars: List[str], min_samples: int = 50) -> Dict:
 """Validate spezifische Kombination auf größerem Sample."""
 
 matching_pairs = []
 
 for pair in pairs:
 l3_id = pair["layer3"]
 l4_id = pair["layer4"]
 seed = identity_to_seed(l3_id)
 
 if len(seed) >= 55 and len(l3_id) > 27 and len(l4_id) > 27:
 # Check ob Kombination passt
 matches = True
 for i, seed_pos in enumerate(seed_positions):
 if len(seed) <= seed_pos or seed[seed_pos].lower() != seed_chars[i].lower():
 matches = False
 break
 
 if matches:
 matching_pairs.append(pair)
 
 if len(matching_pairs) < min_samples:
 return {
 "error": f"Not enough samples: {len(matching_pairs)} < {min_samples}",
 "sample_size": len(matching_pairs)
 }
 
 # Berechne Stabilität
 stable_count = 0
 for pair in matching_pairs:
 l3_id = pair["layer3"]
 l4_id = pair["layer4"]
 if l3_id[27].upper() == l4_id[27].upper():
 stable_count += 1
 
 stability_rate = stable_count / len(matching_pairs)
 
 return {
 "seed_positions": seed_positions,
 "seed_chars": seed_chars,
 "sample_size": len(matching_pairs),
 "stable_count": stable_count,
 "stability_rate": stability_rate,
 "validated": True
 }

def cross_validate(pairs: List[Dict], seed_positions: List[int], seed_chars: List[str], k: int = 5) -> Dict:
 """Cross-Validation for Kombination."""
 
 # Shuffle pairs
 shuffled_pairs = pairs.copy()
 random.seed(42) # Reproduzierbar
 random.shuffle(shuffled_pairs)
 
 # Split in k folds
 fold_size = len(shuffled_pairs) // k
 fold_rates = []
 
 for i in range(k):
 start_idx = i * fold_size
 end_idx = (i + 1) * fold_size if i < k - 1 else len(shuffled_pairs)
 fold_pairs = shuffled_pairs[start_idx:end_idx]
 
 # Finde matching pairs in diesem Fold
 matching = []
 for pair in fold_pairs:
 l3_id = pair["layer3"]
 l4_id = pair["layer4"]
 seed = identity_to_seed(l3_id)
 
 if len(seed) >= 55 and len(l3_id) > 27 and len(l4_id) > 27:
 matches = True
 for j, seed_pos in enumerate(seed_positions):
 if len(seed) <= seed_pos or seed[seed_pos].lower() != seed_chars[j].lower():
 matches = False
 break
 
 if matches:
 matching.append(pair)
 
 if len(matching) > 0:
 stable = sum(1 for p in matching if p["layer3"][27].upper() == p["layer4"][27].upper())
 rate = stable / len(matching)
 fold_rates.append(rate)
 
 if fold_rates:
 mean_rate = sum(fold_rates) / len(fold_rates)
 variance = sum((r - mean_rate) ** 2 for r in fold_rates) / len(fold_rates) if len(fold_rates) > 1 else 0
 std_dev = variance ** 0.5
 
 return {
 "mean_rate": mean_rate,
 "std_dev": std_dev,
 "fold_rates": fold_rates,
 "k": k
 }
 
 return {"error": "No matching pairs in folds"}

def main():
 """Hauptfunktion."""
 print("=" * 80)
 print("MULTI-POSITION MODELS VALIDIERUNG")
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
 
 # Validate Top Kombinationen
 print("🔍 Validate Top Kombinationen...")
 
 # 2-Positionen: a + o (bekannt: 37.3%)
 print(" Teste: Seed[27]='a' + Seed[54]='o'...")
 result_2pos = validate_combination(pairs, [27, 54], ['a', 'o'], min_samples=50)
 if "error" not in result_2pos:
 rate = result_2pos["stability_rate"] * 100
 print(f" ✅ {rate:.1f}% ({result_2pos['stable_count']}/{result_2pos['sample_size']})")
 else:
 print(f" ⚠️ {result_2pos['error']}")
 print()
 
 # 3-Positionen: a + a + e (bekannt: 54.3% auf 35 Fällen)
 print(" Teste: Seed[27]='a' + Seed[54]='a' + Seed[13]='e'...")
 result_3pos = validate_combination(pairs, [27, 54, 13], ['a', 'a', 'e'], min_samples=50)
 if "error" not in result_3pos:
 rate = result_3pos["stability_rate"] * 100
 print(f" ✅ {rate:.1f}% ({result_3pos['stable_count']}/{result_3pos['sample_size']})")
 
 # Cross-Validation
 print(" 🔍 Cross-Validation (5-fold)...")
 cv_result = cross_validate(pairs, [27, 54, 13], ['a', 'a', 'e'], k=5)
 if "error" not in cv_result:
 mean_rate = cv_result["mean_rate"] * 100
 std_dev = cv_result["std_dev"] * 100
 print(f" Mean: {mean_rate:.1f}% ± {std_dev:.1f}%")
 print(f" Folds: {[f'{r*100:.1f}%' for r in cv_result['fold_rates']]}")
 else:
 print(f" ⚠️ {result_3pos['error']}")
 print()
 
 # Zeige Ergebnisse
 print("=" * 80)
 print("VALIDIERUNGSERGEBNISSE")
 print("=" * 80)
 print()
 
 if "error" not in result_2pos:
 rate_2pos = result_2pos["stability_rate"] * 100
 print(f"📊 2-Positionen (Seed[27]='a' + Seed[54]='o'):")
 print(f" Stabilität: {rate_2pos:.1f}% ({result_2pos['stable_count']}/{result_2pos['sample_size']})")
 print()
 
 if "error" not in result_3pos:
 rate_3pos = result_3pos["stability_rate"] * 100
 print(f"📊 3-Positionen (Seed[27]='a' + Seed[54]='a' + Seed[13]='e'):")
 print(f" Stabilität: {rate_3pos:.1f}% ({result_3pos['stable_count']}/{result_3pos['sample_size']})")
 
 if "error" not in cv_result:
 mean_rate = cv_result["mean_rate"] * 100
 std_dev = cv_result["std_dev"] * 100
 print(f" Cross-Validation: {mean_rate:.1f}% ± {std_dev:.1f}%")
 print()
 
 # Speichere Ergebnisse
 output_data = {
 "timestamp": datetime.now().isoformat(),
 "validation_2pos": result_2pos,
 "validation_3pos": result_3pos,
 "cross_validation_3pos": cv_result if "error" not in result_3pos else None
 }
 
 output_file = OUTPUT_DIR / "multi_position_models_validation.json"
 with output_file.open("w") as f:
 json.dump(output_data, f, indent=2)
 print(f"💾 Results saved to: {output_file}")
 
 # Erstelle Report
 report_lines = [
 "# Multi-Position Models Validierung",
 "",
 f"**Generated**: {datetime.now().isoformat()}",
 ""
 ]
 
 if "error" not in result_2pos:
 rate_2pos = result_2pos["stability_rate"] * 100
 report_lines.extend([
 "## 2-Positionen Validierung",
 "",
 f"- **Kombination**: Seed[27]='a' + Seed[54]='o'",
 f"- **Stabilität**: {rate_2pos:.1f}% ({result_2pos['stable_count']}/{result_2pos['sample_size']})",
 ""
 ])
 
 if "error" not in result_3pos:
 rate_3pos = result_3pos["stability_rate"] * 100
 report_lines.extend([
 "## 3-Positionen Validierung",
 "",
 f"- **Kombination**: Seed[27]='a' + Seed[54]='a' + Seed[13]='e'",
 f"- **Stabilität**: {rate_3pos:.1f}% ({result_3pos['stable_count']}/{result_3pos['sample_size']})",
 ""
 ])
 
 if "error" not in cv_result:
 mean_rate = cv_result["mean_rate"] * 100
 std_dev = cv_result["std_dev"] * 100
 report_lines.extend([
 "### Cross-Validation (5-fold)",
 "",
 f"- **Mean**: {mean_rate:.1f}%",
 f"- **Std Dev**: {std_dev:.1f}%",
 f"- **Folds**: {', '.join([f'{r*100:.1f}%' for r in cv_result['fold_rates']])}",
 ""
 ])
 
 report_file = REPORTS_DIR / "multi_position_models_validation_report.md"
 with report_file.open("w") as f:
 f.write("\n".join(report_lines) + "\n")
 print(f"📝 Report gespeichert: {report_file}")

if __name__ == "__main__":
 main()
