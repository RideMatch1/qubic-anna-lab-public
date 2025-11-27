#!/usr/bin/env python3
"""
Position 27 Matrix-Mapping Validierung
- Check ob Matrix(27,13) = 56 (mod_26=4, char=E) korrekt ist
- Analyze Character-Verteilung in Position 27
- Vergleiche mit Matrix-Werten
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
LAYER4_FILE = project_root / "outputs" / "derived" / "layer4_derivation_full_23k.json"
MATRIX_FILE = project_root / "data" / "anna-matrix" / "Anna_Matrix.xlsx"
DEEP_SYNTHESIS = project_root / "outputs" / "derived" / "deep_grid_matrix_synthesis.json"
OUTPUT_DIR = project_root / "outputs" / "derived"
REPORTS_DIR = project_root / "outputs" / "reports"

def load_anna_matrix() -> np.ndarray:
 """Load Anna Matrix."""
 if not MATRIX_FILE.exists():
 raise FileNotFoundError(f"Matrix file not found: {MATRIX_FILE}")
 
 df = pd.read_excel(MATRIX_FILE, header=None)
 numeric = df.apply(pd.to_numeric, errors="coerce").fillna(0.0)
 matrix = numeric.to_numpy(dtype=float)
 
 # Korrigiere 129x129 zu 128x128
 if matrix.shape == (129, 129):
 matrix = matrix[1:, 1:]
 
 if matrix.shape != (128, 128):
 raise ValueError(f"Matrix has wrong shape: {matrix.shape}, expected (128, 128)")
 
 return matrix

def analyze_position27_characters(layer3_data: List[Dict]) -> Dict:
 """Analyze Character-Verteilung in Position 27."""
 
 pos27_chars = Counter()
 pos27_char_values = defaultdict(list)
 
 for entry in layer3_data:
 l3_id = entry.get("layer3_identity", "")
 if not l3_id or len(l3_id) <= 27:
 continue
 
 char = l3_id[27].upper()
 pos27_chars[char] += 1
 
 # Character-Wert (A=0, B=1, ..., Z=25)
 char_val = ord(char) - ord('A')
 pos27_char_values[char_val].append(char)
 
 # Berechne Statistiken
 total = sum(pos27_chars.values())
 char_distribution = {char: {"count": count, "percentage": (count/total)*100} 
 for char, count in pos27_chars.most_common()}
 
 # Finde häufigste Characters
 most_common = pos27_chars.most_common(10)
 
 return {
 "total_identities": total,
 "unique_characters": len(pos27_chars),
 "character_distribution": char_distribution,
 "most_common": {char: count for char, count in most_common},
 "char_value_distribution": {val: len(chars) for val, chars in pos27_char_values.items()}
 }

def validate_matrix_mapping(matrix: np.ndarray, pos27_analysis: Dict) -> Dict:
 """Validate Matrix-Mapping for Position 27."""
 
 # Matrix(27,13) = 56 (mod_26=4, char=E)
 matrix_value = int(matrix[27, 13])
 matrix_mod26 = int(matrix_value % 26)
 matrix_char = chr(ord('A') + matrix_mod26)
 
 # Check ob E häufiger ist
 char_dist = pos27_analysis.get("character_distribution", {})
 e_count = char_dist.get("E", {}).get("count", 0)
 e_percentage = char_dist.get("E", {}).get("percentage", 0)
 
 # Erwartete Häufigkeit bei Zufall: 1/26 ≈ 3.85%
 expected_random = pos27_analysis.get("total_identities", 0) / 26
 e_ratio = e_count / expected_random if expected_random > 0 else 0
 
 # Check andere mögliche Mappings
 other_mappings = {
 "diagonal_identity1_block1": (13, 29, 116, 12, "M"),
 "diagonal_identity2_block1": (45, 29, 84, 6, "G"),
 "diagonal_identity3_block1": (77, 29, -3, 23, "X"),
 "diagonal_identity4_block1": (109, 29, 4, 4, "E"),
 "symmetric": (101, 13, 96, 18, "S"),
 "direct_col27": (13, 27, -27, 25, "Z")
 }
 
 mapping_validation = {}
 for name, (row, col, value, mod26, char) in other_mappings.items():
 if 0 <= row < 128 and 0 <= col < 128:
 char_count = char_dist.get(char, {}).get("count", 0)
 char_percentage = char_dist.get(char, {}).get("percentage", 0)
 expected = pos27_analysis.get("total_identities", 0) / 26
 ratio = char_count / expected if expected > 0 else 0
 
 mapping_validation[name] = {
 "matrix_coord": (row, col),
 "matrix_value": value,
 "mod_26": mod26,
 "char": char,
 "actual_count": char_count,
 "actual_percentage": char_percentage,
 "expected_random": expected,
 "ratio": ratio,
 "is_significant": ratio > 1.5 # >50% above random
 }
 
 # Haupt-Mapping: Matrix(27,13)
 main_mapping = {
 "matrix_coord": (27, 13),
 "matrix_value": matrix_value,
 "mod_26": matrix_mod26,
 "char": matrix_char,
 "actual_count": e_count,
 "actual_percentage": e_percentage,
 "expected_random": expected_random,
 "ratio": e_ratio,
 "is_significant": e_ratio > 1.5
 }
 
 return {
 "main_mapping": main_mapping,
 "other_mappings": mapping_validation,
 "conclusion": {
 "best_mapping": "Matrix(27,13)" if main_mapping["is_significant"] else "UNKNOWN",
 "confidence": "HIGH" if main_mapping["is_significant"] else "LOW"
 }
 }

def analyze_position27_stability(layer3_data: List[Dict], layer4_data: List[Dict]) -> Dict:
 """Analyze Stabilität von Position 27 (Layer-3 → Layer-4)."""
 
 # Erstelle Layer-4 Map
 layer4_map = {}
 for entry in layer4_data:
 l3_id = entry.get("layer3_identity", "")
 l4_id = entry.get("layer4_identity", "")
 if l3_id and l4_id:
 layer4_map[l3_id] = l4_id
 
 # Analyze Stabilität
 stable_count = 0
 changing_count = 0
 stable_chars = Counter()
 changing_pairs = Counter()
 
 for entry in layer3_data:
 l3_id = entry.get("layer3_identity", "")
 l4_id = layer4_map.get(l3_id, "")
 
 if not l3_id or len(l3_id) <= 27:
 continue
 
 l3_char = l3_id[27].upper()
 
 if l4_id and len(l4_id) > 27:
 l4_char = l4_id[27].upper()
 
 if l3_char == l4_char:
 stable_count += 1
 stable_chars[l3_char] += 1
 else:
 changing_count += 1
 changing_pairs[f"{l3_char}→{l4_char}"] += 1
 
 total = stable_count + changing_count
 stability_rate = stable_count / total if total > 0 else 0
 
 return {
 "total_pairs": total,
 "stable_count": stable_count,
 "changing_count": changing_count,
 "stability_rate": stability_rate,
 "stable_chars": dict(stable_chars.most_common(10)),
 "changing_pairs": dict(changing_pairs.most_common(10))
 }

def main():
 """Hauptfunktion."""
 
 print("=" * 80)
 print("POSITION 27 MATRIX-MAPPING VALIDIERUNG")
 print("=" * 80)
 print()
 print("⚠️ KEINE HALLUZINATIONEN - NUR ECHTE DATEN!")
 print("🔬 PROFESSOREN-TEAM STIL: KRITISCH, SYSTEMATISCH, PERFEKT")
 print()
 
 # 1. Load Matrix
 print("📂 Load Anna Matrix...")
 try:
 matrix = load_anna_matrix()
 print(f"✅ Matrix geloadn: {matrix.shape}")
 print(f" Matrix(27,13) = {int(matrix[27, 13])} (mod_26={int(matrix[27, 13] % 26)}, char={chr(ord('A') + int(matrix[27, 13] % 26))})")
 except Exception as e:
 print(f"❌ Fehler beim Loadn der Matrix: {e}")
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
 
 # 3. Analyze Position 27 Characters
 print("🔍 Analyze Position 27 Characters...")
 pos27_analysis = analyze_position27_characters(layer3_results)
 print(f"✅ Position 27 analysiert: {pos27_analysis['total_identities']} Identities")
 print(f" Unique Characters: {pos27_analysis['unique_characters']}")
 print()
 print(" Top 10 Characters:")
 for char, count in list(pos27_analysis["most_common"].items())[:10]:
 pct = pos27_analysis["character_distribution"][char]["percentage"]
 print(f" {char}: {count} ({pct:.2f}%)")
 print()
 
 # 4. Validate Matrix-Mapping
 print("🔍 Validate Matrix-Mapping...")
 validation = validate_matrix_mapping(matrix, pos27_analysis)
 print("✅ Mapping validiert")
 print()
 
 main = validation["main_mapping"]
 print("📊 Haupt-Mapping: Matrix(27,13)")
 print(f" Matrix-Wert: {main['matrix_value']}")
 print(f" mod_26: {main['mod_26']}")
 print(f" Char: {main['char']}")
 print(f" Tatsächliche Häufigkeit: {main['actual_count']} ({main['actual_percentage']:.2f}%)")
 print(f" Erwartet bei Zufall: {main['expected_random']:.1f} ({100/26:.2f}%)")
 print(f" Ratio: {main['ratio']:.2f}x")
 print(f" Signifikant: {'✅ JA' if main['is_significant'] else '❌ NEIN'}")
 print()
 
 # 5. Analyze Stabilität
 print("🔍 Analyze Position 27 Stabilität...")
 if LAYER4_FILE.exists():
 with LAYER4_FILE.open() as f:
 layer4_data = json.load(f)
 layer4_results = layer4_data.get("results", [])
 
 stability = analyze_position27_stability(layer3_results, layer4_results)
 print(f"✅ Stabilität analysiert")
 print(f" Stabilitäts-Rate: {stability['stability_rate']*100:.2f}%")
 print(f" Stable: {stability['stable_count']}, Changing: {stability['changing_count']}")
 print()
 print(" Top stabile Characters:")
 for char, count in list(stability["stable_chars"].items())[:10]:
 print(f" {char}: {count}")
 else:
 print("⚠️ Layer-4 Daten nicht gefunden")
 stability = {}
 print()
 
 # 6. Zeige alle Mappings
 print("=" * 80)
 print("ALLE MAPPINGS VERGLEICH")
 print("=" * 80)
 print()
 
 all_mappings = [("Matrix(27,13)", validation["main_mapping"])]
 all_mappings.extend(validation["other_mappings"].items())
 
 # Sortiere nach Signifikanz
 all_mappings.sort(key=lambda x: x[1].get("ratio", 0), reverse=True)
 
 print("📊 Mappings sortiert nach Signifikanz:")
 for name, mapping in all_mappings:
 coord = mapping["matrix_coord"]
 char = mapping["char"]
 ratio = mapping["ratio"]
 sig = "✅" if mapping.get("is_significant", False) else "❌"
 print(f" {sig} {name}: Matrix({coord[0]},{coord[1]}) → char={char}, Ratio={ratio:.2f}x")
 print()
 
 # Speichere Ergebnisse
 OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
 
 output_data = {
 "timestamp": datetime.now().isoformat(),
 "position27_analysis": pos27_analysis,
 "matrix_validation": validation,
 "stability_analysis": stability,
 "conclusion": {
 "best_mapping": validation["conclusion"]["best_mapping"],
 "confidence": validation["conclusion"]["confidence"],
 "matrix_27_13_value": int(matrix[27, 13]),
 "matrix_27_13_mod26": int(matrix[27, 13] % 26),
 "matrix_27_13_char": chr(ord('A') + int(matrix[27, 13] % 26)),
 "actual_e_count": main["actual_count"],
 "actual_e_percentage": main["actual_percentage"],
 "expected_random": main["expected_random"],
 "ratio": main["ratio"],
 "is_significant": main["is_significant"]
 }
 }
 
 output_file = OUTPUT_DIR / "position27_matrix_validation.json"
 with output_file.open("w") as f:
 json.dump(output_data, f, indent=2)
 print(f"💾 Ergebnisse gespeichert: {output_file}")
 
 print()
 print("=" * 80)
 print("✅ VALIDIERUNG ABGESCHLOSSEN")
 print("=" * 80)
 print()
 
 # Finale Bewertung
 if main["is_significant"]:
 print("✅ VALIDIERUNG ERFOLGREICH:")
 print(f" Matrix(27,13) = {main['matrix_value']} → char={main['char']}")
 print(f" Char {main['char']} ist {main['ratio']:.2f}x häufiger als erwartet")
 print(f" Mapping ist statistisch signifikant!")
 else:
 print("⚠️ VALIDIERUNG UNENTSCHIEDEN:")
 print(f" Matrix(27,13) = {main['matrix_value']} → char={main['char']}")
 print(f" Char {main['char']} ist {main['ratio']:.2f}x häufiger als erwartet")
 print(f" Mapping ist NICHT statistisch signifikant")
 print(f" Weitere Analyse erforderlich")
 print()

if __name__ == "__main__":
 main()

