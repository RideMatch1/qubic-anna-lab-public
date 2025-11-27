#!/usr/bin/env python3
"""
Tiefgründige Grid-Matrix Synthese
- Analyze exakte Matrix-Koordinaten for Position 27
- Verbinde Grid (6,3) mit Matrix-Koordinaten
- Analyze Spalte 6 im Grid-context
- Kritisch hinterfragen und verifizieren
- KEINE Halluzinationen - nur echte Daten!
"""

import json
import sys
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from collections import Counter, defaultdict
from datetime import datetime
import numpy as np

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# Paths
ALL_MESSAGES = project_root / "outputs" / "derived" / "all_anna_messages.json"
GRID_ANALYSIS = project_root / "outputs" / "derived" / "grid_matrix_connection_analysis.json"
MATRIX_COORD = project_root / "outputs" / "derived" / "matrix_coordinate_analysis.json"
POS27_MATRIX = project_root / "outputs" / "derived" / "position27_matrix_relationship.json"
LAYER3_FILE = project_root / "outputs" / "derived" / "layer3_derivation_23k_complete.json"
# Versuche verschiedene Matrix-Paths
ANNA_MATRIX_PATHS = [
 project_root / "data" / "anna-matrix" / "Anna_Matrix.xlsx",
 project_root / "data" / "Anna_Matrix.xlsx",
 project_root / "data" / "anna_matrix.json",
]
OUTPUT_DIR = project_root / "outputs" / "derived"
REPORTS_DIR = project_root / "outputs" / "reports"

def load_anna_matrix() -> Optional[np.ndarray]:
 """Load Anna Matrix."""
 import pandas as pd
 
 # Versuche verschiedene Paths
 matrix_file = None
 for path in ANNA_MATRIX_PATHS:
 if path.exists():
 matrix_file = path
 break
 
 if matrix_file is None:
 print(f"⚠️ Anna Matrix nicht gefunden in: {[str(p) for p in ANNA_MATRIX_PATHS]}")
 return None
 
 try:
 # Excel-Datei
 if matrix_file.suffix == '.xlsx':
 df = pd.read_excel(matrix_file, header=None)
 numeric = df.apply(pd.to_numeric, errors="coerce").fillna(0.0)
 matrix = numeric.to_numpy(dtype=float)
 # JSON-Datei
 elif matrix_file.suffix == '.json':
 with matrix_file.open() as f:
 data = json.load(f)
 if isinstance(data, list):
 matrix = np.array(data)
 elif isinstance(data, dict):
 if "matrix" in data:
 matrix = np.array(data["matrix"])
 elif "data" in data:
 matrix = np.array(data["data"])
 else:
 matrix = np.array(list(data.values()))
 else:
 matrix = np.array(data)
 else:
 print(f"⚠️ Unbekanntes Dateiformat: {matrix_file.suffix}")
 return None
 
 # Stelle sicher dass es 128x128 ist (oder 129x129 mit Header)
 if matrix.shape == (129, 129):
 # Entferne erste Zeile und Spalte (Header)
 matrix = matrix[1:, 1:]
 elif matrix.shape == (128, 128):
 pass # Perfekt
 else:
 print(f"⚠️ Matrix hat falsche Form: {matrix.shape}, erwartet (128, 128) oder (129, 129)")
 return None
 
 # Finale Prüfung
 if matrix.shape != (128, 128):
 print(f"⚠️ Matrix hat nach Korrektur falsche Form: {matrix.shape}")
 return None
 
 return matrix
 except Exception as e:
 print(f"❌ Fehler beim Loadn der Matrix: {e}")
 import traceback
 traceback.print_exc()
 return None

def get_identity_extraction_pattern() -> Dict:
 """Load Identity-Extraktions-Pattern."""
 
 if not MATRIX_COORD.exists():
 return {}
 
 with MATRIX_COORD.open() as f:
 data = json.load(f)
 
 return data

def calculate_position_to_matrix_mapping(position: int, extraction_pattern: Dict) -> List[Tuple[int, int, str]]:
 """
 Berechne Matrix-Koordinaten for eine Identity-Position.
 
 Position 27 = Block 1, Position 13 im Block
 Block 1 = Positionen 14-27
 """
 
 # Block-Struktur: 4 Blocks à 14 Characters
 block = position // 14
 pos_in_block = position % 14
 
 # Position 27 = Block 1, Position 13 im Block
 # Block 1 = Positionen 14-27
 
 possible_mappings = []
 
 # Hypothese 1: Direkte Diagonal-Extraktion (wie Layer-1)
 # Block 1 könnte aus verschiedenen Regionen kommen
 # Analyze alle möglichen Extraktions-Patterns
 
 if "diagonal_coordinates" in extraction_pattern:
 for coord_data in extraction_pattern["diagonal_coordinates"]:
 identity_idx = coord_data.get("identity_index", 0)
 block_idx = coord_data.get("block_index", 0)
 
 # Wenn Block 1
 if block_idx == 1:
 all_coords = coord_data.get("all_coordinates", [])
 if pos_in_block < len(all_coords):
 coord = all_coords[pos_in_block]
 possible_mappings.append((
 coord[0], 
 coord[1], 
 f"diagonal_identity{identity_idx}_block{block_idx}"
 ))
 
 # Hypothese 2: Zeile 27, Spalte = Position im Block
 possible_mappings.append((27, pos_in_block, "direct_row27"))
 
 # Hypothese 3: Block-basierte Mapping
 # Block 1 könnte aus Zeile 14-27 kommen
 block_row = 14 + pos_in_block
 possible_mappings.append((block_row, pos_in_block, "block_based"))
 
 # Hypothese 4: Symmetrisch
 possible_mappings.append((128 - 27, pos_in_block, "symmetric"))
 
 # Hypothese 5: Spalte 27
 possible_mappings.append((pos_in_block, 27, "direct_col27"))
 
 return possible_mappings

def analyze_matrix_values_at_coordinates(matrix: np.ndarray, coordinates: List[Tuple[int, int, str]]) -> Dict:
 """Analyze Matrix-Werte an verschiedenen Koordinaten."""
 
 results = {}
 
 for row, col, hypothesis in coordinates:
 if 0 <= row < 128 and 0 <= col < 128:
 value = int(matrix[row, col])
 mod_26 = value % 26
 
 results[hypothesis] = {
 "coordinate": (row, col),
 "value": value,
 "mod_26": mod_26,
 "char": chr(ord('A') + mod_26) if 0 <= mod_26 < 26 else "?"
 }
 
 return results

def analyze_grid_column6_to_matrix(grid_analysis: Dict, matrix: np.ndarray) -> Dict:
 """Analyze Verbindung zwischen Grid Spalte 6 und Matrix."""
 
 # Spalte 6 im Grid enthält alle Block-Ende-Positionen
 # Position 13: Grid (6, 1) -> Identity Position 13
 # Position 27: Grid (6, 3) -> Identity Position 27
 # Position 41: Grid (6, 5) -> Identity Position 41
 # Position 55: Grid (6, 7) -> Identity Position 55
 
 block_end_positions = [13, 27, 41, 55]
 column6_analysis = {}
 
 for pos in block_end_positions:
 block = pos // 14
 pos_in_block = pos % 14
 
 # Mögliche Matrix-Koordinaten
 possible_coords = [
 (pos, pos_in_block, f"direct_pos{pos}"),
 (block * 14 + pos_in_block, 0, f"block_based_pos{pos}"),
 (128 - pos, pos_in_block, f"symmetric_pos{pos}")
 ]
 
 matrix_values = analyze_matrix_values_at_coordinates(matrix, possible_coords)
 
 column6_analysis[f"position_{pos}"] = {
 "grid_coords": (6, pos // 7), # Vereinfacht
 "block": block,
 "pos_in_block": pos_in_block,
 "possible_matrix_coords": matrix_values
 }
 
 return column6_analysis

def analyze_matrix_column6(matrix: np.ndarray) -> Dict:
 """Analyze Matrix-Spalte 6 direkt."""
 
 if matrix.shape[1] < 7:
 return {}
 
 col_6 = matrix[:, 6]
 
 return {
 "mean": float(np.mean(col_6)),
 "std": float(np.std(col_6)),
 "zeros": int(np.sum(col_6 == 0)),
 "unique_values": len(np.unique(col_6)),
 "min": float(np.min(col_6)),
 "max": float(np.max(col_6)),
 "sample_values": [int(col_6[i]) for i in [13, 27, 41, 55] if i < len(col_6)]
 }

def analyze_matrix_row27(matrix: np.ndarray) -> Dict:
 """Analyze Matrix-Zeile 27."""
 
 if matrix.shape[0] < 28:
 return {}
 
 row_27 = matrix[27, :]
 
 return {
 "mean": float(np.mean(row_27)),
 "std": float(np.std(row_27)),
 "zeros": int(np.sum(row_27 == 0)),
 "unique_values": len(np.unique(row_27)),
 "min": float(np.min(row_27)),
 "max": float(np.max(row_27)),
 "value_at_col6": int(row_27[6]) if len(row_27) > 6 else None,
 "value_at_col13": int(row_27[13]) if len(row_27) > 13 else None
 }

def main():
 """Hauptfunktion."""
 
 print("=" * 80)
 print("TIEFGRÜNDIGE GRID-MATRIX SYNTHESE")
 print("=" * 80)
 print()
 print("⚠️ KEINE HALLUZINATIONEN - NUR ECHTE DATEN!")
 print("🔬 KRITISCH HINTERFRAGEN, VERIFIZIEREN, PERFEKT")
 print()
 
 # 1. Load Anna Matrix
 print("📂 Load Anna Matrix...")
 matrix = load_anna_matrix()
 if matrix is None:
 print("❌ Konnte Matrix nicht loadn - stoppe Analyse")
 return
 print(f"✅ Matrix geloadn: {matrix.shape}")
 print()
 
 # 2. Load Extraktions-Pattern
 print("📂 Load Identity-Extraktions-Pattern...")
 extraction_pattern = get_identity_extraction_pattern()
 if extraction_pattern:
 print(f"✅ Pattern geloadn: {len(extraction_pattern.get('diagonal_coordinates', []))} Diagonal-Koordinaten")
 else:
 print("⚠️ Kein Extraktions-Pattern gefunden")
 print()
 
 # 3. Analyze Position 27 Matrix-Koordinaten
 print("🔍 Analyze Position 27 Matrix-Koordinaten...")
 pos27_mappings = calculate_position_to_matrix_mapping(27, extraction_pattern)
 print(f"✅ {len(pos27_mappings)} mögliche Mappings gefunden")
 
 if matrix is not None:
 pos27_matrix_values = analyze_matrix_values_at_coordinates(matrix, pos27_mappings)
 print(f"✅ Matrix-Werte analysiert")
 for hyp, data in pos27_matrix_values.items():
 coord = data["coordinate"]
 value = data["value"]
 char = data["char"]
 print(f" {hyp}: Matrix({coord[0]},{coord[1]}) = {value} (mod_26={data['mod_26']}, char={char})")
 print()
 
 # 4. Analyze Grid Spalte 6 → Matrix
 print("🔍 Analyze Grid Spalte 6 → Matrix Verbindung...")
 if matrix is not None:
 grid_data = {}
 if GRID_ANALYSIS.exists():
 with GRID_ANALYSIS.open() as f:
 grid_data = json.load(f)
 
 column6_analysis = analyze_grid_column6_to_matrix(grid_data, matrix)
 print(f"✅ Spalte 6 analysiert")
 for pos_key, analysis in column6_analysis.items():
 print(f" {pos_key}: Block {analysis['block']}, Pos im Block {analysis['pos_in_block']}")
 for hyp, data in analysis["possible_matrix_coords"].items():
 coord = data["coordinate"]
 value = data["value"]
 print(f" {hyp}: Matrix({coord[0]},{coord[1]}) = {value}")
 print()
 
 # 5. Analyze Matrix-Spalte 6 direkt
 print("🔍 Analyze Matrix-Spalte 6 direkt...")
 if matrix is not None:
 matrix_col6 = analyze_matrix_column6(matrix)
 print(f"✅ Matrix-Spalte 6 analysiert")
 print(f" Mean: {matrix_col6.get('mean', 0):.2f}")
 print(f" Zeros: {matrix_col6.get('zeros', 0)}")
 print(f" Unique Values: {matrix_col6.get('unique_values', 0)}")
 if matrix_col6.get('sample_values'):
 print(f" Sample Values (pos 13,27,41,55): {matrix_col6['sample_values']}")
 print()
 
 # 6. Analyze Matrix-Zeile 27
 print("🔍 Analyze Matrix-Zeile 27...")
 if matrix is not None:
 matrix_row27 = analyze_matrix_row27(matrix)
 print(f"✅ Matrix-Zeile 27 analysiert")
 print(f" Mean: {matrix_row27.get('mean', 0):.2f}")
 print(f" Zeros: {matrix_row27.get('zeros', 0)}")
 print(f" Unique Values: {matrix_row27.get('unique_values', 0)}")
 if matrix_row27.get('value_at_col6') is not None:
 print(f" Value at Col 6: {matrix_row27['value_at_col6']}")
 if matrix_row27.get('value_at_col13') is not None:
 print(f" Value at Col 13: {matrix_row27['value_at_col13']}")
 print()
 
 # Speichere Ergebnisse
 OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
 
 output_data = {
 "timestamp": datetime.now().isoformat(),
 "position27_mappings": pos27_mappings,
 "position27_matrix_values": pos27_matrix_values if matrix is not None else {},
 "column6_analysis": column6_analysis if matrix is not None else {},
 "matrix_column6": matrix_col6 if matrix is not None else {},
 "matrix_row27": matrix_row27 if matrix is not None else {}
 }
 
 output_file = OUTPUT_DIR / "deep_grid_matrix_synthesis.json"
 with output_file.open("w") as f:
 json.dump(output_data, f, indent=2)
 print(f"💾 Ergebnisse gespeichert: {output_file}")
 
 print()
 print("=" * 80)
 print("✅ SYNTHESE ABGESCHLOSSEN")
 print("=" * 80)

if __name__ == "__main__":
 main()

