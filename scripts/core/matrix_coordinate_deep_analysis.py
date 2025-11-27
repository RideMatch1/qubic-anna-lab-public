#!/usr/bin/env python3
"""
Tiefe Matrix-Koordinaten-Analyse: Versteckte Strukturen und Intentionen.

Analysiert:
1. Woher kommen die Comprehensive Scan Identities in der Matrix?
2. Gibt es geografische/strukturelle Patterns?
3. Vergleich mit systematischen Identities
4. Versteckte Koordinaten-Mappings
5. Block-Strukturen und Hierarchien
"""

import json
from pathlib import Path
from typing import List, Dict, Set, Tuple
from collections import Counter, defaultdict
import numpy as np

OUTPUT_DIR = Path(__file__).parent.parent.parent / "outputs" / "derived"
COMPREHENSIVE_SCAN = OUTPUT_DIR / "comprehensive_matrix_scan.json"
SYSTEMATIC_DATA = OUTPUT_DIR / "systematic_matrix_extraction_complete.json"
OUTPUT_FILE = OUTPUT_DIR / "matrix_coordinate_deep_analysis.json"
REPORT_FILE = OUTPUT_DIR / "matrix_coordinate_deep_analysis_report.md"

def analyze_coordinate_patterns(comprehensive_data: Dict) -> Dict:
 """Analyze Koordinaten-Patterns aus Comprehensive Scan."""
 
 pattern_coordinates = defaultdict(list)
 all_coordinates = []
 pattern_stats = {}
 
 results = comprehensive_data.get("results", [])
 
 for pattern_result in results:
 pattern_name = pattern_result.get("pattern_name", "unknown")
 identities = pattern_result.get("identities", [])
 
 for identity_record in identities:
 path = identity_record.get("path", [])
 if path:
 pattern_coordinates[pattern_name].extend(path)
 all_coordinates.extend(path)
 
 # Pattern-Statistiken
 pattern_stats[pattern_name] = {
 "identities_found": pattern_result.get("identities_found", 0),
 "on_chain_count": pattern_result.get("on_chain_count", 0),
 "coordinates_used": len(pattern_coordinates[pattern_name]),
 }
 
 # Analyze Koordinaten-Verteilung
 if all_coordinates:
 # Konvertiere Listen zu Tupeln falls nötig
 coord_tuples = [tuple(coord) if isinstance(coord, list) else coord for coord in all_coordinates]
 rows = [coord[0] for coord in coord_tuples]
 cols = [coord[1] for coord in coord_tuples]
 
 row_distribution = Counter(rows)
 col_distribution = Counter(cols)
 
 # Finde Hotspots (häufig verwendete Koordinaten)
 # Konvertiere Listen zu Tupeln for Counter
 coord_tuples = [tuple(coord) if isinstance(coord, list) else coord for coord in all_coordinates]
 coord_counts = Counter(coord_tuples)
 hotspots = coord_counts.most_common(20)
 
 # Block-Analyse (128x128 Matrix in 16x16 Blöcke)
 block_usage = defaultdict(int)
 for coord in coord_tuples:
 row, col = coord[0], coord[1]
 block_row = row // 16
 block_col = col // 16
 block_usage[(block_row, block_col)] += 1
 
 return {
 "pattern_coordinates": {k: len(v) for k, v in pattern_coordinates.items()},
 "pattern_stats": pattern_stats,
 "total_coordinates": len(all_coordinates),
 "unique_coordinates": len(set(coord_tuples)),
 "row_distribution": dict(row_distribution),
 "col_distribution": dict(col_distribution),
 "hotspots": [(list(coord), count) for coord, count in hotspots],
 "block_usage": {f"{r},{c}": count for (r, c), count in block_usage.items()},
 "most_used_blocks": sorted(block_usage.items(), key=lambda x: x[1], reverse=True)[:10],
 }
 
 return {}

def analyze_geometric_structure(coordinates: List[Tuple[int, int]]) -> Dict:
 """Analyze geometrische Struktur der Koordinaten."""
 
 if not coordinates:
 return {}
 
 rows = [c[0] for c in coordinates]
 cols = [c[1] for c in coordinates]
 
 # Zentrum finden
 center_row = sum(rows) / len(rows)
 center_col = sum(cols) / len(cols)
 
 # Distanzen vom Zentrum
 distances = []
 for row, col in coordinates:
 dist = np.sqrt((row - center_row)**2 + (col - center_col)**2)
 distances.append(dist)
 
 # Cluster-Analyse (einfach)
 clusters = defaultdict(list)
 for i, (row, col) in enumerate(coordinates):
 # Einfaches Clustering: Block-basiert
 block_row = row // 16
 block_col = col // 16
 clusters[(block_row, block_col)].append((row, col))
 
 return {
 "center": (center_row, center_col),
 "spread": {
 "min_distance": min(distances) if distances else 0,
 "max_distance": max(distances) if distances else 0,
 "avg_distance": sum(distances) / len(distances) if distances else 0,
 },
 "clusters": {f"{r},{c}": len(coords) for (r, c), coords in clusters.items()},
 "cluster_count": len(clusters),
 }

def compare_with_systematic(comprehensive_coords: Dict, systematic_data: Dict) -> Dict:
 """Vergleiche Comprehensive Scan mit Systematic Extraction."""
 
 comparison = {
 "coordinate_overlap": 0,
 "unique_comprehensive": 0,
 "unique_systematic": 0,
 "pattern_differences": {},
 }
 
 # Extrahiere Koordinaten aus Systematic (falls vorhanden)
 # Für jetzt: Vergleich der Patterns
 
 return comparison

def analyze_hidden_structure(comprehensive_data: Dict) -> Dict:
 """Analyze versteckte Strukturen in der Matrix."""
 
 results = comprehensive_data.get("results", [])
 
 # Analyze Pattern-Hierarchie
 pattern_hierarchy = {}
 for pattern_result in results:
 pattern_name = pattern_result.get("pattern_name", "unknown")
 on_chain_count = pattern_result.get("on_chain_count", 0)
 identities_found = pattern_result.get("identities_found", 0)
 
 success_rate = (on_chain_count / identities_found * 100) if identities_found > 0 else 0
 
 pattern_hierarchy[pattern_name] = {
 "success_rate": success_rate,
 "on_chain_count": on_chain_count,
 "identities_found": identities_found,
 }
 
 # Sortiere nach Success-Rate
 sorted_patterns = sorted(
 pattern_hierarchy.items(),
 key=lambda x: x[1]["success_rate"],
 reverse=True
 )
 
 # Finde dominante Patterns
 dominant_patterns = [p[0] for p in sorted_patterns[:3]]
 
 return {
 "pattern_hierarchy": pattern_hierarchy,
 "sorted_patterns": sorted_patterns,
 "dominant_patterns": dominant_patterns,
 "most_successful_pattern": sorted_patterns[0][0] if sorted_patterns else None,
 }

def main():
 """Tiefe Matrix-Koordinaten-Analyse."""
 
 print("=" * 80)
 print("TIEFE MATRIX-KOORDINATEN-ANALYSE")
 print("=" * 80)
 print()
 
 if not COMPREHENSIVE_SCAN.exists():
 print(f"❌ Datei nicht gefunden: {COMPREHENSIVE_SCAN}")
 return
 
 print("Load Comprehensive Scan Daten...")
 with COMPREHENSIVE_SCAN.open() as f:
 comprehensive_data = json.load(f)
 
 print(f"✅ {comprehensive_data.get('total_on_chain', 0)} on-chain Identities gefunden")
 print(f"✅ {len(comprehensive_data.get('results', []))} Patterns getestet")
 print()
 
 # 1. Koordinaten-Patterns
 print("1. Analyze Koordinaten-Patterns...")
 coord_patterns = analyze_coordinate_patterns(comprehensive_data)
 if coord_patterns:
 print(f" ✅ {coord_patterns.get('total_coordinates', 0):,} Koordinaten analysiert")
 print(f" ✅ {coord_patterns.get('unique_coordinates', 0):,} unique Koordinaten")
 print(f" ✅ {len(coord_patterns.get('hotspots', []))} Hotspots gefunden")
 
 # 2. Geometrische Struktur
 print("2. Analyze geometrische Struktur...")
 all_coords = []
 for pattern_result in comprehensive_data.get("results", []):
 for identity_record in pattern_result.get("identities", []):
 path = identity_record.get("path", [])
 all_coords.extend([(p[0], p[1]) for p in path if len(p) == 2])
 
 geometric = analyze_geometric_structure(all_coords)
 if geometric:
 print(f" ✅ Zentrum: ({geometric['center'][0]:.1f}, {geometric['center'][1]:.1f})")
 print(f" ✅ {geometric.get('cluster_count', 0)} Cluster gefunden")
 
 # 3. Versteckte Strukturen
 print("3. Analyze versteckte Strukturen...")
 hidden_structure = analyze_hidden_structure(comprehensive_data)
 if hidden_structure.get("most_successful_pattern"):
 print(f" ✅ Erfolgreichstes Pattern: {hidden_structure['most_successful_pattern']}")
 
 print()
 
 # Zusammenfassung
 print("=" * 80)
 print("ZUSAMMENFASSUNG")
 print("=" * 80)
 print()
 
 # Speichere Ergebnisse
 output_data = {
 "coordinate_patterns": coord_patterns,
 "geometric_structure": geometric,
 "hidden_structure": hidden_structure,
 }
 
 OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
 with OUTPUT_FILE.open("w") as f:
 json.dump(output_data, f, indent=2)
 
 print(f"💾 Ergebnisse gespeichert in: {OUTPUT_FILE}")
 
 # Erstelle Report
 report_content = f"""# Tiefe Matrix-Koordinaten-Analyse

**Datum**: 2025-11-22 
**Total on-chain Identities**: {comprehensive_data.get('total_on_chain', 0)}

## 1. Koordinaten-Patterns

### Übersicht
- **Total Koordinaten**: {coord_patterns.get('total_coordinates', 0):,}
- **Unique Koordinaten**: {coord_patterns.get('unique_coordinates', 0):,}
- **Hotspots**: {len(coord_patterns.get('hotspots', []))}

### Pattern-Statistiken
"""
 
 for pattern_name, stats in coord_patterns.get("pattern_stats", {}).items():
 report_content += f"\n#### {pattern_name}\n"
 report_content += f"- Identities gefunden: {stats.get('identities_found', 0)}\n"
 report_content += f"- On-chain: {stats.get('on_chain_count', 0)}\n"
 report_content += f"- Success Rate: {stats.get('on_chain_count', 0)/stats.get('identities_found', 1)*100:.1f}%\n"
 
 report_content += "\n### Hotspots (häufigste Koordinaten)\n"
 for coord, count in coord_patterns.get("hotspots", [])[:10]:
 report_content += f"- `{coord}`: {count}x\n"
 
 report_content += "\n### Block-Nutzung (16x16 Blöcke)\n"
 for (r, c), count in coord_patterns.get("most_used_blocks", [])[:10]:
 report_content += f"- Block ({r}, {c}): {count}x\n"
 
 if geometric:
 report_content += f"""
## 2. Geometrische Struktur

- **Zentrum**: ({geometric['center'][0]:.1f}, {geometric['center'][1]:.1f})
- **Spread**: {geometric['spread']['min_distance']:.1f} - {geometric['spread']['max_distance']:.1f} (Ø {geometric['spread']['avg_distance']:.1f})
- **Cluster**: {geometric.get('cluster_count', 0)}
"""
 
 if hidden_structure:
 report_content += f"""
## 3. Versteckte Strukturen

### Pattern-Hierarchie (nach Success-Rate)
"""
 for pattern_name, data in hidden_structure.get("sorted_patterns", [])[:5]:
 report_content += f"- **{pattern_name}**: {data['success_rate']:.1f}% ({data['on_chain_count']}/{data['identities_found']})\n"
 
 report_content += f"\n### Dominante Patterns\n"
 for pattern in hidden_structure.get("dominant_patterns", []):
 report_content += f"- {pattern}\n"
 
 report_content += """
## Interpretationen

### 1. Koordinaten-Hotspots

**Frage**: Warum werden manche Koordinaten häufiger verwendet?
- Könnte mit Matrix-Struktur zusammenhängen
- Könnte kryptographische Bedeutung haben
- Könnte Teil eines größeren Patterns sein

### 2. Block-Nutzung

**Erkenntnis**: Die Matrix scheint in 16x16 Blöcke unterteilt zu sein.
- Jeder Block könnte eine spezifische Funktion haben
- Die Block-Nutzung könnte ein Pattern zeigen
- Könnte mit der ursprünglichen Matrix-Konstruktion zusammenhängen

### 3. Pattern-Hierarchie

**Erkenntnis**: Manche Patterns sind erfolgreicher als andere.
- Das erfolgreichste Pattern könnte die "Hauptmethode" sein
- Andere Patterns könnten Variationen oder Tests sein
- Die Hierarchie könnte die Intention zeigen

## Nächste Schritte

1. Detaillierte Block-Analyse
2. Vergleich mit systematischen Identities
3. Koordinaten-Mapping zu Seeds
4. Tiefere geometrische Analyse
"""
 
 with REPORT_FILE.open("w") as f:
 f.write(report_content)
 
 print(f"📄 Report erstellt: {REPORT_FILE}")
 print()
 print("✅ Tiefe Matrix-Koordinaten-Analyse abgeschlossen!")

if __name__ == "__main__":
 main()

