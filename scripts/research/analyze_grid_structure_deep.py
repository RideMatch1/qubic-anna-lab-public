#!/usr/bin/env python3
"""
Grid/Raster-Struktur vertiefen
- Analyze exakte Grid-Struktur
- Finde Raster-Patterns
- Verstehe wie Sätze angeordnet sind
- KEINE Halluzinationen - nur echte Daten!
"""

import json
import sys
from pathlib import Path
from typing import Dict, List
from collections import Counter, defaultdict
from datetime import datetime
import math

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

ALL_MESSAGES_FILE = project_root / "outputs" / "derived" / "all_anna_messages.json"
OUTPUT_DIR = project_root / "outputs" / "derived"
REPORTS_DIR = project_root / "outputs" / "reports"

def analyze_grid_structure(sentences: List[Dict]) -> Dict:
 """Analyze Grid-Struktur im Detail."""
 
 # Analyze Positionen
 position_map = defaultdict(list)
 
 for sentence in sentences:
 start_pos = sentence.get("start_position", 0)
 end_pos = sentence.get("end_position", 0)
 mid_pos = (start_pos + end_pos) // 2
 
 position_map[mid_pos].append(sentence)
 
 # Finde Grid-Dimensionen
 # Check verschiedene Grid-Größen (7x7, 8x8, 10x10, etc.)
 grid_analyses = {}
 
 for grid_size in [7, 8, 10, 14, 15]:
 grid_positions = {}
 for pos, sentences_list in position_map.items():
 grid_x = pos % grid_size
 grid_y = pos // grid_size
 grid_key = (grid_x, grid_y)
 
 if grid_key not in grid_positions:
 grid_positions[grid_key] = []
 grid_positions[grid_key].extend(sentences_list)
 
 # Berechne Grid-Dichte
 total_cells = grid_size * grid_size
 filled_cells = len(grid_positions)
 density = filled_cells / total_cells if total_cells > 0 else 0
 
 # Berechne Cluster-Qualität
 cluster_sizes = [len(sentences) for sentences in grid_positions.values()]
 avg_cluster_size = sum(cluster_sizes) / len(cluster_sizes) if cluster_sizes else 0
 max_cluster_size = max(cluster_sizes) if cluster_sizes else 0
 
 grid_analyses[grid_size] = {
 "grid_size": grid_size,
 "total_cells": total_cells,
 "filled_cells": filled_cells,
 "density": density,
 "avg_cluster_size": avg_cluster_size,
 "max_cluster_size": max_cluster_size,
 "grid_positions": {f"{k[0]},{k[1]}": len(v) for k, v in grid_positions.items()}
 }
 
 # Finde beste Grid-Größe (höchste Dichte + Cluster-Qualität)
 best_grid = max(grid_analyses.items(), key=lambda x: (x[1]["density"], x[1]["avg_cluster_size"]))
 
 return {
 "position_map": {k: len(v) for k, v in position_map.items()},
 "grid_analyses": grid_analyses,
 "best_grid": {
 "size": best_grid[0],
 "analysis": best_grid[1]
 }
 }

def analyze_block_end_grid(sentences: List[Dict]) -> Dict:
 """Analyze Grid in Bezug auf Block-Ende-Positionen."""
 
 block_end_positions = [13, 27, 41, 55]
 
 block_end_sentences = defaultdict(list)
 other_sentences = []
 
 for sentence in sentences:
 start_pos = sentence.get("start_position", 0)
 end_pos = sentence.get("end_position", 0)
 mid_pos = (start_pos + end_pos) // 2
 
 # Check ob Satz nahe Block-Ende ist
 is_near_block_end = False
 for block_end in block_end_positions:
 if abs(mid_pos - block_end) <= 3: # ±3 Positionen
 block_end_sentences[block_end].append(sentence)
 is_near_block_end = True
 break
 
 if not is_near_block_end:
 other_sentences.append(sentence)
 
 return {
 "block_end_sentences": {k: len(v) for k, v in block_end_sentences.items()},
 "other_sentences": len(other_sentences),
 "total_block_end": sum(len(v) for v in block_end_sentences.values())
 }

def main():
 """Hauptfunktion."""
 
 print("=" * 80)
 print("GRID/RASTER-STRUKTUR VERTIEFEN")
 print("=" * 80)
 print()
 print("⚠️ KEINE HALLUZINATIONEN - NUR ECHTE DATEN!")
 print()
 
 # Load Sätze
 print("📂 Load Sätze...")
 if not ALL_MESSAGES_FILE.exists():
 print(f"❌ Datei nicht gefunden: {ALL_MESSAGES_FILE}")
 return
 
 with ALL_MESSAGES_FILE.open() as f:
 messages_data = json.load(f)
 
 top_sentences = messages_data.get("top_sentences", [])
 print(f"✅ {len(top_sentences)} Sätze geloadn")
 print()
 
 # Analyze Grid-Struktur
 print("🔍 Analyze Grid-Struktur...")
 grid_analysis = analyze_grid_structure(top_sentences)
 print("✅ Grid-Analyse abgeschlossen")
 print()
 
 # Analyze Block-Ende-Grid
 print("🔍 Analyze Block-Ende-Grid...")
 block_end_analysis = analyze_block_end_grid(top_sentences)
 print("✅ Block-Ende-Analyse abgeschlossen")
 print()
 
 # Zeige Ergebnisse
 print("=" * 80)
 print("ERGEBNISSE")
 print("=" * 80)
 print()
 
 print("📊 Grid-Analysen (verschiedene Größen):")
 for grid_size, analysis in sorted(grid_analysis["grid_analyses"].items()):
 print(f" Grid {grid_size}x{grid_size}:")
 print(f" Dichte: {analysis['density']*100:.1f}%")
 print(f" Gefüllte Zellen: {analysis['filled_cells']}/{analysis['total_cells']}")
 print(f" Ø Cluster-Größe: {analysis['avg_cluster_size']:.1f}")
 print()
 
 best = grid_analysis["best_grid"]
 print(f"📊 Beste Grid-Größe: {best['size']}x{best['size']}")
 print(f" Dichte: {best['analysis']['density']*100:.1f}%")
 print(f" Ø Cluster-Größe: {best['analysis']['avg_cluster_size']:.1f}")
 print()
 
 print("📊 Block-Ende-Analyse:")
 for block_end, count in sorted(block_end_analysis["block_end_sentences"].items()):
 print(f" Position {block_end}: {count} Sätze")
 print(f" Andere Positionen: {block_end_analysis['other_sentences']} Sätze")
 print()
 
 # Speichere Ergebnisse
 OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
 
 output_data = {
 "timestamp": datetime.now().isoformat(),
 "total_sentences": len(top_sentences),
 "grid_analysis": grid_analysis,
 "block_end_analysis": block_end_analysis
 }
 
 output_file = OUTPUT_DIR / "grid_structure_deep_analysis.json"
 with output_file.open("w") as f:
 json.dump(output_data, f, indent=2)
 print(f"💾 Ergebnisse gespeichert: {output_file}")
 
 print()
 print("=" * 80)
 print("✅ ANALYSE ABGESCHLOSSEN")
 print("=" * 80)

if __name__ == "__main__":
 main()

