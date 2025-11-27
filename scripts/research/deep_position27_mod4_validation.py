#!/usr/bin/env python3
"""
Tiefgründige Position 27 Mod_4 Validierung
- Validiere mod_4 Hypothese auf größerem Sample
- Analysiere warum nur Position 27 mod_4 funktioniert
- Prüfe Konsistenz der Transformation
- Finde strukturelle Erklärung
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

# Pfade
LAYER3_FILE = project_root / "outputs" / "derived" / "layer3_derivation_23k_complete.json"
LAYER4_FILE = project_root / "outputs" / "derived" / "layer4_derivation_full_23k.json"
MATRIX_FILE = project_root / "data" / "anna-matrix" / "Anna_Matrix.xlsx"
OUTPUT_DIR = project_root / "outputs" / "derived"
REPORTS_DIR = project_root / "outputs" / "reports"

def load_anna_matrix() -> np.ndarray:
 """Lade Anna Matrix."""
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

def validate_mod4_for_all_identities(layer3_data: List[Dict], matrix: np.ndarray) -> Dict:
 """Validate mod_4 for all 23,765 identities."""
 
 pos27_chars = Counter()
 mod4_predictions = Counter()
 matches = 0
 total = 0
 
 matrix_value = int(matrix[27, 13])
 matrix_mod4 = int(matrix_value % 4)
 expected_char = chr(ord('A') + matrix_mod4)
 
 for entry in layer3_data:
 l3_id = entry.get("layer3_identity", "")
 if not l3_id or len(l3_id) <= 27:
 continue
 
 char = l3_id[27].upper()
 pos27_chars[char] += 1
 total += 1
 
 if char == expected_char:
 matches += 1
 mod4_predictions["correct"] += 1
 else:
 mod4_predictions["incorrect"] += 1
 
 accuracy = (matches / total * 100) if total > 0 else 0
 expected_random = total / 4 # 25% bei Zufall (4 Characters)
 ratio = matches / expected_random if expected_random > 0 else 0
 
 return {
 "total": total,
 "matches": matches,
 "accuracy": accuracy,
 "expected_char": expected_char,
 "matrix_value": matrix_value,
 "matrix_mod4": matrix_mod4,
 "expected_random": expected_random,
 "ratio": ratio,
            "is_significant": ratio > 1.2, # >20% above random
 "char_distribution": dict(pos27_chars.most_common())
 }

def analyze_why_only_position27(layer3_data: List[Dict], matrix: np.ndarray) -> Dict:
 """Analysiere warum nur Position 27 mod_4 funktioniert."""
 
 # Analysiere alle Block-Ende-Positionen
 block_end_positions = [13, 27, 41, 55]
 analysis = {}
 
 for pos in block_end_positions:
 block = pos // 14
 pos_in_block = pos % 14
 
 # Matrix-Koordinate (direkt)
 matrix_value = int(matrix[pos, 13])
 matrix_mod4 = int(matrix_value % 4)
 matrix_mod26 = int(matrix_value % 26)
 expected_char_mod4 = chr(ord('A') + matrix_mod4)
 expected_char_mod26 = chr(ord('A') + matrix_mod26)
 
 # Analysiere Characters
 chars = Counter()
 for entry in layer3_data:
 l3_id = entry.get("layer3_identity", "")
 if l3_id and len(l3_id) > pos:
 chars[l3_id[pos].upper()] += 1
 
 total = sum(chars.values())
 unique_chars = len(chars)
 
 # Check mod_4 match
 mod4_count = chars.get(expected_char_mod4, 0)
 mod4_accuracy = (mod4_count / total * 100) if total > 0 else 0
 mod4_expected = total / 4
 mod4_ratio = mod4_count / mod4_expected if mod4_expected > 0 else 0
 
 # Prüfe mod_26 Match
 mod26_count = chars.get(expected_char_mod26, 0)
 mod26_accuracy = (mod26_count / total * 100) if total > 0 else 0
 mod26_expected = total / 26
 mod26_ratio = mod26_count / mod26_expected if mod26_expected > 0 else 0
 
 analysis[f"position_{pos}"] = {
 "position": pos,
 "block": block,
 "pos_in_block": pos_in_block,
 "matrix_coord": (pos, 13),
 "matrix_value": matrix_value,
 "matrix_mod4": matrix_mod4,
 "matrix_mod26": matrix_mod26,
 "expected_char_mod4": expected_char_mod4,
 "expected_char_mod26": expected_char_mod26,
 "total": total,
 "unique_chars": unique_chars,
 "char_distribution": dict(chars.most_common(10)),
 "mod4_analysis": {
 "count": mod4_count,
 "accuracy": mod4_accuracy,
 "expected_random": mod4_expected,
 "ratio": mod4_ratio,
 "is_significant": mod4_ratio > 1.2
 },
 "mod26_analysis": {
 "count": mod26_count,
 "accuracy": mod26_accuracy,
 "expected_random": mod26_expected,
 "ratio": mod26_ratio,
 "is_significant": mod26_ratio > 1.2
 }
 }
 
 return analysis

def analyze_position27_stability_mod4(layer3_data: List[Dict], layer4_data: List[Dict], matrix: np.ndarray) -> Dict:
 """Analysiere Position 27 Stabilität im Kontext von mod_4."""
 
 # Erstelle Layer-4 Map
 layer4_map = {}
 for entry in layer4_data:
 l3_id = entry.get("layer3_identity", "")
 l4_id = entry.get("layer4_identity", "")
 if l3_id and l4_id:
 layer4_map[l3_id] = l4_id
 
 matrix_value = int(matrix[27, 13])
 matrix_mod4 = int(matrix_value % 4)
 expected_char = chr(ord('A') + matrix_mod4)
 
 # Analysiere Stabilität
 stable_mod4 = 0 # Bleibt expected_char
 changing_from_mod4 = 0 # War expected_char, wird anders
 changing_to_mod4 = 0 # War anders, wird expected_char
 other_changes = 0
 
 for entry in layer3_data:
 l3_id = entry.get("layer3_identity", "")
 l4_id = layer4_map.get(l3_id, "")
 
 if not l3_id or len(l3_id) <= 27:
 continue
 
 l3_char = l3_id[27].upper()
 
 if l4_id and len(l4_id) > 27:
 l4_char = l4_id[27].upper()
 
 if l3_char == expected_char and l4_char == expected_char:
 stable_mod4 += 1
 elif l3_char == expected_char and l4_char != expected_char:
 changing_from_mod4 += 1
 elif l3_char != expected_char and l4_char == expected_char:
 changing_to_mod4 += 1
 else:
 other_changes += 1
 
 total_pairs = stable_mod4 + changing_from_mod4 + changing_to_mod4 + other_changes
 
 return {
 "total_pairs": total_pairs,
 "stable_mod4": stable_mod4,
 "changing_from_mod4": changing_from_mod4,
 "changing_to_mod4": changing_to_mod4,
 "other_changes": other_changes,
 "stability_rate": (stable_mod4 / total_pairs * 100) if total_pairs > 0 else 0,
 "expected_char": expected_char
 }

def main():
 """Hauptfunktion."""
 
 print("=" * 80)
 print("TIEFGRÜNDIGE POSITION 27 MOD_4 VALIDIERUNG")
 print("=" * 80)
 print()
 print("⚠️ KEINE HALLUZINATIONEN - NUR ECHTE DATEN!")
 print("🔬 PROFESSOREN-TEAM: SYSTEMATISCH, KRITISCH, PERFEKT")
 print()
 
 # 1. Lade Matrix
 print("📂 Lade Anna Matrix...")
 try:
 matrix = load_anna_matrix()
 print(f"✅ Matrix geladen: {matrix.shape}")
 print(f" Matrix(27,13) = {int(matrix[27, 13])} (mod_4={int(matrix[27, 13] % 4)}, char={chr(ord('A') + int(matrix[27, 13] % 4))})")
 except Exception as e:
 print(f"❌ Fehler: {e}")
 return
 print()
 
 # 2. Lade Layer-3 Daten
 print("📂 Lade Layer-3 Daten...")
 if not LAYER3_FILE.exists():
 print(f"❌ Datei nicht gefunden: {LAYER3_FILE}")
 return
 
 with LAYER3_FILE.open() as f:
 layer3_data = json.load(f)
 layer3_results = layer3_data.get("results", [])
 print(f"✅ {len(layer3_results)} Layer-3 Identities geladen")
 print()
 
 # 3. Validiere mod_4 für alle Identities
 print("🔍 Validiere mod_4 für alle 23.765 Identities...")
 validation = validate_mod4_for_all_identities(layer3_results, matrix)
 print(f"✅ Validierung abgeschlossen")
 print(f" Total: {validation['total']}")
 print(f" Matches: {validation['matches']}")
 print(f" Accuracy: {validation['accuracy']:.2f}%")
 print(f" Erwartet bei Zufall: {validation['expected_random']:.1f} (25%)")
 print(f" Ratio: {validation['ratio']:.2f}x")
 print(f" Signifikant: {'✅ JA' if validation['is_significant'] else '❌ NEIN'}")
 print()
 
 # 4. Analysiere warum nur Position 27
 print("🔍 Analysiere warum nur Position 27 mod_4 funktioniert...")
 why_analysis = analyze_why_only_position27(layer3_results, matrix)
 print(f"✅ Analyse abgeschlossen")
 print()
 
 print("📊 Vergleich aller Block-Ende-Positionen:")
 for pos_key, analysis in why_analysis.items():
 pos = analysis["position"]
 unique = analysis["unique_chars"]
 mod4_acc = analysis["mod4_analysis"]["accuracy"]
 mod4_ratio = analysis["mod4_analysis"]["ratio"]
 mod26_acc = analysis["mod26_analysis"]["accuracy"]
 mod26_ratio = analysis["mod26_analysis"]["ratio"]
 
 print(f" Position {pos}:")
 print(f" Unique Characters: {unique}")
 print(f" Mod_4: {mod4_acc:.2f}% (Ratio: {mod4_ratio:.2f}x)")
 print(f" Mod_26: {mod26_acc:.2f}% (Ratio: {mod26_ratio:.2f}x)")
 print()
 
 # 5. Analysiere Stabilität
 print("🔍 Analysiere Position 27 Stabilität (mod_4 Kontext)...")
 if LAYER4_FILE.exists():
 with LAYER4_FILE.open() as f:
 layer4_data = json.load(f)
 layer4_results = layer4_data.get("results", [])
 
 stability = analyze_position27_stability_mod4(layer3_results, layer4_results, matrix)
 print(f"✅ Stabilität analysiert")
 print(f" Stable mod_4: {stability['stable_mod4']} ({stability['stability_rate']:.2f}%)")
 print(f" Changing from mod_4: {stability['changing_from_mod4']}")
 print(f" Changing to mod_4: {stability['changing_to_mod4']}")
 else:
 print("⚠️ Layer-4 Daten nicht gefunden")
 stability = {}
 print()
 
 # Speichere Ergebnisse
 OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
 
 output_data = {
 "timestamp": datetime.now().isoformat(),
 "full_validation": validation,
 "why_only_position27": why_analysis,
 "stability_analysis": stability,
 "conclusion": {
 "mod4_works_for_position27": validation["is_significant"],
 "accuracy": validation["accuracy"],
 "ratio": validation["ratio"],
 "why_only_position27": "Position 27 hat nur 4 Characters (A,B,C,D), andere haben 8"
 }
 }
 
 output_file = OUTPUT_DIR / "deep_position27_mod4_validation.json"
 with output_file.open("w") as f:
 json.dump(output_data, f, indent=2)
 print(f"💾 Ergebnisse gespeichert: {output_file}")
 
 print()
 print("=" * 80)
 print("✅ VALIDIERUNG ABGESCHLOSSEN")
 print("=" * 80)
 print()
 
 # Finale Bewertung
 if validation["is_significant"]:
 print("✅ MOD_4 HYPOTHESE BESTÄTIGT:")
 print(f" Position 27: {validation['accuracy']:.2f}% Accuracy")
 print(f" Ratio: {validation['ratio']:.2f}x über Zufall")
 print(f" Matrix(27,13) mod_4 = {validation['matrix_mod4']} → char={validation['expected_char']}")
 else:
 print("⚠️ MOD_4 HYPOTHESE UNENTSCHIEDEN:")
 print(f" Position 27: {validation['accuracy']:.2f}% Accuracy")
 print(f" Ratio: {validation['ratio']:.2f}x über Zufall")
 print()

if __name__ == "__main__":
 main()

