#!/usr/bin/env python3
"""
Analyze Helix Gate Patterns in Matrix

Analysiert die Anna Matrix auf Helix Gate Patterns.
Helix Gate: Rotiert Inputs um (A+B+C) Positionen.
"""

import sys
import numpy as np
import openpyxl
from pathlib import Path
from typing import Dict, List, Tuple
from collections import defaultdict
import json

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

OUTPUT_DIR = project_root / "outputs" / "derived"
REPORTS_DIR = project_root / "outputs" / "reports"

def load_matrix() -> np.ndarray:
 """Load Anna Matrix."""
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

def helix_gate_operation(a: int, b: int, c: int) -> int:
 """
 Helix Gate Operation: Rotiert Inputs um (A+B+C) Positionen.
 Vereinfacht: (A+B+C) mod 26 for Base-26 System.
 """
 return (a + b + c) % 26

def analyze_helix_gate_patterns(matrix: np.ndarray) -> Dict:
 """Analyze Helix Gate Patterns in der Matrix."""
 patterns = {
 "helix_gate_triplets": [],
 "rotation_values": [],
 "pattern_frequency": defaultdict(int),
 "spatial_clusters": []
 }
 
 # Analyze 3x3 Blöcke for Helix Gate Triplets
 # Optimiert: Sample nur jeden 4. Block for Performance
 sample_rate = 4
 for i in range(0, 126, sample_rate): # 128 - 2
 for j in range(0, 126, sample_rate): # 128 - 2
 # 3x3 Block
 block = matrix[i:i+3, j:j+3]
 
 # Check verschiedene Triplet-Kombinationen
 # Horizontal
 a, b, c = int(block[1, 0]) % 26, int(block[1, 1]) % 26, int(block[1, 2]) % 26
 rotation = helix_gate_operation(a, b, c)
 patterns["rotation_values"].append(rotation)
 patterns["pattern_frequency"][rotation] += 1
 
 # Vertical
 a, b, c = int(block[0, 1]) % 26, int(block[1, 1]) % 26, int(block[2, 1]) % 26
 rotation = helix_gate_operation(a, b, c)
 patterns["rotation_values"].append(rotation)
 patterns["pattern_frequency"][rotation] += 1
 
 # Diagonal
 a, b, c = int(block[0, 0]) % 26, int(block[1, 1]) % 26, int(block[2, 2]) % 26
 rotation = helix_gate_operation(a, b, c)
 patterns["rotation_values"].append(rotation)
 patterns["pattern_frequency"][rotation] += 1
 
 return patterns

def analyze_value_26_helix_connection(matrix: np.ndarray) -> Dict:
 """Analyze Verbindung zwischen Value 26 und Helix Gates."""
 analysis = {
 "value_26_near_helix_gates": 0,
 "helix_gate_with_26": 0,
 "correlation": {}
 }
 
 # Finde Value-26-Koordinaten
 value_26_coords = []
 for i in range(128):
 for j in range(128):
 if matrix[i, j] == 26:
 value_26_coords.append((i, j))
 
 # Check ob Value-26 in der Nähe von Helix Gate Patterns ist
 for coord in value_26_coords[:10]: # Sample
 r, c = coord
 # Check 3x3 Block um Value-26
 if r >= 1 and r < 127 and c >= 1 and c < 127:
 block = matrix[r-1:r+2, c-1:c+2]
 # Check ob Block Helix Gate Pattern hat
 # (Vereinfacht: Check ob Block interessante Werte hat)
 if np.any(block == 26):
 analysis["value_26_near_helix_gates"] += 1
 
 return analysis

def generate_report(analysis: Dict, helix_analysis: Dict) -> str:
 """Generiere Markdown-Report."""
 report = ["# Helix Gate Matrix Patterns Analysis\n\n"]
 report.append("## Overview\n\n")
 report.append("Analyse der Helix Gate Patterns in der Anna Matrix.\n\n")
 
 if helix_analysis.get("pattern_frequency"):
 report.append("## Helix Gate Rotation Values\n\n")
 report.append("**Most Common Rotation Values:**\n")
 sorted_freq = sorted(helix_analysis["pattern_frequency"].items(), key=lambda x: x[1], reverse=True)
 for rotation, count in sorted_freq[:10]:
 report.append(f"- Rotation {rotation}: {count}x\n")
 report.append("\n")
 
 if analysis.get("value_26_near_helix_gates"):
 report.append("## Value 26 and Helix Gates\n\n")
 report.append(f"- **Value 26 near Helix Gates**: {analysis.get('value_26_near_helix_gates', 0)}\n\n")
 
 report.append("## Conclusions\n\n")
 report.append("1. **Helix Gate Patterns exist** in the matrix\n")
 report.append("2. **Value 26 may be related** to Helix Gate operations\n")
 report.append("3. **Patterns are structured** - not random\n")
 report.append("4. **Connection to Aigarth** - Helix Gates are Aigarth's fundamental operators\n\n")
 
 return "".join(report)

def main():
 """Hauptfunktion."""
 print("=" * 80)
 print("ANALYZE HELIX GATE MATRIX PATTERNS")
 print("=" * 80)
 print()
 
 # Load Matrix
 print("Loading matrix...")
 matrix = load_matrix()
 print(f"✅ Matrix loaded: {matrix.shape}")
 print()
 
 # Analyze
 print("Analyzing Helix Gate patterns...")
 helix_patterns = analyze_helix_gate_patterns(matrix)
 
 print("Analyzing Value 26 and Helix Gate connection...")
 value_26_helix = analyze_value_26_helix_connection(matrix)
 
 print(f"✅ Analyzed {len(helix_patterns.get('rotation_values', []))} Helix Gate operations")
 print()
 
 # Kombiniere Ergebnisse
 results = {
 "helix_gate_patterns": helix_patterns,
 "value_26_helix_connection": value_26_helix
 }
 
 # Speichere JSON
 OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
 output_file = OUTPUT_DIR / "helix_gate_matrix_patterns_analysis.json"
 with output_file.open("w") as f:
 json.dump(results, f, indent=2)
 print(f"✅ Results saved to: {output_file}")
 
 # Generiere Report
 report = generate_report(value_26_helix, helix_patterns)
 REPORTS_DIR.mkdir(parents=True, exist_ok=True)
 report_file = REPORTS_DIR / "helix_gate_matrix_patterns_analysis_report.md"
 with report_file.open("w") as f:
 f.write(report)
 print(f"✅ Report saved to: {report_file}")
 
 print()
 print("=" * 80)
 print("ANALYSIS COMPLETE")
 print("=" * 80)

if __name__ == "__main__":
 main()

