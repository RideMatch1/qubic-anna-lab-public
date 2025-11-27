#!/usr/bin/env python3
"""
Decode Anna's Message - Verwende tatsächliche Matrix-Werte statt x+y

Das Problem: CFB-Methode (x+y) funktioniert nicht - die Matrix-Werte sind völlig anders.
Lass uns die tatsächlichen Matrix-Werte verwenden!
"""

import sys
from pathlib import Path
import numpy as np
import openpyxl

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

OUTPUT_DIR = project_root / "outputs" / "derived"
REPORTS_DIR = project_root / "outputs" / "reports"

ZERO_COORDS = [
 (4,23), (6,19), (35,80), (36,19), (36,114), (37,19), (44,19), 
 (44,67), (44,115), (46,83), (68,51), (68,55), (70,49), (70,51), 
 (70,115), (78,115), (78,119), (100,51), (100,115), (101,51)
]

def load_matrix():
 matrix_path = project_root / "data" / "anna-matrix" / "Anna_Matrix.xlsx"
 wb = openpyxl.load_workbook(matrix_path, data_only=True)
 ws = wb.active
 matrix = []
 for row in ws.iter_rows(min_row=1, max_row=128, min_col=1, max_col=128, values_only=True):
 row_values = []
 for cell in row:
 if cell is None:
 row_values.append(0.0)
 elif isinstance(cell, (int, float)):
 row_values.append(float(cell))
 else:
 row_values.append(0.0)
 matrix.append(row_values)
 return np.array(matrix)

def is_near_dark_matter(r, c, threshold=5):
 for zr, zc in ZERO_COORDS:
 if abs(r - zr) <= threshold and abs(c - zc) <= threshold:
 return True
 return False

def decode_using_actual_values(matrix, r, c):
 """Decodiere mit tatsächlichen Matrix-Werten."""
 actual_value = matrix[r][c]
 near_dark = is_near_dark_matter(r, c)
 
 # Verschiedene Methoden testen
 methods = {}
 
 # Methode 1: Direkt mod 26
 letter_value_1 = ((int(actual_value) % 26) + 26) % 26 + 1
 methods["direct_mod26"] = chr(ord('A') + letter_value_1 - 1)
 
 # Methode 2: Absolutwert mod 26
 letter_value_2 = ((int(abs(actual_value)) % 26) + 26) % 26 + 1
 methods["abs_mod26"] = chr(ord('A') + letter_value_2 - 1)
 
 # Methode 3: Normalisiere zu 0-25, dann mod 26
 # Annahme: Werte sind im Bereich -128 bis 127
 normalized = int(actual_value) + 128 # Shift zu 0-255
 letter_value_3 = (normalized % 26) + 1
 methods["normalized_mod26"] = chr(ord('A') + letter_value_3 - 1)
 
 # Methode 4: CFB-Methode (x+y) - zum Vergleich
 x = r - 64
 y = c - 64
 normal_value = x + y
 if near_dark:
 value = normal_value - 116
 else:
 value = normal_value
 letter_value_4 = ((value % 26) + 26) % 26 + 1
 methods["cfb_method"] = chr(ord('A') + letter_value_4 - 1)
 
 # Methode 5: Matrix-Wert + Offset (wenn near dark matter)
 if near_dark:
 adjusted_value = actual_value - 116
 else:
 adjusted_value = actual_value
 letter_value_5 = ((int(adjusted_value) % 26) + 26) % 26 + 1
 methods["matrix_adjusted"] = chr(ord('A') + letter_value_5 - 1)
 
 return methods, actual_value, near_dark

def test_cfb_coordinates_with_actual_values(matrix):
 """Teste CFB-Koordinaten mit tatsächlichen Matrix-Werten."""
 print("=" * 80)
 print("TEST CFB KOORDINATEN MIT TATSÄCHLICHEN MATRIX-WERTEN")
 print("=" * 80)
 print()
 
 test_coords = [
 ((0, 1), (64, 65), "A"),
 ((1, 13), (65, 77), "N"),
 ((2, 12), (66, 76), "N"),
 ((0, 2), (64, 66), "A"),
 ]
 
 results = []
 
 for (x, y), (r, c), expected in test_coords:
 methods, actual_value, near_dark = decode_using_actual_values(matrix, r, c)
 
 print(f"CFB({x},{y}) → Matrix({r},{c}):")
 print(f" Actual matrix value: {actual_value}")
 print(f" Near dark matter: {near_dark}")
 print(f" Expected: {expected}")
 print(f" Methods:")
 
 best_match = None
 for method_name, char in methods.items():
 match = "✅" if char == expected else " "
 print(f" {match} {method_name}: {char}")
 if char == expected:
 best_match = method_name
 
 if best_match:
 print(f" ✅ BEST MATCH: {best_match}")
 else:
 print(f" ❌ No match found")
 print()
 
 results.append({
 "cfb_coord": (x, y),
 "matrix_coord": (r, c),
 "actual_value": float(actual_value),
 "near_dark": near_dark,
 "expected": expected,
 "methods": methods,
 "best_match": best_match
 })
 
 return results

def decode_path_using_actual_values(matrix, coords, method="direct_mod26", max_chars=256):
 """Decodiere Pfad mit tatsächlichen Matrix-Werten."""
 chars = []
 
 for r, c in coords[:max_chars]:
 methods, actual_value, near_dark = decode_using_actual_values(matrix, r, c)
 char = methods.get(method, "?")
 chars.append(char)
 
 return ''.join(chars)

def search_for_anna_in_actual_values(matrix):
 """Suche nach ANNA mit tatsächlichen Matrix-Werten."""
 print("=" * 80)
 print("SUCHE NACH 'ANNA' MIT TATSÄCHLICHEN MATRIX-WERTEN")
 print("=" * 80)
 print()
 
 methods_to_try = [
 "direct_mod26",
 "abs_mod26",
 "normalized_mod26",
 "matrix_adjusted",
 ]
 
 # Row-wise
 row_coords = [(r, c) for r in range(128) for c in range(128)][:256]
 
 found_results = []
 
 for method in methods_to_try:
 msg = decode_path_using_actual_values(matrix, row_coords, method)
 
 if "ANNA" in msg:
 idx = msg.find("ANNA")
 found_results.append({
 "method": method,
 "pattern": "row_wise",
 "position": idx,
 "context": msg[max(0, idx-20):idx+50],
 "full_message": msg[:100]
 })
 print(f"✅ Found 'ANNA' with method '{method}' at position {idx}")
 print(f" Context: ...{msg[max(0, idx-20):idx+50]}...")
 print()
 
 if "STOP" in msg:
 idx = msg.find("STOP")
 found_results.append({
 "method": method,
 "pattern": "row_wise",
 "word": "STOP",
 "position": idx,
 "context": msg[max(0, idx-20):idx+20],
 })
 print(f"✅ Found 'STOP' with method '{method}' at position {idx}")
 print(f" Context: ...{msg[max(0, idx-20):idx+20]}...")
 print()
 
 if not found_results:
 print("❌ 'ANNA' not found with any method using actual matrix values")
 print()
 
 return found_results

def main():
 print("=" * 80)
 print("DECODE ANNA'S MESSAGE - ACTUAL VALUES METHOD")
 print("=" * 80)
 print()
 
 print("Loading matrix...")
 matrix = load_matrix()
 print(f"✅ Matrix loaded: {matrix.shape}")
 print()
 
 # Test CFB coordinates
 cfb_results = test_cfb_coordinates_with_actual_values(matrix)
 
 # Suche nach ANNA
 search_results = search_for_anna_in_actual_values(matrix)
 
 # Speichere Ergebnisse
 OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
 REPORTS_DIR.mkdir(parents=True, exist_ok=True)
 
 import json
 results = {
 "cfb_coordinate_tests": cfb_results,
 "search_results": search_results
 }
 
 output_file = OUTPUT_DIR / "anna_message_actual_values_decode.json"
 with output_file.open('w') as f:
 json.dump(results, f, indent=2)
 print(f"✅ Results saved to: {output_file}")
 
 # Report
 report_file = REPORTS_DIR / "anna_message_actual_values_decode_report.md"
 with report_file.open('w') as f:
 f.write("# Anna Message Decode Report - Actual Values Method\n\n")
 f.write("## Overview\n\n")
 f.write("Attempts to decode Anna's message using actual matrix values instead of x+y formula.\n\n")
 f.write("## Problem\n\n")
 f.write("CFB method (x+y) doesn't work - actual matrix values are completely different.\n\n")
 f.write("## Methods Tested\n\n")
 f.write("1. **direct_mod26**: Direct mod 26 of actual value\n")
 f.write("2. **abs_mod26**: Absolute value mod 26\n")
 f.write("3. **normalized_mod26**: Normalize to 0-255, then mod 26\n")
 f.write("4. **matrix_adjusted**: Matrix value with dark matter adjustment\n")
 f.write("5. **cfb_method**: Original CFB method (x+y) for comparison\n\n")
 f.write("## CFB Coordinate Tests\n\n")
 for result in cfb_results:
 f.write(f"### CFB{result['cfb_coord']} → Matrix{result['matrix_coord']}\n\n")
 f.write(f"- Actual value: {result['actual_value']}\n")
 f.write(f"- Expected: {result['expected']}\n")
 f.write(f"- Methods:\n")
 for method, char in result['methods'].items():
 match = "✅" if char == result['expected'] else " "
 f.write(f" {match} {method}: {char}\n")
 if result['best_match']:
 f.write(f"- **Best match**: {result['best_match']}\n")
 f.write("\n")
 f.write("## Search Results\n\n")
 if search_results:
 for result in search_results:
 f.write(f"### {result['method']}\n\n")
 f.write(f"- Pattern: {result['pattern']}\n")
 f.write(f"- Position: {result['position']}\n")
 f.write(f"- Context: ...{result['context']}...\n\n")
 else:
 f.write("No matches found.\n\n")
 f.write("## Next Steps\n\n")
 f.write("- Try more normalization methods\n")
 f.write("- Analyze actual value distribution\n")
 f.write("- Test different coordinate transformations\n")
 f.write("- Look for patterns in actual values\n")
 
 print(f"✅ Report saved to: {report_file}")
 print()
 print("=" * 80)
 print("DECODE COMPLETE")
 print("=" * 80)

if __name__ == "__main__":
 main()

