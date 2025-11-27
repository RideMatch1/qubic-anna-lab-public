#!/usr/bin/env python3
"""
Umfassende Grid-Struktur Analyse
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
GRID_ANALYSIS = project_root / "outputs" / "derived" / "grid_structure_deep_analysis.json"
SENTENCES_FILE = project_root / "outputs" / "practical" / "sentences_for_communication.json"
OUTPUT_DIR = project_root / "outputs" / "derived"
REPORTS_DIR = project_root / "outputs" / "reports"

def load_sentences_from_layer3() -> List[Dict]:
 """Load Sätze direkt aus Layer-3 Identities."""
 
 if not LAYER3_FILE.exists():
 return []
 
 with LAYER3_FILE.open() as f:
 layer3_data = json.load(f)
 
 layer3_results = layer3_data.get("results", [])
 
 # Load Wörterbuch
 dictionary_file = project_root / "outputs" / "practical" / "anna_dictionary.json"
 known_words = set()
 if dictionary_file.exists():
 with dictionary_file.open() as f:
 dictionary = json.load(f)
 all_words = dictionary.get("all_words", {})
 known_words = {word.upper() for word in all_words.keys()}
 
 # Finde Sätze (2+ Wörter, max 20 Zeichen Abstand)
 sentences = []
 for entry in layer3_results:
 l3_id = entry.get("layer3_identity", "")
 if not l3_id or len(l3_id) != 60:
 continue
 
 # Suche nach Wort-Sequenzen
 words_found = []
 for word in known_words:
 if word in l3_id:
 start_pos = l3_id.find(word)
 words_found.append({
 "word": word,
 "start": start_pos,
 "end": start_pos + len(word) - 1
 })
 
 # Sortiere nach Position
 words_found.sort(key=lambda x: x["start"])
 
 # Finde Sequenzen (2+ Wörter, max 20 Zeichen Abstand)
 for i in range(len(words_found)):
 for j in range(i + 1, len(words_found)):
 word1 = words_found[i]
 word2 = words_found[j]
 distance = word2["start"] - word1["end"] - 1
 
 if distance <= 20:
 sentence_words = [word1["word"], word2["word"]]
 start_pos = word1["start"]
 end_pos = word2["end"]
 
 # Erweitere zu längeren Sätzen
 for k in range(j + 1, len(words_found)):
 word3 = words_found[k]
 distance2 = word3["start"] - words_found[k-1]["end"] - 1
 if distance2 <= 20:
 sentence_words.append(word3["word"])
 end_pos = word3["end"]
 else:
 break
 
 sentences.append({
 "identity": l3_id,
 "sentence": " ".join(sentence_words),
 "words": sentence_words,
 "start_position": start_pos,
 "end_position": end_pos,
 "positions": list(range(start_pos, end_pos + 1))
 })
 
 return sentences

def reconstruct_7x7_grid(sentences: List[Dict]) -> Dict:
 """Rekonstruiere exakte 7x7 Grid-Struktur."""
 
 # Grid: 7x7 = 49 Zellen
 grid = [[[] for _ in range(7)] for _ in range(7)]
 grid_stats = {
 "filled": 0,
 "empty": 0,
 "sentence_count": defaultdict(int),
 "position_map": defaultdict(list), # (row, col) -> List[sentence positions]
 "identity_map": defaultdict(set) # (row, col) -> Set[identities]
 }
 
 for sentence in sentences:
 positions = sentence.get("positions", [])
 identity = sentence.get("identity", "")
 
 if not positions:
 continue
 
 # Finde Grid-Koordinaten for jede Position
 for pos in positions:
 # Position in 7x7 Grid: pos % 49
 grid_index = pos % 49
 row = grid_index // 7
 col = grid_index % 7
 
 if 0 <= row < 7 and 0 <= col < 7:
 key = (row, col)
 
 if not grid[row][col]:
 grid_stats["filled"] += 1
 
 grid[row][col].append({
 "position": pos,
 "sentence": sentence.get("sentence", ""),
 "identity": identity
 })
 
 # Stats
 grid_stats["sentence_count"][key] += 1
 grid_stats["position_map"][key].append(pos)
 grid_stats["identity_map"][key].add(identity)
 
 grid_stats["empty"] = 49 - grid_stats["filled"]
 grid_stats["density"] = grid_stats["filled"] / 49 * 100
 
 return {
 "grid": grid,
 "stats": grid_stats
 }

def analyze_grid_column6(grid_data: Dict) -> Dict:
 """Analyze Grid Spalte 6 (kritische Spalte)."""
 
 column6_stats = {
 "filled_cells": 0,
 "total_sentences": 0,
 "total_identities": 0,
 "positions": [],
 "sentence_positions": []
 }
 
 # Spalte 6: col = 6
 for row in range(7):
 key = (row, 6)
 if key in grid_data["stats"]["sentence_count"]:
 column6_stats["filled_cells"] += 1
 column6_stats["total_sentences"] += grid_data["stats"]["sentence_count"][key]
 column6_stats["total_identities"] += len(grid_data["stats"]["identity_map"][key])
 column6_stats["positions"].extend(grid_data["stats"]["position_map"].get(key, []))
 
 # Finde Block-Ende-Positionen in Spalte 6
 block_end_positions = [13, 27, 41, 55]
 column6_block_ends = []
 
 for pos in block_end_positions:
 grid_index = pos % 49
 row = grid_index // 7
 col = grid_index % 7
 
 column6_block_ends.append({
 "position": pos,
 "grid_coord": (row, col),
 "in_column6": col == 6,
 "sentence_count": grid_data["stats"]["sentence_count"].get((row, col), 0)
 })
 
 return {
 "stats": column6_stats,
 "block_end_positions": column6_block_ends,
 "all_in_column6": all(b["in_column6"] for b in column6_block_ends)
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
 identities = list(grid_data["stats"]["identity_map"].get((row, col), []))
 top_hotspots.append({
 "grid_coord": (row, col),
 "sentence_count": count,
 "identity_count": len(identities),
 "positions": sorted(set(positions))[:10] # Erste 10 unique Positionen
 })
 
 return {
 "top_hotspots": top_hotspots,
 "total_hotspots": len(sentence_counts),
 "max_sentences": hotspots[0][1] if hotspots else 0
 }

def analyze_grid_patterns(grid_data: Dict) -> Dict:
 """Analyze Grid-Patterns (Symmetrie, Clusters, etc.)."""
 
 grid = grid_data["grid"]
 patterns = {
 "row_density": [],
 "col_density": [],
 "diagonal_density": {},
 "symmetry": {}
 }
 
 # Zeilen-Dichte
 for row in range(7):
 filled = sum(1 for cell in grid[row] if cell)
 patterns["row_density"].append({
 "row": row,
 "filled": filled,
 "density": filled / 7 * 100
 })
 
 # Spalten-Dichte
 for col in range(7):
 filled = sum(1 for row in range(7) if grid[row][col])
 patterns["col_density"].append({
 "col": col,
 "filled": filled,
 "density": filled / 7 * 100
 })
 
 # Diagonal-Dichte
 # Hauptdiagonale (0,0) -> (6,6)
 main_diag = sum(1 for i in range(7) if grid[i][i])
 # Nebendiagonale (0,6) -> (6,0)
 anti_diag = sum(1 for i in range(7) if grid[i][6-i])
 
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
 if grid[row][col] and grid[row][6-col]:
 horizontal_sym += 1
 # Vertikal: (row, col) <-> (6-row, col)
 if grid[row][col] and grid[6-row][col]:
 vertical_sym += 1
 
 patterns["symmetry"] = {
 "horizontal": horizontal_sym,
 "vertical": vertical_sym
 }
 
 return patterns

def map_grid_to_identity_positions(grid_data: Dict) -> Dict:
 """Mappe Grid-Koordinaten zu Identity-Positionen."""
 
 # Analyze welche Identity-Positionen in welchen Grid-Zellen sind
 position_to_grid = defaultdict(list)
 
 for (row, col), positions in grid_data["stats"]["position_map"].items():
 for pos in positions:
 position_to_grid[pos].append({
 "grid_coord": (row, col),
 "sentence_count": grid_data["stats"]["sentence_count"].get((row, col), 0)
 })
 
 # Analyze Block-Ende-Positionen
 block_end_positions = [13, 27, 41, 55]
 block_end_mapping = []
 
 for pos in block_end_positions:
 grid_index = pos % 49
 row = grid_index // 7
 col = grid_index % 7
 
 block_end_mapping.append({
 "identity_position": pos,
 "grid_coord": (row, col),
 "sentence_count": grid_data["stats"]["sentence_count"].get((row, col), 0),
 "in_column6": col == 6
 })
 
 return {
 "position_to_grid": dict(position_to_grid),
 "block_end_mapping": block_end_mapping
 }

def main():
 """Hauptfunktion."""
 
 print("=" * 80)
 print("UMFASSENDE GRID-STRUKTUR ANALYSE")
 print("=" * 80)
 print()
 print("⚠️ KEINE HALLUZINATIONEN - NUR ECHTE DATEN!")
 print("🔬 PROFESSOREN-TEAM: SYSTEMATISCH, KRITISCH, PERFEKT")
 print()
 
 # 1. Load Sätze
 print("📂 Load Sätze aus Layer-3 Identities...")
 sentences = load_sentences_from_layer3()
 print(f"✅ {len(sentences)} Sätze gefunden")
 print()
 
 # 2. Rekonstruiere 7x7 Grid
 print("🔍 Rekonstruiere 7x7 Grid...")
 grid_data = reconstruct_7x7_grid(sentences)
 stats = grid_data["stats"]
 print(f"✅ Grid rekonstruiert")
 print(f" Gefüllte Zellen: {stats['filled']}/49")
 print(f" Dichte: {stats['density']:.2f}%")
 print(f" Total Sätze: {sum(stats['sentence_count'].values())}")
 print()
 
 # 3. Analyze Spalte 6
 print("🔍 Analyze Grid Spalte 6...")
 column6 = analyze_grid_column6(grid_data)
 print(f"✅ Spalte 6 analysiert")
 print(f" Gefüllte Zellen: {column6['stats']['filled_cells']}")
 print(f" Total Sätze: {column6['stats']['total_sentences']}")
 print(f" Total Identities: {column6['stats']['total_identities']}")
 print(f" Block-Ende-Positionen in Spalte 6: {sum(1 for b in column6['block_end_positions'] if b['in_column6'])}")
 print(f" Alle Block-Ende in Spalte 6: {'✅ JA' if column6['all_in_column6'] else '❌ NEIN'}")
 print()
 
 # Zeige Block-Ende-Positionen
 print("📊 Block-Ende-Positionen:")
 for block_end in column6["block_end_positions"]:
 pos = block_end["position"]
 coord = block_end["grid_coord"]
 in_col6 = "✅" if block_end["in_column6"] else "❌"
 count = block_end["sentence_count"]
 print(f" {in_col6} Position {pos}: Grid{coord}, {count} Sätze")
 print()
 
 # 4. Analyze Hotspots
 print("🔍 Analyze Grid-Hotspots...")
 hotspots = analyze_grid_hotspots(grid_data)
 print(f"✅ Hotspots analysiert")
 print(f" Top Hotspot: Grid{hotspots['top_hotspots'][0]['grid_coord']} mit {hotspots['top_hotspots'][0]['sentence_count']} Sätzen")
 print()
 
 print("📊 Top 5 Hotspots:")
 for i, hotspot in enumerate(hotspots["top_hotspots"][:5], 1):
 coord = hotspot["grid_coord"]
 print(f" {i}. Grid{coord}: {hotspot['sentence_count']} Sätze, {hotspot['identity_count']} Identities")
 print()
 
 # 5. Analyze Patterns
 print("🔍 Analyze Grid-Patterns...")
 patterns = analyze_grid_patterns(grid_data)
 print(f"✅ Patterns analysiert")
 
 row_densities = [f"{r['density']:.1f}%" for r in patterns['row_density']]
 col_densities = [f"{c['density']:.1f}%" for c in patterns['col_density']]
 print(f" Zeilen-Dichte: {row_densities}")
 print(f" Spalten-Dichte: {col_densities}")
 print(f" Hauptdiagonale: {patterns['diagonal_density']['main_diagonal']}/7")
 print(f" Nebendiagonale: {patterns['diagonal_density']['anti_diagonal']}/7")
 print()
 
 # 6. Mappe Grid zu Identity-Positionen
 print("🔍 Mappe Grid zu Identity-Positionen...")
 position_mapping = map_grid_to_identity_positions(grid_data)
 print(f"✅ Mapping analysiert")
 print()
 
 # Speichere Ergebnisse
 OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
 
 output_data = {
 "timestamp": datetime.now().isoformat(),
 "total_sentences": len(sentences),
 "grid_reconstruction": {
 "stats": {
 "filled": stats["filled"],
 "empty": stats["empty"],
 "density": stats["density"],
 "total_sentences": sum(stats["sentence_count"].values()),
 "total_identities": sum(len(ids) for ids in stats["identity_map"].values())
 },
 "grid_size": (7, 7)
 },
 "column6_analysis": column6,
 "hotspots": hotspots,
 "patterns": patterns,
 "position_mapping": position_mapping
 }
 
 output_file = OUTPUT_DIR / "comprehensive_grid_analysis.json"
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
 print(f" Total Sätze: {sum(stats['sentence_count'].values())}")
 print(f" Top Hotspot: Grid{hotspots['top_hotspots'][0]['grid_coord']}")
 print(f" Spalte 6: {column6['stats']['filled_cells']} Zellen, {column6['stats']['total_sentences']} Sätze")
 print(f" Alle Block-Ende in Spalte 6: {'✅' if column6['all_in_column6'] else '❌'}")
 print()

if __name__ == "__main__":
 main()

