#!/usr/bin/env python3
"""
Analyze Matrix-Wert-Patterns - Finde die richtige Decodierungsmethode

Das Problem: CFB-Methode (x+y) funktioniert nicht.
Lass uns die tatsächlichen Matrix-Werte analyzen und Patterns finden!
"""

import sys
from pathlib import Path
import numpy as np
import openpyxl
from collections import Counter

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

OUTPUT_DIR = project_root / "outputs" / "derived"
REPORTS_DIR = project_root / "outputs" / "reports"

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

def analyze_value_distribution(matrix):
 """Analyze Wert-Verteilung."""
 values = matrix.flatten()
 
 print("=" * 80)
 print("MATRIX VALUE DISTRIBUTION ANALYSIS")
 print("=" * 80)
 print()
 
 print(f"Total values: {len(values)}")
 print(f"Min: {values.min()}")
 print(f"Max: {values.max()}")
 print(f"Mean: {values.mean():.2f}")
 print(f"Std: {values.std():.2f}")
 print()
 
 # Wert-Verteilung
 unique, counts = np.unique(values, return_counts=True)
 top_values = sorted(zip(counts, unique), reverse=True)[:20]
 
 print("Top 20 values by frequency:")
 for count, value in top_values:
 print(f" {value:6.1f}: {count:4d} times ({count/len(values)*100:.2f}%)")
 print()
 
 # Check ob Werte in 0-25 Bereich sind (for A-Z)
 in_range = np.sum((values >= 0) & (values <= 25))
 print(f"Values in range 0-25 (direct A-Z): {in_range} ({in_range/len(values)*100:.2f}%)")
 print()
 
 # Check mod 26 Verteilung
 mod26_values = (values.astype(int) % 26)
 mod26_counts = Counter(mod26_values)
 print("Mod 26 distribution (should be uniform for random, non-uniform for encoded):")
 for i in range(26):
 count = mod26_counts.get(i, 0)
 char = chr(ord('A') + i)
 print(f" {char} (mod {i:2d}): {count:4d} ({count/len(values)*100:.2f}%)")
 print()
 
 return {
 "min": float(values.min()),
 "max": float(values.max()),
 "mean": float(values.mean()),
 "std": float(values.std()),
 "top_values": [(float(v), int(c)) for c, v in top_values],
 "in_range_0_25": int(in_range),
 "mod26_distribution": {int(k): int(v) for k, v in mod26_counts.items()}
 }

def test_cfb_coords_with_different_methods(matrix):
 """Teste CFB-Koordinaten mit verschiedenen Methoden."""
 print("=" * 80)
 print("TEST CFB COORDINATES WITH DIFFERENT METHODS")
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
 actual_value = matrix[r][c]
 
 methods = {}
 
 # Methode 1: Direkt mod 26
 methods["direct_mod26"] = chr(ord('A') + ((int(actual_value) % 26) + 26) % 26)
 
 # Methode 2: Absolutwert mod 26
 methods["abs_mod26"] = chr(ord('A') + (int(abs(actual_value)) % 26))
 
 # Methode 3: Normalisiere zu 0-25
 normalized = int(actual_value) + 128
 methods["normalized_mod26"] = chr(ord('A') + (normalized % 26))
 
 # Methode 4: Wert direkt (wenn 0-25)
 if 0 <= actual_value <= 25:
 methods["direct_value"] = chr(ord('A') + int(actual_value))
 else:
 methods["direct_value"] = "?"
 
 # Methode 5: CFB (x+y) - zum Vergleich
 normal_value = x + y
 letter_value = ((normal_value % 26) + 26) % 26 + 1
 methods["cfb_x_plus_y"] = chr(ord('A') + letter_value - 1)
 
 # Methode 6: Matrix-Wert + 26 (wenn negativ)
 if actual_value < 0:
 adjusted = int(actual_value) + 26
 methods["negative_plus_26"] = chr(ord('A') + (adjusted % 26))
 else:
 methods["negative_plus_26"] = chr(ord('A') + (int(actual_value) % 26))
 
 print(f"CFB({x},{y}) → Matrix({r},{c}):")
 print(f" Actual value: {actual_value}")
 print(f" Expected: {expected}")
 print(f" Methods:")
 
 best_matches = []
 for method_name, char in methods.items():
 match = "✅" if char == expected else " "
 print(f" {match} {method_name}: {char}")
 if char == expected:
 best_matches.append(method_name)
 
 if best_matches:
 print(f" ✅ MATCHES: {', '.join(best_matches)}")
 else:
 print(f" ❌ No match")
 print()
 
 results.append({
 "cfb_coord": (x, y),
 "matrix_coord": (r, c),
 "actual_value": float(actual_value),
 "expected": expected,
 "methods": methods,
 "matches": best_matches
 })
 
 return results

def find_best_decoding_method(matrix):
 """Finde die beste Decodierungsmethode durch Testen."""
 print("=" * 80)
 print("FINDING BEST DECODING METHOD")
 print("=" * 80)
 print()
 
 # Test mit CFB-Koordinaten
 test_results = test_cfb_coords_with_different_methods(matrix)
 
 # Zähle Matches pro Methode
 method_scores = {}
 for result in test_results:
 for method in result["matches"]:
 method_scores[method] = method_scores.get(method, 0) + 1
 
 print("Method scores (based on CFB coordinate tests):")
 for method, score in sorted(method_scores.items(), key=lambda x: x[1], reverse=True):
 print(f" {method}: {score}/{len(test_results)} matches")
 print()
 
 if method_scores:
 best_method = max(method_scores.items(), key=lambda x: x[1])
 print(f"✅ Best method: {best_method[0]} ({best_method[1]}/{len(test_results)} matches)")
 else:
 print("❌ No method matches all CFB coordinates")
 print(" Need to find alternative decoding approach")
 
 print()
 
 return method_scores, test_results

def main():
 print("=" * 80)
 print("ANALYZE MATRIX VALUE PATTERNS")
 print("=" * 80)
 print()
 
 print("Loading matrix...")
 matrix = load_matrix()
 print(f"✅ Matrix loaded: {matrix.shape}")
 print()
 
 # Analyze Wert-Verteilung
 distribution = analyze_value_distribution(matrix)
 
 # Teste verschiedene Methoden
 method_scores, test_results = find_best_decoding_method(matrix)
 
 # Speichere Ergebnisse
 OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
 REPORTS_DIR.mkdir(parents=True, exist_ok=True)
 
 import json
 results = {
 "distribution": distribution,
 "method_scores": method_scores,
 "test_results": test_results
 }
 
 output_file = OUTPUT_DIR / "matrix_value_patterns_analysis.json"
 with output_file.open('w') as f:
 json.dump(results, f, indent=2)
 print(f"✅ Results saved to: {output_file}")
 
 # Report
 report_file = REPORTS_DIR / "matrix_value_patterns_analysis_report.md"
 with report_file.open('w') as f:
 f.write("# Matrix Value Patterns Analysis Report\n\n")
 f.write("## Overview\n\n")
 f.write("Analysis of actual matrix values to find the correct decoding method.\n\n")
 f.write("## Problem\n\n")
 f.write("CFB method (x+y) doesn't work - actual matrix values are completely different from x+y.\n\n")
 f.write("## Value Distribution\n\n")
 f.write(f"- Min: {distribution['min']}\n")
 f.write(f"- Max: {distribution['max']}\n")
 f.write(f"- Mean: {distribution['mean']:.2f}\n")
 f.write(f"- Std: {distribution['std']:.2f}\n")
 f.write(f"- Values in range 0-25: {distribution['in_range_0_25']} ({distribution['in_range_0_25']/16384*100:.2f}%)\n\n")
 f.write("## Top Values\n\n")
 for value, count in distribution['top_values'][:10]:
 f.write(f"- {value:6.1f}: {count} times\n")
 f.write("\n## Method Scores\n\n")
 if method_scores:
 for method, score in sorted(method_scores.items(), key=lambda x: x[1], reverse=True):
 f.write(f"- {method}: {score}/{len(test_results)} matches\n")
 else:
 f.write("No methods matched all CFB coordinates.\n")
 f.write("\n## Conclusion\n\n")
 if method_scores:
 best = max(method_scores.items(), key=lambda x: x[1])
 f.write(f"The best method found is **{best[0]}** with {best[1]}/{len(test_results)} matches.\n")
 f.write("However, this may not be the correct method - further analysis needed.\n")
 else:
 f.write("None of the tested methods work with CFB coordinates.\n")
 f.write("This suggests either:\n")
 f.write("1. CFB coordinates are incorrect\n")
 f.write("2. The decoding method is different\n")
 f.write("3. We need to use actual matrix values, not x+y formula\n")
 f.write("\n## Next Steps\n\n")
 f.write("- Try decoding with actual matrix values directly\n")
 f.write("- Test if matrix values map to letters differently\n")
 f.write("- Look for patterns in value sequences\n")
 f.write("- Test if message is encoded in value differences, not absolute values\n")
 
 print(f"✅ Report saved to: {report_file}")
 print()
 print("=" * 80)
 print("ANALYSIS COMPLETE")
 print("=" * 80)

if __name__ == "__main__":
 main()

