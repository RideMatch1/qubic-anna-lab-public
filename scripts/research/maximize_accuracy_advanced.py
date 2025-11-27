#!/usr/bin/env python3
"""
Maximale Accuracy - Erweiterte Optimierungen
- Teste 4-Position-Kombinationen
- Gewichtete Kombinationen mit optimierten Gewichten
- Alle möglichen Kombinationen der Top 10
- KEINE Halluzinationen - nur echte Daten!
"""

import json
import sys
import time
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from collections import Counter, defaultdict
from datetime import datetime
from itertools import combinations
import numpy as np

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# Paths
LAYER3_FILE = project_root / "outputs" / "derived" / "layer3_derivation_23k_complete.json"
OUTPUT_DIR = project_root / "outputs" / "derived"
STATUS_FILE = project_root / "outputs" / "derived" / "maximize_accuracy_advanced_status.txt"

def log_progress(message: str, status_file: Path = STATUS_FILE):
 """Schreibe Fortschritt in Status-Datei."""
 timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
 with status_file.open("a") as f:
 f.write(f"[{timestamp}] {message}\n")
 print(f"[{timestamp}] {message}")

def identity_to_seed(identity: str) -> str:
 """Konvertiere Identity zu Seed."""
 return identity.lower()[:55]

def build_seed_mapping(layer3_data: List[Dict], seed_pos: int, target_pos: int, min_samples: int = 10) -> Dict:
 """Baue Seed-Character-Mapping."""
 mapping = defaultdict(Counter)
 totals = Counter()
 
 for entry in layer3_data:
 l3_id = entry.get("layer3_identity", "")
 if not l3_id or len(l3_id) <= max(seed_pos, target_pos):
 continue
 
 seed = identity_to_seed(l3_id)
 if len(seed) <= seed_pos:
 continue
 
 seed_char = seed[seed_pos].lower()
 identity_char = l3_id[target_pos].upper()
 
 mapping[seed_char][identity_char] += 1
 totals[seed_char] += 1
 
 results = {}
 for seed_char, counter in mapping.items():
 total = totals[seed_char]
 if total >= min_samples:
 most_common = counter.most_common(1)[0]
 success_rate = most_common[1] / total
 
 results[seed_char] = {
 "predicted_char": most_common[0],
 "success_rate": success_rate,
 "count": most_common[1],
 "total": total
 }
 
 return results

def predict_with_seed(seed: str, seed_pos: int, mapping: Dict) -> Optional[str]:
 """Vorhersage basierend auf Seed."""
 if len(seed) <= seed_pos:
 return None
 
 seed_char = seed[seed_pos].lower()
 if seed_char not in mapping:
 return None
 
 return mapping[seed_char]["predicted_char"]

def test_combination(layer3_data: List[Dict], seed_positions: List[int], target_pos: int, sample_size: int = 2000) -> Dict:
 """Teste Kombination von Seed-Positionen."""
 
 # Baue Mappings
 mappings = {}
 for seed_pos in seed_positions:
 mapping = build_seed_mapping(layer3_data, seed_pos, target_pos)
 if mapping:
 mappings[seed_pos] = mapping
 
 if not mappings:
 return {"accuracy": 0, "total": 0}
 
 correct = 0
 total = 0
 
 for entry in layer3_data[:sample_size]:
 l3_id = entry.get("layer3_identity", "")
 if not l3_id or len(l3_id) <= target_pos:
 continue
 
 seed = identity_to_seed(l3_id)
 
 predictions = []
 for seed_pos in seed_positions:
 if seed_pos in mappings:
 pred = predict_with_seed(seed, seed_pos, mappings[seed_pos])
 if pred is not None:
 predictions.append(pred)
 
 if not predictions:
 continue
 
 # Mehrheitsentscheidung
 prediction_counter = Counter(predictions)
 predicted = prediction_counter.most_common(1)[0][0]
 
 actual = l3_id[target_pos].upper()
 if predicted == actual:
 correct += 1
 total += 1
 
 accuracy = (correct / total * 100) if total > 0 else 0
 
 return {
 "positions": seed_positions,
 "accuracy": accuracy,
 "correct": correct,
 "total": total
 }

def test_weighted_combination_optimized(layer3_data: List[Dict], seed_positions: List[int], target_pos: int, sample_size: int = 2000) -> Dict:
 """Teste optimierte gewichtete Kombination."""
 
 # Baue Mappings und berechne individuelle Accuracies
 mappings = {}
 individual_accuracies = {}
 
 for seed_pos in seed_positions:
 mapping = build_seed_mapping(layer3_data, seed_pos, target_pos)
 if mapping:
 mappings[seed_pos] = mapping
 
 # Berechne individuelle Accuracy
 correct = 0
 total = 0
 for entry in layer3_data[:sample_size]:
 l3_id = entry.get("layer3_identity", "")
 if not l3_id or len(l3_id) <= target_pos:
 continue
 
 seed = identity_to_seed(l3_id)
 pred = predict_with_seed(seed, seed_pos, mapping)
 if pred is not None:
 if pred == l3_id[target_pos].upper():
 correct += 1
 total += 1
 
 if total > 0:
 individual_accuracies[seed_pos] = (correct / total * 100)
 
 if not mappings:
 return {"accuracy": 0, "total": 0}
 
 # Normalisiere Gewichte basierend auf Accuracy
 total_acc = sum(individual_accuracies.values())
 weights = {pos: acc / total_acc if total_acc > 0 else 1.0/len(individual_accuracies) 
 for pos, acc in individual_accuracies.items()}
 
 # Teste gewichtete Kombination
 correct = 0
 total = 0
 
 for entry in layer3_data[:sample_size]:
 l3_id = entry.get("layer3_identity", "")
 if not l3_id or len(l3_id) <= target_pos:
 continue
 
 seed = identity_to_seed(l3_id)
 
 weighted_predictions = defaultdict(float)
 for seed_pos in seed_positions:
 if seed_pos in mappings:
 pred = predict_with_seed(seed, seed_pos, mappings[seed_pos])
 if pred is not None:
 weight = weights.get(seed_pos, 1.0)
 weighted_predictions[pred] += weight
 
 if not weighted_predictions:
 continue
 
 predicted = max(weighted_predictions.items(), key=lambda x: x[1])[0]
 
 actual = l3_id[target_pos].upper()
 if predicted == actual:
 correct += 1
 total += 1
 
 accuracy = (correct / total * 100) if total > 0 else 0
 
 return {
 "positions": seed_positions,
 "weights": weights,
 "individual_accuracies": individual_accuracies,
 "accuracy": accuracy,
 "correct": correct,
 "total": total
 }

def main():
 """Hauptfunktion."""
 
 STATUS_FILE.parent.mkdir(parents=True, exist_ok=True)
 with STATUS_FILE.open("w") as f:
 f.write("=" * 80 + "\n")
 f.write("MAXIMALE ACCURACY - ERWEITERTE OPTIMIERUNGEN\n")
 f.write("=" * 80 + "\n")
 f.write(f"Gestartet: {datetime.now().isoformat()}\n")
 f.write("=" * 80 + "\n\n")
 
 log_progress("=" * 80)
 log_progress("MAXIMALE ACCURACY - ERWEITERTE OPTIMIERUNGEN")
 log_progress("=" * 80)
 log_progress("⚠️ KEINE HALLUZINATIONEN - NUR ECHTE DATEN!")
 log_progress("🔬 KRITISCH, SYSTEMATISCH, PERFEKT")
 log_progress("")
 
 # Load Daten
 log_progress("📂 Load Daten...")
 
 if not LAYER3_FILE.exists():
 log_progress(f"❌ Datei nicht gefunden: {LAYER3_FILE}")
 return
 
 with LAYER3_FILE.open() as f:
 layer3_data = json.load(f)
 layer3_results = layer3_data.get("results", [])
 log_progress(f"✅ {len(layer3_results)} Identities geloadn")
 log_progress("")
 
 start_time = time.time()
 
 target_pos = 27
 top_seed_positions = [33, 26, 14, 0, 10, 13, 6, 16, 18, 15] # Top 10
 
 log_progress(f"🔍 POSITION {target_pos} - ERWEITERTE OPTIMIERUNGEN")
 log_progress("")
 
 results = {}
 
 # 1. Teste 4-Position-Kombinationen (Top 6)
 log_progress(" 1. Teste 4-Position-Kombinationen (Top 6)...")
 combo4_results = {}
 
 for combo in combinations(top_seed_positions[:6], 4):
 result = test_combination(layer3_results, list(combo), target_pos, sample_size=2000)
 combo_key = "_".join(map(str, combo))
 combo4_results[combo_key] = result
 
 if combo4_results:
 best_combo4 = max(combo4_results.items(), key=lambda x: x[1]["accuracy"])
 results["best_combo4"] = best_combo4[1]
 log_progress(f" ✅ Beste 4-Position-Kombination: {best_combo4[1]['positions']} ({best_combo4[1]['accuracy']:.2f}%)")
 
 # 2. Teste 5-Position-Kombinationen (Top 6)
 log_progress(" 2. Teste 5-Position-Kombinationen (Top 6)...")
 combo5_results = {}
 
 for combo in combinations(top_seed_positions[:6], 5):
 result = test_combination(layer3_results, list(combo), target_pos, sample_size=2000)
 combo_key = "_".join(map(str, combo))
 combo5_results[combo_key] = result
 
 if combo5_results:
 best_combo5 = max(combo5_results.items(), key=lambda x: x[1]["accuracy"])
 results["best_combo5"] = best_combo5[1]
 log_progress(f" ✅ Beste 5-Position-Kombination: {best_combo5[1]['positions']} ({best_combo5[1]['accuracy']:.2f}%)")
 
 # 3. Teste optimierte gewichtete Kombinationen
 log_progress(" 3. Teste optimierte gewichtete Kombinationen...")
 
 # Top 3
 weighted3 = test_weighted_combination_optimized(layer3_results, top_seed_positions[:3], target_pos, sample_size=2000)
 results["weighted_top3"] = weighted3
 log_progress(f" ✅ Gewichtete Top 3: {weighted3['accuracy']:.2f}%")
 
 # Top 5
 weighted5 = test_weighted_combination_optimized(layer3_results, top_seed_positions[:5], target_pos, sample_size=2000)
 results["weighted_top5"] = weighted5
 log_progress(f" ✅ Gewichtete Top 5: {weighted5['accuracy']:.2f}%")
 
 # Top 10
 weighted10 = test_weighted_combination_optimized(layer3_results, top_seed_positions[:10], target_pos, sample_size=2000)
 results["weighted_top10"] = weighted10
 log_progress(f" ✅ Gewichtete Top 10: {weighted10['accuracy']:.2f}%")
 
 log_progress("")
 
 # Zusammenfassung
 log_progress("📊 ZUSAMMENFASSUNG:")
 log_progress("")
 
 all_results = [
 ("4-Position-Kombination", results.get("best_combo4", {}).get("accuracy", 0)),
 ("5-Position-Kombination", results.get("best_combo5", {}).get("accuracy", 0)),
 ("Gewichtete Top 3", results.get("weighted_top3", {}).get("accuracy", 0)),
 ("Gewichtete Top 5", results.get("weighted_top5", {}).get("accuracy", 0)),
 ("Gewichtete Top 10", results.get("weighted_top10", {}).get("accuracy", 0))
 ]
 
 best_overall = max(all_results, key=lambda x: x[1])
 log_progress(f" 🏆 BESTE METHODE: {best_overall[0]} ({best_overall[1]:.2f}%)")
 log_progress("")
 
 log_progress(" Alle Methoden:")
 for name, acc in sorted(all_results, key=lambda x: x[1], reverse=True):
 marker = "⭐" if (name, acc) == best_overall else " "
 log_progress(f" {marker} {name}: {acc:.2f}%")
 
 log_progress("")
 
 # Speichere Ergebnisse
 OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
 
 def convert_numpy(obj):
 if isinstance(obj, np.integer):
 return int(obj)
 elif isinstance(obj, np.floating):
 return float(obj)
 elif isinstance(obj, np.ndarray):
 return obj.tolist()
 elif isinstance(obj, dict):
 return {k: convert_numpy(v) for k, v in obj.items()}
 elif isinstance(obj, list):
 return [convert_numpy(item) for item in obj]
 return obj
 
 elapsed_time = time.time() - start_time
 
 output_data = {
 "timestamp": datetime.now().isoformat(),
 "target_position": target_pos,
 "top_seed_positions": top_seed_positions,
 "results": convert_numpy(results),
 "best_overall": {
 "method": best_overall[0],
 "accuracy": best_overall[1]
 },
 "elapsed_time_seconds": elapsed_time
 }
 
 output_file = OUTPUT_DIR / "maximize_accuracy_advanced_results.json"
 with output_file.open("w") as f:
 json.dump(output_data, f, indent=2)
 log_progress(f"💾 Ergebnisse gespeichert: {output_file}")
 log_progress("")
 
 log_progress("=" * 80)
 log_progress("✅ ANALYSE ABGESCHLOSSEN")
 log_progress("=" * 80)
 log_progress(f" Gesamtzeit: {elapsed_time:.1f} Sekunden")
 log_progress("")

if __name__ == "__main__":
 main()

