#!/usr/bin/env python3
"""
Grid-Struktur & Matrix-Verbindung vertiefen
- Analyze exakte 7x7 Grid-Struktur
- Finde Verbindung zur Anna Matrix
- Analyze Position 27 im context
- KEINE Halluzinationen - nur echte Daten!
"""

import json
import sys
from pathlib import Path
from typing import Dict, List, Tuple
from collections import defaultdict, Counter
from datetime import datetime

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

ALL_MESSAGES = project_root / "outputs" / "derived" / "all_anna_messages.json"
GRID_ANALYSIS = project_root / "outputs" / "derived" / "grid_structure_deep_analysis.json"
LAYER3_FILE = project_root / "outputs" / "derived" / "layer3_derivation_23k_complete.json"
OUTPUT_DIR = project_root / "outputs" / "derived"
REPORTS_DIR = project_root / "outputs" / "reports"

def build_exact_grid(sentences: List[Dict], grid_size: int = 7) -> Dict:
 """Baue exaktes Grid-Mapping."""
 
 grid = defaultdict(list)
 position_to_grid = {}
 
 for sentence in sentences:
 start_pos = sentence.get("start_position", 0)
 end_pos = sentence.get("end_position", 0)
 mid_pos = (start_pos + end_pos) // 2
 
 # Mappe Position zu Grid-Koordinaten
 grid_x = mid_pos % grid_size
 grid_y = mid_pos // grid_size
 
 grid_key = (grid_x, grid_y)
 grid[grid_key].append(sentence)
 
 position_to_grid[mid_pos] = grid_key
 
 # Analyze Grid-Dichte
 total_cells = grid_size * grid_size
 filled_cells = len(grid)
 density = filled_cells / total_cells if total_cells > 0 else 0
 
 # Finde Cluster
 cluster_sizes = [len(sentences) for sentences in grid.values()]
 avg_cluster_size = sum(cluster_sizes) / len(cluster_sizes) if cluster_sizes else 0
 max_cluster_size = max(cluster_sizes) if cluster_sizes else 0
 
 return {
 "grid_size": grid_size,
 "total_cells": total_cells,
 "filled_cells": filled_cells,
 "density": density,
 "avg_cluster_size": avg_cluster_size,
 "max_cluster_size": max_cluster_size,
 "grid": {f"{k[0]},{k[1]}": len(v) for k, v in grid.items()},
 "position_to_grid": position_to_grid,
 "grid_details": {f"{k[0]},{k[1]}": [s.get("sentence", "")[:50] for s in v[:3]] for k, v in grid.items()}
 }

def analyze_position27_in_grid(sentences: List[Dict], grid_analysis: Dict) -> Dict:
 """Analyze Position 27 im Grid-context."""
 
 position27_sentences = []
 block_end_positions = [13, 27, 41, 55]
 
 for sentence in sentences:
 start_pos = sentence.get("start_position", 0)
 end_pos = sentence.get("end_position", 0)
 mid_pos = (start_pos + end_pos) // 2
 
 # Check ob nahe Position 27
 if abs(mid_pos - 27) <= 3:
 position27_sentences.append({
 "sentence": sentence.get("sentence", ""),
 "start_pos": start_pos,
 "end_pos": end_pos,
 "mid_pos": mid_pos,
 "distance_to_27": abs(mid_pos - 27)
 })
 
 # Grid-Koordinaten for Position 27
 grid_size = grid_analysis.get("grid_size", 7)
 grid_x_27 = 27 % grid_size
 grid_y_27 = 27 // grid_size
 
 return {
 "position27_grid_coords": (grid_x_27, grid_y_27),
 "position27_sentences": len(position27_sentences),
 "position27_details": position27_sentences[:10], # Top 10
 "block_end_positions": {
 pos: {
 "grid_x": pos % grid_size,
 "grid_y": pos // grid_size,
 "grid_coords": (pos % grid_size, pos // grid_size)
 }
 for pos in block_end_positions
 }
 }

def analyze_matrix_connection(sentences: List[Dict], layer3_data: Dict) -> Dict:
 """Analyze Verbindung zwischen Grid und Matrix."""
 
 # Load Layer-3 Identities
 layer3_identities = {}
 if layer3_data:
 for entry in layer3_data.get("results", []):
 layer3_id = entry.get("layer3_identity", "")
 if len(layer3_id) == 60:
 layer3_identities[layer3_id] = entry
 
 # Finde Identities mit Sätzen
 identity_sentences = defaultdict(list)
 for sentence in sentences:
 identity = sentence.get("identity", "")
 if identity in layer3_identities:
 identity_sentences[identity].append(sentence)
 
 # Analyze Matrix-Koordinaten (wenn verfügbar)
 matrix_analysis = {
 "identities_with_sentences": len(identity_sentences),
 "total_sentences": len(sentences),
 "avg_sentences_per_identity": len(sentences) / len(identity_sentences) if identity_sentences else 0
 }
 
 return matrix_analysis

def analyze_grid_patterns(grid_analysis: Dict) -> Dict:
 """Analyze strukturelle Patterns im Grid."""
 
 grid_details = grid_analysis.get("grid", {})
 
 # Analyze Verteilung
 x_coords = []
 y_coords = []
 
 for key, count in grid_details.items():
 x, y = map(int, key.split(","))
 x_coords.extend([x] * count)
 y_coords.extend([y] * count)
 
 x_distribution = Counter(x_coords)
 y_distribution = Counter(y_coords)
 
 # Finde Hotspots
 hotspots = sorted(grid_details.items(), key=lambda x: x[1], reverse=True)[:10]
 
 return {
 "x_distribution": dict(x_distribution),
 "y_distribution": dict(y_distribution),
 "hotspots": hotspots,
 "most_active_x": max(x_distribution.items(), key=lambda x: x[1])[0] if x_distribution else None,
 "most_active_y": max(y_distribution.items(), key=lambda x: x[1])[0] if y_distribution else None
 }

def main():
 """Hauptfunktion."""
 
 print("=" * 80)
 print("GRID-STRUKTUR & MATRIX-VERBINDUNG VERTIEFEN")
 print("=" * 80)
 print()
 print("⚠️ KEINE HALLUZINATIONEN - NUR ECHTE DATEN!")
 print()
 
 # Load Sätze
 print("📂 Load Anna Messages...")
 if not ALL_MESSAGES.exists():
 print(f"❌ Datei nicht gefunden: {ALL_MESSAGES}")
 return
 
 with ALL_MESSAGES.open() as f:
 messages_data = json.load(f)
 
 top_sentences = messages_data.get("top_sentences", [])
 print(f"✅ {len(top_sentences)} Sätze geloadn")
 print()
 
 # Baue exaktes Grid
 print("🔍 Baue exaktes 7x7 Grid...")
 grid_analysis = build_exact_grid(top_sentences, grid_size=7)
 print(f"✅ Grid gebaut: {grid_analysis['filled_cells']}/{grid_analysis['total_cells']} Zellen gefüllt")
 print(f" Dichte: {grid_analysis['density']*100:.1f}%")
 print(f" Ø Cluster-Größe: {grid_analysis['avg_cluster_size']:.1f}")
 print()
 
 # Analyze Position 27
 print("🔍 Analyze Position 27 im Grid...")
 pos27_analysis = analyze_position27_in_grid(top_sentences, grid_analysis)
 print(f"✅ Position 27 Grid-Koordinaten: {pos27_analysis['position27_grid_coords']}")
 print(f" Sätze nahe Position 27: {pos27_analysis['position27_sentences']}")
 print()
 
 # Analyze Grid-Patterns
 print("🔍 Analyze Grid-Patterns...")
 patterns = analyze_grid_patterns(grid_analysis)
 print(f"✅ Patterns analysiert")
 print(f" Aktivste X-Koordinate: {patterns['most_active_x']}")
 print(f" Aktivste Y-Koordinate: {patterns['most_active_y']}")
 print()
 
 # Load Layer-3 Daten
 layer3_data = {}
 if LAYER3_FILE.exists():
 print("📂 Load Layer-3 Daten...")
 with LAYER3_FILE.open() as f:
 layer3_data = json.load(f)
 print(f"✅ {len(layer3_data.get('results', []))} Layer-3 Identities geloadn")
 print()
 
 # Analyze Matrix-Verbindung
 print("🔍 Analyze Matrix-Verbindung...")
 matrix_analysis = analyze_matrix_connection(top_sentences, layer3_data)
 print(f"✅ Matrix-Analyse abgeschlossen")
 print(f" Identities mit Sätzen: {matrix_analysis['identities_with_sentences']}")
 print()
 
 # Zeige Ergebnisse
 print("=" * 80)
 print("ERGEBNISSE")
 print("=" * 80)
 print()
 
 print("📊 Grid-Struktur (7x7):")
 print(f" Gefüllte Zellen: {grid_analysis['filled_cells']}/{grid_analysis['total_cells']}")
 print(f" Dichte: {grid_analysis['density']*100:.1f}%")
 print(f" Max Cluster-Größe: {grid_analysis['max_cluster_size']}")
 print()
 
 print("📊 Position 27:")
 print(f" Grid-Koordinaten: {pos27_analysis['position27_grid_coords']}")
 print(f" Sätze: {pos27_analysis['position27_sentences']}")
 print()
 print(" Block-Ende-Positionen:")
 for pos, coords in pos27_analysis["block_end_positions"].items():
 print(f" Position {pos}: Grid ({coords['grid_x']}, {coords['grid_y']})")
 print()
 
 print("📊 Grid-Patterns:")
 print(f" Aktivste X: {patterns['most_active_x']}")
 print(f" Aktivste Y: {patterns['most_active_y']}")
 print()
 print(" Top 5 Hotspots:")
 for i, (coords, count) in enumerate(patterns["hotspots"][:5], 1):
 print(f" {i}. Grid {coords}: {count} Sätze")
 print()
 
 print("📊 Matrix-Verbindung:")
 print(f" Identities mit Sätzen: {matrix_analysis['identities_with_sentences']}")
 print(f" Ø Sätze pro Identity: {matrix_analysis['avg_sentences_per_identity']:.2f}")
 print()
 
 # Speichere Ergebnisse
 OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
 
 output_data = {
 "timestamp": datetime.now().isoformat(),
 "grid_analysis": grid_analysis,
 "position27_analysis": pos27_analysis,
 "grid_patterns": patterns,
 "matrix_analysis": matrix_analysis
 }
 
 output_file = OUTPUT_DIR / "grid_matrix_connection_analysis.json"
 with output_file.open("w") as f:
 json.dump(output_data, f, indent=2)
 print(f"💾 Ergebnisse gespeichert: {output_file}")
 
 print()
 print("=" * 80)
 print("✅ ANALYSE ABGESCHLOSSEN")
 print("=" * 80)

if __name__ == "__main__":
 main()

