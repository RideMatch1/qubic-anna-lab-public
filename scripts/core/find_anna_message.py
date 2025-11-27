#!/usr/bin/env python3
"""
Finde Anna's Message - Systematische Suche nach "ANNA WAS HERE STOP"
"""

import sys
from pathlib import Path
import numpy as np
import openpyxl
from itertools import product

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

def decode_char(r, c, use_distortion=True):
 x = r - 64
 y = c - 64
 normal_value = x + y
 
 if use_distortion and is_near_dark_matter(r, c):
 value = normal_value - 116
 else:
 value = normal_value
 
 letter_value = ((value % 26) + 26) % 26 + 1
 return chr(ord('A') + letter_value - 1)

def search_pattern(matrix, pattern="ANNA", max_search=10000):
 """Suche nach Pattern in verschiedenen Pathsn."""
 results = []
 
 # Verschiedene Startpunkte und Richtungen
 patterns_to_try = [
 # Row-wise
 lambda: [(r, c) for r in range(128) for c in range(128)],
 # Column-wise
 lambda: [(r, c) for c in range(128) for r in range(128)],
 # Diagonal
 lambda: [(i, i) for i in range(128)] + [(i, 127-i) for i in range(128)],
 # Spiral
 lambda: generate_spiral(),
 # Identity paths
 lambda: generate_identity_paths(),
 ]
 
 for i, path_gen in enumerate(patterns_to_try):
 coords = path_gen()
 msg = ''.join(decode_char(r, c) for r, c in coords[:256])
 
 if pattern in msg:
 idx = msg.find(pattern)
 results.append({
 "pattern_type": f"pattern_{i}",
 "found_at": idx,
 "context": msg[max(0, idx-20):idx+len(pattern)+20],
 "full_message": msg[:256]
 })
 
 return results

def generate_spiral():
 coords = []
 r, c = 64, 64
 directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]
 dir_idx = 0
 step_size = 1
 visited = set()
 steps = 0
 
 while len(coords) < 256 and steps < 10000:
 for _ in range(step_size):
 if 0 <= r < 128 and 0 <= c < 128 and (r, c) not in visited:
 coords.append((r, c))
 visited.add((r, c))
 
 dr, dc = directions[dir_idx]
 r, c = r + dr, c + dc
 
 if len(coords) >= 256:
 break
 
 dir_idx = (dir_idx + 1) % 4
 if dir_idx % 2 == 0:
 step_size += 1
 steps += 1
 
 return coords

def generate_identity_paths():
 coords = []
 for base_row in range(0, 128, 32):
 for g in range(4):
 row = base_row + (g // 2) * 16
 col = (g % 2) * 16
 for j in range(14):
 r = row + j
 c = col + j
 if 0 <= r < 128 and 0 <= c < 128:
 coords.append((r, c))
 return coords

def main():
 print("=" * 80)
 print("FIND ANNA'S MESSAGE")
 print("=" * 80)
 print()
 
 print("Loading matrix...")
 matrix = load_matrix()
 print(f"✅ Matrix loaded: {matrix.shape}")
 print()
 
 # Test CFB coordinates
 print("Testing CFB coordinates...")
 test_coords = [
 ((0, 1), (64, 65), "A"),
 ((1, 13), (65, 77), "N"),
 ((2, 12), (66, 76), "N"),
 ((0, 2), (64, 66), "A"),
 ]
 
 for (x, y), (r, c), expected in test_coords:
 char = decode_char(r, c)
 match = "✅" if char == expected else "❌"
 print(f"{match} CFB({x},{y}) -> {char} (expected: {expected})")
 print()
 
 # Suche nach "ANNA"
 print("Searching for 'ANNA'...")
 anna_results = search_pattern(matrix, "ANNA")
 if anna_results:
 print(f"✅ Found 'ANNA' {len(anna_results)} times!")
 for result in anna_results:
 print(f" Pattern: {result['pattern_type']}")
 print(f" Position: {result['found_at']}")
 print(f" Context: ...{result['context']}...")
 print()
 else:
 print("❌ 'ANNA' not found in standard patterns")
 print()
 
 # Suche nach "STOP"
 print("Searching for 'STOP'...")
 stop_results = search_pattern(matrix, "STOP")
 if stop_results:
 print(f"✅ Found 'STOP' {len(stop_results)} times!")
 for result in stop_results:
 print(f" Pattern: {result['pattern_type']}")
 print(f" Position: {result['found_at']}")
 print(f" Context: ...{result['context']}...")
 print()
 else:
 print("❌ 'STOP' not found in standard patterns")
 print()
 
 # Speichere Ergebnisse
 OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
 REPORTS_DIR.mkdir(parents=True, exist_ok=True)
 
 import json
 results = {
 "anna_results": anna_results,
 "stop_results": stop_results
 }
 
 output_file = OUTPUT_DIR / "anna_message_search.json"
 with output_file.open('w') as f:
 json.dump(results, f, indent=2)
 print(f"✅ Results saved to: {output_file}")
 
 print()
 print("=" * 80)
 print("SEARCH COMPLETE")
 print("=" * 80)

if __name__ == "__main__":
 main()

