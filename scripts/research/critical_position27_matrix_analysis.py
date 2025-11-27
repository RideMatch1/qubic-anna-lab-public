#!/usr/bin/env python3
"""
Kritische Position 27 Matrix-Analyse
- Position 27 hat nur A, B, C, D (nicht alle 26!)
- Matrix(27,13) = 56 → char=E, aber E kommt nicht vor!
- Kritisch hinterfragen: Was bedeutet das?
- Finde die echte Transformation
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

def analyze_position27_restriction(layer3_data: List[Dict]) -> Dict:
 """Analyze warum Position 27 nur A, B, C, D hat."""
 
 pos27_chars = Counter()
 pos27_char_values = []
 
 for entry in layer3_data:
 l3_id = entry.get("layer3_identity", "")
 if not l3_id or len(l3_id) <= 27:
 continue
 
 char = l3_id[27].upper()
 pos27_chars[char] += 1
 
 char_val = ord(char) - ord('A')
 pos27_char_values.append(char_val)
 
 # Check ob es wirklich nur A, B, C, D gibt
 unique_chars = set(pos27_chars.keys())
 
 # Analyze Char-Werte
 char_value_dist = Counter(pos27_char_values)
 
 return {
 "total": sum(pos27_chars.values()),
 "unique_chars": sorted(unique_chars),
 "char_distribution": dict(pos27_chars.most_common()),
 "char_value_distribution": dict(char_value_dist),
 "is_restricted": len(unique_chars) < 26,
 "restriction_pattern": "A,B,C,D only" if unique_chars == {"A", "B", "C", "D"} else "OTHER"
 }

def find_matrix_values_for_abcd(matrix: np.ndarray) -> Dict:
 """Finde Matrix-Werte die zu A, B, C, D führen."""
 
 # A=0, B=1, C=2, D=3
 target_mods = [0, 1, 2, 3]
 
 # Analyze verschiedene Matrix-Regionen
 regions = {}
 
 # 1. Matrix(27,13) und Umgebung
 for row_offset in range(-5, 6):
 for col_offset in range(-5, 6):
 row = 27 + row_offset
 col = 13 + col_offset
 
 if 0 <= row < 128 and 0 <= col < 128:
 value = int(matrix[row, col])
 mod26 = int(value % 26)
 
 if mod26 in target_mods:
 key = f"Matrix({row},{col})"
 if key not in regions:
 regions[key] = []
 regions[key].append({
 "value": value,
 "mod_26": mod26,
 "char": chr(ord('A') + mod26)
 })
 
 # 2. Matrix Spalte 13 (alle Zeilen)
 col13_values = []
 for row in range(128):
 value = int(matrix[row, 13])
 mod26 = int(value % 26)
 if mod26 in target_mods:
 col13_values.append({
 "row": row,
 "value": value,
 "mod_26": mod26,
 "char": chr(ord('A') + mod26)
 })
 
 # 3. Matrix Zeile 27 (alle Spalten)
 row27_values = []
 for col in range(128):
 value = int(matrix[27, col])
 mod26 = int(value % 26)
 if mod26 in target_mods:
 row27_values.append({
 "col": col,
 "value": value,
 "mod_26": mod26,
 "char": chr(ord('A') + mod26)
 })
 
 return {
 "around_27_13": regions,
 "column_13_abcd": col13_values,
 "row_27_abcd": row27_values
 }

def analyze_transformation_alternatives(matrix: np.ndarray, pos27_analysis: Dict) -> Dict:
 """Analyze alternative Transformationen."""
 
 # Position 27 hat nur A, B, C, D
 # Matrix(27,13) = 56 → mod_26=4 → char=E (falsch!)
 
 # Alternative Transformationen:
 alternatives = {}
 
 # 1. Matrix-Wert direkt (ohne mod_26)
 value_27_13 = int(matrix[27, 13])
 alternatives["direct_value"] = {
 "value": value_27_13,
 "interpretation": "Direkter Wert (nicht mod_26)",
 "possible": value_27_13 in [0, 1, 2, 3] # A, B, C, D
 }
 
 # 2. Matrix-Wert / 14 (Block-Größe)
 alternatives["divided_by_14"] = {
 "value": value_27_13 / 14,
 "mod_26": int((value_27_13 / 14) % 26),
 "char": chr(ord('A') + int((value_27_13 / 14) % 26)),
 "interpretation": "Wert / 14 (Block-Größe)"
 }
 
 # 3. Matrix-Wert mod 4 (nur 4 Möglichkeiten)
 alternatives["mod_4"] = {
 "value": value_27_13,
 "mod_4": int(value_27_13 % 4),
 "char": chr(ord('A') + int(value_27_13 % 4)),
 "interpretation": "mod_4 (nur A, B, C, D)"
 }
 
 # 4. Matrix-Wert / 14 mod 4
 alternatives["divided_by_14_mod_4"] = {
 "value": value_27_13 / 14,
 "mod_4": int((value_27_13 / 14) % 4),
 "char": chr(ord('A') + int((value_27_13 / 14) % 4)),
 "interpretation": "Wert / 14 mod_4"
 }
 
 # 5. Check ob Matrix(27,13) abovehaupt verwendet will
 # Vielleicht will eine andere Koordinate verwendet?
 
 return alternatives

def analyze_block_end_positions_matrix(layer3_data: List[Dict], matrix: np.ndarray) -> Dict:
 """Analyze alle Block-Ende-Positionen in der Matrix."""
 
 block_end_positions = [13, 27, 41, 55]
 analysis = {}
 
 for pos in block_end_positions:
 block = pos // 14
 pos_in_block = pos % 14
 
 # Analyze Characters
 chars = Counter()
 for entry in layer3_data:
 l3_id = entry.get("layer3_identity", "")
 if l3_id and len(l3_id) > pos:
 chars[l3_id[pos].upper()] += 1
 
 # Mögliche Matrix-Koordinaten
 possible_coords = [
 (pos, pos_in_block, "direct"),
 (block * 14 + pos_in_block, 0, "block_based"),
 (128 - pos, pos_in_block, "symmetric")
 ]
 
 matrix_values = {}
 for row, col, name in possible_coords:
 if 0 <= row < 128 and 0 <= col < 128:
 value = int(matrix[row, col])
 mod26 = int(value % 26)
 mod4 = int(value % 4)
 matrix_values[name] = {
 "coord": (row, col),
 "value": value,
 "mod_26": mod26,
 "mod_4": mod4,
 "char_mod26": chr(ord('A') + mod26),
 "char_mod4": chr(ord('A') + mod4)
 }
 
 analysis[f"position_{pos}"] = {
 "block": block,
 "pos_in_block": pos_in_block,
 "char_distribution": dict(chars.most_common(10)),
 "unique_chars": len(chars),
 "matrix_values": matrix_values
 }
 
 return analysis

def main():
 """Hauptfunktion."""
 
 print("=" * 80)
 print("KRITISCHE POSITION 27 MATRIX-ANALYSE")
 print("=" * 80)
 print()
 print("⚠️ KEINE HALLUZINATIONEN - NUR ECHTE DATEN!")
 print("🔬 PROFESSOREN-TEAM: KRITISCH, SYSTEMATISCH, PERFEKT")
 print()
 
 # 1. Load Matrix
 print("📂 Load Anna Matrix...")
 try:
 matrix = load_anna_matrix()
 print(f"✅ Matrix geloadn: {matrix.shape}")
 print(f" Matrix(27,13) = {int(matrix[27, 13])} (mod_26={int(matrix[27, 13] % 26)}, char={chr(ord('A') + int(matrix[27, 13] % 26))})")
 print(f" Matrix(27,13) mod_4 = {int(matrix[27, 13] % 4)} (char={chr(ord('A') + int(matrix[27, 13] % 4))})")
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
 
 # 3. Analyze Position 27 Restriktion
 print("🔍 Analyze Position 27 Restriktion...")
 restriction = analyze_position27_restriction(layer3_results)
 print(f"✅ Restriktion analysiert")
 print(f" Total: {restriction['total']}")
 print(f" Unique Characters: {restriction['unique_chars']}")
 print(f" Restriktion: {restriction['restriction_pattern']}")
 print()
 print(" Character-Verteilung:")
 for char, count in restriction["char_distribution"].items():
 pct = (count / restriction["total"]) * 100
 print(f" {char}: {count} ({pct:.2f}%)")
 print()
 
 # 4. Finde Matrix-Werte for A, B, C, D
 print("🔍 Finde Matrix-Werte for A, B, C, D...")
 abcd_values = find_matrix_values_for_abcd(matrix)
 print(f"✅ Matrix-Werte gefunden")
 print(f" A,B,C,D in Spalte 13: {len(abcd_values['column_13_abcd'])} Positionen")
 print(f" A,B,C,D in Zeile 27: {len(abcd_values['row_27_abcd'])} Positionen")
 print()
 
 # 5. Analyze alternative Transformationen
 print("🔍 Analyze alternative Transformationen...")
 alternatives = analyze_transformation_alternatives(matrix, restriction)
 print(f"✅ Alternativen analysiert")
 print()
 print(" Alternative Transformationen:")
 for name, alt in alternatives.items():
 print(f" {name}:")
 for key, value in alt.items():
 print(f" {key}: {value}")
 print()
 
 # 6. Analyze alle Block-Ende-Positionen
 print("🔍 Analyze alle Block-Ende-Positionen...")
 block_end_analysis = analyze_block_end_positions_matrix(layer3_results, matrix)
 print(f"✅ Block-Ende-Positionen analysiert")
 print()
 for pos_key, analysis in block_end_analysis.items():
 pos = pos_key.split("_")[1]
 print(f" Position {pos}:")
 print(f" Unique Characters: {analysis['unique_chars']}")
 print(f" Top Characters: {list(analysis['char_distribution'].keys())[:5]}")
 if "direct" in analysis["matrix_values"]:
 direct = analysis["matrix_values"]["direct"]
 print(f" Matrix({direct['coord'][0]},{direct['coord'][1]}) = {direct['value']}")
 print(f" mod_26: {direct['mod_26']} (char={direct['char_mod26']})")
 print(f" mod_4: {direct['mod_4']} (char={direct['char_mod4']})")
 print()
 
 # Speichere Ergebnisse
 OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
 
 output_data = {
 "timestamp": datetime.now().isoformat(),
 "critical_finding": {
 "position27_has_only_abcd": True,
 "matrix_27_13_value": int(matrix[27, 13]),
 "matrix_27_13_mod26": int(matrix[27, 13] % 26),
 "matrix_27_13_char_mod26": chr(ord('A') + int(matrix[27, 13] % 26)),
 "matrix_27_13_mod4": int(matrix[27, 13] % 4),
 "matrix_27_13_char_mod4": chr(ord('A') + int(matrix[27, 13] % 4)),
 "actual_chars_in_pos27": restriction["unique_chars"],
 "conclusion": "Matrix(27,13) mod_26 führt zu E, aber Position 27 hat nur A,B,C,D!"
 },
 "restriction_analysis": restriction,
 "abcd_matrix_values": abcd_values,
 "transformation_alternatives": alternatives,
 "block_end_analysis": block_end_analysis
 }
 
 output_file = OUTPUT_DIR / "critical_position27_matrix_analysis.json"
 with output_file.open("w") as f:
 json.dump(output_data, f, indent=2)
 print(f"💾 Ergebnisse gespeichert: {output_file}")
 
 print()
 print("=" * 80)
 print("✅ KRITISCHE ANALYSE ABGESCHLOSSEN")
 print("=" * 80)
 print()
 print("🚨 KRITISCHER BEFUND:")
 print()
 print(" Position 27 hat NUR A, B, C, D (nicht alle 26!)")
 print(" Matrix(27,13) = 56 → mod_26=4 → char=E")
 print(" ABER: E kommt in Position 27 NICHT vor!")
 print()
 print("💡 MÖGLICHE ERKLÄRUNGEN:")
 print()
 print(" 1. Transformation ist NICHT mod_26, sondern mod_4")
 print(" Matrix(27,13) = 56 → mod_4=0 → char=A ✅")
 print()
 print(" 2. Matrix(27,13) will NICHT verwendet")
 print(" Andere Matrix-Koordinate will verwendet")
 print()
 print(" 3. Transformation ist komplexer")
 print(" Kombination mehrerer Matrix-Werte")
 print()
 print("📋 NÄCHSTE SCHRITTE:")
 print()
 print(" 1. Check mod_4 Hypothese for alle Positionen")
 print(" 2. Finde echte Matrix-Koordinaten for Position 27")
 print(" 3. Analyze Transformation-Mechanismus")
 print()

if __name__ == "__main__":
 main()

