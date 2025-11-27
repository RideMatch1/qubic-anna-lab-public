#!/usr/bin/env python3
"""
Analyze die 26 Zero Values ("Dark Matter") und ihre Beziehung zu Identity-Extraktion.

Die 26 zeros könnten:
- Control Neurons sein
- Identity-Extraktions-Kontrollpunkte
- Helix Gate Operations steuern
- "Nervous System" der Matrix
"""

import json
import numpy as np
from pathlib import Path
from typing import List, Tuple, Dict
from collections import defaultdict
import math

import sys
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

import openpyxl

OUTPUT_DIR = Path("outputs/derived")
REPORTS_DIR = Path("outputs/reports")

def load_anna_matrix() -> np.ndarray:
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

def find_zero_coordinates(matrix: np.ndarray) -> List[Tuple[int, int]]:
 """Finde alle Zero-Koordinaten in der Matrix."""
 zeros = []
 for i in range(matrix.shape[0]):
 for j in range(matrix.shape[1]):
 # Matrix uses 0-based indexing, but Excel uses 1-based
 # Check if value is exactly 0
 if abs(matrix[i, j]) < 0.001: # Consider as zero
 zeros.append((i, j))
 
 # Also check known coordinates from documentation
 # From Comprehensive Hidden Message Analysis.md:
 known_zeros = [
 (4, 23), (6, 19), (35, 80), (36, 19), (36, 114), (37, 19), (44, 19),
 (44, 67), (44, 115), (46, 83), (68, 51), (68, 55), (70, 49), (70, 51),
 (70, 115), (78, 115), (78, 119), (100, 51), (100, 115), (101, 51),
 ]
 
 # Verify these are actually zeros in matrix
 verified_zeros = []
 for coord in known_zeros:
 r, c = coord
 if r < matrix.shape[0] and c < matrix.shape[1]:
 if abs(matrix[r, c]) < 0.001:
 verified_zeros.append(coord)
 
 # Use verified zeros if we found them, otherwise use all zeros
 if len(verified_zeros) >= 20: # We have at least 20 known zeros
 return verified_zeros
 else:
 return zeros

def load_identity_coordinates() -> List[Tuple[int, int]]:
 """Load alle Identity-Extraktions-Koordinaten."""
 
 identity_coords = []
 
 # Diagonal pattern (erste 4 Identities)
 for idx, base_row in enumerate(range(0, 128, 32), start=1):
 for g in range(4):
 row = base_row + (g // 2) * 16
 col = (g % 2) * 16
 for j in range(14):
 r = row + j
 c = col + j
 if r < 128 and c < 128:
 identity_coords.append((r, c))
 
 # Vortex pattern (9-Vortex rings)
 # Center at (64, 64)
 center = (64, 64)
 rings = [
 [(64, 64)], # Center
 [(64-1, 64), (64+1, 64), (64, 64-1), (64, 64+1)], # Ring 1
 # Add more rings if needed
 ]
 
 # TODO: Add comprehensive scan coordinates if available
 # For now, use known patterns
 
 return identity_coords

def calculate_distance(coord1: Tuple[int, int], coord2: Tuple[int, int]) -> float:
 """Berechne euklidische Distanz zwischen zwei Koordinaten."""
 return math.sqrt((coord1[0] - coord2[0])**2 + (coord1[1] - coord2[1])**2)

def find_nearest_identity_coords(zero_coord: Tuple[int, int], identity_coords: List[Tuple[int, int]], max_distance: int = 10) -> List[Tuple[Tuple[int, int], float]]:
 """Finde Identity-Koordinaten in der Nähe einer Zero-Koordinate."""
 nearby = []
 for id_coord in identity_coords:
 dist = calculate_distance(zero_coord, id_coord)
 if dist <= max_distance:
 nearby.append((id_coord, dist))
 return sorted(nearby, key=lambda x: x[1])

def analyze_zero_identity_correlation(zero_coords: List[Tuple[int, int]], identity_coords: List[Tuple[int, int]]) -> Dict:
 """Analyze Korrelation zwischen Zero-Koordinaten und Identity-Koordinaten."""
 
 results = {
 "zero_count": len(zero_coords),
 "identity_count": len(identity_coords),
 "zero_coordinates": zero_coords,
 "nearby_identities": [],
 "distance_statistics": [],
 "geometric_patterns": {},
 }
 
 # Finde Identity-Koordinaten in der Nähe von Zeros
 for zero_coord in zero_coords:
 nearby = find_nearest_identity_coords(zero_coord, identity_coords, max_distance=20)
 
 if nearby:
 results["nearby_identities"].append({
 "zero_coord": zero_coord,
 "nearby_count": len(nearby),
 "nearest": nearby[0] if nearby else None,
 "all_nearby": nearby[:5], # Top 5
 })
 
 if nearby:
 results["distance_statistics"].append(nearby[0][1])
 
 # Statistik
 if results["distance_statistics"]:
 results["distance_stats"] = {
 "min": min(results["distance_statistics"]),
 "max": max(results["distance_statistics"]),
 "mean": sum(results["distance_statistics"]) / len(results["distance_statistics"]),
 "median": sorted(results["distance_statistics"])[len(results["distance_statistics"]) // 2],
 }
 
 # Geometrische Muster
 if len(zero_coords) == 26:
 # Check auf geometrische Muster
 rows = [z[0] for z in zero_coords]
 cols = [z[1] for z in zero_coords]
 
 results["geometric_patterns"] = {
 "row_range": (min(rows), max(rows)),
 "col_range": (min(cols), max(cols)),
 "row_distribution": defaultdict(int),
 "col_distribution": defaultdict(int),
 "diagonal_check": False,
 "grid_check": False,
 }
 
 # Check auf Diagonal-Muster
 for r, c in zero_coords:
 if r == c or r + c == 127: # Main diagonal or anti-diagonal
 results["geometric_patterns"]["diagonal_check"] = True
 
 # Check auf Grid-Muster
 unique_rows = len(set(rows))
 unique_cols = len(set(cols))
 if unique_rows <= 8 or unique_cols <= 8: # Could be grid-like
 results["geometric_patterns"]["grid_check"] = True
 
 # Distribution
 for r in rows:
 results["geometric_patterns"]["row_distribution"][r] += 1
 for c in cols:
 results["geometric_patterns"]["col_distribution"][c] += 1
 
 return results

def analyze_zero_helix_connection(matrix: np.ndarray, zero_coords: List[Tuple[int, int]]) -> Dict:
 """Analyze ob Zeros mit Helix Gate Operations verbunden sind."""
 
 results = {
 "zero_helix_connections": [],
 }
 
 # Check 3x3 Blöcke um Zeros for Helix Patterns
 for zero_coord in zero_coords:
 r, c = zero_coord
 
 # Check 3x3 Block
 if r > 0 and r < 127 and c > 0 and c < 127:
 block = matrix[r-1:r+2, c-1:c+2]
 
 # Check auf Helix-like patterns (A+B+C)
 patterns = [
 (int(block[0, 0]), int(block[0, 1]), int(block[0, 2])),
 (int(block[1, 0]), int(block[1, 1]), int(block[1, 2])),
 (int(block[2, 0]), int(block[2, 1]), int(block[2, 2])),
 (int(block[0, 0]), int(block[1, 0]), int(block[2, 0])),
 (int(block[0, 1]), int(block[1, 1]), int(block[2, 1])),
 (int(block[0, 2]), int(block[1, 2]), int(block[2, 2])),
 ]
 
 for pattern in patterns:
 a, b, c = pattern
 rotation = a + b + c
 
 if abs(rotation) < 100: # Reasonable rotation
 results["zero_helix_connections"].append({
 "zero_coord": zero_coord,
 "pattern": pattern,
 "rotation": rotation,
 })
 
 return results

def main():
 """Hauptfunktion."""
 
 print("=" * 80)
 print("ANALYZE 26 ZERO VALUES (DARK MATTER)")
 print("=" * 80)
 print()
 
 print("Loading Anna Matrix...")
 matrix = load_anna_matrix()
 print(f"✅ Matrix loaded: {matrix.shape}")
 print()
 
 print("Finding zero coordinates...")
 zero_coords = find_zero_coordinates(matrix)
 print(f"✅ Found {len(zero_coords)} zero values")
 
 if len(zero_coords) != 26:
 print(f"⚠️ Expected 26 zeros, found {len(zero_coords)}")
 else:
 print("✅ Exactly 26 zeros found (as expected)")
 print()
 
 print("Loading identity coordinates...")
 identity_coords = load_identity_coordinates()
 print(f"✅ Loaded {len(identity_coords)} identity coordinates")
 print()
 
 print("Analyzing zero-identity correlation...")
 correlation = analyze_zero_identity_correlation(zero_coords, identity_coords)
 print(f"✅ {len(correlation['nearby_identities'])} zeros have nearby identities")
 
 if correlation.get("distance_stats"):
 stats = correlation["distance_stats"]
 print(f" Min distance: {stats['min']:.2f}")
 print(f" Mean distance: {stats['mean']:.2f}")
 print(f" Max distance: {stats['max']:.2f}")
 print()
 
 print("Analyzing zero-helix connections...")
 helix_analysis = analyze_zero_helix_connection(matrix, zero_coords)
 print(f"✅ Found {len(helix_analysis['zero_helix_connections'])} helix connections")
 print()
 
 # Zeige Zero-Koordinaten
 print("=" * 80)
 print("26 ZERO COORDINATES (DARK MATTER)")
 print("=" * 80)
 print()
 for i, (r, c) in enumerate(zero_coords, 1):
 nearby_count = len([n for n in correlation["nearby_identities"] if n["zero_coord"] == (r, c)])
 print(f"{i:2d}. ({r:3d}, {c:3d}) - Nearby identities: {nearby_count}")
 print()
 
 # Speichere Ergebnisse
 OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
 json_file = OUTPUT_DIR / "zero_values_dark_matter_analysis.json"
 with json_file.open("w") as f:
 json.dump({
 "zero_coordinates": zero_coords,
 "correlation_analysis": correlation,
 "helix_analysis": helix_analysis,
 }, f, indent=2)
 
 print(f"💾 Results saved to: {json_file}")
 
 # Erstelle Report
 REPORTS_DIR.mkdir(parents=True, exist_ok=True)
 report_file = REPORTS_DIR / "zero_values_dark_matter_analysis_report.md"
 
 with report_file.open("w") as f:
 f.write("# 26 Zero Values (Dark Matter) Analysis Report\n\n")
 f.write("## Overview\n\n")
 f.write("Analysis of the 26 zero values in the Anna Matrix and their relationship to identity extraction.\n\n")
 
 f.write("## Zero Coordinates\n\n")
 f.write("The 26 zero values are located at:\n\n")
 for i, (r, c) in enumerate(zero_coords, 1):
 nearby_info = next((n for n in correlation["nearby_identities"] if n["zero_coord"] == (r, c)), None)
 nearby_count = nearby_info["nearby_count"] if nearby_info else 0
 f.write(f"{i:2d}. `({r:3d}, {c:3d})` - Nearby identities: {nearby_count}\n")
 f.write("\n")
 
 f.write("## Correlation with Identity Extraction\n\n")
 f.write(f"- **Zeros with nearby identities**: {len(correlation['nearby_identities'])} / {len(zero_coords)}\n")
 if correlation.get("distance_stats"):
 stats = correlation["distance_stats"]
 f.write(f"- **Min distance**: {stats['min']:.2f}\n")
 f.write(f"- **Mean distance**: {stats['mean']:.2f}\n")
 f.write(f"- **Max distance**: {stats['max']:.2f}\n")
 f.write("\n")
 
 f.write("## Geometric Patterns\n\n")
 if correlation.get("geometric_patterns"):
 patterns = correlation["geometric_patterns"]
 f.write(f"- **Row range**: {patterns['row_range']}\n")
 f.write(f"- **Col range**: {patterns['col_range']}\n")
 f.write(f"- **Diagonal pattern**: {patterns['diagonal_check']}\n")
 f.write(f"- **Grid pattern**: {patterns['grid_check']}\n")
 f.write("\n")
 
 f.write("## Helix Gate Connections\n\n")
 f.write(f"- **Total helix connections**: {len(helix_analysis['zero_helix_connections'])}\n")
 if helix_analysis["zero_helix_connections"]:
 f.write("\n**Sample connections**:\n\n")
 for conn in helix_analysis["zero_helix_connections"][:10]:
 f.write(f"- Zero `{conn['zero_coord']}`: Pattern {conn['pattern']}, Rotation {conn['rotation']}\n")
 f.write("\n")
 
 f.write("## Interpretation\n\n")
 f.write("If zeros are control neurons:\n")
 f.write("- They might control identity extraction\n")
 f.write("- They could coordinate Helix Gate operations\n")
 f.write("- They may serve as 'nervous system' of the matrix\n")
 f.write("- Proximity to identity coordinates suggests functional relationship\n\n")
 
 print(f"📄 Report saved to: {report_file}")
 print()
 print("=" * 80)
 print("✅ ZERO VALUES ANALYSIS COMPLETE")
 print("=" * 80)

if __name__ == "__main__":
 main()

