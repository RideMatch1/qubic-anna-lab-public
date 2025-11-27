#!/usr/bin/env python3
"""
Analyze Matrix-Beziehung for Position 27
- Welche Matrix-Koordinaten erzeugen Position 27?
- Gibt es spezielle Matrix-Werte?
"""

import json
import numpy as np
from pathlib import Path
from typing import Dict, List, Tuple
from collections import Counter, defaultdict
from datetime import datetime

project_root = Path(__file__).parent.parent.parent
MATRIX_FILE = project_root / "data" / "anna-matrix" / "Anna_Matrix.xlsx"
LAYER3_FILE = project_root / "outputs" / "derived" / "layer3_derivation_23k_complete.json"
LAYER4_FILE = project_root / "outputs" / "derived" / "layer4_derivation_full_23k.json"
OUTPUT_DIR = project_root / "outputs" / "derived"
REPORTS_DIR = project_root / "outputs" / "reports"

def load_anna_matrix() -> np.ndarray:
 """Load Anna Matrix aus Excel."""
 import pandas as pd
 
 if not MATRIX_FILE.exists():
 raise FileNotFoundError(f"Matrix file not found: {MATRIX_FILE}")
 
 df = pd.read_excel(MATRIX_FILE, header=None)
 numeric = df.apply(pd.to_numeric, errors="coerce").fillna(0.0)
 matrix = numeric.to_numpy(dtype=float)
 return matrix

def get_matrix_coordinates_for_position(position: int) -> List[Tuple[int, int]]:
 """
 Berechne Matrix-Koordinaten for eine Identity-Position.
 
 Identity hat 60 Characters = 4 Blocks à 14 Characters (56) + Checksum (4)
 Position 27 ist in Block 1, Position 13 im Block
 
 Vereinfachte Annahme: Identity will sequenziell aus Matrix extrahiert
 """
 # Block-Struktur: 4 Blocks à 14 Characters
 block = position // 14
 pos_in_block = position % 14
 
 # Annahme: Jeder Block will aus einer Matrix-Region extrahiert
 # Block 0: Position 0-13
 # Block 1: Position 14-27 (Position 27 ist Block 1, Pos 13)
 # Block 2: Position 28-41
 # Block 3: Position 42-55
 
 # Position 27 = Block 1, Position 13 im Block
 # Das entspricht welcher Matrix-Koordinate?
 
 # Vereinfachte Mapping-Hypothese:
 # - Block 0 könnte aus Zeile 0-13 kommen
 # - Block 1 könnte aus Zeile 14-27 kommen
 # - Position 27 = Block 1, Pos 13 = könnte Zeile 27, Spalte 13 sein
 
 # Oder: Position 27 könnte aus einer speziellen Matrix-Region kommen
 # Müssen wir durch Analyse herausfinden
 
 # Für jetzt: Teste verschiedene Hypothesen
 possible_coords = []
 
 # Hypothese 1: Direkte Mapping (Position = Zeile, Spalte = Block-Position)
 possible_coords.append((27, pos_in_block))
 
 # Hypothese 2: Block-basiert (Block * 14 + Position im Block)
 possible_coords.append((block * 14 + pos_in_block, 0))
 
 # Hypothese 3: Symmetrisch (128 - Position)
 possible_coords.append((128 - 27, pos_in_block))
 
 return possible_coords

def analyze_position27_matrix_values(matrix: np.ndarray, layer3_data: List[Dict], layer4_data: List[Dict]) -> Dict:
 """Analyze Matrix-Werte for Position 27."""
 
 # Erstelle Mapping Layer-3 → Layer-4
 layer4_map = {}
 for entry in layer4_data:
 l3_id = entry.get("layer3_identity", "")
 l4_id = entry.get("layer4_identity", "")
 if l3_id and l4_id:
 layer4_map[l3_id] = l4_id
 
 # Analyze Position 27 Characters
 pos27_l3_chars = Counter()
 pos27_l4_chars = Counter()
 pos27_stable_chars = Counter()
 pos27_changing_chars = Counter()
 
 # Matrix-Werte for stabile vs. changing Characters
 stable_matrix_values = []
 changing_matrix_values = []
 
 for l3_entry in layer3_data:
 l3_id = l3_entry.get("layer3_identity", "")
 l4_id = layer4_map.get(l3_id, "")
 
 if not l3_id or len(l3_id) <= 27:
 continue
 
 pos27_char_l3 = l3_id[27].upper()
 pos27_l3_chars[pos27_char_l3] += 1
 
 if l4_id and len(l4_id) > 27:
 pos27_char_l4 = l4_id[27].upper()
 pos27_l4_chars[pos27_char_l4] += 1
 
 if pos27_char_l3 == pos27_char_l4:
 pos27_stable_chars[pos27_char_l3] += 1
 # Versuche Matrix-Wert zu finden
 # Position 27 könnte aus verschiedenen Matrix-Koordinaten kommen
 # Teste verschiedene Hypothesen
 char_val = ord(pos27_char_l3) - ord('A')
 # Matrix-Wert sollte char_val % 26 entsprechen
 # Aber wir wissen nicht welche Koordinate
 stable_matrix_values.append(char_val)
 else:
 pos27_changing_chars[pos27_char_l3] += 1
 char_val_l3 = ord(pos27_char_l3) - ord('A')
 char_val_l4 = ord(pos27_char_l4) - ord('A')
 changing_matrix_values.append((char_val_l3, char_val_l4))
 
 return {
 "pos27_l3_distribution": dict(pos27_l3_chars.most_common(10)),
 "pos27_l4_distribution": dict(pos27_l4_chars.most_common(10)),
 "pos27_stable_chars": dict(pos27_stable_chars.most_common(10)),
 "pos27_changing_chars": dict(pos27_changing_chars.most_common(10)),
 "stable_matrix_values": {
 "mean": np.mean(stable_matrix_values) if stable_matrix_values else 0,
 "median": np.median(stable_matrix_values) if stable_matrix_values else 0,
 "distribution": dict(Counter(stable_matrix_values).most_common(10))
 }
 }

def analyze_matrix_region_around_position27(matrix: np.ndarray) -> Dict:
 """Analyze Matrix-Region um Position 27."""
 
 # Position 27 könnte aus verschiedenen Regionen kommen
 # Analyze verschiedene Hypothesen
 
 regions = {}
 
 # Hypothese 1: Zeile 27
 if 27 < matrix.shape[0]:
 row_27 = matrix[27, :]
 regions["row_27"] = {
 "mean": float(np.mean(row_27)),
 "std": float(np.std(row_27)),
 "zeros": int(np.sum(row_27 == 0)),
 "unique_values": len(np.unique(row_27))
 }
 
 # Hypothese 2: Spalte 27
 if 27 < matrix.shape[1]:
 col_27 = matrix[:, 27]
 regions["col_27"] = {
 "mean": float(np.mean(col_27)),
 "std": float(np.std(col_27)),
 "zeros": int(np.sum(col_27 == 0)),
 "unique_values": len(np.unique(col_27))
 }
 
 # Hypothese 3: Block 1 Region (Zeile 14-27)
 if 27 < matrix.shape[0]:
 block1_rows = matrix[14:28, :]
 regions["block1_region"] = {
 "mean": float(np.mean(block1_rows)),
 "std": float(np.std(block1_rows)),
 "zeros": int(np.sum(block1_rows == 0)),
 "unique_values": len(np.unique(block1_rows))
 }
 
 # Hypothese 4: Position 27, Spalte 13 (Block-Position)
 if 27 < matrix.shape[0] and 13 < matrix.shape[1]:
 coord_27_13 = matrix[27, 13]
 regions["coord_27_13"] = {
 "value": int(coord_27_13),
 "mod_26": int(coord_27_13 % 26)
 }
 
 return regions

def main():
 """Hauptfunktion."""
 print("=" * 80)
 print("POSITION 27 MATRIX-BEZIEHUNG ANALYSE")
 print("=" * 80)
 print()
 
 # Load Daten
 print("📂 Load Anna Matrix...")
 matrix = load_anna_matrix()
 print(f"✅ Matrix geloadn: {matrix.shape}")
 print()
 
 print("📂 Load Layer-3 Daten...")
 with LAYER3_FILE.open() as f:
 layer3_data = json.load(f)
 layer3_results = layer3_data.get("results", [])
 print(f"✅ {len(layer3_results)} Layer-3 Identities geloadn")
 print()
 
 print("📂 Load Layer-4 Daten...")
 with LAYER4_FILE.open() as f:
 layer4_data = json.load(f)
 layer4_results = layer4_data.get("results", [])
 print(f"✅ {len(layer4_results)} Layer-4 Identities geloadn")
 print()
 
 # Analyze Position 27 Matrix-Werte
 print("🔍 Analyze Position 27 Matrix-Werte...")
 pos27_analysis = analyze_position27_matrix_values(matrix, layer3_results, layer4_results)
 print("✅ Position 27 Matrix-Werte analysiert")
 print()
 
 # Analyze Matrix-Region
 print("🔍 Analyze Matrix-Region um Position 27...")
 matrix_regions = analyze_matrix_region_around_position27(matrix)
 print("✅ Matrix-Region analysiert")
 print()
 
 # Zeige Ergebnisse
 print("=" * 80)
 print("ERGEBNISSE")
 print("=" * 80)
 print()
 
 # Position 27 Character Distribution
 stable_chars = pos27_analysis.get("pos27_stable_chars", {})
 if stable_chars:
 print("📊 Top stabile Characters bei Position 27:")
 for char, count in list(stable_chars.items())[:10]:
 print(f" {char}: {count} Fälle")
 print()
 
 # Matrix-Regionen
 if matrix_regions:
 print("📊 Matrix-Regionen um Position 27:")
 for region_name, stats in matrix_regions.items():
 print(f" {region_name}:")
 for key, value in stats.items():
 print(f" {key}: {value}")
 print()
 
 # Speichere Ergebnisse
 output_data = {
 "timestamp": datetime.now().isoformat(),
 "position27_analysis": pos27_analysis,
 "matrix_regions": matrix_regions
 }
 
 output_file = OUTPUT_DIR / "position27_matrix_relationship.json"
 with output_file.open("w") as f:
 json.dump(output_data, f, indent=2)
 print(f"💾 Results saved to: {output_file}")
 
 # Erstelle Report
 report_lines = [
 "# Position 27 Matrix-Beziehung Analyse",
 "",
 f"**Generated**: {datetime.now().isoformat()}",
 "",
 "## Position 27 Character Distribution",
 ""
 ]
 
 if stable_chars:
 report_lines.append("### Stabile Characters:")
 for char, count in list(stable_chars.items())[:10]:
 report_lines.append(f"- **{char}**: {count} Fälle")
 report_lines.append("")
 
 if matrix_regions:
 report_lines.extend([
 "## Matrix-Regionen",
 ""
 ])
 for region_name, stats in matrix_regions.items():
 report_lines.append(f"### {region_name}:")
 for key, value in stats.items():
 report_lines.append(f"- **{key}**: {value}")
 report_lines.append("")
 
 report_file = REPORTS_DIR / "position27_matrix_relationship_report.md"
 with report_file.open("w") as f:
 f.write("\n".join(report_lines) + "\n")
 print(f"📝 Report gespeichert: {report_file}")

if __name__ == "__main__":
 main()

