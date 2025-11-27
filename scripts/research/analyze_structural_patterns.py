#!/usr/bin/env python3
"""
Strukturelle Patterns Analyse
- Check mathematische Notwendigkeit von "alle Block-Ende in Spalte 6"
- Analyze strukturelle Patterns die wirklich bestätigt sind
- Keine LLM-Halluzinationen - nur echte Daten!
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
OUTPUT_DIR = project_root / "outputs" / "derived"
REPORTS_DIR = project_root / "outputs" / "reports"

def check_mathematical_necessity() -> Dict:
 """Check ob 'alle Block-Ende in Spalte 6' mathematisch notwendig ist."""
 
 block_end_positions = [13, 27, 41, 55]
 grid_size = 7
 
 results = {}
 
 for pos in block_end_positions:
 # Berechne Grid-Koordinate
 grid_index = pos % (grid_size * grid_size) # pos % 49
 row = grid_index // grid_size
 col = grid_index % grid_size
 
 # Check verschiedene Grid-Größen
 for test_grid_size in [5, 6, 7, 8, 9, 10]:
 test_grid_index = pos % (test_grid_size * test_grid_size)
 test_row = test_grid_index // test_grid_size
 test_col = test_grid_index % test_grid_size
 
 if test_grid_size not in results:
 results[test_grid_size] = {}
 
 if f"position_{pos}" not in results[test_grid_size]:
 results[test_grid_size][f"position_{pos}"] = {
 "position": pos,
 "grid_coord": (test_row, test_col),
 "col": test_col
 }
 
 # Check ob alle in derselben Spalte for verschiedene Grid-Größen
 grid_analysis = {}
 for grid_size, positions in results.items():
 cols = [p["col"] for p in positions.values()]
 all_same_col = len(set(cols)) == 1
 grid_analysis[grid_size] = {
 "all_same_col": all_same_col,
 "cols": cols,
 "unique_cols": len(set(cols))
 }
 
 return {
 "block_end_positions": block_end_positions,
 "grid_7x7": results.get(7, {}),
 "grid_analysis": grid_analysis,
 "conclusion": {
 "is_mathematically_necessary_7x7": grid_analysis.get(7, {}).get("all_same_col", False),
 "is_unique_to_7x7": all(
 not grid_analysis.get(size, {}).get("all_same_col", False)
 for size in [5, 6, 8, 9, 10]
 )
 }
 }

def analyze_block_structure() -> Dict:
 """Analyze Block-Struktur der Identities."""
 
 # Identity hat 60 Characters = 4 Blocks à 14 Characters (56) + Checksum (4)
 # Block-Ende-Positionen: 13, 27, 41, 55
 
 block_structure = {
 "total_chars": 60,
 "body_chars": 56,
 "checksum_chars": 4,
 "blocks": 4,
 "chars_per_block": 14,
 "block_end_positions": [13, 27, 41, 55]
 }
 
 # Analyze Positionen
 position_analysis = {}
 for i, pos in enumerate(block_structure["block_end_positions"]):
 block = i
 pos_in_block = pos % 14
 
 position_analysis[f"block_{block}"] = {
 "block": block,
 "end_position": pos,
 "pos_in_block": pos_in_block,
 "is_block_end": pos_in_block == 13
 }
 
 return {
 "structure": block_structure,
 "position_analysis": position_analysis
 }

def analyze_grid_mapping_patterns() -> Dict:
 """Analyze Grid-Mapping-Patterns."""
 
 # Teste verschiedene Positionen
 test_positions = list(range(0, 60, 1)) # Alle Positionen 0-59
 grid_size = 7
 
 # Analyze welche Spalten verwendet werden
 col_distribution = Counter()
 row_distribution = Counter()
 
 for pos in test_positions:
 grid_index = pos % (grid_size * grid_size)
 row = grid_index // grid_size
 col = grid_index % grid_size
 
 col_distribution[col] += 1
 row_distribution[row] += 1
 
 # Analyze Block-Ende-Positionen speziell
 block_end_positions = [13, 27, 41, 55]
 block_end_cols = []
 block_end_rows = []
 
 for pos in block_end_positions:
 grid_index = pos % (grid_size * grid_size)
 row = grid_index // grid_size
 col = grid_index % grid_size
 block_end_cols.append(col)
 block_end_rows.append(row)
 
 return {
 "grid_size": grid_size,
 "total_positions": len(test_positions),
 "col_distribution": dict(col_distribution),
 "row_distribution": dict(row_distribution),
 "block_end_cols": block_end_cols,
 "block_end_rows": block_end_rows,
 "all_block_end_same_col": len(set(block_end_cols)) == 1,
 "block_end_col": block_end_cols[0] if block_end_cols else None
 }

def analyze_character_restrictions() -> Dict:
 """Analyze Character-Restriktionen (Position 27 hat nur A,B,C,D)."""
 
 if not LAYER3_FILE.exists():
 return {"error": "Layer-3 Daten nicht gefunden"}
 
 with LAYER3_FILE.open() as f:
 layer3_data = json.load(f)
 layer3_results = layer3_data.get("results", [])
 
 # Analyze alle Positionen
 position_analysis = {}
 
 for pos in range(60):
 chars = Counter()
 for entry in layer3_results:
 l3_id = entry.get("layer3_identity", "")
 if l3_id and len(l3_id) > pos:
 chars[l3_id[pos].upper()] += 1
 
 unique_chars = len(chars)
 position_analysis[f"position_{pos}"] = {
 "position": pos,
 "unique_chars": unique_chars,
 "total": sum(chars.values()),
 "char_distribution": dict(chars.most_common(10))
 }
 
 # Finde Positionen mit Restriktionen (< 26 Characters)
 restricted_positions = []
 for pos_key, analysis in position_analysis.items():
 if analysis["unique_chars"] < 26:
 restricted_positions.append({
 "position": analysis["position"],
 "unique_chars": analysis["unique_chars"],
 "chars": list(analysis["char_distribution"].keys())[:analysis["unique_chars"]]
 })
 
 return {
 "position_analysis": position_analysis,
 "restricted_positions": restricted_positions,
 "total_restricted": len(restricted_positions)
 }

def main():
 """Hauptfunktion."""
 
 print("=" * 80)
 print("STRUKTURELLE PATTERNS ANALYSE")
 print("=" * 80)
 print()
 print("⚠️ KEINE HALLUZINATIONEN - NUR ECHTE DATEN!")
 print("🔬 KRITISCH, SYSTEMATISCH, PERFEKT")
 print()
 
 # 1. Check mathematische Notwendigkeit
 print("🔍 Check mathematische Notwendigkeit von 'alle Block-Ende in Spalte 6'...")
 math_check = check_mathematical_necessity()
 print(f"✅ Mathematische Prüfung abgeschlossen")
 print()
 
 print("📊 Grid-Größen-Vergleich:")
 for grid_size, analysis in sorted(math_check["grid_analysis"].items()):
 same_col = "✅" if analysis["all_same_col"] else "❌"
 unique_cols = analysis["unique_cols"]
 print(f" {same_col} Grid {grid_size}x{grid_size}: {unique_cols} verschiedene Spalten")
 print()
 
 is_necessary = math_check["conclusion"]["is_mathematically_necessary_7x7"]
 is_unique = math_check["conclusion"]["is_unique_to_7x7"]
 print(f" Ist mathematisch notwendig (7x7): {'✅ JA' if is_necessary else '❌ NEIN'}")
 print(f" Ist einzigartig for 7x7: {'✅ JA' if is_unique else '❌ NEIN'}")
 print()
 
 # 2. Analyze Block-Struktur
 print("🔍 Analyze Block-Struktur...")
 block_analysis = analyze_block_structure()
 print(f"✅ Block-Struktur analysiert")
 print(f" Blocks: {block_analysis['structure']['blocks']}")
 print(f" Chars pro Block: {block_analysis['structure']['chars_per_block']}")
 print(f" Block-Ende-Positionen: {block_analysis['structure']['block_end_positions']}")
 print()
 
 # 3. Analyze Grid-Mapping-Patterns
 print("🔍 Analyze Grid-Mapping-Patterns...")
 grid_patterns = analyze_grid_mapping_patterns()
 print(f"✅ Grid-Mapping analysiert")
 print(f" Alle Block-Ende in derselben Spalte: {'✅ JA' if grid_patterns['all_block_end_same_col'] else '❌ NEIN'}")
 print(f" Block-Ende Spalte: {grid_patterns['block_end_col']}")
 print(f" Spalten-Verteilung: {grid_patterns['col_distribution']}")
 print()
 
 # 4. Analyze Character-Restriktionen
 print("🔍 Analyze Character-Restriktionen...")
 char_restrictions = analyze_character_restrictions()
 if "error" not in char_restrictions:
 print(f"✅ Character-Restriktionen analysiert")
 print(f" Positionen mit Restriktionen: {char_restrictions['total_restricted']}")
 print()
 
 print("📊 Positionen mit < 26 Characters:")
 for restricted in char_restrictions["restricted_positions"][:10]:
 pos = restricted["position"]
 unique = restricted["unique_chars"]
 chars = restricted["chars"]
 print(f" Position {pos}: {unique} Characters ({', '.join(chars[:5])}...)")
 else:
 print(f"⚠️ {char_restrictions['error']}")
 print()
 
 # Speichere Ergebnisse
 OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
 
 output_data = {
 "timestamp": datetime.now().isoformat(),
 "mathematical_necessity": math_check,
 "block_structure": block_analysis,
 "grid_mapping_patterns": grid_patterns,
 "character_restrictions": char_restrictions
 }
 
 output_file = OUTPUT_DIR / "structural_patterns_analysis.json"
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
 print(f" Mathematisch notwendig (7x7): {'✅ JA' if is_necessary else '❌ NEIN'}")
 print(f" Einzigartig for 7x7: {'✅ JA' if is_unique else '❌ NEIN'}")
 print(f" Alle Block-Ende in Spalte 6: {'✅ JA' if grid_patterns['all_block_end_same_col'] else '❌ NEIN'}")
 if "error" not in char_restrictions:
 print(f" Positionen mit Restriktionen: {char_restrictions['total_restricted']}")
 print()

if __name__ == "__main__":
 main()
