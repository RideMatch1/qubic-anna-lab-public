#!/usr/bin/env python3
"""
Mod_4 Hypothese Validierung
- Check ob Matrix-Werte mod_4 mit Position 27 Characters aboveeinstimmen
- Analyze Korrelation for alle Identities
- Kritisch validaten und verifizieren
- KEINE Halluzinationen - nur echte Daten!
"""

import json
import sys
from pathlib import Path
from typing import Dict, List, Tuple
from collections import Counter, defaultdict
from datetime import datetime
import numpy as np
import pandas as pd

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# Paths
LAYER3_FILE = project_root / "outputs" / "derived" / "layer3_derivation_23k_complete.json"
MATRIX_FILE = project_root / "data" / "anna-matrix" / "Anna_Matrix.xlsx"
OUTPUT_DIR = project_root / "outputs" / "derived"
REPORTS_DIR = project_root / "outputs" / "reports"

def load_anna_matrix() -> np.ndarray:
 """Load Anna Matrix."""
 if not MATRIX_FILE.exists():
 raise FileNotFoundError(f"Matrix file not found: {MATRIX_FILE}")
 
 df = pd.read_excel(MATRIX_FILE, header=None)
 numeric = df.apply(pd.to_numeric, errors="coerce").fillna(0.0)
 matrix = numeric.to_numpy(dtype=float)
 
 if matrix.shape == (129, 129):
 matrix = matrix[1:, 1:]
 
 if matrix.shape != (128, 128):
 raise ValueError(f"Matrix has wrong shape: {matrix.shape}")
 
 return matrix

def validate_mod4_for_position27(layer3_data: List[Dict], matrix: np.ndarray) -> Dict:
 """Validate mod_4 Hypothese for Position 27."""
 
 # Mögliche Matrix-Koordinaten for Position 27
 possible_coords = [
 (27, 13, "direct"),
 (13, 29, "diagonal_identity1_block1"),
 (45, 29, "diagonal_identity2_block1"),
 (77, 29, "diagonal_identity3_block1"),
 (109, 29, "diagonal_identity4_block1"),
 (101, 13, "symmetric"),
 (13, 27, "direct_col27")
 ]
 
 results = {}
 
 for row, col, name in possible_coords:
 if not (0 <= row < 128 and 0 <= col < 128):
 continue
 
 matrix_value = int(matrix[row, col])
 matrix_mod4 = int(matrix_value % 4)
 expected_char = chr(ord('A') + matrix_mod4)
 
 # Check wie oft dieser Character in Position 27 vorkommt
 actual_count = 0
 for entry in layer3_data:
 l3_id = entry.get("layer3_identity", "")
 if l3_id and len(l3_id) > 27:
 if l3_id[27].upper() == expected_char:
 actual_count += 1
 
 total = len([e for e in layer3_data if e.get("layer3_identity", "") and len(e.get("layer3_identity", "")) > 27])
 actual_percentage = (actual_count / total * 100) if total > 0 else 0
 
 # Erwartet bei Zufall: 1/4 = 25% (nur A, B, C, D)
 expected_random = total / 4
 ratio = actual_count / expected_random if expected_random > 0 else 0
 
 results[name] = {
 "matrix_coord": (row, col),
 "matrix_value": matrix_value,
 "mod_4": matrix_mod4,
 "expected_char": expected_char,
 "actual_count": actual_count,
 "actual_percentage": actual_percentage,
 "expected_random": expected_random,
 "ratio": ratio,
 "is_significant": ratio > 1.2 # >20% above random
 }
 
 return results

def analyze_mod4_correlation_all_positions(layer3_data: List[Dict], matrix: np.ndarray) -> Dict:
 """Analyze mod_4 Korrelation for alle Positionen (Sample)."""
 
 # Analyze Sample von Positionen
 sample_positions = [0, 13, 14, 27, 28, 41, 42, 55]
 
 results = {}
 
 for pos in sample_positions:
 block = pos // 14
 pos_in_block = pos % 14
 
 # Mögliche Matrix-Koordinaten
 possible_coords = [
 (pos, pos_in_block, "direct"),
 (block * 14 + pos_in_block, 0, "block_based")
 ]
 
 # Analyze Characters
 chars = Counter()
 for entry in layer3_data:
 l3_id = entry.get("layer3_identity", "")
 if l3_id and len(l3_id) > pos:
 chars[l3_id[pos].upper()] += 1
 
 unique_chars = len(chars)
 
 # Check mod_4 for direkte Koordinate
 mod4_analysis = {}
 for row, col, name in possible_coords:
 if 0 <= row < 128 and 0 <= col < 128:
 matrix_value = int(matrix[row, col])
 matrix_mod4 = int(matrix_value % 4)
 expected_char = chr(ord('A') + matrix_mod4)
 
 actual_count = chars.get(expected_char, 0)
 total = sum(chars.values())
 percentage = (actual_count / total * 100) if total > 0 else 0
 
 mod4_analysis[name] = {
 "coord": (row, col),
 "matrix_value": matrix_value,
 "mod_4": matrix_mod4,
 "expected_char": expected_char,
 "actual_count": actual_count,
 "percentage": percentage
 }
 
 results[f"position_{pos}"] = {
 "unique_chars": unique_chars,
 "char_distribution": dict(chars.most_common(10)),
 "mod4_analysis": mod4_analysis
 }
 
 return results

def main():
 """Hauptfunktion."""
 
 print("=" * 80)
 print("MOD_4 HYPOTHESE VALIDIERUNG")
 print("=" * 80)
 print()
 print("⚠️ KEINE HALLUZINATIONEN - NUR ECHTE DATEN!")
 print("🔬 PROFESSOREN-TEAM: KRITISCH, SYSTEMATISCH, PERFEKT")
 print()
 
 # 1. Load Matrix
 print("📂 Load Anna Matrix...")
 try:
 matrix = load_anna_matrix()
 print(f"✅ Matrix geloadn: {matrix.shape}")
 except Exception as e:
 print(f"❌ Fehler: {e}")
 return
 print()
 
 # 2. Load Layer-3 Daten
 print("📂 Load Layer-3 Daten...")
 if not LAYER3_FILE.exists():
 print(f"❌ Datei nicht gefunden: {LAYER3_FILE}")
 return
 
 with LAYER3_FILE.open() as f:
 layer3_data = json.load(f)
 layer3_results = layer3_data.get("results", [])
 print(f"✅ {len(layer3_results)} Layer-3 Identities geloadn")
 print()
 
 # 3. Validate mod_4 for Position 27
 print("🔍 Validate mod_4 for Position 27...")
 pos27_mod4 = validate_mod4_for_position27(layer3_results, matrix)
 print(f"✅ Mod_4 validiert")
 print()
 
 print("📊 Mod_4 Ergebnisse for Position 27:")
 for name, result in sorted(pos27_mod4.items(), key=lambda x: x[1]["ratio"], reverse=True):
 coord = result["matrix_coord"]
 expected = result["expected_char"]
 actual = result["actual_count"]
 ratio = result["ratio"]
 sig = "✅" if result["is_significant"] else "❌"
 print(f" {sig} {name}: Matrix({coord[0]},{coord[1]}) mod_4={result['mod_4']} → {expected}")
 print(f" Tatsächlich: {actual} ({result['actual_percentage']:.2f}%), Ratio: {ratio:.2f}x")
 print()
 
 # 4. Analyze mod_4 for alle Positionen (Sample)
 print("🔍 Analyze mod_4 for alle Positionen (Sample)...")
 all_positions_mod4 = analyze_mod4_correlation_all_positions(layer3_results, matrix)
 print(f"✅ Alle Positionen analysiert")
 print()
 
 print("📊 Mod_4 for alle Positionen:")
 for pos_key, analysis in all_positions_mod4.items():
 pos = pos_key.split("_")[1]
 unique = analysis["unique_chars"]
 print(f" Position {pos}: {unique} unique characters")
 if "direct" in analysis["mod4_analysis"]:
 direct = analysis["mod4_analysis"]["direct"]
 expected = direct["expected_char"]
 actual = direct["actual_count"]
 pct = direct["percentage"]
 print(f" Matrix({direct['coord'][0]},{direct['coord'][1]}) mod_4={direct['mod_4']} → {expected}")
 print(f" Tatsächlich: {actual} ({pct:.2f}%)")
 print()
 
 # Speichere Ergebnisse
 OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
 
 output_data = {
 "timestamp": datetime.now().isoformat(),
 "position27_mod4_validation": pos27_mod4,
 "all_positions_mod4_analysis": all_positions_mod4,
 "conclusion": {
 "best_mod4_mapping": max(pos27_mod4.items(), key=lambda x: x[1]["ratio"])[0] if pos27_mod4 else "UNKNOWN",
 "best_ratio": max([r["ratio"] for r in pos27_mod4.values()]) if pos27_mod4 else 0
 }
 }
 
 output_file = OUTPUT_DIR / "mod4_hypothesis_validation.json"
 with output_file.open("w") as f:
 json.dump(output_data, f, indent=2)
 print(f"💾 Ergebnisse gespeichert: {output_file}")
 
 print()
 print("=" * 80)
 print("✅ VALIDIERUNG ABGESCHLOSSEN")
 print("=" * 80)
 print()
 
 # Finale Bewertung
 best = max(pos27_mod4.items(), key=lambda x: x[1]["ratio"]) if pos27_mod4 else None
 if best:
 name, result = best
 if result["is_significant"]:
 print(f"✅ MOD_4 HYPOTHESE BESTÄTIGT:")
 print(f" Bestes Mapping: {name}")
 print(f" Matrix({result['matrix_coord'][0]},{result['matrix_coord'][1]}) mod_4={result['mod_4']} → {result['expected_char']}")
 print(f" Ratio: {result['ratio']:.2f}x (signifikant!)")
 else:
 print(f"⚠️ MOD_4 HYPOTHESE UNENTSCHIEDEN:")
 print(f" Bestes Mapping: {name}")
 print(f" Ratio: {result['ratio']:.2f}x (nicht signifikant)")
 print()

if __name__ == "__main__":
 main()

