#!/usr/bin/env python3
"""
Transformation-Mechanismus entschlüsseln
- Analyze wie Matrix → Identity Transformation funktioniert
- Teste verschiedene Transformationen (mod_26, mod_4, komplex)
- Validate for alle Positionen
- Finde die echte Formel
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

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# Paths
LAYER3_FILE = project_root / "outputs" / "derived" / "layer3_derivation_23k_complete.json"
MATRIX_FILE = project_root / "data" / "anna-matrix" / "Anna_Matrix.xlsx"
MATRIX_COORD = project_root / "outputs" / "derived" / "matrix_coordinate_analysis.json"
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

def get_identity_extraction_coordinates() -> Dict:
 """Load Identity-Extraktions-Koordinaten."""
 if not MATRIX_COORD.exists():
 return {}
 
 with MATRIX_COORD.open() as f:
 data = json.load(f)
 
 return data

def test_transformation_formulas(matrix: np.ndarray, coord: Tuple[int, int], actual_char: str) -> Dict:
 """Teste verschiedene Transformation-Formeln."""
 
 row, col = coord
 if not (0 <= row < 128 and 0 <= col < 128):
 return {}
 
 value = int(matrix[row, col])
 actual_char_val = ord(actual_char.upper()) - ord('A')
 
 formulas = {}
 
 # Formel 1: mod_26 (Standard)
 formulas["mod_26"] = {
 "formula": "value % 26",
 "result": int(value % 26),
 "char": chr(ord('A') + int(value % 26)),
 "matches": int(value % 26) == actual_char_val
 }
 
 # Formel 2: mod_4
 formulas["mod_4"] = {
 "formula": "value % 4",
 "result": int(value % 4),
 "char": chr(ord('A') + int(value % 4)),
 "matches": int(value % 4) == actual_char_val
 }
 
 # Formel 3: abs(value) % 26
 formulas["abs_mod_26"] = {
 "formula": "abs(value) % 26",
 "result": int(abs(value) % 26),
 "char": chr(ord('A') + int(abs(value) % 26)),
 "matches": int(abs(value) % 26) == actual_char_val
 }
 
 # Formel 4: abs(value) % 4
 formulas["abs_mod_4"] = {
 "formula": "abs(value) % 4",
 "result": int(abs(value) % 4),
 "char": chr(ord('A') + int(abs(value) % 4)),
 "matches": int(abs(value) % 4) == actual_char_val
 }
 
 # Formel 5: (value + 26) % 26 (for negative Werte)
 formulas["normalized_mod_26"] = {
 "formula": "(value + 26) % 26",
 "result": int((value + 26) % 26),
 "char": chr(ord('A') + int((value + 26) % 26)),
 "matches": int((value + 26) % 26) == actual_char_val
 }
 
 # Formel 6: (value + 4) % 4
 formulas["normalized_mod_4"] = {
 "formula": "(value + 4) % 4",
 "result": int((value + 4) % 4),
 "char": chr(ord('A') + int((value + 4) % 4)),
 "matches": int((value + 4) % 4) == actual_char_val
 }
 
 # Formel 7: value // 14 % 26 (Block-basiert)
 formulas["block_mod_26"] = {
 "formula": "value // 14 % 26",
 "result": int((value // 14) % 26) if value != 0 else 0,
 "char": chr(ord('A') + int((value // 14) % 26)) if value != 0 else 'A',
 "matches": (int((value // 14) % 26) if value != 0 else 0) == actual_char_val
 }
 
 # Formel 8: value // 14 % 4
 formulas["block_mod_4"] = {
 "formula": "value // 14 % 4",
 "result": int((value // 14) % 4) if value != 0 else 0,
 "char": chr(ord('A') + int((value // 14) % 4)) if value != 0 else 'A',
 "matches": (int((value // 14) % 4) if value != 0 else 0) == actual_char_val
 }
 
 return formulas

def analyze_transformation_for_position(position: int, layer3_data: List[Dict], matrix: np.ndarray, extraction_coords: Dict) -> Dict:
 """Analyze Transformation for eine spezifische Position."""
 
 block = position // 14
 pos_in_block = position % 14
 
 # Sammle alle Characters an dieser Position
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
 (128 - position, pos_in_block, "symmetric")
 ]
 
 # Teste Transformationen for jede Koordinate
 transformation_results = {}
 
 for row, col, name in possible_coords:
 if not (0 <= row < 128 and 0 <= col < 128):
 continue
 
 coord = (row, col)
 matrix_value = int(matrix[row, col])
 
 # Teste alle Formeln
 formulas = {}
 for char, count in chars.most_common(5): # Top 5 Characters
 char_formulas = test_transformation_formulas(matrix, coord, char)
 for formula_name, formula_result in char_formulas.items():
 if formula_result["matches"]:
 if formula_name not in formulas:
 formulas[formula_name] = {
 "formula": formula_result["formula"],
 "matrix_coord": coord,
 "matrix_value": matrix_value,
 "matches": [],
 "match_count": 0,
 "match_percentage": 0
 }
 formulas[formula_name]["matches"].append({
 "char": char,
 "count": count,
 "percentage": (count / total * 100) if total > 0 else 0
 })
 formulas[formula_name]["match_count"] += count
 
 # Berechne Match-Percentage for jede Formel
 for formula_name, formula_data in formulas.items():
 formula_data["match_percentage"] = (formula_data["match_count"] / total * 100) if total > 0 else 0
 
 transformation_results[name] = {
 "coord": coord,
 "matrix_value": matrix_value,
 "formulas": formulas
 }
 
 return {
 "position": position,
 "block": block,
 "pos_in_block": pos_in_block,
 "total_identities": total,
 "unique_chars": unique_chars,
 "char_distribution": dict(chars.most_common(10)),
 "transformation_results": transformation_results
 }

def analyze_all_block_end_positions(layer3_data: List[Dict], matrix: np.ndarray, extraction_coords: Dict) -> Dict:
 """Analyze Transformation for alle Block-Ende-Positionen."""
 
 block_end_positions = [13, 27, 41, 55]
 results = {}
 
 for pos in block_end_positions:
 print(f" Analyze Position {pos}...")
 analysis = analyze_transformation_for_position(pos, layer3_data, matrix, extraction_coords)
 results[f"position_{pos}"] = analysis
 
 return results

def find_best_transformation_formula(all_results: Dict) -> Dict:
 """Finde die beste Transformation-Formel above alle Positionen."""
 
 formula_scores = defaultdict(lambda: {"matches": 0, "total": 0, "positions": []})
 
 for pos_key, analysis in all_results.items():
 for coord_name, coord_data in analysis.get("transformation_results", {}).items():
 for formula_name, formula_data in coord_data.get("formulas", {}).items():
 match_count = formula_data.get("match_count", 0)
 total = analysis.get("total_identities", 0)
 
 formula_scores[formula_name]["matches"] += match_count
 formula_scores[formula_name]["total"] += total
 formula_scores[formula_name]["positions"].append({
 "position": analysis.get("position"),
 "coord": coord_name,
 "match_count": match_count,
 "match_percentage": formula_data.get("match_percentage", 0)
 })
 
 # Berechne Gesamt-Score for jede Formel
 formula_rankings = []
 for formula_name, score_data in formula_scores.items():
 total_matches = score_data["matches"]
 total_identities = score_data["total"]
 overall_percentage = (total_matches / total_identities * 100) if total_identities > 0 else 0
 
 formula_rankings.append({
 "formula": formula_name,
 "overall_percentage": overall_percentage,
 "total_matches": total_matches,
 "total_identities": total_identities,
 "positions_analyzed": len(score_data["positions"])
 })
 
 # Sortiere nach Gesamt-Percentage
 formula_rankings.sort(key=lambda x: x["overall_percentage"], reverse=True)
 
 return {
 "rankings": formula_rankings,
 "best_formula": formula_rankings[0] if formula_rankings else None
 }

def main():
 """Hauptfunktion."""
 
 print("=" * 80)
 print("TRANSFORMATION-MECHANISMUS ENTSCHLÜSSELN")
 print("=" * 80)
 print()
 print("⚠️ KEINE HALLUZINATIONEN - NUR ECHTE DATEN!")
 print("🔬 PROFESSOREN-TEAM: SYSTEMATISCH, KRITISCH, PERFEKT")
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
 print(f"✅ {len(layer3_results)} Layer-3 Identities geloadn")
 print()
 
 # 3. Load Extraktions-Koordinaten
 print("📂 Load Extraktions-Koordinaten...")
 extraction_coords = get_identity_extraction_coordinates()
 if extraction_coords:
 print(f"✅ {len(extraction_coords.get('diagonal_coordinates', []))} Koordinaten geloadn")
 else:
 print("⚠️ Keine Extraktions-Koordinaten gefunden")
 print()
 
 # 4. Analyze alle Block-Ende-Positionen
 print("🔍 Analyze Transformation for Block-Ende-Positionen...")
 block_end_results = analyze_all_block_end_positions(layer3_results, matrix, extraction_coords)
 print(f"✅ {len(block_end_results)} Positionen analysiert")
 print()
 
 # 5. Zeige Ergebnisse for jede Position
 print("=" * 80)
 print("ERGEBNISSE PRO POSITION")
 print("=" * 80)
 print()
 
 for pos_key, analysis in block_end_results.items():
 pos = analysis["position"]
 unique = analysis["unique_chars"]
 print(f"📊 Position {pos}:")
 print(f" Unique Characters: {unique}")
 print(f" Top Characters: {list(analysis['char_distribution'].keys())[:5]}")
 
 # Zeige beste Transformation for diese Position
 best_formula = None
 best_percentage = 0
 
 for coord_name, coord_data in analysis.get("transformation_results", {}).items():
 for formula_name, formula_data in coord_data.get("formulas", {}).items():
 pct = formula_data.get("match_percentage", 0)
 if pct > best_percentage:
 best_percentage = pct
 best_formula = {
 "formula": formula_name,
 "coord": coord_name,
 "matrix_coord": formula_data["matrix_coord"],
 "percentage": pct
 }
 
 if best_formula:
 coord = best_formula["matrix_coord"]
 print(f" Beste Transformation: {best_formula['formula']}")
 print(f" Matrix({coord[0]},{coord[1]}), Match: {best_percentage:.2f}%")
 print()
 
 # 6. Finde beste Formel above alle Positionen
 print("=" * 80)
 print("BESTE TRANSFORMATION-FORMEL (ÜBER ALLE POSITIONEN)")
 print("=" * 80)
 print()
 
 formula_analysis = find_best_transformation_formula(block_end_results)
 
 print("📊 Formel-Rankings:")
 for i, ranking in enumerate(formula_analysis["rankings"][:10], 1):
 print(f" {i}. {ranking['formula']}: {ranking['overall_percentage']:.2f}% ({ranking['total_matches']}/{ranking['total_identities']})")
 print()
 
 if formula_analysis["best_formula"]:
 best = formula_analysis["best_formula"]
 print(f"✅ Beste Formel: {best['formula']}")
 print(f" Gesamt-Match: {best['overall_percentage']:.2f}%")
 print(f" Positionen analysiert: {best['positions_analyzed']}")
 print()
 
 # Speichere Ergebnisse
 OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
 
 output_data = {
 "timestamp": datetime.now().isoformat(),
 "block_end_positions_analysis": block_end_results,
 "formula_rankings": formula_analysis,
 "conclusion": {
 "best_formula": formula_analysis["best_formula"]["formula"] if formula_analysis["best_formula"] else "UNKNOWN",
 "best_percentage": formula_analysis["best_formula"]["overall_percentage"] if formula_analysis["best_formula"] else 0
 }
 }
 
 output_file = OUTPUT_DIR / "transformation_mechanism_deciphered.json"
 with output_file.open("w") as f:
 json.dump(output_data, f, indent=2)
 print(f"💾 Ergebnisse gespeichert: {output_file}")
 
 print()
 print("=" * 80)
 print("✅ ANALYSE ABGESCHLOSSEN")
 print("=" * 80)

if __name__ == "__main__":
 main()

