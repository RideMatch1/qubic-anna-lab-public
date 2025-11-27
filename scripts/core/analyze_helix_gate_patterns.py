#!/usr/bin/env python3
"""
Analyze Anna Matrix auf Helix Gate Patterns.

Helix Gate: 3 Inputs (A, B, C) -> Output rotiert um A+B+C Positionen
"""

import numpy as np
from pathlib import Path
from typing import List, Tuple, Dict
from collections import defaultdict, Counter
import json

import sys
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

import openpyxl
import numpy as np

def load_anna_matrix():
 """Load Anna Matrix direkt mit openpyxl."""
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
 # Skip non-numeric cells
 row_values.append(0.0)
 matrix.append(row_values)
 
 class Payload:
 def __init__(self, matrix):
 self.matrix = np.array(matrix)
 
 return Payload(np.array(matrix))

OUTPUT_DIR = Path("outputs/derived")
REPORTS_DIR = Path("outputs/reports")

def helix_operation(a: int, b: int, c: int) -> Tuple[int, int, int]:
 """
 Helix Gate Operation: Rotiert (A, B, C) um A+B+C Positionen.
 
 Args:
 a, b, c: Input values
 
 Returns:
 Rotated tuple (A, B, C)
 """
 rotation = a + b + c
 values = [a, b, c]
 rotated = values[rotation % 3:] + values[:rotation % 3]
 return tuple(rotated)

def find_helix_patterns_in_matrix(matrix: np.ndarray) -> Dict:
 """Suche nach Helix Gate Patterns in der Matrix."""
 
 results = {
 "three_input_groups": [],
 "rotation_patterns": [],
 "helix_candidates": [],
 }
 
 rows, cols = matrix.shape
 
 # Suche nach 3x3 Blöcken (könnten Helix Gates sein)
 for i in range(rows - 2):
 for j in range(cols - 2):
 block = matrix[i:i+3, j:j+3]
 
 # Extrahiere 3 Inputs (verschiedene Patterns)
 patterns = [
 # Horizontal
 (int(block[0, 0]), int(block[0, 1]), int(block[0, 2])),
 # Vertical
 (int(block[0, 0]), int(block[1, 0]), int(block[2, 0])),
 # Diagonal
 (int(block[0, 0]), int(block[1, 1]), int(block[2, 2])),
 # Anti-diagonal
 (int(block[0, 2]), int(block[1, 1]), int(block[2, 0])),
 ]
 
 for pattern in patterns:
 a, b, c = pattern
 rotation = a + b + c
 
 # Check ob Rotation Sinn macht
 if abs(rotation) < 100: # Reasonable rotation
 results["three_input_groups"].append({
 "coords": (i, j),
 "pattern": pattern,
 "rotation": rotation,
 })
 
 # Check ob Output in Matrix existiert
 rotated = helix_operation(a, b, c)
 results["rotation_patterns"].append({
 "input": pattern,
 "output": rotated,
 "rotation": rotation,
 "coords": (i, j),
 })

 return results

def analyze_identity_coordinates_for_helix(matrix: np.ndarray, identity_coords: List[Tuple[int, int]]) -> Dict:
 """Analyze ob Identity-Koordinaten Helix Patterns folgen."""
 
 results = {
 "helix_groups": [],
 "rotation_analysis": [],
 }
 
 # Gruppiere Koordinaten in 3er-Gruppen
 for i in range(0, len(identity_coords) - 2, 3):
 group = identity_coords[i:i+3]
 
 if len(group) == 3:
 values = [int(matrix[r, c]) for r, c in group]
 a, b, c = values
 
 rotation = a + b + c
 rotated = helix_operation(a, b, c)
 
 results["helix_groups"].append({
 "coords": group,
 "values": values,
 "rotation": rotation,
 "rotated": rotated,
 })
 
 # Check ob nächste Koordinaten rotierte Werte haben
 if i + 3 < len(identity_coords):
 next_group = identity_coords[i+3:i+6]
 if len(next_group) == 3:
 next_values = [int(matrix[r, c]) for r, c in next_group]
 matches = sum(1 for v in next_values if v in rotated)
 
 results["rotation_analysis"].append({
 "group": group,
 "values": values,
 "next_group": next_group,
 "next_values": next_values,
 "rotation": rotation,
 "matches": matches,
 })
 
 return results

def load_identity_coordinates() -> List[Tuple[int, int]]:
 """Load Koordinaten aller gefundenen Identities."""
 
 # Load aus on-chain validation
 complete_file = OUTPUT_DIR / "checksum_identities_onchain_validation_complete.json"
 if not complete_file.exists():
 return []
 
 # Für jetzt: Verwende bekannte Patterns
 # Später: Load alle Koordinaten aus validation data
 coords = []
 
 # Diagonal pattern (erste 4 Identities)
 for idx, base_row in enumerate(range(0, 128, 32), start=1):
 for g in range(4):
 row = base_row + (g // 2) * 16
 col = (g % 2) * 16
 for j in range(14):
 r = row + j
 c = col + j
 if r < 128 and c < 128:
 coords.append((r, c))
 
 return coords

def main():
 """Hauptfunktion."""
 
 print("=" * 80)
 print("ANALYZE HELIX GATE PATTERNS IN ANNA MATRIX")
 print("=" * 80)
 print()
 
 print("Loading Anna Matrix...")
 payload = load_anna_matrix()
 matrix = payload.matrix
 print(f"✅ Matrix loaded: {matrix.shape}")
 print()
 
 print("Searching for Helix Gate patterns...")
 helix_results = find_helix_patterns_in_matrix(matrix)
 print(f"✅ Found {len(helix_results['three_input_groups'])} three-input groups")
 print(f"✅ Found {len(helix_results['rotation_patterns'])} rotation patterns")
 print()
 
 print("Analyzing identity coordinates for Helix patterns...")
 identity_coords = load_identity_coordinates()
 print(f"✅ Loaded {len(identity_coords)} identity coordinates")
 
 if identity_coords:
 identity_helix = analyze_identity_coordinates_for_helix(matrix, identity_coords)
 print(f"✅ Analyzed {len(identity_helix['helix_groups'])} helix groups in identities")
 print(f"✅ Found {len(identity_helix['rotation_analysis'])} rotation analyses")
 print()
 
 # Statistik
 print("=" * 80)
 print("STATISTICS")
 print("=" * 80)
 print()
 
 rotations = [r["rotation"] for r in helix_results["rotation_patterns"]]
 if rotations:
 rotation_counter = Counter(rotations)
 print("Top 10 rotation values:")
 for rot, count in rotation_counter.most_common(10):
 print(f" Rotation {rot}: {count} occurrences")
 print()
 
 # Speichere Ergebnisse
 OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
 json_file = OUTPUT_DIR / "helix_gate_analysis.json"
 with json_file.open("w") as f:
 json.dump({
 "matrix_helix_patterns": helix_results,
 "identity_helix_patterns": identity_helix if identity_coords else {},
 "statistics": {
 "total_three_input_groups": len(helix_results["three_input_groups"]),
 "total_rotation_patterns": len(helix_results["rotation_patterns"]),
 "top_rotations": dict(rotation_counter.most_common(10)) if rotations else {},
 },
 }, f, indent=2)
 
 print(f"💾 Results saved to: {json_file}")
 
 # Erstelle Report
 REPORTS_DIR.mkdir(parents=True, exist_ok=True)
 report_file = REPORTS_DIR / "helix_gate_analysis_report.md"
 
 with report_file.open("w") as f:
 f.write("# Helix Gate Pattern Analysis Report\n\n")
 f.write("## Overview\n\n")
 f.write("This report analyzes the Anna Matrix for Helix Gate patterns.\n\n")
 f.write("## Helix Gate Operation\n\n")
 f.write("Helix Gate: Takes 3 inputs (A, B, C) and rotates them by A+B+C positions.\n\n")
 f.write("## Results\n\n")
 f.write(f"- **Total three-input groups found**: {len(helix_results['three_input_groups'])}\n")
 f.write(f"- **Total rotation patterns found**: {len(helix_results['rotation_patterns'])}\n")
 f.write(f"- **Identity helix groups analyzed**: {len(identity_helix.get('helix_groups', []))}\n\n")
 
 if rotations:
 f.write("## Top Rotation Values\n\n")
 for rot, count in rotation_counter.most_common(10):
 f.write(f"- Rotation {rot}: {count} occurrences\n")
 f.write("\n")
 
 f.write("## Interpretation\n\n")
 f.write("If Helix Gate patterns are present in the matrix, this would suggest:\n")
 f.write("- The matrix structure follows Aigarth's Helix Gate logic\n")
 f.write("- Identity extraction might be guided by Helix operations\n")
 f.write("- The matrix could be Aigarth tissue data\n\n")
 
 print(f"📄 Report saved to: {report_file}")
 print()
 print("=" * 80)
 print("✅ HELIX GATE ANALYSIS COMPLETE")
 print("=" * 80)

if __name__ == "__main__":
 main()

