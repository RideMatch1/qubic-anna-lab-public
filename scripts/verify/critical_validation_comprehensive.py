#!/usr/bin/env python3
"""
Kritische umfassende Validierung aller Erkenntnisse
- Alternative Hypothesen testen
- Statistische Robustheit checkn
- Potenzielle Fehlerquellen identifizieren
- Cross-Validation
"""

import json
import sys
from pathlib import Path
from typing import Dict, List, Tuple
from collections import Counter, defaultdict
from datetime import datetime
import random
import numpy as np
from scipy.stats import chi2_contingency, fisher_exact
from scipy.stats import binomtest

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

LAYER3_FILE = project_root / "outputs" / "derived" / "layer3_derivation_23k_complete.json"
LAYER4_FILE = project_root / "outputs" / "derived" / "layer4_derivation_full_23k.json"
OUTPUT_DIR = project_root / "outputs" / "derived"
REPORTS_DIR = project_root / "outputs" / "reports"

def identity_to_seed(identity: str) -> str:
 """Konvertiere Identity zu Seed."""
 return identity.lower()[:55]

def load_pairs() -> List[Dict]:
 """Load Layer-3 → Layer-4 Paare."""
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

def test_random_hypothesis(pairs: List[Dict], n_iterations: int = 1000) -> Dict:
 """Teste ob Ergebnisse durch Zufall erklärbar sind."""
 
 # Berechne tatsächliche Rate for Seed[27]='a' + Seed[54]='o'
 actual_matching = []
 for pair in pairs:
 seed = identity_to_seed(pair["layer3"])
 if len(seed) >= 55 and seed[27].lower() == 'a' and seed[54].lower() == 'o':
 stable = pair["layer3"][27].upper() == pair["layer4"][27].upper()
 actual_matching.append(stable)
 
 if not actual_matching:
 return {"error": "No matching pairs"}
 
 actual_rate = sum(actual_matching) / len(actual_matching)
 actual_stable = sum(actual_matching)
 actual_total = len(actual_matching)
 
 # Simuliere zufällige Verteilung
 baseline_rate = 0.257 # Durchschnittliche Stabilität Position 27
 random_rates = []
 
 for _ in range(n_iterations):
 # Zufällige Stichprobe gleicher Größe
 random_sample = np.random.binomial(1, baseline_rate, actual_total)
 random_rate = np.mean(random_sample)
 random_rates.append(random_rate)
 
 # Berechne p-Wert (wie wahrscheinlich ist es, dass actual_rate durch Zufall entsteht?)
 p_value = sum(1 for r in random_rates if r >= actual_rate) / n_iterations
 
 # Binomial Test
 binom_result = binomtest(actual_stable, actual_total, baseline_rate, alternative='greater')
 binom_p = binom_result.pvalue
 
 return {
 "actual_rate": actual_rate,
 "actual_stable": actual_stable,
 "actual_total": actual_total,
 "baseline_rate": baseline_rate,
 "random_simulation_mean": np.mean(random_rates),
 "random_simulation_std": np.std(random_rates),
 "p_value_simulation": p_value,
 "p_value_binomial": binom_p,
 "significant": p_value < 0.05 and binom_p < 0.05,
 "effect_size": actual_rate - baseline_rate
 }

def test_alternative_combinations(pairs: List[Dict]) -> Dict:
 """Teste alternative Kombinationen - könnte es andere bessere geben?"""
 
 # Teste alle möglichen 2-Positionen Kombinationen
 candidate_positions = [0, 4, 13, 27, 30, 54]
 all_combinations = []
 
 for pos1 in candidate_positions:
 for pos2 in candidate_positions:
 if pos1 >= pos2:
 continue
 
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
 if total >= 20: # Mindestens 20 Fälle
 rate = stats["stable"] / total
 all_combinations.append({
 "positions": [pos1, pos2],
 "combination": combo,
 "rate": rate,
 "stable": stats["stable"],
 "total": total
 })
 
 # Sortiere nach Rate
 all_combinations.sort(key=lambda x: x["rate"], reverse=True)
 
 # Check ob Seed[27]='a' + Seed[54]='o' wirklich beste ist
 best_combo = all_combinations[0] if all_combinations else None
 our_combo = next((c for c in all_combinations if c["positions"] == [27, 54] and c["combination"] == "a_o"), None)
 
 return {
 "all_combinations": all_combinations[:20], # Top 20
 "best_combination": best_combo,
 "our_combination": our_combo,
 "is_best": our_combo == best_combo if our_combo and best_combo else False,
 "better_combinations": [c for c in all_combinations[:10] if c["rate"] > (our_combo["rate"] if our_combo else 0) and c != our_combo]
 }

def cross_validate_combination(pairs: List[Dict], seed_positions: List[int], seed_chars: List[str], k: int = 10) -> Dict:
 """10-fold Cross-Validation for Kombination."""
 
 # Shuffle pairs
 shuffled_pairs = pairs.copy()
 random.seed(42)
 random.shuffle(shuffled_pairs)
 
 fold_size = len(shuffled_pairs) // k
 fold_results = []
 
 for i in range(k):
 start_idx = i * fold_size
 end_idx = (i + 1) * fold_size if i < k - 1 else len(shuffled_pairs)
 fold_pairs = shuffled_pairs[start_idx:end_idx]
 
 # Finde matching pairs
 matching = []
 for pair in fold_pairs:
 seed = identity_to_seed(pair["layer3"])
 if len(seed) >= 55:
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
 fold_results.append({
 "fold": i + 1,
 "rate": rate,
 "stable": stable,
 "total": len(matching)
 })
 
 if fold_results:
 rates = [r["rate"] for r in fold_results]
 mean_rate = np.mean(rates)
 std_rate = np.std(rates)
 min_rate = np.min(rates)
 max_rate = np.max(rates)
 
 return {
 "mean_rate": mean_rate,
 "std_rate": std_rate,
 "min_rate": min_rate,
 "max_rate": max_rate,
 "fold_results": fold_results,
 "k": k,
 "robust": std_rate < 0.10 # Standardabweichung < 10%
 }
 
 return {"error": "No matching pairs in folds"}

def test_data_quality(pairs: List[Dict]) -> Dict:
 """Check Datenqualität - gibt es systematische Fehler?"""
 
 issues = {
 "invalid_identities": 0,
 "invalid_seeds": 0,
 "missing_matches": 0,
 "length_mismatches": 0,
 "character_issues": 0
 }
 
 seed_lengths = Counter()
 identity_lengths = Counter()
 
 for pair in pairs:
 l3_id = pair["layer3"]
 l4_id = pair["layer4"]
 seed = identity_to_seed(l3_id)
 
 # Check Längen
 if len(l3_id) != 60:
 issues["length_mismatches"] += 1
 if len(l4_id) != 60:
 issues["length_mismatches"] += 1
 if len(seed) != 55:
 issues["invalid_seeds"] += 1
 
 seed_lengths[len(seed)] += 1
 identity_lengths[len(l3_id)] += 1
 
 # Check Characters
 if not l3_id.isupper() or not all(c.isalnum() for c in l3_id):
 issues["character_issues"] += 1
 
 return {
 "issues": issues,
 "seed_lengths": dict(seed_lengths),
 "identity_lengths": dict(identity_lengths),
 "total_pairs": len(pairs),
 "data_quality_score": 1.0 - (sum(issues.values()) / (len(pairs) * 5)) if pairs else 0
 }

def test_confounding_variables(pairs: List[Dict]) -> Dict:
 """Check auf Confounding Variables - gibt es andere Faktoren?"""
 
 # Check ob andere Seed-Positionen auch korrelieren
 correlations = {}
 
 for seed_pos in [0, 4, 13, 30]:
 char_rates = defaultdict(lambda: {"stable": 0, "changing": 0})
 
 for pair in pairs:
 seed = identity_to_seed(pair["layer3"])
 if len(seed) > seed_pos:
 char = seed[seed_pos].lower()
 stable = pair["layer3"][27].upper() == pair["layer4"][27].upper()
 
 if stable:
 char_rates[char]["stable"] += 1
 else:
 char_rates[char]["changing"] += 1
 
 # Berechne Varianz der Raten
 rates = []
 for char, stats in char_rates.items():
 total = stats["stable"] + stats["changing"]
 if total >= 10:
 rate = stats["stable"] / total
 rates.append(rate)
 
 if rates:
 variance = np.var(rates)
 correlations[seed_pos] = {
 "variance": variance,
 "mean_rate": np.mean(rates),
 "max_rate": np.max(rates),
 "min_rate": np.min(rates)
 }
 
 return {
 "correlations": correlations,
 "strongest_correlation": max(correlations.items(), key=lambda x: x[1]["variance"]) if correlations else None
 }

def main():
 """Hauptfunktion."""
 print("=" * 80)
 print("KRITISCHE UMFASSENDE VALIDIERUNG")
 print("=" * 80)
 print()
 
 # Load Daten
 print("📂 Load Daten...")
 pairs = load_pairs()
 print(f"✅ {len(pairs)} Paare geloadn")
 print()
 
 # 1. Teste Random-Hypothese
 print("🔍 Teste Random-Hypothese (könnte 37.3% Zufall sein?)...")
 random_test = test_random_hypothesis(pairs, n_iterations=1000)
 if "error" not in random_test:
 print(f" ✅ Actual Rate: {random_test['actual_rate']*100:.1f}%")
 print(f" ✅ Baseline Rate: {random_test['baseline_rate']*100:.1f}%")
 print(f" ✅ p-Wert (Simulation): {random_test['p_value_simulation']:.6f}")
 print(f" ✅ p-Wert (Binomial): {random_test['p_value_binomial']:.6f}")
 print(f" ✅ Signifikant: {'JA' if random_test['significant'] else 'NEIN'}")
 print(f" ✅ Effect Size: {random_test['effect_size']*100:.1f}%")
 print()
 
 # 2. Teste alternative Kombinationen
 print("🔍 Teste alternative Kombinationen...")
 alt_combinations = test_alternative_combinations(pairs)
 if alt_combinations.get("best_combination"):
 best = alt_combinations["best_combination"]
 print(f" ✅ Beste Kombination: Positions {best['positions']}, Rate: {best['rate']*100:.1f}%")
 if alt_combinations.get("our_combination"):
 our = alt_combinations["our_combination"]
 print(f" ✅ Unsere Kombination: Positions {our['positions']}, Rate: {our['rate']*100:.1f}%")
 print(f" ✅ Ist beste: {'JA' if alt_combinations['is_best'] else 'NEIN'}")
 if alt_combinations.get("better_combinations"):
 print(f" ⚠️ {len(alt_combinations['better_combinations'])} bessere Kombinationen gefunden!")
 print()
 
 # 3. Cross-Validation
 print("🔍 10-fold Cross-Validation...")
 cv_result = cross_validate_combination(pairs, [27, 54], ['a', 'o'], k=10)
 if "error" not in cv_result:
 print(f" ✅ Mean Rate: {cv_result['mean_rate']*100:.1f}% ± {cv_result['std_rate']*100:.1f}%")
 print(f" ✅ Min: {cv_result['min_rate']*100:.1f}%, Max: {cv_result['max_rate']*100:.1f}%")
 print(f" ✅ Robust: {'JA' if cv_result['robust'] else 'NEIN'}")
 print()
 
 # 4. Datenqualität
 print("🔍 Check Datenqualität...")
 data_quality = test_data_quality(pairs)
 print(f" ✅ Data Quality Score: {data_quality['data_quality_score']*100:.1f}%")
 print(f" ✅ Issues: {data_quality['issues']}")
 print()
 
 # 5. Confounding Variables
 print("🔍 Check Confounding Variables...")
 confounding = test_confounding_variables(pairs)
 if confounding.get("strongest_correlation"):
 pos, stats = confounding["strongest_correlation"]
 print(f" ✅ Stärkste Korrelation: Position {pos} (Variance: {stats['variance']:.6f})")
 print()
 
 # Konvertiere numpy types zu Python types for JSON
 def convert_to_python(obj):
 if isinstance(obj, np.bool_):
 return bool(obj)
 elif isinstance(obj, np.integer):
 return int(obj)
 elif isinstance(obj, np.floating):
 return float(obj)
 elif isinstance(obj, dict):
 return {k: convert_to_python(v) for k, v in obj.items()}
 elif isinstance(obj, list):
 return [convert_to_python(item) for item in obj]
 return obj
 
 # Speichere Ergebnisse
 output_data = {
 "timestamp": datetime.now().isoformat(),
 "random_hypothesis_test": convert_to_python(random_test),
 "alternative_combinations": convert_to_python(alt_combinations),
 "cross_validation": convert_to_python(cv_result),
 "data_quality": convert_to_python(data_quality),
 "confounding_variables": convert_to_python(confounding)
 }
 
 output_file = OUTPUT_DIR / "critical_validation_comprehensive.json"
 with output_file.open("w") as f:
 json.dump(output_data, f, indent=2)
 print(f"💾 Results saved to: {output_file}")
 
 # Erstelle kritischen Report
 report_lines = [
 "# Kritische Umfassende Validierung",
 "",
 f"**Generated**: {datetime.now().isoformat()}",
 "",
 "## 1. Random-Hypothese Test",
 ""
 ]
 
 if "error" not in random_test:
 report_lines.extend([
 f"- **Actual Rate**: {random_test['actual_rate']*100:.1f}%",
 f"- **Baseline Rate**: {random_test['baseline_rate']*100:.1f}%",
 f"- **p-Wert (Simulation)**: {random_test['p_value_simulation']:.6f}",
 f"- **p-Wert (Binomial)**: {random_test['p_value_binomial']:.6f}",
 f"- **Signifikant**: {'✅ JA' if random_test['significant'] else '❌ NEIN'}",
 f"- **Effect Size**: {random_test['effect_size']*100:.1f}%",
 ""
 ])
 
 report_lines.extend([
 "## 2. Alternative Kombinationen",
 ""
 ])
 
 if alt_combinations.get("best_combination"):
 best = alt_combinations["best_combination"]
 report_lines.append(f"- **Beste Kombination**: Positions {best['positions']}, Rate: {best['rate']*100:.1f}%")
 if alt_combinations.get("our_combination"):
 our = alt_combinations["our_combination"]
 report_lines.append(f"- **Unsere Kombination**: Positions {our['positions']}, Rate: {our['rate']*100:.1f}%")
 report_lines.append(f"- **Ist beste**: {'✅ JA' if alt_combinations['is_best'] else '❌ NEIN'}")
 report_lines.append("")
 
 report_lines.extend([
 "## 3. Cross-Validation",
 ""
 ])
 
 if "error" not in cv_result:
 report_lines.extend([
 f"- **Mean Rate**: {cv_result['mean_rate']*100:.1f}% ± {cv_result['std_rate']*100:.1f}%",
 f"- **Min**: {cv_result['min_rate']*100:.1f}%, **Max**: {cv_result['max_rate']*100:.1f}%",
 f"- **Robust**: {'✅ JA' if cv_result['robust'] else '❌ NEIN'}",
 ""
 ])
 
 report_lines.extend([
 "## 4. Datenqualität",
 "",
 f"- **Data Quality Score**: {data_quality['data_quality_score']*100:.1f}%",
 f"- **Issues**: {data_quality['issues']}",
 ""
 ])
 
 report_file = REPORTS_DIR / "critical_validation_comprehensive_report.md"
 with report_file.open("w") as f:
 f.write("\n".join(report_lines) + "\n")
 print(f"📝 Report gespeichert: {report_file}")
 
 # Zusammenfassung
 print("=" * 80)
 print("VALIDIERUNGS-ZUSAMMENFASSUNG")
 print("=" * 80)
 print()
 
 if "error" not in random_test:
 if random_test['significant']:
 print("✅ Random-Hypothese: ABGELEHNT (Ergebnis ist signifikant)")
 else:
 print("⚠️ Random-Hypothese: NICHT ABGELEHNT (könnte Zufall sein)")
 print()
 
 if alt_combinations.get("is_best"):
 print("✅ Unsere Kombination ist BESTE gefundene")
 elif alt_combinations.get("better_combinations"):
 print(f"⚠️ {len(alt_combinations['better_combinations'])} bessere Kombinationen gefunden!")
 print()
 
 if "error" not in cv_result:
 if cv_result['robust']:
 print("✅ Cross-Validation: ROBUST (niedrige Varianz)")
 else:
 print("⚠️ Cross-Validation: NICHT ROBUST (hohe Varianz)")
 print()

if __name__ == "__main__":
 main()

