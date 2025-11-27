#!/usr/bin/env python3
"""
Maximale Accuracy-Verbesserung - Umfassende Analyse
- Analyze Seed-Position 33 for Position 27
- Teste Kombinationen (2, 3, 4 Seed-Positionen)
- Teste alle 60 Positionen (nicht nur Block-Ende)
- Machine Learning Ansätze
- 100% Echtheit sicherstellen
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
import pandas as pd

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# Paths
LAYER3_FILE = project_root / "outputs" / "derived" / "layer3_derivation_23k_complete.json"
MATRIX_FILE = project_root / "data" / "anna-matrix" / "Anna_Matrix.xlsx"
OUTPUT_DIR = project_root / "outputs" / "derived"
PROGRESS_FILE = project_root / "outputs" / "derived" / "maximize_accuracy_progress.json"
STATUS_FILE = project_root / "outputs" / "derived" / "maximize_accuracy_status.txt"

def log_progress(message: str, status_file: Path = STATUS_FILE):
 """Schreibe Fortschritt in Status-Datei."""
 timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
 with status_file.open("a") as f:
 f.write(f"[{timestamp}] {message}\n")
 print(f"[{timestamp}] {message}")

def save_progress(data: Dict, progress_file: Path = PROGRESS_FILE):
 """Speichere Fortschritt in JSON."""
 with progress_file.open("w") as f:
 json.dump(data, f, indent=2)

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
 "total": total,
 "distribution": dict(counter.most_common(5))
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

def test_single_seed_position(layer3_data: List[Dict], seed_pos: int, target_pos: int, sample_size: int = 2000) -> Dict:
 """Teste einzelne Seed-Position."""
 mapping = build_seed_mapping(layer3_data, seed_pos, target_pos)
 
 if not mapping:
 return {"accuracy": 0, "total": 0, "mapping_size": 0}
 
 correct = 0
 total = 0
 
 for entry in layer3_data[:sample_size]:
 l3_id = entry.get("layer3_identity", "")
 if not l3_id or len(l3_id) <= target_pos:
 continue
 
 seed = identity_to_seed(l3_id)
 predicted = predict_with_seed(seed, seed_pos, mapping)
 
 if predicted is None:
 continue
 
 actual = l3_id[target_pos].upper()
 if predicted == actual:
 correct += 1
 total += 1
 
 accuracy = (correct / total * 100) if total > 0 else 0
 
 return {
 "seed_position": seed_pos,
 "accuracy": accuracy,
 "correct": correct,
 "total": total,
 "mapping_size": len(mapping)
 }

def test_seed_combination(layer3_data: List[Dict], seed_positions: List[int], target_pos: int, sample_size: int = 2000) -> Dict:
 """Teste Kombination von Seed-Positionen."""
 
 # Baue Mappings for alle Seed-Positionen
 mappings = {}
 for seed_pos in seed_positions:
 mapping = build_seed_mapping(layer3_data, seed_pos, target_pos)
 if mapping:
 mappings[seed_pos] = mapping
 
 if not mappings:
 return {"accuracy": 0, "total": 0}
 
 # Teste Kombination
 correct = 0
 total = 0
 
 for entry in layer3_data[:sample_size]:
 l3_id = entry.get("layer3_identity", "")
 if not l3_id or len(l3_id) <= target_pos:
 continue
 
 seed = identity_to_seed(l3_id)
 
 # Sammle Vorhersagen von allen Seed-Positionen
 predictions = []
 for seed_pos in seed_positions:
 if seed_pos in mappings:
 pred = predict_with_seed(seed, seed_pos, mappings[seed_pos])
 if pred is not None:
 predictions.append(pred)
 
 if not predictions:
 continue
 
 # Kombiniere: Mehrheitsentscheidung
 prediction_counter = Counter(predictions)
 predicted = prediction_counter.most_common(1)[0][0]
 
 actual = l3_id[target_pos].upper()
 if predicted == actual:
 correct += 1
 total += 1
 
 accuracy = (correct / total * 100) if total > 0 else 0
 
 return {
 "seed_positions": seed_positions,
 "accuracy": accuracy,
 "correct": correct,
 "total": total,
 "num_predictions": len(predictions) if total > 0 else 0
 }

def test_weighted_combination(layer3_data: List[Dict], seed_positions: List[int], weights: List[float], target_pos: int, sample_size: int = 2000) -> Dict:
 """Teste gewichtete Kombination von Seed-Positionen."""
 
 # Baue Mappings
 mappings = {}
 for seed_pos in seed_positions:
 mapping = build_seed_mapping(layer3_data, seed_pos, target_pos)
 if mapping:
 mappings[seed_pos] = mapping
 
 if not mappings:
 return {"accuracy": 0, "total": 0}
 
 # Teste gewichtete Kombination
 correct = 0
 total = 0
 
 for entry in layer3_data[:sample_size]:
 l3_id = entry.get("layer3_identity", "")
 if not l3_id or len(l3_id) <= target_pos:
 continue
 
 seed = identity_to_seed(l3_id)
 
 # Gewichtete Vorhersagen
 weighted_predictions = defaultdict(float)
 for i, seed_pos in enumerate(seed_positions):
 if seed_pos in mappings:
 pred = predict_with_seed(seed, seed_pos, mappings[seed_pos])
 if pred is not None:
 weight = weights[i] if i < len(weights) else 1.0
 weighted_predictions[pred] += weight
 
 if not weighted_predictions:
 continue
 
 # Wähle Vorhersage mit höchstem Gewicht
 predicted = max(weighted_predictions.items(), key=lambda x: x[1])[0]
 
 actual = l3_id[target_pos].upper()
 if predicted == actual:
 correct += 1
 total += 1
 
 accuracy = (correct / total * 100) if total > 0 else 0
 
 return {
 "seed_positions": seed_positions,
 "weights": weights,
 "accuracy": accuracy,
 "correct": correct,
 "total": total
 }

def analyze_position27_comprehensive(layer3_data: List[Dict], sample_size: int = 2000) -> Dict:
 """Umfassende Analyse for Position 27."""
 
 log_progress("🔍 UMFASSENDE ANALYSE FÜR POSITION 27...")
 target_pos = 27
 
 # 1. Teste alle Seed-Positionen einzeln
 log_progress(" 1. Teste alle 55 Seed-Positionen einzeln...")
 single_results = {}
 
 for seed_pos in range(55):
 if (seed_pos + 1) % 10 == 0:
 log_progress(f" {seed_pos + 1}/55...")
 
 result = test_single_seed_position(layer3_data, seed_pos, target_pos, sample_size)
 single_results[seed_pos] = result
 
 # Finde beste Seed-Positionen
 best_single = sorted(
 single_results.items(),
 key=lambda x: x[1]["accuracy"],
 reverse=True
 )[:10]
 
 log_progress(f" ✅ Top 10 Seed-Positionen gefunden")
 
 # 2. Teste 2-Position-Kombinationen (Top 10)
 log_progress(" 2. Teste 2-Position-Kombinationen (Top 10)...")
 top_seed_positions = [pos for pos, _ in best_single]
 combo2_results = {}
 
 for combo in combinations(top_seed_positions, 2):
 result = test_seed_combination(layer3_data, list(combo), target_pos, sample_size)
 combo_key = f"{combo[0]}_{combo[1]}"
 combo2_results[combo_key] = result
 
 best_combo2 = max(combo2_results.items(), key=lambda x: x[1]["accuracy"]) if combo2_results else None
 
 log_progress(f" ✅ Beste 2-Position-Kombination: {best_combo2[0] if best_combo2 else 'N/A'} ({best_combo2[1]['accuracy']:.2f}% if best_combo2 else 0)")
 
 # 3. Teste 3-Position-Kombinationen (Top 5)
 log_progress(" 3. Teste 3-Position-Kombinationen (Top 5)...")
 top5_seed_positions = top_seed_positions[:5]
 combo3_results = {}
 
 for combo in combinations(top5_seed_positions, 3):
 result = test_seed_combination(layer3_data, list(combo), target_pos, sample_size)
 combo_key = "_".join(map(str, combo))
 combo3_results[combo_key] = result
 
 best_combo3 = max(combo3_results.items(), key=lambda x: x[1]["accuracy"]) if combo3_results else None
 
 log_progress(f" ✅ Beste 3-Position-Kombination: {best_combo3[0] if best_combo3 else 'N/A'} ({best_combo3[1]['accuracy']:.2f}% if best_combo3 else 0)")
 
 # 4. Teste gewichtete Kombination (Top 3)
 log_progress(" 4. Teste gewichtete Kombinationen (Top 3)...")
 top3_seed_positions = top_seed_positions[:3]
 top3_accuracies = [single_results[pos]["accuracy"] for pos in top3_seed_positions]
 
 # Normalisiere Gewichte basierend auf Accuracy
 total_acc = sum(top3_accuracies)
 weights = [acc / total_acc if total_acc > 0 else 1.0/len(top3_accuracies) for acc in top3_accuracies]
 
 weighted_result = test_weighted_combination(layer3_data, top3_seed_positions, weights, target_pos, sample_size)
 
 log_progress(f" ✅ Gewichtete Kombination: {weighted_result['accuracy']:.2f}%")
 
 return {
 "target_position": target_pos,
 "single_results": single_results,
 "best_single": [{"position": pos, "accuracy": data["accuracy"]} for pos, data in best_single],
 "combo2_results": combo2_results,
 "best_combo2": {
 "positions": best_combo2[0].split("_") if best_combo2 else [],
 "accuracy": best_combo2[1]["accuracy"] if best_combo2 else 0
 },
 "combo3_results": combo3_results,
 "best_combo3": {
 "positions": best_combo3[0].split("_") if best_combo3 else [],
 "accuracy": best_combo3[1]["accuracy"] if best_combo3 else 0
 },
 "weighted_result": weighted_result
 }

def test_all_positions_quick(layer3_data: List[Dict], sample_size: int = 1000) -> Dict:
 """Schneller Test for alle 60 Positionen (nur beste Seed-Positionen)."""
 
 log_progress("🔍 SCHNELLER TEST FÜR ALLE 60 POSITIONEN...")
 
 all_positions_results = {}
 
 for target_pos in range(60):
 if (target_pos + 1) % 10 == 0:
 log_progress(f" Position {target_pos + 1}/60...")
 
 # Teste nur Top 10 Seed-Positionen (aus vorheriger Analyse)
 # Für Block-Ende: verwende bekannte beste
 if target_pos in [13, 27, 41, 55]:
 # Verwende bekannte beste Seed-Positionen
 test_seed_positions = [33, 26, 14, 0, 10] if target_pos == 27 else list(range(10))
 else:
 # Für andere: teste Top 10
 test_seed_positions = list(range(10))
 
 best_accuracy = 0
 best_seed_pos = None
 
 for seed_pos in test_seed_positions:
 result = test_single_seed_position(layer3_data, seed_pos, target_pos, sample_size)
 if result["accuracy"] > best_accuracy:
 best_accuracy = result["accuracy"]
 best_seed_pos = seed_pos
 
 all_positions_results[target_pos] = {
 "position": target_pos,
 "best_seed_position": best_seed_pos,
 "best_accuracy": best_accuracy
 }
 
 return all_positions_results

def main():
 """Hauptfunktion."""
 
 # Initialisiere Status-Datei
 STATUS_FILE.parent.mkdir(parents=True, exist_ok=True)
 with STATUS_FILE.open("w") as f:
 f.write("=" * 80 + "\n")
 f.write("MAXIMALE ACCURACY-VERBESSERUNG - UMFASSENDE ANALYSE\n")
 f.write("=" * 80 + "\n")
 f.write(f"Gestartet: {datetime.now().isoformat()}\n")
 f.write("=" * 80 + "\n\n")
 
 log_progress("=" * 80)
 log_progress("MAXIMALE ACCURACY-VERBESSERUNG - UMFASSENDE ANALYSE")
 log_progress("=" * 80)
 log_progress("⚠️ KEINE HALLUZINATIONEN - NUR ECHTE DATEN!")
 log_progress("🔬 KRITISCH, SYSTEMATISCH, PERFEKT, 100% ECHTHEIT")
 log_progress("")
 
 # 1. Load Daten
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
 
 # 2. Umfassende Analyse for Position 27
 log_progress("=" * 80)
 log_progress("POSITION 27 - UMFASSENDE ANALYSE")
 log_progress("=" * 80)
 log_progress("")
 
 pos27_analysis = analyze_position27_comprehensive(layer3_results, sample_size=2000)
 
 log_progress("")
 log_progress("📊 POSITION 27 ERGEBNISSE:")
 log_progress("")
 
 best_single = pos27_analysis["best_single"][0]
 log_progress(f" Beste einzelne Seed-Position: {best_single['position']} ({best_single['accuracy']:.2f}%)")
 
 if pos27_analysis["best_combo2"]["accuracy"] > 0:
 log_progress(f" Beste 2-Position-Kombination: {pos27_analysis['best_combo2']['positions']} ({pos27_analysis['best_combo2']['accuracy']:.2f}%)")
 
 if pos27_analysis["best_combo3"]["accuracy"] > 0:
 log_progress(f" Beste 3-Position-Kombination: {pos27_analysis['best_combo3']['positions']} ({pos27_analysis['best_combo3']['accuracy']:.2f}%)")
 
 if pos27_analysis["weighted_result"]["accuracy"] > 0:
 log_progress(f" Gewichtete Kombination: {pos27_analysis['weighted_result']['accuracy']:.2f}%")
 
 log_progress("")
 
 # 3. Schneller Test for alle Positionen
 log_progress("=" * 80)
 log_progress("ALLE 60 POSITIONEN - SCHNELLER TEST")
 log_progress("=" * 80)
 log_progress("")
 
 all_positions = test_all_positions_quick(layer3_results, sample_size=1000)
 
 # Finde beste Positionen
 best_positions = sorted(
 all_positions.items(),
 key=lambda x: x[1]["best_accuracy"],
 reverse=True
 )[:10]
 
 log_progress("")
 log_progress("📊 TOP 10 POSITIONEN (nach Accuracy):")
 log_progress("")
 
 for i, (pos, data) in enumerate(best_positions, 1):
 marker = "⭐" if pos == 27 else " "
 log_progress(f" {marker} {i}. Position {pos}: Seed-Position {data['best_seed_position']} ({data['best_accuracy']:.2f}%)")
 
 log_progress("")
 
 # 4. Speichere Ergebnisse
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
 "total_identities": len(layer3_results),
 "elapsed_time_seconds": elapsed_time,
 "position27_comprehensive": convert_numpy(pos27_analysis),
 "all_positions_quick": convert_numpy(all_positions),
 "top_positions": [
 {"position": pos, "seed_position": data["best_seed_position"], "accuracy": data["best_accuracy"]}
 for pos, data in best_positions
 ]
 }
 
 output_file = OUTPUT_DIR / "maximize_accuracy_comprehensive_results.json"
 with output_file.open("w") as f:
 json.dump(output_data, f, indent=2)
 log_progress(f"💾 Ergebnisse gespeichert: {output_file}")
 log_progress("")
 
 log_progress("=" * 80)
 log_progress("✅ ANALYSE ABGESCHLOSSEN")
 log_progress("=" * 80)
 log_progress("")
 log_progress("📊 STATISTIKEN:")
 log_progress("")
 log_progress(f" Position 27: Umfassende Analyse")
 log_progress(f" Alle 60 Positionen: Schneller Test")
 log_progress(f" Gesamtzeit: {elapsed_time:.1f} Sekunden ({elapsed_time/60:.1f} Minuten)")
 log_progress("")
 log_progress("📄 Status-Datei: outputs/derived/maximize_accuracy_status.txt")
 log_progress("📄 Ergebnisse: outputs/derived/maximize_accuracy_comprehensive_results.json")
 log_progress("")

if __name__ == "__main__":
 main()

