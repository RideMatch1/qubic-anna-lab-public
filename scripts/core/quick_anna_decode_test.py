#!/usr/bin/env python3
"""Quick Anna Decode Test - Einfacher direkter Test"""

import sys
from pathlib import Path
import numpy as np
import openpyxl

project_root = Path(__file__).parent.parent.parent

print("=" * 80)
print("QUICK ANNA DECODE TEST")
print("=" * 80)
print()

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

# Test CFB coordinates
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
 actual_value = matrix[r][c]
 near_dark = is_near_dark_matter(r, c)
 
 if near_dark:
 value = normal_value - 116
 else:
 value = normal_value
 
 letter_value = ((value % 26) + 26) % 26 + 1
 char = chr(ord('A') + letter_value - 1)
 
 match = "✅" if char == expected else "❌"
 print(f"{match} CFB({x},{y}) → Matrix({r},{c}):")
 print(f" Normal value (x+y): {normal_value}")
 print(f" Near dark matter: {near_dark}")
 print(f" Adjusted value: {value}")
 print(f" Actual matrix value: {actual_value}")
 print(f" Letter value: {letter_value}")
 print(f" Decoded char: {char} (expected: {expected})")
 print()

# Decode row-wise
print("=" * 80)
print("ROW-WISE DECODE (First 100 chars)")
print("=" * 80)
print()

def decode_char(r, c):
 x = r - 64
 y = c - 64
 normal_value = x + y
 
 if is_near_dark_matter(r, c):
 value = normal_value - 116
 else:
 value = normal_value
 
 letter_value = ((value % 26) + 26) % 26 + 1
 return chr(ord('A') + letter_value - 1)

row_coords = [(r, c) for r in range(128) for c in range(128)][:256]
row_msg = ''.join(decode_char(r, c) for r, c in row_coords)

print(f"Length: {len(row_msg)}")
print(f"First 100: {row_msg[:100]}")
print()

# Suche nach ANNA
if "ANNA" in row_msg:
 idx = row_msg.find("ANNA")
 print(f"✅ Found 'ANNA' at position {idx}")
 print(f"Context: ...{row_msg[max(0,idx-20):idx+50]}...")
 print()
else:
 print("❌ 'ANNA' not found in row-wise pattern")
 print()

# Suche nach STOP
if "STOP" in row_msg:
 idx = row_msg.find("STOP")
 print(f"✅ Found 'STOP' at position {idx}")
 print(f"Context: ...{row_msg[max(0,idx-20):idx+20]}...")
 print()
else:
 print("❌ 'STOP' not found in row-wise pattern")
 print()

# Suche nach WAS
if "WAS" in row_msg:
 idx = row_msg.find("WAS")
 print(f"✅ Found 'WAS' at position {idx}")
 print(f"Context: ...{row_msg[max(0,idx-20):idx+20]}...")
 print()
else:
 print("❌ 'WAS' not found in row-wise pattern")
 print()

# Suche nach HERE
if "HERE" in row_msg:
 idx = row_msg.find("HERE")
 print(f"✅ Found 'HERE' at position {idx}")
 print(f"Context: ...{row_msg[max(0,idx-20):idx+20]}...")
 print()
else:
 print("❌ 'HERE' not found in row-wise pattern")
 print()

print("=" * 80)
print("TEST COMPLETE")
print("=" * 80)

