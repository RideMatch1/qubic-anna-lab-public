#!/usr/bin/env python3
"""
Find Real Seed for Matrix Identity

Wenn eine Identity in der Matrix ist, dann muss der Seed, der sie produziert,
auch in der Matrix sein. Dieses Script findet den echten Seed.
"""

import sys
import subprocess
from pathlib import Path
import numpy as np
import openpyxl
from typing import Optional, List, Tuple

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

OUTPUT_DIR = project_root / "outputs" / "derived"
REPORTS_DIR = project_root / "outputs" / "reports"
VENV_PYTHON = project_root / "venv-tx" / "bin" / "python"

def load_matrix():
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

def base26_char(value: float) -> str:
 """Konvertiere Matrix-Wert zu Base-26 Char."""
 val = int(value) % 26
 if val < 0:
 val += 26
 return chr(ord('A') + val)

def find_identity_coordinates(matrix_identity: str, matrix: np.ndarray) -> List[Tuple[int, int]]:
 """
 Finde Koordinaten, wo die Identity in der Matrix vorkommt.
 
 Sucht nach der Identity (oder Teilen davon) in der Matrix.
 """
 coords = []
 
 # Extrahiere den Body (erste 56 Zeichen)
 identity_body = matrix_identity[:56].lower()
 
 # Suche nach Patterns in der Matrix
 for r in range(128):
 for c in range(128):
 # Teste horizontale Sequenz
 if c + 56 <= 128:
 seq = ''.join(base26_char(matrix[r, c+i]) for i in range(56))
 if seq.lower() == identity_body:
 coords.append((r, c))
 
 # Teste vertikale Sequenz
 if r + 56 <= 128:
 seq = ''.join(base26_char(matrix[r+i, c]) for i in range(56))
 if seq.lower() == identity_body:
 coords.append((r, c))
 
 return coords

def extract_55_chars_around(matrix: np.ndarray, r: int, c: int, direction: str = 'horizontal') -> Optional[str]:
 """
 Extrahiere 55 Zeichen um eine Koordinate herum.
 
 Richtungen:
 - horizontal: Links/Rechts
 - vertical: Oben/Unten
 - diagonal: Diagonal
 - reverse: Rückwärts
 """
 chars = []
 
 if direction == 'horizontal':
 # Horizontal: Start bei c-27, Ende bei c+27 (55 Zeichen)
 start_c = max(0, c - 27)
 end_c = min(128, start_c + 55)
 if end_c - start_c == 55:
 for col in range(start_c, end_c):
 chars.append(base26_char(matrix[r, col]))
 
 elif direction == 'vertical':
 # Vertikal: Start bei r-27, Ende bei r+27
 start_r = max(0, r - 27)
 end_r = min(128, start_r + 55)
 if end_r - start_r == 55:
 for row in range(start_r, end_r):
 chars.append(base26_char(matrix[row, c]))
 
 elif direction == 'diagonal':
 # Diagonal: Von (r-27, c-27) zu (r+27, c+27)
 start_r = max(0, r - 27)
 start_c = max(0, c - 27)
 if start_r + 55 <= 128 and start_c + 55 <= 128:
 for i in range(55):
 chars.append(base26_char(matrix[start_r + i, start_c + i]))
 
 elif direction == 'reverse_horizontal':
 # Rückwärts horizontal
 end_c = min(128, c + 27)
 start_c = max(0, end_c - 55)
 if end_c - start_c == 55:
 for col in range(end_c - 1, start_c - 1, -1):
 chars.append(base26_char(matrix[r, col]))
 
 if len(chars) == 55:
 return ''.join(chars).lower()
 return None

def derive_identity_from_seed(seed: str) -> Optional[str]:
 """Leite Identity aus Seed ab."""
 if not VENV_PYTHON.exists():
 return None
 
 script = f"""
from qubipy.crypto.utils import (
 get_subseed_from_seed,
 get_private_key_from_subseed,
 get_public_key_from_private_key,
 get_identity_from_public_key,
)

seed = "{seed}"
seed_bytes = seed.encode('utf-8')
subseed = get_subseed_from_seed(seed_bytes)
private_key = get_private_key_from_subseed(subseed)
public_key = get_public_key_from_private_key(private_key)
identity = get_identity_from_public_key(public_key)
print(identity)
"""
 
 try:
 result = subprocess.run(
 [str(VENV_PYTHON), "-c", script],
 capture_output=True,
 text=True,
 timeout=10,
 cwd=project_root
 )
 
 if result.returncode == 0:
 identity = result.stdout.strip()
 if len(identity) == 60 and identity.isupper():
 return identity
 return None
 except Exception:
 return None

def find_real_seed_for_identity(matrix_identity: str, matrix: np.ndarray) -> Optional[Tuple[str, str, Tuple[int, int]]]:
 """
 Finde den echten Seed, der die Matrix-Identity produziert.
 
 Returns: (seed, direction, coordinates) oder None
 """
 print(f"Searching for real seed for identity: {matrix_identity[:40]}...")
 print()
 
 # 1. Finde Identity-Koordinaten
 coords = find_identity_coordinates(matrix_identity, matrix)
 print(f"Found {len(coords)} coordinate(s) where identity appears")
 print()
 
 if not coords:
 print("❌ Identity not found in matrix")
 return None
 
 # 2. Für jede Koordinate: Teste 55-Zeichen-Sequenzen
 directions = ['horizontal', 'vertical', 'diagonal', 'reverse_horizontal']
 
 for coord in coords:
 r, c = coord
 print(f"Testing coordinates ({r}, {c})...")
 
 for direction in directions:
 seed_candidate = extract_55_chars_around(matrix, r, c, direction)
 
 if seed_candidate:
 print(f" Testing {direction}: {seed_candidate[:30]}...")
 derived_identity = derive_identity_from_seed(seed_candidate)
 
 if derived_identity == matrix_identity:
 print(f" ✅ FOUND! Seed: {seed_candidate}")
 print(f" Direction: {direction}")
 print(f" Coordinates: ({r}, {c})")
 return (seed_candidate, direction, coord)
 elif derived_identity:
 print(f" Produces: {derived_identity[:40]}... (not matching)")
 
 print()
 print("❌ No matching seed found")
 return None

def main():
 print("=" * 80)
 print("FIND REAL SEED FOR MATRIX IDENTITY")
 print("=" * 80)
 print()
 
 # Test mit bekanntem Beispiel
 matrix_identity = "AAAAEWAFWVVYUUAAAAEWAFWVVYUUAAAAEWAFWVVYUUAAAAEWAFWVVYUUKVKM"
 
 print("Loading matrix...")
 matrix = load_matrix()
 print(f"✅ Matrix loaded: {matrix.shape}")
 print()
 
 result = find_real_seed_for_identity(matrix_identity, matrix)
 
 if result:
 seed, direction, coords = result
 print()
 print("=" * 80)
 print("SUCCESS!")
 print("=" * 80)
 print(f"Real seed: {seed}")
 print(f"Direction: {direction}")
 print(f"Coordinates: {coords}")
 print()
 
 # Speichere Ergebnis
 OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
 import json
 result_data = {
 "matrix_identity": matrix_identity,
 "real_seed": seed,
 "direction": direction,
 "coordinates": coords,
 }
 
 output_file = OUTPUT_DIR / "real_seed_found.json"
 with output_file.open('w') as f:
 json.dump(result_data, f, indent=2)
 print(f"✅ Result saved to: {output_file}")
 else:
 print()
 print("=" * 80)
 print("NOT FOUND")
 print("=" * 80)
 print("The real seed might be:")
 print("1. In a different location")
 print("2. Encoded differently")
 print("3. Derived from multiple paths")
 print("4. Not directly in the matrix")
 
 print()
 print("=" * 80)
 print("SEARCH COMPLETE")
 print("=" * 80)

if __name__ == "__main__":
 main()

