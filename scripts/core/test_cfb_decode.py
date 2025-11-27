#!/usr/bin/env python3
"""Test CFB Decode Method - Direkter Test"""

import sys
from pathlib import Path
import numpy as np
import openpyxl

project_root = Path(__file__).parent.parent.parent

# Load Matrix
print("Loading matrix...")
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
matrix = np.array(matrix)
print(f"✅ Matrix loaded: {matrix.shape}")
print()

# Zero-Koordinaten
ZERO_COORDS = [
 (4,23), (6,19), (35,80), (36,19), (36,114), (37,19), (44,19), 
 (44,67), (44,115), (46,83), (68,51), (68,55), (70,49), (70,51), 
 (70,115), (78,115), (78,119), (100,51), (100,115), (101,51)
]

def is_near_dark_matter(r, c, threshold=5):
 for zr, zc in ZERO_COORDS:
 if abs(r - zr) <= threshold and abs(c - zc) <= threshold:
 return True
 return False

# Test CFB Koordinaten
print("=" * 80)
print("TEST CFB KOORDINATEN")
print("=" * 80)
print()

test_coords = [
 ((0, 1), (64, 65), "A"),
 ((1, 13), (65, 77), "N"),
 ((2, 12), (66, 76), "N"),
 ((0, 2), (64, 66), "A"),
]

for (x, y), (r, c), expected in test_coords:
 normal_value = x + y
 actual_matrix_value = matrix[r][c]
 near_dark = is_near_dark_matter(r, c)
 
 if near_dark:
 value = normal_value - 116
 else:
 value = normal_value
 
 letter_value = ((value % 26) + 26) % 26 + 1
 char = chr(ord('A') + letter_value - 1)
 
 print(f"CFB({x},{y}) → Matrix({r},{c}):")
 print(f" Normal value (x+y): {normal_value}")
 print(f" Near dark matter: {near_dark}")
 print(f" Adjusted value: {value}")
 print(f" Actual matrix value: {actual_matrix_value}")
 print(f" Letter value: {letter_value}")
 print(f" Decoded char: {char} (expected: {expected})")
 if char == expected:
 print(f" ✅ MATCH!")
 else:
 print(f" ❌ NO MATCH")
 print()

# Test verschiedene Paths
print("=" * 80)
print("TEST VERSCHIEDENE PFADE")
print("=" * 80)
print()

def decode_path(coords, max_chars=256):
 chars = []
 for r, c in coords[:max_chars]:
 x = r - 64
 y = c - 64
 normal_value = x + y
 
 if is_near_dark_matter(r, c):
 value = normal_value - 116
 else:
 value = normal_value
 
 letter_value = ((value % 26) + 26) % 26 + 1
 char = chr(ord('A') + letter_value - 1)
 chars.append(char)
 
 return ''.join(chars)

# Spiral
print("1. Spiral Pattern:")
spiral_coords = []
r, c = 64, 64
directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]
dir_idx = 0
step_size = 1
visited = set()
steps = 0

while len(spiral_coords) < 256 and steps < 10000:
 for _ in range(step_size):
 if 0 <= r < 128 and 0 <= c < 128 and (r, c) not in visited:
 spiral_coords.append((r, c))
 visited.add((r, c))
 
 dr, dc = directions[dir_idx]
 r, c = r + dr, c + dc
 
 if len(spiral_coords) >= 256:
 break
 
 dir_idx = (dir_idx + 1) % 4
 if dir_idx % 2 == 0:
 step_size += 1
 steps += 1

spiral_msg = decode_path(spiral_coords)
print(f" Length: {len(spiral_msg)}")
print(f" First 50 chars: {spiral_msg[:50]}")
if "ANNA" in spiral_msg:
 idx = spiral_msg.find("ANNA")
 print(f" ✅ Found 'ANNA' at position {idx}")
 print(f" Context: ...{spiral_msg[max(0,idx-10):idx+20]}...")
print()

# Row-wise
print("2. Row-wise Pattern:")
row_coords = [(r, c) for r in range(128) for c in range(128)][:256]
row_msg = decode_path(row_coords)
print(f" Length: {len(row_msg)}")
print(f" First 50 chars: {row_msg[:50]}")
if "ANNA" in row_msg:
 idx = row_msg.find("ANNA")
 print(f" ✅ Found 'ANNA' at position {idx}")
 print(f" Context: ...{row_msg[max(0,idx-10):idx+20]}...")
print()

# Column-wise
print("3. Column-wise Pattern:")
col_coords = [(r, c) for c in range(128) for r in range(128)][:256]
col_msg = decode_path(col_coords)
print(f" Length: {len(col_msg)}")
print(f" First 50 chars: {col_msg[:50]}")
if "ANNA" in col_msg:
 idx = col_msg.find("ANNA")
 print(f" ✅ Found 'ANNA' at position {idx}")
 print(f" Context: ...{col_msg[max(0,idx-10):idx+20]}...")
print()

# Suche nach "ANNA WAS HERE STOP"
print("=" * 80)
print("SUCHE NACH 'ANNA WAS HERE STOP'")
print("=" * 80)
print()

all_messages = [
 ("Spiral", spiral_msg),
 ("Row-wise", row_msg),
 ("Column-wise", col_msg),
]

for name, msg in all_messages:
 if "ANNA" in msg:
 idx = msg.find("ANNA")
 print(f"✅ '{name}' contains 'ANNA' at position {idx}")
 print(f" Context: ...{msg[max(0,idx-10):idx+50]}...")
 print()
 
 if "STOP" in msg:
 idx = msg.find("STOP")
 print(f"✅ '{name}' contains 'STOP' at position {idx}")
 print(f" Context: ...{msg[max(0,idx-10):idx+20]}...")
 print()
 
 if "WAS" in msg:
 idx = msg.find("WAS")
 print(f"✅ '{name}' contains 'WAS' at position {idx}")
 print(f" Context: ...{msg[max(0,idx-10):idx+20]}...")
 print()

print("=" * 80)
print("TEST COMPLETE")
print("=" * 80)

