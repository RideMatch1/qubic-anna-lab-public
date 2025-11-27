#!/usr/bin/env python3
"""
Find Missing Zeros

Findet die fehlenden 6 Zeros (wir haben 20 von 26).
"""

import sys
import numpy as np
from pathlib import Path
from typing import List, Tuple

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from analysis.utils.data_loader import load_anna_matrix

OUTPUT_DIR = project_root / "outputs" / "derived"
REPORTS_DIR = project_root / "outputs" / "reports"

# Bekannte Zeros (20 von 26)
KNOWN_ZEROS = [
 (4, 23), (6, 19), (35, 80), (36, 19), (36, 114), (37, 19), (44, 19),
 (44, 67), (44, 115), (46, 83), (68, 51), (68, 55), (70, 49), (70, 51),
 (70, 115), (78, 115), (78, 119), (100, 51), (100, 115), (101, 51),
]

def find_all_zeros(matrix: np.ndarray) -> List[Tuple[int, int]]:
 """Finde alle Zero-Werte in der Matrix."""
 zeros = []
 
 for r in range(128):
 for c in range(128):
 value = matrix[r, c]
 # Check ob Wert genau 0.0 ist (mit Toleranz for Float)
 if abs(value) < 0.0001:
 zeros.append((r, c))
 
 return zeros

def analyze_zero_patterns(zeros: List[Tuple[int, int]]) -> dict:
 """Analyze Patterns in Zero-Koordinaten."""
 known_set = set(KNOWN_ZEROS)
 all_zeros_set = set(zeros)
 
 missing = [z for z in zeros if z not in known_set]
 new_zeros = [z for z in missing if z not in known_set]
 
 # Analyze Patterns
 row_dist = {}
 col_dist = {}
 
 for r, c in zeros:
 row_dist[r] = row_dist.get(r, 0) + 1
 col_dist[c] = col_dist.get(c, 0) + 1
 
 return {
 "total_zeros": len(zeros),
 "known_zeros": len(KNOWN_ZEROS),
 "missing_zeros": missing,
 "row_distribution": row_dist,
 "col_distribution": col_dist,
 "all_zeros": zeros
 }

def main():
 """Hauptfunktion."""
 print("=" * 80)
 print("FIND MISSING ZEROS")
 print("=" * 80)
 print()
 
 # Load Matrix
 print("Loading Anna Matrix...")
 payload = load_anna_matrix()
 matrix = payload.matrix
 print(f"✅ Matrix loaded: {matrix.shape}")
 print()
 
 # Finde alle Zeros
 print("Finding all zero values...")
 all_zeros = find_all_zeros(matrix)
 print(f"✅ Found {len(all_zeros)} zero values")
 print()
 
 # Analyze
 analysis = analyze_zero_patterns(all_zeros)
 
 print("=" * 80)
 print("RESULTS")
 print("=" * 80)
 print()
 print(f"Total zeros found: {analysis['total_zeros']}")
 print(f"Known zeros: {analysis['known_zeros']}")
 print(f"Missing zeros: {len(analysis['missing_zeros'])}")
 print()
 
 if analysis['missing_zeros']:
 print("Missing zeros (coordinates):")
 for r, c in analysis['missing_zeros']:
 print(f" ({r}, {c})")
 print()
 
 # Row/Column Patterns
 print("Row distribution (zeros per row):")
 for row in sorted(analysis['row_distribution'].keys()):
 count = analysis['row_distribution'][row]
 print(f" Row {row}: {count} zeros")
 print()
 
 print("Column distribution (zeros per column):")
 for col in sorted(analysis['col_distribution'].keys()):
 count = analysis['col_distribution'][col]
 if count > 1: # Nur Columns mit mehreren Zeros
 print(f" Column {col}: {count} zeros")
 print()
 
 # Speichere Ergebnisse
 OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
 import json
 
 results = {
 "total_zeros": analysis['total_zeros'],
 "known_zeros": KNOWN_ZEROS,
 "all_zeros": analysis['all_zeros'],
 "missing_zeros": analysis['missing_zeros'],
 "row_distribution": analysis['row_distribution'],
 "col_distribution": analysis['col_distribution']
 }
 
 output_json = OUTPUT_DIR / "missing_zeros_analysis.json"
 with output_json.open("w") as f:
 json.dump(results, f, indent=2)
 
 # Report
 REPORTS_DIR.mkdir(parents=True, exist_ok=True)
 output_md = REPORTS_DIR / "missing_zeros_analysis_report.md"
 
 with output_md.open("w") as f:
 f.write("# Missing Zeros Analysis Report\n\n")
 f.write("**Generated**: 2025-11-25\n\n")
 f.write("## Summary\n\n")
 f.write(f"- **Total zeros found**: {analysis['total_zeros']}\n")
 f.write(f"- **Known zeros**: {analysis['known_zeros']}\n")
 f.write(f"- **Missing zeros**: {len(analysis['missing_zeros'])}\n\n")
 
 if analysis['missing_zeros']:
 f.write("## Missing Zeros\n\n")
 f.write("Coordinates:\n\n")
 for r, c in analysis['missing_zeros']:
 f.write(f"- `({r}, {c})`\n")
 f.write("\n")
 
 f.write("## All Zero Coordinates\n\n")
 f.write("Complete list of all zero coordinates:\n\n")
 for r, c in sorted(analysis['all_zeros']):
 known_mark = "✅" if (r, c) in KNOWN_ZEROS else "🆕"
 f.write(f"- {known_mark} `({r}, {c})`\n")
 f.write("\n")
 
 print(f"💾 Results saved to: {output_json}")
 print(f"📄 Report saved to: {output_md}")
 print()
 
 return results

if __name__ == "__main__":
 main()

