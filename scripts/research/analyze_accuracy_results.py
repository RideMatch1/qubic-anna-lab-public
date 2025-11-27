#!/usr/bin/env python3
"""
Analyze Genauigkeits-Verbesserungs-Ergebnisse
- Zeige beste Transformationen
- Analyze Kombinationen
- Erstelle Report
"""

import json
from pathlib import Path

project_root = Path(__file__).parent.parent.parent
INPUT_FILE = project_root / "outputs" / "derived" / "accuracy_improvement_analysis.json"

def main():
 with INPUT_FILE.open() as f:
 data = json.load(f)
 
 print("=" * 80)
 print("GENAUIGKEITS-VERBESSERUNGS-ANALYSE")
 print("=" * 80)
 print()
 
 # Analyze Transformation-Ergebnisse
 print("📊 BESTE TRANSFORMATIONEN PRO POSITION:")
 print()
 
 trans_results = data.get("transformation_results", {})
 for pos_key in sorted(trans_results.keys()):
 pos = int(pos_key.split("_")[1])
 results = trans_results[pos_key]
 
 # Finde beste Transformation
 best = max(results.items(), key=lambda x: x[1].get("ratio", 0))
 best_name = best[0]
 best_data = best[1]
 
 marker = "⭐" if pos == 27 else " "
 print(f" {marker} Position {pos}:")
 print(f" Beste: {best_name}")
 print(f" Accuracy: {best_data['accuracy']:.2f}%")
 print(f" Ratio: {best_data['ratio']:.2f}x")
 print(f" Erwartet: {best_data['expected']:.2f}%")
 print()
 
 # Analyze Kombinationen
 print("📊 BESTE POSITION-KOMBINATIONEN:")
 print()
 
 combo_results = data.get("combo_results", {})
 if combo_results:
 # Sortiere nach Accuracy
 sorted_combos = sorted(
 combo_results.items(),
 key=lambda x: x[1].get("accuracy", 0),
 reverse=True
 )[:10]
 
 for i, (key, combo_data) in enumerate(sorted_combos, 1):
 positions = combo_data.get("positions", [])
 transformations = combo_data.get("transformations", [])
 accuracy = combo_data.get("accuracy", 0)
 
 print(f" {i}. Position {positions[0]} ({transformations[0]}) + {positions[1]} ({transformations[1]}):")
 print(f" Accuracy: {accuracy:.2f}%")
 print(f" Correct: {combo_data.get('correct', 0)} / {combo_data.get('total', 0)}")
 print()
 else:
 print(" Keine Kombinationen gefunden")
 print()
 
 # Zusammenfassung
 print("=" * 80)
 print("ZUSAMMENFASSUNG")
 print("=" * 80)
 print()
 
 # Finde beste Einzel-Position
 single_results = data.get("single_position_results", {})
 if single_results:
 best_single = max(single_results.items(), key=lambda x: x[1].get("accuracy", 0))
 print(f"Beste Einzel-Position: {best_single[0]}")
 print(f" Accuracy: {best_single[1].get('accuracy', 0):.2f}%")
 print()
 
 # Finde beste Kombination
 if combo_results:
 best_combo = max(combo_results.items(), key=lambda x: x[1].get("accuracy", 0))
 combo_data = best_combo[1]
 positions = combo_data.get("positions", [])
 transformations = combo_data.get("transformations", [])
 accuracy = combo_data.get("accuracy", 0)
 
 print(f"Beste Kombination: Position {positions[0]} ({transformations[0]}) + {positions[1]} ({transformations[1]})")
 print(f" Accuracy: {accuracy:.2f}%")
 print()

if __name__ == "__main__":
 main()

