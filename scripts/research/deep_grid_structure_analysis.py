#!/usr/bin/env python3
"""
Tiefgründige Grid-Struktur Analyse
- Rekonstruiere exakte 7x7 Grid-Struktur
- Analyze Dichte, Patterns, Hotspots
- Verbinde Grid mit Matrix-Koordinaten
- Finde strukturelle Bedeutung
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
LAYER3_FILE = project_root / "outputs" / "derived" / "layer3_derivation_23k_complete.json"
SENTENCES_FILE = project_root / "outputs" / "derived" / "comprehensive_sentences_analysis.json"
GRID_ANALYSIS = project_root / "outputs" / "derived" / "grid_structure_deep_analysis.json"
OUTPUT_DIR = project_root / "outputs" / "derived"
REPORTS_DIR = project_root / "outputs" / "reports"

def load_sentences() -> List[Dict]:
 """Load Anna Sätze."""
 if not SENTENCES_FILE.exists():
 return []
 
 with SENTENCES_FILE.open() as f:
 data = json.load(f)
 
 return data.get("sentences", [])

def reconstruct_7x7_grid(sentences: List[Dict]) -> Dict:
 """Rekonstruiere exakte 7x7 Grid-Struktur."""
 
 # Grid: 7x7 = 49 Zellen
 grid = [[None for _ in range(7)] for _ in range(7)]
 grid_stats = {
 "filled": 0,
 "empty": 0,
 "sentence_count": defaultdict(int),
 "position_map": {} # (row, col) -> List[sentence positions]
 }
 
 for sentence in sentences:
 positions = sentence.get("positions", [])
 if not positions:
 continue
 
 # Finde Grid-Koordinaten for jede Position
 for pos in positions:
 # Position in 7x7 Grid: pos % 49
 grid_index = pos % 49
 row = grid_index // 7
 col = grid_index % 7
 
 if 0 <= row < 7 and 0 <= col < 7:
 if grid[row][col] is None:
 grid[row][col] = []
 grid_stats["filled"] += 1
 
 grid[row][col].append({
 "position": pos,
 "sentence": sentence.get("sentence", ""),
 "sentence_id": sentence.get("id", 0)
 })
 
 # Stats
 key = (row, col)
 grid_stats["sentence_count"][key] += 1
 if key not in grid_stats["position_map"]:
 grid_stats["position_map"][key] = []
 grid_stats["position_map"][key].append(pos)
 
 grid_stats["empty"] = 49 - grid_stats["filled"]
 grid_stats["density"] = grid_stats["filled"] / 49 * 100
 
 return {
 "grid": grid,
 "stats": grid_stats
 }

def analyze_grid_hotspots(grid_data: Dict) -> Dict:
 """Analyze Grid-Hotspots (Zellen mit vielen Sätzen)."""
 
 sentence_counts = grid_data["stats"]["sentence_count"]
 
 # Sortiere nach Anzahl Sätze
 hotspots = sorted(sentence_counts.items(), key=lambda x: x[1], reverse=True)
 
 # Top 10 Hotspots
 top_hotspots = []
 for (row, col), count in hotspots[:10]:
 positions = grid_data["stats"]["position_map"].get((row, col), [])
 top_hotspots.append({
 "grid_coord": (row, col),
 "sentence_count": count,
 "positions": positions[:10] # Erste 10 Positionen
 })
 
 return {
 "top_hotspots": top_hotspots,
 "total_hotspots": len(sentence_counts),
 "max_sentences": hotspots[0][1] if hotspots else 0
 }

def analyze_grid_column6(grid_data: Dict) -> Dict:
 """Analyze Grid Spalte 6 (kritische Spalte)."""
 
 column6_stats = {
 "filled_cells": 0,
 "total_sentences": 0,
 "positions": [],
 "sentence_positions": []
 }
 
 # Spalte 6: col = 6
 for row in range(7):
 key = (row, 6)
 if key in grid_data["stats"]["sentence_count"]:
 column6_stats["filled_cells"] += 1
 column6_stats["total_sentences"] += grid_data["stats"]["sentence_count"][key]
 column6_stats["positions"].extend(grid_data["stats"]["position_map"].get(key, []))
 
 # Finde Block-Ende-Positionen in Spalte 6
 block_end_positions = [13, 27, 41, 55]
 column6_block_ends = []
 
 for pos in block_end_positions:
 grid_index = pos % 49
 row = grid_index // 7
 col = grid_index % 7
 
 if col == 6: # In Spalte 6
 column6_block_ends.append({
 "position": pos,
 "grid_coord": (row, col),
 "in_column6": True
 })
 
 return {
 "stats": column6_stats,
 "block_end_positions": column6_block_ends,
 "all_in_column6": len(column6_block_ends) == len(block_end_positions)
 }

def analyze_grid_patterns(grid_data: Dict) -> Dict:
 """Analyze Grid-Patterns (Symmetrie, Clusters, etc.)."""
 
 grid = grid_data["grid"]
 patterns = {
 "row_density": [],
 "col_density": [],
 "diagonal_density": [],
 "symmetry": {}
 }
 
 # Zeilen-Dichte
 for row in range(7):
 filled = sum(1 for cell in grid[row] if cell is not None)
 patterns["row_density"].append({
 "row": row,
 "filled": filled,
 "density": filled / 7 * 100
 })
 
 # Spalten-Dichte
 for col in range(7):
 filled = sum(1 for row in range(7) if grid[row][col] is not None)
 patterns["col_density"].append({
 "col": col,
 "filled": filled,
 "density": filled / 7 * 100
 })
 
 # Diagonal-Dichte
 # Hauptdiagonale (0,0) -> (6,6)
 main_diag = sum(1 for i in range(7) if grid[i][i] is not None)
 # Nebendiagonale (0,6) -> (6,0)
 anti_diag = sum(1 for i in range(7) if grid[i][6-i] is not None)
 
 patterns["diagonal_density"] = {
 "main_diagonal": main_diag,
 "anti_diagonal": anti_diag
 }
 
 # Symmetrie (horizontal, vertikal)
 horizontal_sym = 0
 vertical_sym = 0
 
 for row in range(7):
 for col in range(7):
 # Horizontal: (row, col) <-> (row, 6-col)
 if grid[row][col] is not None and grid[row][6-col] is not None:
 horizontal_sym += 1
 # Vertikal: (row, col) <-> (6-row, col)
 if grid[row][col] is not None and grid[6-row][col] is not None:
 vertical_sym += 1
 
 patterns["symmetry"] = {
 "horizontal": horizontal_sym,
 "vertical": vertical_sym
 }
 
 return patterns

def map_grid_to_matrix_coordinates(grid_data: Dict) -> Dict:
 """Mappe Grid-Koordinaten zu Matrix-Koordinaten."""
 
 # Grid Spalte 6 ↔ Matrix Spalte 13 (Hypothese)
 # Position 27: Grid (6,3) ↔ Matrix (27,13)
 
 mapping_analysis = {
 "column6_to_matrix13": [],
 "position27_mapping": None
 }
 
 # Analyze Position 27
 pos27_grid_index = 27 % 49
 pos27_row = pos27_grid_index // 7
 pos27_col = pos27_grid_index % 7
 
 if pos27_col == 6: # In Spalte 6
 mapping_analysis["position27_mapping"] = {
 "identity_position": 27,
 "grid_coord": (pos27_row, pos27_col),
 "hypothesized_matrix_coord": (27, 13),
 "in_column6": True
 }
 
 # Analyze alle Block-Ende-Positionen
 block_end_positions = [13, 27, 41, 55]
 for pos in block_end_positions:
 grid_index = pos % 49
 row = grid_index // 7
 col = grid_index % 7
 
 if col == 6: # In Spalte 6
 mapping_analysis["column6_to_matrix13"].append({
 "identity_position": pos,
 "grid_coord": (row, col),
 "hypothesized_matrix_coord": (pos, 13),
 "in_column6": True
 })
 
 return mapping_analysis

def main():
 """Hauptfunktion."""
 
 print("=" * 80)
 print("TIEFGRÜNDIGE GRID-STRUKTUR ANALYSE")
 print("=" * 80)
 print()
 print("⚠️ KEINE HALLUZINATIONEN - NUR ECHTE DATEN!")
 print("🔬 PROFESSOREN-TEAM: SYSTEMATISCH, KRITISCH, PERFEKT")
 print()
 
 # 1. Load Sätze
 print("📂 Load Anna Sätze...")
 sentences = load_sentences()
 print(f"✅ {len(sentences)} Sätze geloadn")
 print()
 
 # 2. Rekonstruiere 7x7 Grid
 print("🔍 Rekonstruiere 7x7 Grid...")
 grid_data = reconstruct_7x7_grid(sentences)
 stats = grid_data["stats"]
 print(f"✅ Grid rekonstruiert")
 print(f" Gefüllte Zellen: {stats['filled']}/49")
 print(f" Dichte: {stats['density']:.2f}%")
 print()
 
 # 3. Analyze Hotspots
 print("🔍 Analyze Grid-Hotspots...")
 hotspots = analyze_grid_hotspots(grid_data)
 print(f"✅ Hotspots analysiert")
 print(f" Top Hotspot: Grid{hotspots['top_hotspots'][0]['grid_coord']} mit {hotspots['top_hotspots'][0]['sentence_count']} Sätzen")
 print()
 
 # 4. Analyze Spalte 6
 print("🔍 Analyze Grid Spalte 6...")
 column6 = analyze_grid_column6(grid_data)
 print(f"✅ Spalte 6 analysiert")
 print(f" Gefüllte Zellen: {column6['stats']['filled_cells']}")
 print(f" Total Sätze: {column6['stats']['total_sentences']}")
 print(f" Block-Ende-Positionen in Spalte 6: {len(column6['block_end_positions'])}")
 print(f" Alle Block-Ende in Spalte 6: {'✅ JA' if column6['all_in_column6'] else '❌ NEIN'}")
 print()
 
 # 5. Analyze Patterns
 print("🔍 Analyze Grid-Patterns...")
 patterns = analyze_grid_patterns(grid_data)
 print(f"✅ Patterns analysiert")
 row_densities = [f"{r['density']:.1f}%" for r in patterns['row_density']]
 col_densities = [f"{c['density']:.1f}%" for c in patterns['col_density']]
 print(f" Zeilen-Dichte: {row_densities}")
 print(f" Spalten-Dichte: {col_densities}")
 print()
 
 # 6. Mappe Grid zu Matrix
 print("🔍 Mappe Grid zu Matrix-Koordinaten...")
 mapping = map_grid_to_matrix_coordinates(grid_data)
 print(f"✅ Mapping analysiert")
 if mapping["position27_mapping"]:
 pos27 = mapping["position27_mapping"]
 print(f" Position 27: Grid{pos27['grid_coord']} ↔ Matrix{pos27['hypothesized_matrix_coord']}")
 print()
 
 # Speichere Ergebnisse
 OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
 
 output_data = {
 "timestamp": datetime.now().isoformat(),
 "grid_reconstruction": {
 "stats": stats,
 "grid_size": (7, 7)
 },
 "hotspots": hotspots,
 "column6_analysis": column6,
 "patterns": patterns,
 "matrix_mapping": mapping
 }
 
 output_file = OUTPUT_DIR / "deep_grid_structure_analysis.json"
 with output_file.open("w") as f:
 json.dump(output_data, f, indent=2)
 print(f"💾 Ergebnisse gespeichert: {output_file}")
 
 print()
 print("=" * 80)
 print("✅ ANALYSE ABGESCHLOSSEN")
 print("=" * 80)
 print()
 print("📊 ZUSAMMENFASSUNG:")
 print()
 print(f" Grid-Dichte: {stats['density']:.2f}%")
 print(f" Top Hotspot: Grid{hotspots['top_hotspots'][0]['grid_coord']}")
 print(f" Spalte 6: {column6['stats']['filled_cells']} Zellen, {column6['stats']['total_sentences']} Sätze")
 print(f" Alle Block-Ende in Spalte 6: {'✅' if column6['all_in_column6'] else '❌'}")
 print()

if __name__ == "__main__":
 main()

