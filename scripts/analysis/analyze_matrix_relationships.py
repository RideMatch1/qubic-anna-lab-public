#!/usr/bin/env python3
"""
Analyze Matrix-Beziehungen for Layer-3 und Layer-4
"""

import json
import numpy as np
from pathlib import Path
from typing import Dict, List
from collections import Counter, defaultdict
from datetime import datetime

project_root = Path(__file__).parent.parent.parent
LAYER3_FILE = project_root / "outputs" / "derived" / "layer3_derivation_23k_complete.json"
LAYER4_FILE = project_root / "outputs" / "derived" / "layer4_derivation_sample_5000.json"
MATRIX_FILE = project_root / "outputs" / "analysis" / "anna_matrix.npy"
OUTPUT_DIR = project_root / "outputs" / "derived"
REPORTS_DIR = project_root / "outputs" / "reports"

def load_matrix() -> np.ndarray:
 """Load Anna Matrix."""
 if MATRIX_FILE.exists():
 return np.load(str(MATRIX_FILE))
 return None

def identity_to_matrix_coords(identity: str, extraction_method: str = "diagonal") -> List[tuple]:
 """Konvertiere Identity zu Matrix-Koordinaten (vereinfacht)."""
 # Dies ist eine vereinfachte Version - die echte Extraktion ist komplexer
 coords = []
 # Placeholder - würde echte Koordinaten-Mapping benötigen
 return coords

def analyze_matrix_relationships(layer3_data: List[Dict], layer4_data: List[Dict], matrix: np.ndarray) -> Dict:
 """Analyze Beziehungen zwischen Identities und Matrix."""
 
 if matrix is None:
 return {"error": "Matrix not found"}
 
 # Analyze Character-Werte in Matrix
 matrix_values = matrix.flatten()
 value_distribution = Counter(matrix_values)
 
 # Analyze Zero-Positions
 zero_positions = np.where(matrix == 0)
 zero_coords = list(zip(zero_positions[0], zero_positions[1]))
 
 # Analyze Character-Frequenzen in Identities vs. Matrix
 layer3_chars = Counter()
 layer4_chars = Counter()
 
 for entry in layer3_data:
 identity = entry.get("layer3_identity", "")
 for char in identity:
 layer3_chars[char.upper()] += 1
 
 for entry in layer4_data:
 identity = entry.get("layer4_identity", "")
 for char in identity:
 layer4_chars[char.upper()] += 1
 
 # Matrix-Werte zu Characters (value % 26)
 matrix_char_distribution = Counter()
 for value in matrix_values:
 char_index = int(value) % 26
 char = chr(ord('A') + char_index)
 matrix_char_distribution[char] += 1
 
 return {
 "matrix_stats": {
 "shape": matrix.shape,
 "total_cells": matrix.size,
 "unique_values": len(np.unique(matrix)),
 "min_value": int(np.min(matrix)),
 "max_value": int(np.max(matrix)),
 "mean_value": float(np.mean(matrix)),
 "zero_count": int(np.sum(matrix == 0))
 },
 "zero_positions": zero_coords,
 "value_distribution": dict(value_distribution.most_common(20)),
 "matrix_char_distribution": dict(matrix_char_distribution),
 "layer3_char_distribution": dict(layer3_chars.most_common(26)),
 "layer4_char_distribution": dict(layer4_chars.most_common(26))
 }

def main():
 """Hauptfunktion."""
 print("=" * 80)
 print("MATRIX-BEZIEHUNGEN ANALYSE")
 print("=" * 80)
 print()
 
 # Load Daten
 print("📂 Load Daten...")
 layer3_data = load_layer_data(LAYER3_FILE)
 layer4_data = load_layer_data(LAYER4_FILE)
 matrix = load_matrix()
 
 print(f"✅ Layer-3: {len(layer3_data)} Identities")
 print(f"✅ Layer-4: {len(layer4_data)} Identities")
 print(f"✅ Matrix: {'Geloadn' if matrix is not None else 'Nicht gefunden'}")
 print()
 
 if matrix is None:
 print("⚠️ Matrix nicht gefunden - abovespringe Matrix-Analyse")
 return
 
 # Analyze Matrix-Beziehungen
 print("🔍 Analyze Matrix-Beziehungen...")
 matrix_analysis = analyze_matrix_relationships(layer3_data, layer4_data, matrix)
 print("✅ Matrix-Beziehungen analysiert")
 print()
 
 # Speichere Ergebnisse
 output_data = {
 "timestamp": datetime.now().isoformat(),
 "matrix_analysis": matrix_analysis
 }
 
 output_file = OUTPUT_DIR / "matrix_relationships_analysis.json"
 with output_file.open("w") as f:
 json.dump(output_data, f, indent=2)
 print(f"💾 Results saved to: {output_file}")
 
 # Erstelle Report
 report_lines = [
 "# Matrix-Beziehungen Analyse",
 "",
 f"**Generated**: {datetime.now().isoformat()}",
 "",
 "## Matrix Statistiken",
 ""
 ]
 
 if "matrix_stats" in matrix_analysis:
 stats = matrix_analysis["matrix_stats"]
 report_lines.extend([
 f"- **Shape**: {stats.get('shape', 'N/A')}",
 f"- **Total Cells**: {stats.get('total_cells', 0):,}",
 f"- **Unique Values**: {stats.get('unique_values', 0)}",
 f"- **Min Value**: {stats.get('min_value', 0)}",
 f"- **Max Value**: {stats.get('max_value', 0)}",
 f"- **Mean Value**: {stats.get('mean_value', 0):.2f}",
 f"- **Zero Count**: {stats.get('zero_count', 0)}",
 ""
 ])
 
 report_lines.extend([
 "## Character Distribution Vergleich",
 "",
 "### Matrix (value % 26):"
 ])
 
 matrix_chars = matrix_analysis.get("matrix_char_distribution", {})
 for char in sorted(matrix_chars.keys()):
 count = matrix_chars[char]
 report_lines.append(f"- **{char}**: {count}")
 report_lines.append("")
 
 report_file = REPORTS_DIR / "matrix_relationships_analysis_report.md"
 with report_file.open("w") as f:
 f.write("\n".join(report_lines) + "\n")
 print(f"📝 Report gespeichert: {report_file}")

if __name__ == "__main__":
 def load_layer_data(file_path: Path) -> List[Dict]:
 if not file_path.exists():
 return []
 with file_path.open() as f:
 data = json.load(f)
 return data.get("results", [])
 
 LAYER3_FILE = project_root / "outputs" / "derived" / "layer3_derivation_23k_complete.json"
 LAYER4_FILE = project_root / "outputs" / "derived" / "layer4_derivation_sample_5000.json"
 
 main()

