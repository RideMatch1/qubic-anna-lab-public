#!/usr/bin/env python3
"""
Matrix Spalte 13 Tiefgründige Analyse
- Alle Block-Ende-Positionen verwenden Spalte 13
- Finde Patterns in Spalte 13
- Verbinde mit Grid Spalte 6
- KEINE Halluzinationen - nur echte Daten!
"""

import json
import sys
from pathlib import Path
from typing import Dict, List, Tuple
from collections import Counter, defaultdict
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

def analyze_column13(matrix: np.ndarray) -> Dict:
 """Analyze Matrix Spalte 13 vollständig."""
 
 col = 13
 column_values = [int(matrix[row, col]) for row in range(128)]
 
 # Statistiken
 stats = {
 "mean": float(np.mean(column_values)),
 "median": float(np.median(column_values)),
 "std": float(np.std(column_values)),
 "min": int(np.min(column_values)),
 "max": int(np.max(column_values)),
 "zeros": sum(1 for v in column_values if v == 0),
 "unique_values": len(set(column_values))
 }
 
 # Value Distribution
 value_dist = Counter(column_values)
 
 # Mod_26 Distribution
 mod26_dist = Counter(int(v % 26) for v in column_values)
 
 # Mod_4 Distribution
 mod4_dist = Counter(int(v % 4) for v in column_values)
 
 # Block-Ende-Positionen in Spalte 13
 block_end_positions = [13, 27, 41, 55]
 block_end_values = {}
 
 for pos in block_end_positions:
 # Direkte Koordinate
 direct_value = int(matrix[pos, col])
 # Symmetric Koordinate
 symmetric_row = 128 - pos
 symmetric_value = int(matrix[symmetric_row, col]) if 0 <= symmetric_row < 128 else None
 
 block_end_values[f"position_{pos}"] = {
 "position": pos,
 "direct_coord": (pos, col),
 "direct_value": direct_value,
 "direct_mod26": int(direct_value % 26),
 "direct_mod4": int(direct_value % 4),
 "symmetric_coord": (symmetric_row, col) if symmetric_value is not None else None,
 "symmetric_value": symmetric_value,
 "symmetric_mod26": int(symmetric_value % 26) if symmetric_value is not None else None,
 "symmetric_mod4": int(symmetric_value % 4) if symmetric_value is not None else None
 }
 
 return {
 "column": col,
 "stats": stats,
 "value_distribution": dict(value_dist.most_common(20)),
 "mod26_distribution": dict(mod26_dist),
 "mod4_distribution": dict(mod4_dist),
 "block_end_values": block_end_values
 }

def analyze_column13_patterns(matrix: np.ndarray, layer3_data: List[Dict]) -> Dict:
 """Analyze Patterns in Spalte 13 im context von Identities."""
 
 col = 13
 block_end_positions = [13, 27, 41, 55]
 
 # Analyze welche Matrix-Werte zu welchen Characters führen
 position_analysis = {}
 
 for pos in block_end_positions:
 # Direkte und Symmetric Koordinaten
 direct_row = pos
 symmetric_row = 128 - pos
 
 direct_value = int(matrix[direct_row, col])
 symmetric_value = int(matrix[symmetric_row, col]) if 0 <= symmetric_row < 128 else None
 
 # Sammle Characters an dieser Position
 chars = Counter()
 for entry in layer3_data:
 l3_id = entry.get("layer3_identity", "")
 if l3_id and len(l3_id) > pos:
 chars[l3_id[pos].upper()] += 1
 
 # Teste verschiedene Transformationen
 transformations = {}
 
 # Direkte Transformationen
 for name, func in [
 ("direct_mod26", lambda v: int(v % 26)),
 ("direct_mod4", lambda v: int(v % 4)),
 ("direct_abs_mod26", lambda v: int(abs(v) % 26)),
 ("direct_abs_mod4", lambda v: int(abs(v) % 4))
 ]:
 try:
 result = func(direct_value)
 char = chr(ord('A') + result)
 count = chars.get(char, 0)
 total = sum(chars.values())
 accuracy = (count / total * 100) if total > 0 else 0
 
 transformations[name] = {
 "value": direct_value,
 "result": result,
 "char": char,
 "count": count,
 "accuracy": accuracy
 }
 except:
 pass
 
 # Symmetric Transformationen
 if symmetric_value is not None:
 for name, func in [
 ("symmetric_mod26", lambda v: int(v % 26)),
 ("symmetric_mod4", lambda v: int(v % 4)),
 ("symmetric_abs_mod26", lambda v: int(abs(v) % 26)),
 ("symmetric_abs_mod4", lambda v: int(abs(v) % 4))
 ]:
 try:
 result = func(symmetric_value)
 char = chr(ord('A') + result)
 count = chars.get(char, 0)
 total = sum(chars.values())
 accuracy = (count / total * 100) if total > 0 else 0
 
 transformations[name] = {
 "value": symmetric_value,
 "result": result,
 "char": char,
 "count": count,
 "accuracy": accuracy
 }
 except:
 pass
 
 # Finde beste Transformation
 best_transformation = None
 best_accuracy = 0
 
 for name, trans_data in transformations.items():
 if trans_data.get("accuracy", 0) > best_accuracy:
 best_accuracy = trans_data["accuracy"]
 best_transformation = name
 
 position_analysis[f"position_{pos}"] = {
 "position": pos,
 "direct_coord": (direct_row, col),
 "symmetric_coord": (symmetric_row, col) if symmetric_value is not None else None,
 "char_distribution": dict(chars.most_common(10)),
 "unique_chars": len(chars),
 "transformations": transformations,
 "best_transformation": best_transformation,
 "best_accuracy": best_accuracy
 }
 
 return position_analysis

def analyze_column13_grid_connection(matrix: np.ndarray) -> Dict:
 """Analyze Verbindung zwischen Matrix Spalte 13 und Grid Spalte 6."""
 
 col = 13
 
 # Grid Spalte 6 Hypothese
 # Alle Block-Ende-Positionen sind in Grid Spalte 6
 # Position 27: Grid(3, 6) ↔ Matrix(27, 13)
 
 block_end_positions = [13, 27, 41, 55]
 
 grid_connection = {}
 
 for pos in block_end_positions:
 # Grid-Koordinate
 grid_index = pos % 49
 grid_row = grid_index // 7
 grid_col = grid_index % 7
 
 # Matrix-Koordinaten
 direct_coord = (pos, col)
 symmetric_coord = (128 - pos, col)
 
 direct_value = int(matrix[pos, col])
 symmetric_value = int(matrix[128 - pos, col]) if 0 <= (128 - pos) < 128 else None
 
 grid_connection[f"position_{pos}"] = {
 "position": pos,
 "grid_coord": (grid_row, grid_col),
 "grid_col": grid_col,
 "in_grid_column6": grid_col == 6,
 "matrix_direct": {
 "coord": direct_coord,
 "value": direct_value
 },
 "matrix_symmetric": {
 "coord": symmetric_coord,
 "value": symmetric_value
 } if symmetric_value is not None else None
 }
 
 # Check ob alle in Grid Spalte 6
 all_in_column6 = all(
 grid_connection[f"position_{pos}"]["in_grid_column6"]
 for pos in block_end_positions
 )
 
 return {
 "grid_column6_hypothesis": "Grid Spalte 6 ↔ Matrix Spalte 13",
 "block_end_positions": grid_connection,
 "all_in_grid_column6": all_in_column6,
 "matrix_column": col
 }

def main():
 """Hauptfunktion."""
 
 print("=" * 80)
 print("MATRIX SPALTE 13 TIEFGRÜNDIGE ANALYSE")
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
 
 # 2. Analyze Spalte 13
 print("🔍 Analyze Matrix Spalte 13...")
 col13_analysis = analyze_column13(matrix)
 stats = col13_analysis["stats"]
 print(f"✅ Spalte 13 analysiert")
 print()
 
 print("📊 Statistiken:")
 print(f" Mean: {stats['mean']:.2f}")
 print(f" Median: {stats['median']:.2f}")
 print(f" Std: {stats['std']:.2f}")
 print(f" Min: {stats['min']}, Max: {stats['max']}")
 print(f" Zeros: {stats['zeros']}")
 print(f" Unique Values: {stats['unique_values']}")
 print()
 
 # 3. Block-Ende-Positionen in Spalte 13
 print("📊 Block-Ende-Positionen in Spalte 13:")
 for pos_key, pos_data in col13_analysis["block_end_values"].items():
 pos = pos_data["position"]
 direct = pos_data["direct_value"]
 direct_mod26 = pos_data["direct_mod26"]
 direct_mod4 = pos_data["direct_mod4"]
 symmetric = pos_data.get("symmetric_value")
 
 print(f" Position {pos}:")
 print(f" Direkt: Matrix({pos},13) = {direct} (mod_26={direct_mod26}, mod_4={direct_mod4})")
 if symmetric is not None:
 sym_mod26 = pos_data["symmetric_mod26"]
 sym_mod4 = pos_data["symmetric_mod4"]
 print(f" Symmetric: Matrix({128-pos},13) = {symmetric} (mod_26={sym_mod26}, mod_4={sym_mod4})")
 print()
 
 # 4. Analyze Patterns mit Identities
 print("🔍 Analyze Patterns mit Identities...")
 if LAYER3_FILE.exists():
 with LAYER3_FILE.open() as f:
 layer3_data = json.load(f)
 layer3_results = layer3_data.get("results", [])
 
 patterns = analyze_column13_patterns(matrix, layer3_results)
 print(f"✅ Patterns analysiert")
 print()
 
 print("📊 Beste Transformationen pro Position:")
 for pos_key, pos_analysis in patterns.items():
 pos = pos_analysis["position"]
 best = pos_analysis["best_transformation"]
 accuracy = pos_analysis["best_accuracy"]
 if best:
 best_data = pos_analysis["transformations"][best]
 char = best_data["char"]
 print(f" Position {pos}: {best} → {char} ({accuracy:.2f}%)")
 else:
 print("⚠️ Layer-3 Daten nicht gefunden")
 patterns = {}
 print()
 
 # 5. Analyze Grid-Verbindung
 print("🔍 Analyze Grid-Verbindung...")
 grid_connection = analyze_column13_grid_connection(matrix)
 print(f"✅ Grid-Verbindung analysiert")
 print()
 
 print("📊 Grid ↔ Matrix Verbindung:")
 print(f" Hypothese: {grid_connection['grid_column6_hypothesis']}")
 print(f" Alle in Grid Spalte 6: {'✅ JA' if grid_connection['all_in_grid_column6'] else '❌ NEIN'}")
 print()
 
 for pos_key, pos_data in grid_connection["block_end_positions"].items():
 pos = pos_data["position"]
 grid_coord = pos_data["grid_coord"]
 in_col6 = "✅" if pos_data["in_grid_column6"] else "❌"
 direct = pos_data["matrix_direct"]
 print(f" {in_col6} Position {pos}: Grid{grid_coord} ↔ Matrix{direct['coord']} = {direct['value']}")
 print()
 
 # Speichere Ergebnisse
 OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
 
 output_data = {
 "timestamp": datetime.now().isoformat(),
 "column13_analysis": col13_analysis,
 "patterns_analysis": patterns,
 "grid_connection": grid_connection
 }
 
 output_file = OUTPUT_DIR / "matrix_column13_analysis.json"
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
 print(f" Matrix Spalte 13: {stats['unique_values']} unique values")
 print(f" Mean: {stats['mean']:.2f}, Std: {stats['std']:.2f}")
 print(f" Zeros: {stats['zeros']}")
 print(f" Alle Block-Ende in Grid Spalte 6: {'✅' if grid_connection['all_in_grid_column6'] else '❌'}")
 print()

if __name__ == "__main__":
 main()

