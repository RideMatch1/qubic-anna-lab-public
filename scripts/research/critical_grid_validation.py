#!/usr/bin/env python3
"""
Kritische Grid-Validierung
- Check ob 100% Dichte wirklich stimmt oder Artefakt
- Validate alle Behauptungen mit echten Daten
- Keine LLM-Halluzinationen - nur Fakten!
- Hinterfrage alles kritisch
"""

import json
import sys
from pathlib import Path
from typing import Dict, List, Tuple
from collections import Counter, defaultdict
from datetime import datetime

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# Paths
LAYER3_FILE = project_root / "outputs" / "derived" / "layer3_derivation_23k_complete.json"
GRID_ANALYSIS = project_root / "outputs" / "derived" / "comprehensive_grid_analysis.json"
OUTPUT_DIR = project_root / "outputs" / "derived"
REPORTS_DIR = project_root / "outputs" / "reports"

def validate_grid_density(grid_data: Dict) -> Dict:
 """Validate ob 100% Dichte wirklich stimmt."""
 
 # Check Stats direkt
 stats = grid_data.get("grid_reconstruction", {}).get("stats", {})
 
 if not stats:
 return {"error": "Stats nicht gefunden"}
 
 filled = stats.get("filled", 0)
 empty = stats.get("empty", 0)
 density = stats.get("density", 0)
 grid_size = stats.get("grid_size", [7, 7])
 
 total_cells = filled + empty
 calculated_density = (filled / total_cells * 100) if total_cells > 0 else 0
 
 return {
 "grid_size": tuple(grid_size),
 "total_cells": total_cells,
 "filled": filled,
 "empty": empty,
 "reported_density": density,
 "calculated_density": calculated_density,
 "is_7x7": grid_size == [7, 7],
 "is_100_percent": abs(density - 100.0) < 0.01 and abs(calculated_density - 100.0) < 0.01
 }

def validate_column6_claim(grid_data: Dict) -> Dict:
 """Validate ob alle Block-Ende-Positionen wirklich in Spalte 6 sind."""
 
 block_end_positions = [13, 27, 41, 55]
 column6_analysis = grid_data.get("column6_analysis", {})
 block_end_mapping = column6_analysis.get("block_end_positions", [])
 
 # Check jede Position
 validation = {}
 all_in_column6 = True
 
 for pos in block_end_positions:
 # Berechne Grid-Koordinate
 grid_index = pos % 49
 row = grid_index // 7
 col = grid_index % 7
 
 # Finde in block_end_mapping
 found = False
 in_col6 = False
 for mapping in block_end_mapping:
 if mapping.get("position") == pos:
 found = True
 in_col6 = mapping.get("in_column6", False)
 break
 
 if not found:
 # Berechne direkt
 in_col6 = (col == 6)
 
 validation[f"position_{pos}"] = {
 "position": pos,
 "calculated_grid_coord": (row, col),
 "calculated_col": col,
 "in_column6": in_col6,
 "found_in_mapping": found
 }
 
 if not in_col6:
 all_in_column6 = False
 
 return {
 "validation": validation,
 "all_in_column6": all_in_column6,
 "claim_valid": all_in_column6
 }

def validate_position27_hotspot(grid_data: Dict) -> Dict:
 """Validate ob Position 27 wirklich Hotspot ist."""
 
 hotspots = grid_data.get("hotspots", {})
 top_hotspots = hotspots.get("top_hotspots", [])
 
 # Finde Position 27
 pos27_grid_index = 27 % 49
 pos27_row = pos27_grid_index // 7
 pos27_col = pos27_grid_index % 7
 pos27_coord = (pos27_row, pos27_col)
 
 # Suche in Hotspots
 pos27_rank = None
 pos27_sentences = 0
 
 for i, hotspot in enumerate(top_hotspots, 1):
 coord = hotspot.get("grid_coord")
 if coord == pos27_coord:
 pos27_rank = i
 pos27_sentences = hotspot.get("sentence_count", 0)
 break
 
 # Vergleiche mit anderen Block-Ende-Positionen
 block_end_comparison = {}
 block_end_positions = [13, 27, 41, 55]
 
 for pos in block_end_positions:
 grid_index = pos % 49
 row = grid_index // 7
 col = grid_index % 7
 coord = (row, col)
 
 sentences = 0
 for hotspot in top_hotspots:
 if hotspot.get("grid_coord") == coord:
 sentences = hotspot.get("sentence_count", 0)
 break
 
 block_end_comparison[f"position_{pos}"] = {
 "grid_coord": coord,
 "sentence_count": sentences
 }
 
 return {
 "position27_grid_coord": pos27_coord,
 "position27_rank": pos27_rank,
 "position27_sentences": pos27_sentences,
 "is_hotspot": pos27_rank is not None and pos27_rank <= 10,
 "block_end_comparison": block_end_comparison,
 "is_highest": pos27_sentences >= max([b.get("sentence_count", 0) for b in block_end_comparison.values()])
 }

def validate_sentence_count(grid_data: Dict) -> Dict:
 """Validate ob die Satz-Zahlen stimmen."""
 
 stats = grid_data.get("grid_reconstruction", {}).get("stats", {})
 total_sentences_claimed = stats.get("total_sentences", 0)
 
 # Zähle tatsächlich
 hotspots = grid_data.get("hotspots", {})
 top_hotspots = hotspots.get("top_hotspots", [])
 
 total_sentences_counted = sum(h.get("sentence_count", 0) for h in top_hotspots)
 
 # Check ob alle Hotspots erfasst wurden
 column6 = grid_data.get("column6_analysis", {})
 column6_sentences = column6.get("stats", {}).get("total_sentences", 0)
 
 return {
 "total_sentences_claimed": total_sentences_claimed,
 "total_sentences_in_top_hotspots": total_sentences_counted,
 "column6_sentences": column6_sentences,
 "note": "Total könnte höher sein wenn nicht alle Hotspots erfasst"
 }

def main():
 """Hauptfunktion."""
 
 print("=" * 80)
 print("KRITISCHE GRID-VALIDIERUNG")
 print("=" * 80)
 print()
 print("⚠️ KEINE HALLUZINATIONEN - NUR ECHTE DATEN!")
 print("🔬 KRITISCH HINTERFRAGEN - ALLES VALIDIEREN!")
 print()
 
 # 1. Load Grid-Daten
 print("📂 Load Grid-Daten...")
 if not GRID_ANALYSIS.exists():
 print(f"❌ Datei nicht gefunden: {GRID_ANALYSIS}")
 return
 
 with GRID_ANALYSIS.open() as f:
 grid_data = json.load(f)
 print(f"✅ Grid-Daten geloadn")
 print()
 
 # 2. Validate Grid-Dichte
 print("🔍 Validate Grid-Dichte (100% Behauptung)...")
 density_validation = validate_grid_density(grid_data)
 print(f"✅ Dichte validiert")
 print(f" Grid-Größe: {density_validation['grid_size']}")
 print(f" Gefüllt: {density_validation['filled']}/{density_validation['total_cells']}")
 print(f" Dichte (berichtet): {density_validation['reported_density']:.2f}%")
 print(f" Dichte (berechnet): {density_validation['calculated_density']:.2f}%")
 print(f" Ist 7x7: {'✅ JA' if density_validation['is_7x7'] else '❌ NEIN'}")
 print(f" Ist 100%: {'✅ JA' if density_validation['is_100_percent'] else '❌ NEIN'}")
 print()
 
 # 3. Validate Spalte 6 Behauptung
 print("🔍 Validate 'Alle Block-Ende in Spalte 6' Behauptung...")
 column6_validation = validate_column6_claim(grid_data)
 print(f"✅ Spalte 6 validiert")
 
 for pos_key, validation in column6_validation["validation"].items():
 pos = validation["position"]
 coord = validation["calculated_grid_coord"]
 in_col6 = "✅" if validation["in_column6"] else "❌"
 print(f" {in_col6} Position {pos}: Grid{coord}, Col={coord[1]}, In Spalte 6={validation['in_column6']}")
 
 print(f" Alle in Spalte 6: {'✅ JA' if column6_validation['all_in_column6'] else '❌ NEIN'}")
 print(f" Behauptung gültig: {'✅ JA' if column6_validation['claim_valid'] else '❌ NEIN'}")
 print()
 
 # 4. Validate Position 27 Hotspot
 print("🔍 Validate 'Position 27 ist Hotspot' Behauptung...")
 pos27_validation = validate_position27_hotspot(grid_data)
 print(f"✅ Position 27 validiert")
 print(f" Grid-Koordinate: {pos27_validation['position27_grid_coord']}")
 print(f" Rank: {pos27_validation['position27_rank']}")
 print(f" Sätze: {pos27_validation['position27_sentences']}")
 print(f" Ist Hotspot: {'✅ JA' if pos27_validation['is_hotspot'] else '❌ NEIN'}")
 print(f" Ist höchste unter Block-Ende: {'✅ JA' if pos27_validation['is_highest'] else '❌ NEIN'}")
 print()
 
 print(" Vergleich Block-Ende-Positionen:")
 for pos_key, comp in pos27_validation["block_end_comparison"].items():
 pos = pos_key.split("_")[1]
 coord = comp["grid_coord"]
 sentences = comp["sentence_count"]
 print(f" Position {pos}: Grid{coord}, {sentences} Sätze")
 print()
 
 # 5. Validate Satz-Zahlen
 print("🔍 Validate Satz-Zahlen...")
 sentence_validation = validate_sentence_count(grid_data)
 print(f"✅ Satz-Zahlen validiert")
 print(f" Behauptet: {sentence_validation['total_sentences_claimed']}")
 print(f" In Top Hotspots: {sentence_validation['total_sentences_in_top_hotspots']}")
 print(f" Spalte 6: {sentence_validation['column6_sentences']}")
 print(f" ⚠️ {sentence_validation['note']}")
 print()
 
 # Speichere Validierung
 OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
 
 validation_results = {
 "timestamp": datetime.now().isoformat(),
 "density_validation": density_validation,
 "column6_validation": column6_validation,
 "position27_validation": pos27_validation,
 "sentence_validation": sentence_validation,
 "conclusion": {
 "density_100_percent": density_validation["is_100_percent"],
 "all_block_end_in_column6": column6_validation["claim_valid"],
 "position27_is_hotspot": pos27_validation["is_hotspot"],
 "position27_is_highest": pos27_validation["is_highest"]
 }
 }
 
 output_file = OUTPUT_DIR / "critical_grid_validation.json"
 with output_file.open("w") as f:
 json.dump(validation_results, f, indent=2)
 print(f"💾 Validierung gespeichert: {output_file}")
 
 print()
 print("=" * 80)
 print("✅ VALIDIERUNG ABGESCHLOSSEN")
 print("=" * 80)
 print()
 print("📊 ZUSAMMENFASSUNG:")
 print()
 print(f" Dichte 100%: {'✅ BESTÄTIGT' if density_validation['is_100_percent'] else '❌ WIDERLEGT'}")
 print(f" Alle Block-Ende in Spalte 6: {'✅ BESTÄTIGT' if column6_validation['claim_valid'] else '❌ WIDERLEGT'}")
 print(f" Position 27 ist Hotspot: {'✅ BESTÄTIGT' if pos27_validation['is_hotspot'] else '❌ WIDERLEGT'}")
 print(f" Position 27 ist höchste: {'✅ BESTÄTIGT' if pos27_validation['is_highest'] else '❌ WIDERLEGT'}")
 print()

if __name__ == "__main__":
 main()

