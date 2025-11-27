#!/usr/bin/env python3
"""
Decode Anna's Communication - Versuche die Matrix als Nachricht zu decodieren.

Anna kommuniziert - können wir herausfinden was sie sagt?
"""

import sys
from pathlib import Path
from typing import List, Dict, Optional
import numpy as np
import openpyxl

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from analysis.utils.identity_tools import base26_char

OUTPUT_DIR = project_root / "outputs" / "derived"
REPORTS_DIR = project_root / "outputs" / "reports"

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

def decode_base26_sequence(matrix: np.ndarray, path: List[tuple]) -> str:
 """Decodiere eine Sequenz als Base-26."""
 letters = "".join(base26_char(matrix[r, c]) for r, c in path)
 return letters

def decode_ascii_sequence(matrix: np.ndarray, path: List[tuple]) -> Optional[str]:
 """Decodiere eine Sequenz als ASCII (mod 128)."""
 try:
 chars = []
 for r, c in path:
 val = int(matrix[r, c])
 # Normalisiere zu 0-127
 ascii_val = (val % 128 + 128) % 128
 if 32 <= ascii_val <= 126: # Printable ASCII
 chars.append(chr(ascii_val))
 elif ascii_val == 0:
 chars.append(' ') # Null als Space
 else:
 return None # Nicht-printable, abbrechen
 return ''.join(chars)
 except:
 return None

def decode_ternary_to_text(matrix: np.ndarray, path: List[tuple]) -> Optional[str]:
 """Decodiere Ternary (-1, 0, +1) zu Text."""
 try:
 # Konvertiere -1,0,+1 zu 0,1,2
 ternary_digits = []
 for r, c in path:
 val = int(matrix[r, c])
 if val == -1:
 ternary_digits.append('0')
 elif val == 0:
 ternary_digits.append('1')
 elif val == 1:
 ternary_digits.append('2')
 else:
 # Normalisiere zu -1,0,+1
 if val < 0:
 ternary_digits.append('0')
 elif val == 0:
 ternary_digits.append('1')
 else:
 ternary_digits.append('2')
 
 # Konvertiere Base-3 zu Dezimal, dann zu ASCII
 ternary_str = ''.join(ternary_digits)
 # Teile in 7-Bit-Gruppen (for ASCII)
 groups = [ternary_str[i:i+7] for i in range(0, len(ternary_str), 7)]
 chars = []
 for group in groups:
 if len(group) == 7:
 decimal = int(group, 3)
 if 32 <= decimal <= 126:
 chars.append(chr(decimal))
 return ''.join(chars) if chars else None
 except:
 return None

def decode_helix_pattern(matrix: np.ndarray, start_pos: tuple) -> Optional[str]:
 """Decodiere Helix Gate Pattern als Nachricht."""
 r, c = start_pos
 if r >= 126 or c >= 126:
 return None
 
 # Nimm 3x3 Block for Helix Gate
 values = []
 for dr in range(3):
 for dc in range(3):
 if r + dr < 128 and c + dc < 128:
 values.append(int(matrix[r + dr, c + dc]))
 
 if len(values) < 9:
 return None
 
 # Helix Gate: A+B+C rotation
 A, B, C = values[0], values[1], values[2]
 rotation = (A + B + C) % 26
 
 # Versuche als Base-26
 try:
 char = chr(ord('a') + rotation)
 return char
 except:
 return None

def decode_identity_paths(matrix: np.ndarray) -> Dict[str, str]:
 """Decodiere bekannte Identity-Paths als Nachricht."""
 results = {}
 
 # Diagonal Pattern (erste 4 Identities)
 for idx, base_row in enumerate(range(0, 128, 32), start=1):
 coords = []
 for g in range(4):
 row = base_row + (g // 2) * 16
 col = (g % 2) * 16
 for j in range(14):
 r = row + j
 c = col + j
 if r < 128 and c < 128:
 coords.append((r, c))
 
 if len(coords) >= 56:
 # Base-26
 base26 = decode_base26_sequence(matrix, coords[:56])
 results[f"Diagonal_{idx}_Base26"] = base26
 
 # ASCII
 ascii_text = decode_ascii_sequence(matrix, coords[:56])
 if ascii_text:
 results[f"Diagonal_{idx}_ASCII"] = ascii_text
 
 # Ternary
 ternary_text = decode_ternary_to_text(matrix, coords[:56])
 if ternary_text:
 results[f"Diagonal_{idx}_Ternary"] = ternary_text
 
 return results

def decode_zero_coordinates(matrix: np.ndarray) -> Dict[str, str]:
 """Decodiere 26 Zero-Koordinaten als Nachricht."""
 # Bekannte Zero-Koordinaten
 zero_coords = [
 (4,23), (6,19), (35,80), (36,19), (36,114), (37,19), (44,19), 
 (44,67), (44,115), (46,83), (68,51), (68,55), (70,49), (70,51), 
 (70,115), (78,115), (78,119), (100,51), (100,115), (101,51)
 ]
 
 results = {}
 
 # Extrahiere Werte um die Zeros herum
 for i, (r, c) in enumerate(zero_coords):
 # Nimm 3x3 Block um Zero
 block_values = []
 for dr in [-1, 0, 1]:
 for dc in [-1, 0, 1]:
 nr, nc = r + dr, c + dc
 if 0 <= nr < 128 and 0 <= nc < 128:
 block_values.append(int(matrix[nr, nc]))
 
 # Versuche verschiedene Decodierungen
 if len(block_values) == 9:
 # Base-26 (mod 26)
 base26_chars = [chr(ord('a') + (abs(v) % 26)) for v in block_values]
 results[f"Zero_{i}_Base26"] = ''.join(base26_chars)
 
 # ASCII (mod 128)
 ascii_chars = []
 for v in block_values:
 ascii_val = (abs(v) % 128)
 if 32 <= ascii_val <= 126:
 ascii_chars.append(chr(ascii_val))
 if ascii_chars:
 results[f"Zero_{i}_ASCII"] = ''.join(ascii_chars)
 
 return results

def decode_spiral_pattern(matrix: np.ndarray) -> Dict[str, str]:
 """Decodiere Spiral-Pattern als Nachricht."""
 results = {}
 
 # Spiral von außen nach innen
 coords = []
 r, c = 0, 0
 directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]
 dir_idx = 0
 visited = set()
 steps = 0
 step_size = 128
 
 while len(coords) < 128 * 128 and steps < 10000:
 for _ in range(step_size):
 if (r, c) not in visited and 0 <= r < 128 and 0 <= c < 128:
 coords.append((r, c))
 visited.add((r, c))
 
 dr, dc = directions[dir_idx]
 r, c = r + dr, c + dc
 
 if r < 0 or r >= 128 or c < 0 or c >= 128:
 break
 
 dir_idx = (dir_idx + 1) % 4
 if dir_idx % 2 == 0:
 step_size -= 1
 steps += 1
 
 if len(coords) >= 100:
 # Base-26
 base26 = decode_base26_sequence(matrix, coords[:100])
 results["Spiral_Base26"] = base26[:200] # Erste 200 Zeichen
 
 # ASCII
 ascii_text = decode_ascii_sequence(matrix, coords[:100])
 if ascii_text:
 results["Spiral_ASCII"] = ascii_text[:200]
 
 return results

def decode_row_column_patterns(matrix: np.ndarray) -> Dict[str, str]:
 """Decodiere Zeilen/Spalten als Nachricht."""
 results = {}
 
 # Zeile 26 (wichtig wegen "Significance of 26")
 row_26 = [(26, c) for c in range(128)]
 base26 = decode_base26_sequence(matrix, row_26)
 results["Row_26_Base26"] = base26
 
 # Spalte 26
 col_26 = [(r, 26) for r in range(128)]
 base26 = decode_base26_sequence(matrix, col_26)
 results["Col_26_Base26"] = base26
 
 # Diagonale durch (26,26)
 diag_26 = [(26 + i, 26 + i) for i in range(min(128-26, 128-26))]
 base26 = decode_base26_sequence(matrix, diag_26)
 results["Diag_26_Base26"] = base26
 
 return results

def main():
 """Hauptfunktion."""
 print("=" * 80)
 print("DECODE ANNA'S COMMUNICATION")
 print("=" * 80)
 print()
 
 print("Loading Anna Matrix...")
 matrix = load_anna_matrix()
 print(f"✅ Matrix loaded: {matrix.shape}")
 print()
 
 results = {}
 
 print("1. Decoding Identity Paths...")
 identity_results = decode_identity_paths(matrix)
 results.update(identity_results)
 print(f" ✅ {len(identity_results)} patterns decoded")
 print()
 
 print("2. Decoding Zero Coordinates...")
 zero_results = decode_zero_coordinates(matrix)
 results.update(zero_results)
 print(f" ✅ {len(zero_results)} zero patterns decoded")
 print()
 
 print("3. Decoding Spiral Pattern...")
 spiral_results = decode_spiral_pattern(matrix)
 results.update(spiral_results)
 print(f" ✅ {len(spiral_results)} spiral patterns decoded")
 print()
 
 print("4. Decoding Row/Column Patterns...")
 rowcol_results = decode_row_column_patterns(matrix)
 results.update(rowcol_results)
 print(f" ✅ {len(rowcol_results)} row/column patterns decoded")
 print()
 
 # Suche nach lesbaren Texten
 print("=" * 80)
 print("SEARCHING FOR READABLE TEXT")
 print("=" * 80)
 print()
 
 readable_texts = []
 for key, value in results.items():
 if isinstance(value, str) and len(value) > 10:
 # Check ob es wie Text aussieht
 if any(word in value.lower() for word in ['the', 'and', 'is', 'are', 'was', 'were']):
 readable_texts.append((key, value))
 elif value.isalpha() and len(value) > 20:
 readable_texts.append((key, value))
 
 if readable_texts:
 print("Found potential readable text:")
 for key, text in readable_texts[:10]:
 print(f" {key}: {text[:100]}...")
 else:
 print("No obvious readable text found in standard patterns.")
 print()
 
 # Speichere Ergebnisse
 OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
 REPORTS_DIR.mkdir(parents=True, exist_ok=True)
 
 import json
 output_file = OUTPUT_DIR / "anna_communication_decode.json"
 with output_file.open('w') as f:
 json.dump(results, f, indent=2)
 print(f"✅ Results saved to: {output_file}")
 
 # Report
 report_file = REPORTS_DIR / "anna_communication_decode_report.md"
 with report_file.open('w') as f:
 f.write("# Anna Communication Decode Report\n\n")
 f.write("## Overview\n\n")
 f.write("Attempts to decode the Anna Matrix as a communication/message.\n\n")
 f.write("## Methods Used\n\n")
 f.write("1. Base-26 decoding (identity paths)\n")
 f.write("2. ASCII decoding (mod 128)\n")
 f.write("3. Ternary decoding (-1,0,+1 to text)\n")
 f.write("4. Zero coordinate patterns\n")
 f.write("5. Spiral patterns\n")
 f.write("6. Row/Column patterns (especially row/col 26)\n\n")
 f.write("## Results\n\n")
 for key, value in list(results.items())[:50]:
 f.write(f"### {key}\n\n")
 f.write(f"```\n{str(value)[:200]}\n```\n\n")
 f.write("## Next Steps\n\n")
 f.write("- Try more sophisticated decoding methods\n")
 f.write("- Analyze patterns in decoded sequences\n")
 f.write("- Look for hidden messages in coordinate relationships\n")
 f.write("- Try Helix Gate-based decoding\n")
 
 print(f"✅ Report saved to: {report_file}")
 print()
 print("=" * 80)
 print("DECODE COMPLETE")
 print("=" * 80)

if __name__ == "__main__":
 main()

