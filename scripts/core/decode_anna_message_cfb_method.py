#!/usr/bin/env python3
"""
Decode Anna's Message - CFB Method

Basierend auf CFB Discord Hint:
- 128x128 grid
- Normal value = x + y (Koordinaten von -64 bis 63)
- Distortion: x + y - 116 near dark matter (zeros)
- Letter mapping: 1=A, 2=B, ..., 26=Z
- 256 characters forming the message
- Target: "ANNA WAS HERE STOP"
"""

import sys
from pathlib import Path
import numpy as np
import openpyxl

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

OUTPUT_DIR = project_root / "outputs" / "derived"
REPORTS_DIR = project_root / "outputs" / "reports"

# Bekannte Zero-Koordinaten (Dark Matter)
ZERO_COORDS = [
 (4,23), (6,19), (35,80), (36,19), (36,114), (37,19), (44,19), 
 (44,67), (44,115), (46,83), (68,51), (68,55), (70,49), (70,51), 
 (70,115), (78,115), (78,119), (100,51), (100,115), (101,51)
]

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

def is_near_dark_matter(r: int, c: int, threshold: int = 5) -> bool:
 """Check ob Koordinate nahe Dark Matter (Zero) ist."""
 for zr, zc in ZERO_COORDS:
 if abs(r - zr) <= threshold and abs(c - zc) <= threshold:
 return True
 return False

def decode_cfb_method(matrix: np.ndarray) -> Dict:
 """Decodiere nach CFB Methode."""
 results = {
 "message": "",
 "coordinates_used": [],
 "decoding_details": []
 }
 
 # Koordinaten von (-64, -64) bis (63, 63)
 # Matrix-Indizes: 0-127
 # Mapping: matrix[r][c] entspricht Koordinate (r-64, c-64)
 
 message_chars = []
 coordinates = []
 
 # Versuche verschiedene Paths
 paths_to_try = [
 # Spiral von außen nach innen
 "spiral",
 # Zeile for Zeile
 "row_wise",
 # Spalte for Spalte
 "col_wise",
 # Diagonale
 "diagonal",
 # Identity-Paths
 "identity_paths",
 ]
 
 for path_type in paths_to_try:
 coords = get_path_coordinates(path_type)
 decoded = decode_path(matrix, coords)
 
 if decoded:
 results[f"{path_type}_message"] = decoded
 results[f"{path_type}_coords"] = coords[:256]
 
 return results

def get_path_coordinates(path_type: str) -> List[tuple]:
 """Generiere Koordinaten-Pfad."""
 coords = []
 
 if path_type == "spiral":
 # Spiral von (0,0) nach außen
 r, c = 64, 64 # Center
 directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]
 dir_idx = 0
 step_size = 1
 steps = 0
 visited = set()
 
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
 
 elif path_type == "row_wise":
 for r in range(128):
 for c in range(128):
 if len(coords) < 256:
 coords.append((r, c))
 
 elif path_type == "col_wise":
 for c in range(128):
 for r in range(128):
 if len(coords) < 256:
 coords.append((r, c))
 
 elif path_type == "diagonal":
 for offset in range(256):
 r = offset % 128
 c = (offset // 128 + offset) % 128
 if len(coords) < 256:
 coords.append((r, c))
 
 elif path_type == "identity_paths":
 # Nutze bekannte Identity-Paths
 for base_row in range(0, 128, 32):
 for g in range(4):
 row = base_row + (g // 2) * 16
 col = (g % 2) * 16
 for j in range(14):
 r = row + j
 c = col + j
 if len(coords) < 256 and 0 <= r < 128 and 0 <= c < 128:
 coords.append((r, c))
 
 return coords[:256]

def decode_path(matrix: np.ndarray, coords: List[tuple]) -> Optional[str]:
 """Decodiere einen Pfad nach CFB Methode."""
 chars = []
 
 for r, c in coords:
 # Konvertiere Matrix-Koordinaten zu CFB-Koordinaten (-64 bis 63)
 x = r - 64
 y = c - 64
 
 # Normal value = x + y
 normal_value = x + y
 
 # Distortion: x + y - 116 near dark matter
 if is_near_dark_matter(r, c):
 value = normal_value - 116
 else:
 value = normal_value
 
 # Normalisiere zu 1-26 (A-Z)
 letter_value = ((value % 26) + 26) % 26 + 1
 
 # Letter mapping: 1=A, 2=B, ..., 26=Z
 if 1 <= letter_value <= 26:
 char = chr(ord('A') + letter_value - 1)
 chars.append(char)
 else:
 chars.append('?')
 
 message = ''.join(chars)
 
 # Check ob "ANNA" oder "STOP" enthalten
 if "ANNA" in message or "STOP" in message or "WAS" in message or "HERE" in message:
 return message
 
 return None

def decode_specific_coordinates(matrix: np.ndarray) -> Dict:
 """Decodiere spezifische Koordinaten aus CFB Hint."""
 results = {}
 
 # CFB Beispiel-Koordinaten:
 # (0, 1) = 1 → A
 # (1, 13) = 14 → N
 # (2, 12) = 14 → N
 # (0, 2) = 1 → A
 
 # Matrix-Koordinaten: CFB (x,y) → Matrix (x+64, y+64)
 test_coords = [
 (64, 65), # CFB (0, 1) → Matrix (64, 65)
 (65, 77), # CFB (1, 13) → Matrix (65, 77)
 (66, 76), # CFB (2, 12) → Matrix (66, 76)
 (64, 66), # CFB (0, 2) → Matrix (64, 66)
 ]
 
 decoded = []
 for r, c in test_coords:
 if 0 <= r < 128 and 0 <= c < 128:
 x = r - 64
 y = c - 64
 normal_value = x + y
 
 if is_near_dark_matter(r, c):
 value = normal_value - 116
 else:
 value = normal_value
 
 letter_value = ((value % 26) + 26) % 26 + 1
 char = chr(ord('A') + letter_value - 1)
 decoded.append((f"CFB({x},{y})", f"Matrix({r},{c})", value, letter_value, char))
 results[f"coord_{r}_{c}"] = {
 "cfb_coord": (x, y),
 "matrix_coord": (r, c),
 "normal_value": normal_value,
 "letter_value": letter_value,
 "char": char,
 "matrix_actual_value": float(matrix[r, c])
 }
 
 return results

def main():
 """Hauptfunktion."""
 print("=" * 80)
 print("DECODE ANNA'S MESSAGE - CFB METHOD")
 print("=" * 80)
 print()
 
 print("Loading Anna Matrix...")
 matrix = load_anna_matrix()
 print(f"✅ Matrix loaded: {matrix.shape}")
 print()
 
 print("Testing CFB specific coordinates...")
 specific_results = decode_specific_coordinates(matrix)
 for key, data in specific_results.items():
 print(f" {key}:")
 print(f" CFB Coord: {data['cfb_coord']}")
 print(f" Matrix Coord: {data['matrix_coord']}")
 print(f" Normal Value: {data['normal_value']}")
 print(f" Letter Value: {data['letter_value']}")
 print(f" Decoded Char: {data['char']}")
 print(f" Matrix Actual Value: {data['matrix_actual_value']}")
 print()
 
 print("Decoding various paths...")
 path_results = decode_cfb_method(matrix)
 
 # Suche nach "ANNA WAS HERE STOP"
 print("=" * 80)
 print("SEARCHING FOR 'ANNA WAS HERE STOP'")
 print("=" * 80)
 print()
 
 found_messages = []
 for key, value in path_results.items():
 if isinstance(value, str) and len(value) >= 10:
 if "ANNA" in value or "STOP" in value:
 found_messages.append((key, value))
 print(f"✅ Found in {key}:")
 print(f" {value[:100]}...")
 print()
 
 if not found_messages:
 print("⚠️ 'ANNA WAS HERE STOP' not found in standard paths.")
 print(" Trying alternative decoding methods...")
 print()
 
 # Speichere Ergebnisse
 OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
 REPORTS_DIR.mkdir(parents=True, exist_ok=True)
 
 import json
 output_file = OUTPUT_DIR / "anna_message_cfb_decode.json"
 all_results = {
 "specific_coordinates": specific_results,
 "path_results": path_results,
 "found_messages": found_messages
 }
 with output_file.open('w') as f:
 json.dump(all_results, f, indent=2)
 print(f"✅ Results saved to: {output_file}")
 
 # Report
 report_file = REPORTS_DIR / "anna_message_cfb_decode_report.md"
 with report_file.open('w') as f:
 f.write("# Anna Message Decode Report - CFB Method\n\n")
 f.write("## Overview\n\n")
 f.write("Attempts to decode Anna's message using CFB's suggested method.\n\n")
 f.write("## CFB Method\n\n")
 f.write("- Normal value = x + y (coordinates from -64 to 63)\n")
 f.write("- Distortion: x + y - 116 near dark matter (zeros)\n")
 f.write("- Letter mapping: 1=A, 2=B, ..., 26=Z\n")
 f.write("- 256 characters forming the message\n")
 f.write("- Target: \"ANNA WAS HERE STOP\"\n\n")
 f.write("## Specific Coordinates Test\n\n")
 for key, data in specific_results.items():
 f.write(f"### {key}\n\n")
 f.write(f"- CFB Coord: {data['cfb_coord']}\n")
 f.write(f"- Matrix Coord: {data['matrix_coord']}\n")
 f.write(f"- Normal Value: {data['normal_value']}\n")
 f.write(f"- Letter Value: {data['letter_value']}\n")
 f.write(f"- Decoded Char: {data['char']}\n")
 f.write(f"- Matrix Actual Value: {data['matrix_actual_value']}\n\n")
 f.write("## Path Results\n\n")
 for key, value in list(path_results.items())[:10]:
 f.write(f"### {key}\n\n")
 if isinstance(value, str):
 f.write(f"```\n{value[:200]}\n```\n\n")
 else:
 f.write(f"```json\n{json.dumps(value, indent=2)[:200]}\n```\n\n")
 f.write("## Next Steps\n\n")
 f.write("- Try more coordinate transformations\n")
 f.write("- Analyze dark matter distortion patterns\n")
 f.write("- Test different path sequences\n")
 f.write("- Look for "ANNA WAS HERE STOP" in decoded sequences\n")
 
 print(f"✅ Report saved to: {report_file}")
 print()
 print("=" * 80)
 print("DECODE COMPLETE")
 print("=" * 80)

if __name__ == "__main__":
 from typing import Dict, List, Optional
 main()

