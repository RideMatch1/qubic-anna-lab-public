#!/usr/bin/env python3
"""
Finde Transformation for Position 13, 41, 55
- Teste verschiedene Formeln (mod_4, mod_26, komplex)
- Validate auf echten Daten
- KEINE Halluzinationen - nur echte Daten!
"""

import json
import sys
from pathlib import Path
from typing import Dict, List, Tuple
from collections import Counter
from datetime import datetime
import numpy as np
import pandas as pd

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

def test_transformation_formulas(matrix: np.ndarray, coord: Tuple[int, int], actual_chars: Counter) -> Dict:
 """Teste verschiedene Transformation-Formeln."""
 
 row, col = coord
 if not (0 <= row < 128 and 0 <= col < 128):
 return {}
 
 value = int(matrix[row, col])
 total = sum(actual_chars.values())
 
 formulas = {}
 
 # Formel 1: mod_26
 mod26 = int(value % 26)
 char_mod26 = chr(ord('A') + mod26)
 count_mod26 = actual_chars.get(char_mod26, 0)
 formulas["mod_26"] = {
 "formula": "value % 26",
 "result": mod26,
 "char": char_mod26,
 "count": count_mod26,
 "accuracy": (count_mod26 / total * 100) if total > 0 else 0
 }
 
 # Formel 2: abs(value) % 26
 abs_mod26 = int(abs(value) % 26)
 char_abs_mod26 = chr(ord('A') + abs_mod26)
 count_abs_mod26 = actual_chars.get(char_abs_mod26, 0)
 formulas["abs_mod_26"] = {
 "formula": "abs(value) % 26",
 "result": abs_mod26,
 "char": char_abs_mod26,
 "count": count_abs_mod26,
 "accuracy": (count_abs_mod26 / total * 100) if total > 0 else 0
 }
 
 # Formel 3: (value + 26) % 26
 norm_mod26 = int((value + 26) % 26)
 char_norm_mod26 = chr(ord('A') + norm_mod26)
 count_norm_mod26 = actual_chars.get(char_norm_mod26, 0)
 formulas["normalized_mod_26"] = {
 "formula": "(value + 26) % 26",
 "result": norm_mod26,
 "char": char_norm_mod26,
 "count": count_norm_mod26,
 "accuracy": (count_norm_mod26 / total * 100) if total > 0 else 0
 }
 
 # Formel 4: mod_4
 mod4 = int(value % 4)
 char_mod4 = chr(ord('A') + mod4)
 count_mod4 = actual_chars.get(char_mod4, 0)
 formulas["mod_4"] = {
 "formula": "value % 4",
 "result": mod4,
 "char": char_mod4,
 "count": count_mod4,
 "accuracy": (count_mod4 / total * 100) if total > 0 else 0
 }
 
 # Formel 5: abs(value) % 4
 abs_mod4 = int(abs(value) % 4)
 char_abs_mod4 = chr(ord('A') + abs_mod4)
 count_abs_mod4 = actual_chars.get(char_abs_mod4, 0)
 formulas["abs_mod_4"] = {
 "formula": "abs(value) % 4",
 "result": abs_mod4,
 "char": char_abs_mod4,
 "count": count_abs_mod4,
 "accuracy": (count_abs_mod4 / total * 100) if total > 0 else 0
 }
 
 # Formel 6: value // 14 % 26 (Block-basiert)
 if value != 0:
 block_mod26 = int((value // 14) % 26)
 char_block_mod26 = chr(ord('A') + block_mod26)
 count_block_mod26 = actual_chars.get(char_block_mod26, 0)
 formulas["block_mod_26"] = {
 "formula": "value // 14 % 26",
 "result": block_mod26,
 "char": char_block_mod26,
 "count": count_block_mod26,
 "accuracy": (count_block_mod26 / total * 100) if total > 0 else 0
 }
 
 # Formel 7: value // 14 % 4
 if value != 0:
 block_mod4 = int((value // 14) % 4)
 char_block_mod4 = chr(ord('A') + block_mod4)
 count_block_mod4 = actual_chars.get(char_block_mod4, 0)
 formulas["block_mod_4"] = {
 "formula": "value // 14 % 4",
 "result": block_mod4,
 "char": char_block_mod4,
 "count": count_block_mod4,
 "accuracy": (count_block_mod4 / total * 100) if total > 0 else 0
 }
 
 return formulas

def analyze_position(position: int, layer3_data: List[Dict], matrix: np.ndarray) -> Dict:
 """Analyze Transformation for eine Position."""
 
 block = position // 14
 pos_in_block = position % 14
 
 # Sammle Characters
 chars = Counter()
 for entry in layer3_data:
 l3_id = entry.get("layer3_identity", "")
 if l3_id and len(l3_id) > position:
 chars[l3_id[position].upper()] += 1
 
 total = sum(chars.values())
 unique_chars = len(chars)
 
 # Mögliche Matrix-Koordinaten
 possible_coords = [
 (position, pos_in_block, "direct"),
 (block * 14 + pos_in_block, 0, "block_based"),
 (128 - position, pos_in_block, "symmetric"),
 (position, 13, "col_13"), # Spalte 13 (wie Position 27)
 ]
 
 # Teste Transformationen for jede Koordinate
 results = {}
 
 for row, col, name in possible_coords:
 if not (0 <= row < 128 and 0 <= col < 128):
 continue
 
 coord = (row, col)
 formulas = test_transformation_formulas(matrix, coord, chars)
 
 # Finde beste Formel
 best_formula = None
 best_accuracy = 0
 
 for formula_name, formula_data in formulas.items():
 accuracy = formula_data.get("accuracy", 0)
 if accuracy > best_accuracy:
 best_accuracy = accuracy
 best_formula = formula_name
 
 results[name] = {
 "coord": coord,
 "matrix_value": int(matrix[row, col]),
 "formulas": formulas,
 "best_formula": best_formula,
 "best_accuracy": best_accuracy
 }
 
 return {
 "position": position,
 "block": block,
 "pos_in_block": pos_in_block,
 "total": total,
 "unique_chars": unique_chars,
 "char_distribution": dict(chars.most_common(10)),
 "transformation_results": results
 }

def main():
 """Hauptfunktion."""
 
 print("=" * 80)
 print("TRANSFORMATION FÜR POSITION 13, 41, 55 FINDEN")
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
 
 # 3. Analyze Positionen
 positions = [13, 41, 55]
 all_results = {}
 
 for pos in positions:
 print(f"🔍 Analyze Position {pos}...")
 analysis = analyze_position(pos, layer3_results, matrix)
 all_results[f"position_{pos}"] = analysis
 print(f"✅ Position {pos} analysiert")
 print()
 
 # 4. Zeige Ergebnisse
 print("=" * 80)
 print("ERGEBNISSE")
 print("=" * 80)
 print()
 
 for pos_key, analysis in all_results.items():
 pos = analysis["position"]
 unique = analysis["unique_chars"]
 print(f"📊 Position {pos}:")
 print(f" Unique Characters: {unique}")
 print(f" Top Characters: {list(analysis['char_distribution'].keys())[:5]}")
 print()
 
 # Zeige beste Transformation
 best_overall = None
 best_accuracy = 0
 best_coord = None
 best_formula_name = None
 
 for coord_name, coord_data in analysis.get("transformation_results", {}).items():
 accuracy = coord_data.get("best_accuracy", 0)
 formula = coord_data.get("best_formula")
 
 if accuracy > best_accuracy:
 best_accuracy = accuracy
 best_coord = coord_data["coord"]
 best_formula_name = formula
 best_overall = coord_name
 
 if best_overall:
 best_data = analysis["transformation_results"][best_overall]
 best_formula_data = best_data["formulas"][best_formula_name]
 print(f" Beste Transformation: {best_formula_name}")
 print(f" Koordinate: {best_overall} - Matrix{best_coord}")
 print(f" Matrix-Wert: {best_data['matrix_value']}")
 print(f" Vorhergesagter Char: {best_formula_data['char']}")
 print(f" Accuracy: {best_accuracy:.2f}%")
 print(f" Count: {best_formula_data['count']}/{analysis['total']}")
 print()
 
 # Erwartet bei Zufall
 if unique == 8:
 expected_random = analysis['total'] / 8
 elif unique == 4:
 expected_random = analysis['total'] / 4
 else:
 expected_random = analysis['total'] / 26
 
 ratio = best_formula_data['count'] / expected_random if expected_random > 0 else 0
 print(f" Erwartet bei Zufall: {expected_random:.1f}")
 print(f" Ratio: {ratio:.2f}x")
 print()
 else:
 print(f" ⚠️ Keine gute Transformation gefunden")
 print()
 
 # Speichere Ergebnisse
 OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
 
 output_data = {
 "timestamp": datetime.now().isoformat(),
 "positions_analyzed": positions,
 "results": all_results
 }
 
 output_file = OUTPUT_DIR / "transformation_other_positions.json"
 with output_file.open("w") as f:
 json.dump(output_data, f, indent=2)
 print(f"💾 Ergebnisse gespeichert: {output_file}")
 print()
 
 print("=" * 80)
 print("✅ ANALYSE ABGESCHLOSSEN")
 print("=" * 80)

if __name__ == "__main__":
 main()

