#!/usr/bin/env python3
"""
Seed-basierte Vorhersage for höhere Genauigkeit
- Nutze Seed-Positionen for Vorhersagen
- Kombiniere Matrix- und Seed-basierte Ansätze
- KEINE Halluzinationen - nur echte Daten!
"""

import json
import sys
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from collections import Counter, defaultdict
from datetime import datetime
import numpy as np

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# Paths
LAYER3_FILE = project_root / "outputs" / "derived" / "layer3_derivation_23k_complete.json"
OUTPUT_DIR = project_root / "outputs" / "derived"
REPORTS_DIR = project_root / "outputs" / "reports"

def identity_to_seed(identity: str) -> str:
 """Konvertiere Identity zu Seed."""
 return identity.lower()[:55]

def build_seed_character_mapping(layer3_data: List[Dict], seed_pos: int, target_pos: int) -> Dict:
 """Baue Mapping von Seed-Character zu Identity-Character."""
 
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
 
 # Berechne Erfolgsraten
 results = {}
 for seed_char, counter in mapping.items():
 total = totals[seed_char]
 if total >= 10: # Mindestens 10 Samples
 most_common = counter.most_common(1)[0]
 success_rate = most_common[1] / total
 
 results[seed_char] = {
 "predicted_char": most_common[0],
 "success_rate": success_rate,
 "count": most_common[1],
 "total": total,
 "all_distributions": dict(counter.most_common(5))
 }
 
 return results

def predict_with_seed(seed: str, seed_pos: int, target_pos: int, mapping: Dict) -> Optional[str]:
 """Vorhersage basierend auf Seed-Character."""
 if len(seed) <= seed_pos:
 return None
 
 seed_char = seed[seed_pos].lower()
 if seed_char not in mapping:
 return None
 
 return mapping[seed_char]["predicted_char"]

def test_seed_based_accuracy(layer3_data: List[Dict], seed_pos: int, target_pos: int) -> Dict:
 """Teste Seed-basierte Genauigkeit."""
 
 # Baue Mapping
 mapping = build_seed_character_mapping(layer3_data, seed_pos, target_pos)
 
 # Teste Accuracy
 correct = 0
 total = 0
 covered = 0 # Wie viele haben ein Mapping?
 
 for entry in layer3_data:
 l3_id = entry.get("layer3_identity", "")
 if not l3_id or len(l3_id) <= target_pos:
 continue
 
 seed = identity_to_seed(l3_id)
 predicted = predict_with_seed(seed, seed_pos, target_pos, mapping)
 
 if predicted is None:
 continue
 
 covered += 1
 actual = l3_id[target_pos].upper()
 
 if predicted == actual:
 correct += 1
 total += 1
 
 accuracy = (correct / total * 100) if total > 0 else 0
 coverage = (covered / len(layer3_data) * 100) if layer3_data else 0
 
 return {
 "seed_position": seed_pos,
 "target_position": target_pos,
 "accuracy": accuracy,
 "correct": correct,
 "total": total,
 "coverage": coverage,
 "mapping_size": len(mapping)
 }

def test_combined_approach(layer3_data: List[Dict], target_pos: int, matrix_prediction: Optional[str] = None) -> Dict:
 """Teste kombinierte Ansätze (Matrix + Seed)."""
 
 # Teste verschiedene Seed-Positionen
 seed_positions = [0, 4, 13, 27, 30, 54] # Bekannte wichtige Positionen
 
 best_seed_pos = None
 best_accuracy = 0
 best_mapping = None
 
 for seed_pos in seed_positions:
 result = test_seed_based_accuracy(layer3_data, seed_pos, target_pos)
 if result["accuracy"] > best_accuracy:
 best_accuracy = result["accuracy"]
 best_seed_pos = seed_pos
 best_mapping = build_seed_character_mapping(layer3_data, seed_pos, target_pos)
 
 # Teste kombinierte Vorhersage
 if matrix_prediction and best_seed_pos is not None:
 # Kombiniere: Wenn beide gleich sind, verwende sie, sonst verwende Seed
 combined_correct = 0
 combined_total = 0
 
 for entry in layer3_data:
 l3_id = entry.get("layer3_identity", "")
 if not l3_id or len(l3_id) <= target_pos:
 continue
 
 seed = identity_to_seed(l3_id)
 seed_pred = predict_with_seed(seed, best_seed_pos, target_pos, best_mapping)
 
 if seed_pred is None:
 continue
 
 # Kombiniere: Wenn Matrix und Seed gleich sind, verwende sie
 if matrix_prediction == seed_pred:
 predicted = matrix_prediction
 else:
 predicted = seed_pred # Bevorzuge Seed
 
 actual = l3_id[target_pos].upper()
 if predicted == actual:
 combined_correct += 1
 combined_total += 1
 
 combined_accuracy = (combined_correct / combined_total * 100) if combined_total > 0 else 0
 else:
 combined_accuracy = best_accuracy
 
 return {
 "best_seed_position": best_seed_pos,
 "seed_accuracy": best_accuracy,
 "combined_accuracy": combined_accuracy,
 "matrix_prediction": matrix_prediction
 }

def main():
 """Hauptfunktion."""
 
 print("=" * 80)
 print("SEED-BASED PREDICTION FOR HIGHER ACCURACY")
 print("=" * 80)
 print()
 print("⚠️ KEINE HALLUZINATIONEN - NUR ECHTE DATEN!")
 print("🔬 KRITISCH, SYSTEMATISCH, PERFEKT")
 print()
 
 # 1. Load Layer-3 Daten
 print("📂 Load Layer-3 Daten...")
 if not LAYER3_FILE.exists():
 print(f"❌ Datei nicht gefunden: {LAYER3_FILE}")
 return
 
 with LAYER3_FILE.open() as f:
 layer3_data = json.load(f)
 layer3_results = layer3_data.get("results", [])
 print(f"✅ {len(layer3_results)} Identities geloadn")
 print()
 
 # 2. Teste Seed-basierte Vorhersage for Position 27
 print("🔍 Teste Seed-basierte Vorhersage for Position 27...")
 target_pos = 27
 seed_positions = [0, 4, 13, 27, 30, 54]
 
 seed_results = {}
 for seed_pos in seed_positions:
 print(f" Seed-Position {seed_pos}...")
 result = test_seed_based_accuracy(layer3_results, seed_pos, target_pos)
 seed_results[f"seed_{seed_pos}"] = result
 print(f" Accuracy: {result['accuracy']:.2f}% (Coverage: {result['coverage']:.2f}%)")
 print()
 
 # Finde beste Seed-Position
 best_seed_result = max(seed_results.items(), key=lambda x: x[1]["accuracy"])
 print(f"📊 Beste Seed-Position: {best_seed_result[0]} ({best_seed_result[1]['accuracy']:.2f}%)")
 print()
 
 # 3. Teste kombinierte Ansätze
 print("🔍 Teste kombinierte Ansätze (Matrix + Seed)...")
 # Matrix-Vorhersage for Position 27: 'A' (mod_4)
 matrix_pred = "A"
 
 combined_result = test_combined_approach(layer3_results, target_pos, matrix_pred)
 print(f" Seed-basierte Accuracy: {combined_result['seed_accuracy']:.2f}%")
 print(f" Kombinierte Accuracy: {combined_result['combined_accuracy']:.2f}%")
 print()
 
 # 4. Teste for andere Block-Ende-Positionen
 print("🔍 Teste for andere Block-Ende-Positionen...")
 block_end_positions = [13, 41, 55]
 
 all_results = {}
 for pos in block_end_positions:
 print(f" Position {pos}...")
 best_seed_acc = 0
 best_seed_pos = None
 
 for seed_pos in seed_positions:
 result = test_seed_based_accuracy(layer3_results, seed_pos, pos)
 if result["accuracy"] > best_seed_acc:
 best_seed_acc = result["accuracy"]
 best_seed_pos = seed_pos
 
 all_results[f"position_{pos}"] = {
 "position": pos,
 "best_seed_position": best_seed_pos,
 "seed_accuracy": best_seed_acc
 }
 print(f" Beste Seed-Position: {best_seed_pos} ({best_seed_acc:.2f}%)")
 print()
 
 # Speichere Ergebnisse
 OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
 
 output_data = {
 "timestamp": datetime.now().isoformat(),
 "position_27_seed_results": seed_results,
 "position_27_combined": combined_result,
 "other_positions": all_results,
 "conclusion": {
 "best_seed_position_27": best_seed_result[0],
 "seed_accuracy_27": best_seed_result[1]["accuracy"],
 "combined_accuracy_27": combined_result["combined_accuracy"]
 }
 }
 
 output_file = OUTPUT_DIR / "seed_based_prediction_results.json"
 with output_file.open("w") as f:
 json.dump(output_data, f, indent=2)
 print(f"💾 Ergebnisse gespeichert: {output_file}")
 print()
 
 print("=" * 80)
 print("✅ ANALYSE ABGESCHLOSSEN")
 print("=" * 80)
 print()
 print("📊 ZUSAMMENFASSUNG:")
 print()
 print(f" Position 27:")
 print(f" Beste Seed-Position: {best_seed_result[0]}")
 print(f" Seed-Accuracy: {best_seed_result[1]['accuracy']:.2f}%")
 print(f" Kombinierte Accuracy: {combined_result['combined_accuracy']:.2f}%")
 print()

if __name__ == "__main__":
 main()

