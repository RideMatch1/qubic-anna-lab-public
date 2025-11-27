#!/usr/bin/env python3
"""
Direkte Analyse der 26 Zero-Koordinaten aus der Dokumentation.

Koordinaten aus Comprehensive Hidden Message Analysis.md
"""

import json
import math
from pathlib import Path
from typing import List, Tuple, Dict
from collections import defaultdict
from datetime import datetime

import sys
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

OUTPUT_DIR = Path("outputs/derived")
REPORTS_DIR = Path("outputs/reports")

# Bekannte Zero-Koordinaten aus Dokumentation
# (Excel 1-based, wir verwenden 0-based)
KNOWN_ZEROS = [
 (4, 23), (6, 19), (35, 80), (36, 19), (36, 114), (37, 19), (44, 19),
 (44, 67), (44, 115), (46, 83), (68, 51), (68, 55), (70, 49), (70, 51),
 (70, 115), (78, 115), (78, 119), (100, 51), (100, 115), (101, 51),
]

# Die Dokumentation zeigt nur 20, wir erwarten 26
# Wir müssen die restlichen 6 finden oder mit den 20 arbeiten

def load_identity_coordinates() -> List[Tuple[int, int]]:
 """Load alle Identity-Extraktions-Koordinaten."""
 
 identity_coords = []
 
 # Diagonal pattern (erste 4 Identities)
 for idx, base_row in enumerate(range(0, 128, 32), start=1):
 for g in range(4):
 row = base_row + (g // 2) * 16
 col = (g % 2) * 16
 for j in range(14):
 r = row + j
 c = col + j
 if r < 128 and c < 128:
 identity_coords.append((r, c))
 
 return identity_coords

def calculate_distance(coord1: Tuple[int, int], coord2: Tuple[int, int]) -> float:
 """Berechne euklidische Distanz."""
 return math.sqrt((coord1[0] - coord2[0])**2 + (coord1[1] - coord2[1])**2)

def find_nearby_identities(zero_coord: Tuple[int, int], identity_coords: List[Tuple[int, int]], max_distance: int = 20) -> List[Tuple[Tuple[int, int], float]]:
 """Finde Identity-Koordinaten in der Nähe."""
 nearby = []
 for id_coord in identity_coords:
 dist = calculate_distance(zero_coord, id_coord)
 if dist <= max_distance:
 nearby.append((id_coord, dist))
 return sorted(nearby, key=lambda x: x[1])

def analyze_geometric_patterns(zero_coords: List[Tuple[int, int]]) -> Dict:
 """Analyze geometrische Muster in Zero-Koordinaten."""
 
 rows = [z[0] for z in zero_coords]
 cols = [z[1] for z in zero_coords]
 
 patterns = {
 "row_range": (min(rows), max(rows)),
 "col_range": (min(cols), max(cols)),
 "row_distribution": defaultdict(int),
 "col_distribution": defaultdict(int),
 "diagonal_check": False,
 "anti_diagonal_check": False,
 "clusters": [],
 }
 
 # Distribution
 for r in rows:
 patterns["row_distribution"][r] += 1
 for c in cols:
 patterns["col_distribution"][c] += 1
 
 # Diagonal checks
 for r, c in zero_coords:
 if r == c:
 patterns["diagonal_check"] = True
 if r + c == 127:
 patterns["anti_diagonal_check"] = True
 
 # Cluster analysis (find groups of zeros close together)
 clusters = []
 used = set()
 
 for zero in zero_coords:
 if zero in used:
 continue
 
 cluster = [zero]
 used.add(zero)
 
 for other_zero in zero_coords:
 if other_zero in used:
 continue
 
 dist = calculate_distance(zero, other_zero)
 if dist <= 5: # Within 5 units
 cluster.append(other_zero)
 used.add(other_zero)
 
 if len(cluster) > 1:
 clusters.append(cluster)
 
 patterns["clusters"] = clusters
 
 return patterns

def main():
 """Hauptfunktion."""
 
 print("=" * 80)
 print("ANALYZE 26 ZERO VALUES (DARK MATTER) - DIRECT ANALYSIS")
 print("=" * 80)
 print()
 
 # Verwende bekannte Zeros (20 von 26)
 zero_coords = KNOWN_ZEROS
 print(f"✅ Using {len(zero_coords)} known zero coordinates")
 print()
 
 print("Loading identity coordinates...")
 identity_coords = load_identity_coordinates()
 print(f"✅ Loaded {len(identity_coords)} identity coordinates")
 print()
 
 print("Analyzing zero-identity correlation...")
 correlation_results = []
 all_distances = []
 
 for zero_coord in zero_coords:
 nearby = find_nearby_identities(zero_coord, identity_coords, max_distance=20)
 
 correlation_results.append({
 "zero_coord": zero_coord,
 "nearby_count": len(nearby),
 "nearest": nearby[0] if nearby else None,
 "all_nearby": nearby[:5],
 })
 
 if nearby:
 all_distances.append(nearby[0][1])
 
 zeros_with_nearby = len([r for r in correlation_results if r["nearby_count"] > 0])
 print(f"✅ {zeros_with_nearby} / {len(zero_coords)} zeros have nearby identities")
 
 if all_distances:
 print(f" Min distance: {min(all_distances):.2f}")
 print(f" Mean distance: {sum(all_distances)/len(all_distances):.2f}")
 print(f" Max distance: {max(all_distances):.2f}")
 print()
 
 print("Analyzing geometric patterns...")
 geometric = analyze_geometric_patterns(zero_coords)
 print(f"✅ Row range: {geometric['row_range']}")
 print(f"✅ Col range: {geometric['col_range']}")
 print(f"✅ Clusters found: {len(geometric['clusters'])}")
 print()
 
 # Zeige Details
 print("=" * 80)
 print("ZERO COORDINATES WITH NEARBY IDENTITIES")
 print("=" * 80)
 print()
 
 for i, result in enumerate(correlation_results, 1):
 zero = result["zero_coord"]
 nearby_count = result["nearby_count"]
 nearest = result["nearest"]
 
 print(f"{i:2d}. Zero at ({zero[0]:3d}, {zero[1]:3d})")
 if nearest:
 nearest_coord, dist = nearest
 print(f" Nearest identity: ({nearest_coord[0]:3d}, {nearest_coord[1]:3d}) - Distance: {dist:.2f}")
 print(f" Total nearby identities: {nearby_count}")
 print()
 
 # Speichere Ergebnisse
 OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
 json_file = OUTPUT_DIR / "26_zeros_dark_matter_analysis.json"
 with json_file.open("w") as f:
 json.dump({
 "zero_coordinates": zero_coords,
 "correlation_results": correlation_results,
 "geometric_patterns": geometric,
 "statistics": {
 "zeros_with_nearby": zeros_with_nearby,
 "total_zeros": len(zero_coords),
 "min_distance": min(all_distances) if all_distances else None,
 "mean_distance": sum(all_distances)/len(all_distances) if all_distances else None,
 "max_distance": max(all_distances) if all_distances else None,
 },
 }, f, indent=2)
 
 print(f"💾 Results saved to: {json_file}")
 
 # Erstelle Report
 REPORTS_DIR.mkdir(parents=True, exist_ok=True)
 report_file = REPORTS_DIR / "26_zeros_dark_matter_analysis_report.md"
 
 with report_file.open("w") as f:
 f.write("# 26 Zero Values (Dark Matter) Analysis Report\n\n")
 f.write(f"**Generated**: {datetime.now().isoformat()}\n\n")
 f.write("## Overview\n\n")
 f.write("Analysis of the 26 zero values (20 known coordinates) and their relationship to identity extraction.\n\n")
 
 f.write("## Zero Coordinates\n\n")
 f.write("Known zero coordinates (20 of 26):\n\n")
 for i, (r, c) in enumerate(zero_coords, 1):
 result = correlation_results[i-1]
 nearby_count = result["nearby_count"]
 nearest = result["nearest"]
 f.write(f"{i:2d}. `({r:3d}, {c:3d})`")
 if nearest:
 nearest_coord, dist = nearest
 f.write(f" - Nearest identity: `({nearest_coord[0]:3d}, {nearest_coord[1]:3d})` (distance: {dist:.2f})")
 f.write(f" - Nearby identities: {nearby_count}\n")
 f.write("\n")
 
 f.write("## Correlation Statistics\n\n")
 f.write(f"- **Zeros with nearby identities**: {zeros_with_nearby} / {len(zero_coords)}\n")
 if all_distances:
 f.write(f"- **Min distance**: {min(all_distances):.2f}\n")
 f.write(f"- **Mean distance**: {sum(all_distances)/len(all_distances):.2f}\n")
 f.write(f"- **Max distance**: {max(all_distances):.2f}\n")
 f.write("\n")
 
 f.write("## Geometric Patterns\n\n")
 f.write(f"- **Row range**: {geometric['row_range']}\n")
 f.write(f"- **Col range**: {geometric['col_range']}\n")
 f.write(f"- **On main diagonal**: {geometric['diagonal_check']}\n")
 f.write(f"- **On anti-diagonal**: {geometric['anti_diagonal_check']}\n")
 f.write(f"- **Clusters found**: {len(geometric['clusters'])}\n")
 
 if geometric['clusters']:
 f.write("\n**Clusters**:\n\n")
 for i, cluster in enumerate(geometric['clusters'], 1):
 f.write(f"Cluster {i}: {cluster}\n")
 f.write("\n")
 
 f.write("## Interpretation\n\n")
 f.write("If zeros are control neurons:\n")
 f.write("- Proximity to identity coordinates suggests functional relationship\n")
 f.write("- They might control identity extraction points\n")
 f.write("- They could coordinate Helix Gate operations\n")
 f.write("- They may serve as 'nervous system' of the matrix\n")
 f.write("- Clusters might indicate control regions\n\n")
 
 print(f"📄 Report saved to: {report_file}")
 print()
 print("=" * 80)
 print("✅ 26 ZEROS ANALYSIS COMPLETE")
 print("=" * 80)

if __name__ == "__main__":
 main()

