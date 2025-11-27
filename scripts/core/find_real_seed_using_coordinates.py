#!/usr/bin/env python3
"""
Find Real Seed Using Identity Extraction Coordinates

Wenn wir wissen, wo eine Identity in der Matrix extrahiert wurde,
können wir um diese Koordinaten herum nach dem echten Seed suchen.
"""

import sys
import subprocess
from pathlib import Path
import numpy as np
import openpyxl
from typing import Optional, List, Tuple
import json

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
 return chr(ord('a') + val).lower()

def extract_55_chars_from_coords(matrix: np.ndarray, start_r: int, start_c: int, direction: str = 'horizontal') -> Optional[str]:
 """
 Extrahiere 55 Zeichen ab einer Start-Koordinate.
 
 Richtungen:
 - horizontal: Rechts
 - vertical: Unten
 - diagonal: Diagonal (rechts-unten)
 - reverse_horizontal: Links
 - reverse_vertical: Oben
 - reverse_diagonal: Diagonal (links-oben)
 """
 chars = []
 
 if direction == 'horizontal':
 if start_c + 55 <= 128:
 for col in range(start_c, start_c + 55):
 chars.append(base26_char(matrix[start_r, col]))
 
 elif direction == 'vertical':
 if start_r + 55 <= 128:
 for row in range(start_r, start_r + 55):
 chars.append(base26_char(matrix[row, start_c]))
 
 elif direction == 'diagonal':
 if start_r + 55 <= 128 and start_c + 55 <= 128:
 for i in range(55):
 chars.append(base26_char(matrix[start_r + i, start_c + i]))
 
 elif direction == 'reverse_horizontal':
 if start_c >= 54:
 for col in range(start_c, start_c - 55, -1):
 chars.append(base26_char(matrix[start_r, col]))
 
 elif direction == 'reverse_vertical':
 if start_r >= 54:
 for row in range(start_r, start_r - 55, -1):
 chars.append(base26_char(matrix[row, start_c]))
 
 elif direction == 'reverse_diagonal':
 if start_r >= 54 and start_c >= 54:
 for i in range(55):
 chars.append(base26_char(matrix[start_r - i, start_c - i]))
 
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

def find_seed_around_identity_coords(matrix: np.ndarray, identity_coords: List[Tuple[int, int]], expected_identity: str) -> Optional[Tuple[str, str, Tuple[int, int]]]:
 """
 Suche nach dem echten Seed um die Identity-Koordinaten herum.
 
 Args:
 matrix: Anna Matrix
 identity_coords: Liste von Koordinaten, wo die Identity extrahiert wurde
 expected_identity: Die erwartete Identity
 
 Returns: (seed, direction, start_coord) oder None
 """
 print(f"Searching for real seed around {len(identity_coords)} identity coordinates...")
 print(f"Expected identity: {expected_identity[:40]}...")
 print()
 
 # Teste verschiedene Start-Positionen und Richtungen
 directions = ['horizontal', 'vertical', 'diagonal', 'reverse_horizontal', 'reverse_vertical', 'reverse_diagonal']
 
 # Teste um jede Koordinate herum
 total_tests = 0
 for idx, coord in enumerate(identity_coords):
 r, c = coord
 if idx % 10 == 0:
 print(f"Testing coordinate {idx+1}/{len(identity_coords)}: ({r}, {c})...")
 
 # Teste verschiedene Offsets (reduziert for Performance)
 offsets = [-30, -20, -10, 0, 10, 20, 30]
 
 for offset_r in offsets:
 for offset_c in offsets:
 test_r = r + offset_r
 test_c = c + offset_c
 
 if test_r < 0 or test_c < 0 or test_r >= 128 or test_c >= 128:
 continue
 
 for direction in directions:
 seed_candidate = extract_55_chars_from_coords(matrix, test_r, test_c, direction)
 
 if seed_candidate:
 total_tests += 1
 if total_tests % 50 == 0:
 print(f" Tested {total_tests} seed candidates...")
 
 derived_identity = derive_identity_from_seed(seed_candidate)
 
 if derived_identity == expected_identity:
 print(f" ✅ FOUND! Seed: {seed_candidate}")
 print(f" Direction: {direction}")
 print(f" Start: ({test_r}, {test_c})")
 print(f" Offset from identity: ({offset_r}, {offset_c})")
 print(f" Total tests: {total_tests}")
 return (seed_candidate, direction, (test_r, test_c))
 
 print(f" ❌ No matching seed found after {total_tests} tests")
 return None

def get_identity_extraction_coords_from_comprehensive_scan(identity: str) -> List[Tuple[int, int]]:
 """
 Versuche die Extraktions-Koordinaten aus dem Comprehensive Scan zu finden.
 
 Für jetzt: Verwende strategische Start-Positionen basierend auf bekannten Patterns.
 """
 # Strategische Start-Positionen basierend auf bekannten Extraktions-Mustern
 # Diagonal: Start bei (0,0), (32,0), (64,0), (96,0) etc.
 # Vortex: Center bei (64,64)
 # Comprehensive: Verschiedene Start-Positionen
 
 coords = []
 
 # Diagonal-Pattern Start-Positionen
 for base_row in range(0, 128, 32):
 for base_col in range(0, 128, 32):
 coords.append((base_row, base_col))
 
 # Vortex Center und Umgebung
 for offset_r in range(-10, 11, 5):
 for offset_c in range(-10, 11, 5):
 coords.append((64 + offset_r, 64 + offset_c))
 
 # Zusätzliche strategische Positionen
 for r in range(0, 128, 16):
 for c in range(0, 128, 16):
 if (r, c) not in coords:
 coords.append((r, c))
 
 return coords[:100] # Limit for Performance

def main():
 print("=" * 80)
 print("FIND REAL SEED USING IDENTITY COORDINATES")
 print("=" * 80)
 print()
 
 # Test mit bekanntem Beispiel
 matrix_identity = "AAAAEWAFWVVYUUAAAAEWAFWVVYUUAAAAEWAFWVVYUUAAAAEWAFWVVYUUKVKM"
 
 print("Loading matrix...")
 matrix = load_matrix()
 print(f"✅ Matrix loaded: {matrix.shape}")
 print()
 
 print("Getting identity extraction coordinates...")
 identity_coords = get_identity_extraction_coords_from_comprehensive_scan(matrix_identity)
 print(f"✅ Testing {len(identity_coords)} coordinate regions")
 print()
 
 result = find_seed_around_identity_coords(matrix, identity_coords, matrix_identity)
 
 if result:
 seed, direction, coords = result
 print()
 print("=" * 80)
 print("SUCCESS!")
 print("=" * 80)
 print(f"Real seed: {seed}")
 print(f"Direction: {direction}")
 print(f"Start coordinates: {coords}")
 print()
 
 # Speichere Ergebnis
 OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
 result_data = {
 "matrix_identity": matrix_identity,
 "real_seed": seed,
 "direction": direction,
 "start_coordinates": coords,
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
 print("1. In a different location (not around identity coordinates)")
 print("2. Encoded differently")
 print("3. Derived from multiple paths")
 print("4. Not directly in the matrix")
 
 print()
 print("=" * 80)
 print("SEARCH COMPLETE")
 print("=" * 80)

if __name__ == "__main__":
 main()

