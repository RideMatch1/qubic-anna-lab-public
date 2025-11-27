#!/usr/bin/env python3
"""
Systematische Genauigkeits-Verbesserung
- Teste Kombinationen von Positionen
- Teste verschiedene Transformationen
- Teste Multi-Position-Models
- KEINE Halluzinationen - nur echte Daten!
"""

import json
import sys
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from collections import Counter, defaultdict
from datetime import datetime
import numpy as np
import pandas as pd
from itertools import combinations

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# Paths
LAYER3_FILE = project_root / "outputs" / "derived" / "layer3_derivation_23k_complete.json"
MATRIX_FILE = project_root / "data" / "anna-matrix" / "Anna_Matrix.xlsx"
OUTPUT_DIR = project_root / "outputs" / "derived"
REPORTS_DIR = project_root / "outputs" / "reports"

def load_anna_matrix() -> np.ndarray:
 """Load Anna Matrix."""
 if not MATRIX_FILE.exists():
 raise FileNotFoundError(f"Matrix file not found: {MATRIX_FILE}")
 
 df = pd.read_excel(MATRIX_FILE, header=None)
 numeric = df.apply(pd.to_numeric, errors="coerce").fillna(0.0)
 matrix = numeric.to_numpy(dtype=float)
 
 if matrix.shape == (129, 129):
 matrix = matrix[1:, 1:]
 
 if matrix.shape != (128, 128):
 raise ValueError(f"Matrix has wrong shape: {matrix.shape}")
 
 return matrix

def get_matrix_coord(position: int, grid_col: int) -> Tuple[int, int]:
 """Berechne Matrix-Koordinate basierend auf Mapping-Formel."""
 # Spalte-Mapping: Grid Col + 7 = Matrix Col
 matrix_col = grid_col + 7
 
 # Row-Mapping:
 if position == 27:
 matrix_row = position # Direkt
 else:
 matrix_row = 128 - position # Symmetric
 
 return (matrix_row, matrix_col)

def get_grid_coord(position: int) -> Tuple[int, int]:
 """Berechne Grid-Koordinate for Position."""
 grid_index = position % 49
 grid_row = grid_index // 7
 grid_col = grid_index % 7
 return (grid_row, grid_col)

def predict_char_single_position(matrix: np.ndarray, position: int, transformation: str = "mod_26") -> str:
 """Vorhersage for eine einzelne Position."""
 grid_row, grid_col = get_grid_coord(position)
 matrix_row, matrix_col = get_matrix_coord(position, grid_col)
 
 if not (0 <= matrix_row < 128 and 0 <= matrix_col < 128):
 return None
 
 matrix_value = matrix[matrix_row, matrix_col]
 
 if transformation == "mod_26":
 char = chr(ord('A') + (int(matrix_value) % 26))
 elif transformation == "mod_4":
 char = chr(ord('A') + (int(matrix_value) % 4))
 elif transformation == "abs_mod_4":
 char = chr(ord('A') + (abs(int(matrix_value)) % 4))
 else:
 return None
 
 return char

def test_single_position_accuracy(matrix: np.ndarray, layer3_data: List[Dict], position: int, transformation: str = "mod_26") -> Dict:
 """Teste Genauigkeit for eine einzelne Position."""
 correct = 0
 total = 0
 
 for entry in layer3_data:
 l3_id = entry.get("layer3_identity", "")
 if not l3_id or len(l3_id) <= position:
 continue
 
 predicted = predict_char_single_position(matrix, position, transformation)
 if predicted is None:
 continue
 
 actual = l3_id[position].upper()
 if predicted == actual:
 correct += 1
 total += 1
 
 accuracy = (correct / total * 100) if total > 0 else 0
 return {
 "position": position,
 "transformation": transformation,
 "accuracy": accuracy,
 "correct": correct,
 "total": total
 }

def test_position_combinations(matrix: np.ndarray, layer3_data: List[Dict], positions: List[int], transformations: List[str]) -> Dict:
 """Teste Kombinationen von Positionen."""
 results = {}
 
 # Teste alle Kombinationen
 for r in range(1, len(positions) + 1):
 for pos_combo in combinations(positions, r):
 for trans_combo in combinations(transformations, r):
 if len(pos_combo) != len(trans_combo):
 continue
 
 # Teste diese Kombination
 correct = 0
 total = 0
 
 for entry in layer3_data:
 l3_id = entry.get("layer3_identity", "")
 if not l3_id or len(l3_id) <= max(pos_combo):
 continue
 
 # Check alle Positionen
 all_match = True
 for pos, trans in zip(pos_combo, trans_combo):
 predicted = predict_char_single_position(matrix, pos, trans)
 if predicted is None or predicted != l3_id[pos].upper():
 all_match = False
 break
 
 if all_match:
 correct += 1
 total += 1
 
 accuracy = (correct / total * 100) if total > 0 else 0
 
 combo_key = f"{pos_combo}_{trans_combo}"
 results[combo_key] = {
 "positions": pos_combo,
 "transformations": trans_combo,
 "accuracy": accuracy,
 "correct": correct,
 "total": total
 }
 
 return results

def test_alternative_transformations(matrix: np.ndarray, layer3_data: List[Dict], position: int) -> Dict:
 """Teste alternative Transformationen for eine Position."""
 transformations = [
 "mod_26",
 "mod_4",
 "abs_mod_4",
 "mod_8",
 "mod_13",
 "mod_29"
 ]
 
 results = {}
 
 for trans in transformations:
 grid_row, grid_col = get_grid_coord(position)
 matrix_row, matrix_col = get_matrix_coord(position, grid_col)
 
 if not (0 <= matrix_row < 128 and 0 <= matrix_col < 128):
 continue
 
 matrix_value = matrix[matrix_row, matrix_col]
 
 # Berechne Character basierend auf Transformation
 if trans == "mod_26":
 char = chr(ord('A') + (int(matrix_value) % 26))
 elif trans == "mod_4":
 char = chr(ord('A') + (int(matrix_value) % 4))
 elif trans == "abs_mod_4":
 char = chr(ord('A') + (abs(int(matrix_value)) % 4))
 elif trans == "mod_8":
 char = chr(ord('A') + (int(matrix_value) % 8))
 elif trans == "mod_13":
 char = chr(ord('A') + (int(matrix_value) % 13))
 elif trans == "mod_29":
 char = chr(ord('A') + (int(matrix_value) % 29))
 else:
 continue
 
 # Teste Accuracy
 correct = 0
 total = 0
 
 for entry in layer3_data:
 l3_id = entry.get("layer3_identity", "")
 if not l3_id or len(l3_id) <= position:
 continue
 
 actual = l3_id[position].upper()
 if char == actual:
 correct += 1
 total += 1
 
 accuracy = (correct / total * 100) if total > 0 else 0
 
 # Erwartete Accuracy bei Zufall
 if trans in ["mod_4", "abs_mod_4"]:
 expected = 25.0 # 1/4
 elif trans == "mod_8":
 expected = 12.5 # 1/8
 elif trans == "mod_13":
 expected = 100.0 / 13 # ~7.69%
 elif trans == "mod_26":
 expected = 100.0 / 26 # ~3.85%
 elif trans == "mod_29":
 expected = 100.0 / 29 # ~3.45%
 else:
 expected = 0
 
 ratio = accuracy / expected if expected > 0 else 0
 
 results[trans] = {
 "transformation": trans,
 "predicted_char": char,
 "accuracy": accuracy,
 "expected": expected,
 "ratio": ratio,
 "correct": correct,
 "total": total
 }
 
 return results

def main():
 """Hauptfunktion."""
 
 print("=" * 80)
 print("SYSTEMATISCHE GENAUIGKEITS-VERBESSERUNG")
 print("=" * 80)
 print()
 print("⚠️ KEINE HALLUZINATIONEN - NUR ECHTE DATEN!")
 print("🔬 KRITISCH, SYSTEMATISCH, PERFEKT")
 print()
 
 # 1. Load Matrix
 print("📂 Load Anna Matrix...")
 try:
 matrix = load_anna_matrix()
 print(f"✅ Matrix geloadn: {matrix.shape}")
 except Exception as e:
 print(f"❌ Fehler: {e}")
 return
 print()
 
 # 2. Load Layer-3 Daten
 print("📂 Load Layer-3 Daten...")
 if not LAYER3_FILE.exists():
 print(f"❌ Datei nicht gefunden: {LAYER3_FILE}")
 return
 
 with LAYER3_FILE.open() as f:
 layer3_data = json.load(f)
 layer3_results = layer3_data.get("results", [])
 print(f"✅ {len(layer3_results)} Identities geloadn")
 print()
 
 # 3. Teste alternative Transformationen for Block-Ende-Positionen
 print("🔍 Teste alternative Transformationen...")
 block_end_positions = [13, 27, 41, 55]
 transformation_results = {}
 
 for pos in block_end_positions:
 print(f" Position {pos}...")
 results = test_alternative_transformations(matrix, layer3_results, pos)
 transformation_results[f"position_{pos}"] = results
 
 # Zeige beste Transformation
 best = max(results.items(), key=lambda x: x[1]["ratio"])
 print(f" Beste: {best[0]} ({best[1]['accuracy']:.2f}%, {best[1]['ratio']:.2f}x)")
 print()
 
 # 4. Teste einzelne Positionen mit verschiedenen Transformationen
 print("🔍 Teste einzelne Positionen...")
 single_position_results = {}
 
 for pos in block_end_positions:
 for trans in ["mod_26", "mod_4", "abs_mod_4"]:
 result = test_single_position_accuracy(matrix, layer3_results, pos, trans)
 key = f"pos_{pos}_{trans}"
 single_position_results[key] = result
 print()
 
 # 5. Teste Position-Kombinationen
 print("🔍 Teste Position-Kombinationen...")
 print(" (Das kann eine Weile dauern...)")
 
 # Teste nur 2-Position-Kombinationen for Geschwindigkeit
 combo_results = {}
 for pos1, pos2 in combinations(block_end_positions, 2):
 print(f" Kombination: {pos1} + {pos2}...")
 
 # Teste verschiedene Transformation-Kombinationen
 for trans1 in ["mod_26", "mod_4"]:
 for trans2 in ["mod_26", "mod_4"]:
 correct = 0
 total = 0
 
 for entry in layer3_results:
 l3_id = entry.get("layer3_identity", "")
 if not l3_id or len(l3_id) <= max(pos1, pos2):
 continue
 
 pred1 = predict_char_single_position(matrix, pos1, trans1)
 pred2 = predict_char_single_position(matrix, pos2, trans2)
 
 if pred1 is None or pred2 is None:
 continue
 
 if pred1 == l3_id[pos1].upper() and pred2 == l3_id[pos2].upper():
 correct += 1
 total += 1
 
 accuracy = (correct / total * 100) if total > 0 else 0
 
 # Erwartete Accuracy (Produkt der Einzel-Accuracies)
 # Vereinfacht: Annahme Unabhängigkeit
 expected = (accuracy / 100) ** 2 * 100 if accuracy > 0 else 0
 
 combo_key = f"{pos1}_{trans1}_{pos2}_{trans2}"
 combo_results[combo_key] = {
 "positions": [pos1, pos2],
 "transformations": [trans1, trans2],
 "accuracy": accuracy,
 "expected": expected,
 "correct": correct,
 "total": total
 }
 
 print()
 
 # 6. Analyze Ergebnisse
 print("📊 ANALYSE:")
 print()
 
 print("Beste Transformationen pro Position:")
 for pos_key, results in transformation_results.items():
 pos = int(pos_key.split("_")[1])
 best = max(results.items(), key=lambda x: x[1]["ratio"])
 marker = "⭐" if pos == 27 else " "
 print(f" {marker} Position {pos}: {best[0]} ({best[1]['accuracy']:.2f}%, {best[1]['ratio']:.2f}x)")
 print()
 
 print("Beste Position-Kombinationen:")
 best_combos = sorted(combo_results.items(), key=lambda x: x[1]["accuracy"], reverse=True)[:5]
 for i, (key, data) in enumerate(best_combos, 1):
 parts = key.split("_")
 if len(parts) >= 4:
 pos1, trans1, pos2, trans2 = parts[0], parts[1], parts[2], parts[3]
 print(f" {i}. Position {pos1} ({trans1}) + {pos2} ({trans2}): {data['accuracy']:.2f}%")
 else:
 print(f" {i}. {key}: {data['accuracy']:.2f}%")
 print()
 
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
 
 output_data = {
 "timestamp": datetime.now().isoformat(),
 "transformation_results": convert_numpy(transformation_results),
 "single_position_results": convert_numpy(single_position_results),
 "combo_results": convert_numpy(combo_results),
 "conclusion": {
 "best_single": max(single_position_results.items(), key=lambda x: x[1]["accuracy"]),
 "best_combo": max(combo_results.items(), key=lambda x: x[1]["accuracy"]) if combo_results else None
 }
 }
 
 output_file = OUTPUT_DIR / "accuracy_improvement_analysis.json"
 with output_file.open("w") as f:
 json.dump(output_data, f, indent=2)
 print(f"💾 Ergebnisse gespeichert: {output_file}")
 print()
 
 print("=" * 80)
 print("✅ ANALYSE ABGESCHLOSSEN")
 print("=" * 80)

if __name__ == "__main__":
 main()

