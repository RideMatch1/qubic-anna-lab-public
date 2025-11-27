#!/usr/bin/env python3
"""
Validate Mapping-Formel auf allen Positionen
- Teste Spalte-Mapping for alle Grid Spalten
- Teste Row-Mapping for alle Positionen
- Check ob Formel allgemein gilt
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

def get_grid_coord(position: int) -> Tuple[int, int]:
 """Berechne Grid-Koordinate for Position."""
 grid_index = position % 49
 grid_row = grid_index // 7
 grid_col = grid_index % 7
 return (grid_row, grid_col)

def calculate_matrix_coord(position: int, grid_col: int) -> Tuple[int, int]:
 """Berechne Matrix-Koordinate basierend auf Mapping-Formel."""
 
 # Spalte-Mapping: Grid Col + 7 = Matrix Col
 matrix_col = grid_col + 7
 
 # Row-Mapping:
 # Position 27: direkt
 # Andere: symmetric (128 - position)
 if position == 27:
 matrix_row = position # Direkt
 else:
 matrix_row = 128 - position # Symmetric
 
 return (matrix_row, matrix_col)

def validate_mapping_all_positions(matrix: np.ndarray, layer3_data: List[Dict]) -> Dict:
 """Validate Mapping-Formel auf allen Positionen."""
 
 results = {}
 
 # Teste alle Positionen 0-59
 for pos in range(60):
 grid_row, grid_col = get_grid_coord(pos)
 matrix_row, matrix_col = calculate_matrix_coord(pos, grid_col)
 
 # Check ob Koordinate gültig ist
 if not (0 <= matrix_row < 128 and 0 <= matrix_col < 128):
 results[f"position_{pos}"] = {
 "position": pos,
 "grid_coord": (grid_row, grid_col),
 "matrix_coord": (matrix_row, matrix_col),
 "valid_coord": False,
 "error": "Out of bounds"
 }
 continue
 
 # Hole Matrix-Wert
 matrix_value = matrix[matrix_row, matrix_col]
 
 # Berechne erwartete Characters
 mod_26_char = chr(ord('A') + (int(matrix_value) % 26))
 mod_4_char = chr(ord('A') + (int(matrix_value) % 4))
 
 # Analyze tatsächliche Characters an dieser Position
 chars = Counter()
 for entry in layer3_data:
 l3_id = entry.get("layer3_identity", "")
 if l3_id and len(l3_id) > pos:
 chars[l3_id[pos].upper()] += 1
 
 total = sum(chars.values())
 if total == 0:
 continue
 
 # Check Accuracy
 mod_26_count = chars.get(mod_26_char, 0)
 mod_4_count = chars.get(mod_4_char, 0)
 
 mod_26_accuracy = (mod_26_count / total) * 100 if total > 0 else 0
 mod_4_accuracy = (mod_4_count / total) * 100 if total > 0 else 0
 
 # Erwartete Accuracy bei Zufall
 expected_mod_26 = (1 / 26) * 100 # ~3.85%
 expected_mod_4 = (1 / 4) * 100 # 25%
 
 results[f"position_{pos}"] = {
 "position": pos,
 "grid_coord": (grid_row, grid_col),
 "matrix_coord": (matrix_row, matrix_col),
 "matrix_value": float(matrix_value),
 "mod_26_char": mod_26_char,
 "mod_4_char": mod_4_char,
 "mod_26_accuracy": mod_26_accuracy,
 "mod_4_accuracy": mod_4_accuracy,
 "expected_mod_26": expected_mod_26,
 "expected_mod_4": expected_mod_4,
 "mod_26_ratio": mod_26_accuracy / expected_mod_26 if expected_mod_26 > 0 else 0,
 "mod_4_ratio": mod_4_accuracy / expected_mod_4 if expected_mod_4 > 0 else 0,
 "total_identities": total,
 "unique_chars": len(chars),
 "top_chars": dict(chars.most_common(5))
 }
 
 return results

def analyze_validation_results(results: Dict) -> Dict:
 """Analyze Validierungs-Ergebnisse."""
 
 # Filtere gültige Ergebnisse
 valid_results = {
 k: v for k, v in results.items()
 if v.get("valid_coord", True) and v.get("total_identities", 0) > 0
 }
 
 # Analyze Mod_26 Accuracy
 mod_26_accuracies = [
 v["mod_26_accuracy"] for v in valid_results.values()
 ]
 mod_26_ratios = [
 v["mod_26_ratio"] for v in valid_results.values()
 ]
 
 # Analyze Mod_4 Accuracy
 mod_4_accuracies = [
 v["mod_4_accuracy"] for v in valid_results.values()
 ]
 mod_4_ratios = [
 v["mod_4_ratio"] for v in valid_results.values()
 ]
 
 # Finde beste Positionen
 best_mod_26 = sorted(
 valid_results.items(),
 key=lambda x: x[1].get("mod_26_ratio", 0),
 reverse=True
 )[:10]
 
 best_mod_4 = sorted(
 valid_results.items(),
 key=lambda x: x[1].get("mod_4_ratio", 0),
 reverse=True
 )[:10]
 
 return {
 "total_positions": len(valid_results),
 "mod_26_stats": {
 "mean_accuracy": np.mean(mod_26_accuracies) if mod_26_accuracies else 0,
 "mean_ratio": np.mean(mod_26_ratios) if mod_26_ratios else 0,
 "max_accuracy": max(mod_26_accuracies) if mod_26_accuracies else 0,
 "max_ratio": max(mod_26_ratios) if mod_26_ratios else 0
 },
 "mod_4_stats": {
 "mean_accuracy": np.mean(mod_4_accuracies) if mod_4_accuracies else 0,
 "mean_ratio": np.mean(mod_4_ratios) if mod_4_ratios else 0,
 "max_accuracy": max(mod_4_accuracies) if mod_4_accuracies else 0,
 "max_ratio": max(mod_4_ratios) if mod_4_ratios else 0
 },
 "best_mod_26": [
 {
 "position": v["position"],
 "accuracy": v["mod_26_accuracy"],
 "ratio": v["mod_26_ratio"]
 }
 for k, v in best_mod_26
 ],
 "best_mod_4": [
 {
 "position": v["position"],
 "accuracy": v["mod_4_accuracy"],
 "ratio": v["mod_4_ratio"]
 }
 for k, v in best_mod_4
 ]
 }

def main():
 """Hauptfunktion."""
 
 print("=" * 80)
 print("VALIDIERUNG MAPPING-FORMEL AUF ALLEN POSITIONEN")
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
 
 # 3. Validate Mapping auf allen Positionen
 print("🔍 Validate Mapping auf allen Positionen...")
 results = validate_mapping_all_positions(matrix, layer3_results)
 print(f"✅ {len(results)} Positionen validiert")
 print()
 
 # 4. Analyze Ergebnisse
 print("🔍 Analyze Ergebnisse...")
 analysis = analyze_validation_results(results)
 print(f"✅ Analyse abgeschlossen")
 print()
 
 print("📊 STATISTIKEN:")
 print()
 print(" Mod_26 Transformation:")
 print(f" Mean Accuracy: {analysis['mod_26_stats']['mean_accuracy']:.2f}%")
 print(f" Mean Ratio: {analysis['mod_26_stats']['mean_ratio']:.2f}x")
 print(f" Max Accuracy: {analysis['mod_26_stats']['max_accuracy']:.2f}%")
 print(f" Max Ratio: {analysis['mod_26_stats']['max_ratio']:.2f}x")
 print()
 print(" Mod_4 Transformation:")
 print(f" Mean Accuracy: {analysis['mod_4_stats']['mean_accuracy']:.2f}%")
 print(f" Mean Ratio: {analysis['mod_4_stats']['mean_ratio']:.2f}x")
 print(f" Max Accuracy: {analysis['mod_4_stats']['max_accuracy']:.2f}%")
 print(f" Max Ratio: {analysis['mod_4_stats']['max_ratio']:.2f}x")
 print()
 
 print("📊 BESTE POSITIONEN (Mod_26):")
 for i, pos_data in enumerate(analysis["best_mod_26"][:5], 1):
 marker = "⭐" if pos_data["position"] == 27 else " "
 print(f" {marker} {i}. Position {pos_data['position']}: {pos_data['accuracy']:.2f}% ({pos_data['ratio']:.2f}x)")
 print()
 
 print("📊 BESTE POSITIONEN (Mod_4):")
 for i, pos_data in enumerate(analysis["best_mod_4"][:5], 1):
 marker = "⭐" if pos_data["position"] == 27 else " "
 print(f" {marker} {i}. Position {pos_data['position']}: {pos_data['accuracy']:.2f}% ({pos_data['ratio']:.2f}x)")
 print()
 
 # Speichere Ergebnisse
 OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
 
 # Konvertiere numpy-Typen zu Python-native Typen
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
 "results": convert_numpy(results),
 "analysis": convert_numpy(analysis),
 "conclusion": {
 "mapping_formula_valid": bool(analysis["mod_26_stats"]["mean_ratio"] > 1.0 or analysis["mod_4_stats"]["mean_ratio"] > 1.0),
 "best_transformation": "mod_4" if analysis["mod_4_stats"]["mean_ratio"] > analysis["mod_26_stats"]["mean_ratio"] else "mod_26"
 }
 }
 
 output_file = OUTPUT_DIR / "mapping_validation_all_positions.json"
 with output_file.open("w") as f:
 json.dump(output_data, f, indent=2)
 print(f"💾 Ergebnisse gespeichert: {output_file}")
 print()
 
 print("=" * 80)
 print("✅ VALIDIERUNG ABGESCHLOSSEN")
 print("=" * 80)
 print()
 print("📊 ZUSAMMENFASSUNG:")
 print()
 if analysis["mod_26_stats"]["mean_ratio"] > 1.0:
 print(f" ✅ Mod_26: {analysis['mod_26_stats']['mean_ratio']:.2f}x above random")
 else:
 print(f" ⚠️ Mod_26: {analysis['mod_26_stats']['mean_ratio']:.2f}x (nicht besser als Zufall)")
 
 if analysis["mod_4_stats"]["mean_ratio"] > 1.0:
 print(f" ✅ Mod_4: {analysis['mod_4_stats']['mean_ratio']:.2f}x above random")
 else:
 print(f" ⚠️ Mod_4: {analysis['mod_4_stats']['mean_ratio']:.2f}x (nicht besser als Zufall)")
 print()

if __name__ == "__main__":
 main()

