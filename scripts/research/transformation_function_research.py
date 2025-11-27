#!/usr/bin/env python3
"""
Transformation Function Research

Forscht nach der wahren Transformation-Funktion f(Matrix) = Seed.
Testet verschiedene Hypothesen und findet Patterns.
"""

import json
import sys
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from collections import Counter, defaultdict
import numpy as np

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from analysis.utils.data_loader import load_anna_matrix

OUTPUT_DIR = project_root / "outputs" / "derived"
REPORTS_DIR = project_root / "outputs" / "reports"

def load_mapping_data() -> Dict:
 """Load Mapping-Daten."""
 db_file = project_root / "outputs" / "analysis" / "complete_mapping_database.json"
 
 if not db_file.exists():
 return {}
 
 with db_file.open() as f:
 return json.load(f)

def analyze_documented_vs_real_patterns(db: Dict) -> Dict:
 """Analyze Patterns zwischen dokumentierten und realen Identities."""
 seed_to_doc_id = db.get("seed_to_doc_id", {})
 seed_to_real_id = db.get("seed_to_real_id", {})
 
 if not seed_to_doc_id or not seed_to_real_id:
 return {}
 
 # Sample for Performance
 sample_size = min(1000, len(seed_to_doc_id))
 sample_seeds = list(seed_to_doc_id.keys())[:sample_size]
 
 patterns = {
 "position_analysis": defaultdict(list),
 "char_mapping": defaultdict(Counter),
 "difference_patterns": Counter(),
 "transformation_hypotheses": []
 }
 
 for seed in sample_seeds:
 doc_id = seed_to_doc_id.get(seed)
 real_id = seed_to_real_id.get(seed)
 
 if not doc_id or not real_id:
 continue
 
 # Position-by-Position Analyse
 for pos in range(min(len(doc_id), len(real_id))):
 doc_char = doc_id[pos]
 real_char = real_id[pos]
 
 if doc_char != real_char:
 patterns["position_analysis"][pos].append((doc_char, real_char))
 patterns["char_mapping"][pos][(doc_char, real_char)] += 1
 
 # Char-Differenz
 diff = (ord(real_char) - ord(doc_char)) % 26
 patterns["difference_patterns"][diff] += 1
 
 return patterns

def test_transformation_hypotheses(db: Dict, matrix: np.ndarray) -> List[Dict]:
 """Teste verschiedene Transformation-Hypothesen."""
 hypotheses = []
 
 seed_to_doc_id = db.get("seed_to_doc_id", {})
 seed_to_real_id = db.get("seed_to_real_id", {})
 
 if not seed_to_doc_id or not seed_to_real_id:
 return []
 
 # Sample
 sample_seeds = list(seed_to_doc_id.keys())[:100]
 
 # Hypothese 1: Seed ist dokumentierte Identity (lower[:55])
 hypothesis1 = {
 "name": "identity.lower()[:55]",
 "description": "Current approximation - documented identity to seed",
 "matches": 0,
 "tested": len(sample_seeds)
 }
 
 for seed in sample_seeds:
 doc_id = seed_to_doc_id.get(seed)
 if doc_id:
 test_seed = doc_id.lower()[:55]
 if test_seed == seed:
 hypothesis1["matches"] += 1
 
 hypothesis1["success_rate"] = (hypothesis1["matches"] / hypothesis1["tested"]) * 100
 hypotheses.append(hypothesis1)
 
 # Hypothese 2: Seed ist dokumentierte Identity (lower, aber andere Länge)
 hypothesis2 = {
 "name": "identity.lower()[:54] or [:56]",
 "description": "Different length extraction",
 "matches": 0,
 "tested": len(sample_seeds)
 }
 
 for seed in sample_seeds:
 doc_id = seed_to_doc_id.get(seed)
 if doc_id:
 test_seed_54 = doc_id.lower()[:54]
 test_seed_56 = doc_id.lower()[:56]
 if test_seed_54 == seed or test_seed_56 == seed:
 hypothesis2["matches"] += 1
 
 hypothesis2["success_rate"] = (hypothesis2["matches"] / hypothesis2["tested"]) * 100
 hypotheses.append(hypothesis2)
 
 # Hypothese 3: Seed kommt aus Matrix-Koordinaten (nicht Identity)
 # Das würde bedeuten, dass die dokumentierte Identity nicht direkt aus Seed kommt
 hypothesis3 = {
 "name": "Matrix coordinates → Seed (not Identity)",
 "description": "Seed extracted directly from matrix, not from identity",
 "matches": 0,
 "tested": 0,
 "note": "Requires coordinate mapping - complex to test"
 }
 hypotheses.append(hypothesis3)
 
 return hypotheses

def analyze_seed_characteristics(db: Dict) -> Dict:
 """Analyze Seed-Charakteristika."""
 seed_to_real_id = db.get("seed_to_real_id", {})
 
 if not seed_to_real_id:
 return {}
 
 sample_seeds = list(seed_to_real_id.keys())[:1000]
 
 characteristics = {
 "length_distribution": Counter(),
 "char_distribution": Counter(),
 "repeating_patterns": Counter(),
 "unique_chars": set(),
 "common_prefixes": Counter(),
 "common_suffixes": Counter()
 }
 
 for seed in sample_seeds:
 if not seed:
 continue
 
 characteristics["length_distribution"][len(seed)] += 1
 characteristics["char_distribution"].update(seed)
 characteristics["unique_chars"].update(seed)
 
 # Prefixes und Suffixes
 if len(seed) >= 3:
 characteristics["common_prefixes"][seed[:3]] += 1
 characteristics["common_suffixes"][seed[-3:]] += 1
 
 # Repeating patterns
 for i in range(len(seed) - 1):
 if seed[i] == seed[i+1]:
 characteristics["repeating_patterns"][seed[i:i+2]] += 1
 
 return {
 "length_distribution": dict(characteristics["length_distribution"]),
 "char_distribution": dict(characteristics["char_distribution"].most_common(26)),
 "repeating_patterns": dict(characteristics["repeating_patterns"].most_common(20)),
 "unique_chars_count": len(characteristics["unique_chars"]),
 "common_prefixes": dict(characteristics["common_prefixes"].most_common(10)),
 "common_suffixes": dict(characteristics["common_suffixes"].most_common(10))
 }

def find_coordinate_patterns(matrix: np.ndarray, db: Dict) -> Dict:
 """Finde Patterns in Matrix-Koordinaten die zu Seeds führen könnten."""
 # Das ist komplex - wir müssten wissen welche Koordinaten zu welchen Seeds gehören
 # Für jetzt analyzen wir bekannte Extraction-Koordinaten
 
 # Bekannte Diagonal-Koordinaten (erste 4 Identities)
 diagonal_coords = []
 for base_row in [0, 32, 64, 96]:
 for block in range(4):
 row_offset = base_row + (block // 2) * 16
 col_offset = (block % 2) * 16
 for j in range(14):
 row = row_offset + j
 col = col_offset + j
 if row < 128 and col < 128:
 diagonal_coords.append((row, col))
 
 # Analyze Werte an diesen Koordinaten
 coord_values = []
 for row, col in diagonal_coords[:56]: # Erste 56 for eine Identity
 value = matrix[row, col]
 coord_values.append({
 "coordinate": (row, col),
 "value": float(value),
 "base26": int(value) % 26 if not np.isnan(value) else None,
 "base26_char": chr(ord('A') + (int(value) % 26)) if not np.isnan(value) else None
 })
 
 return {
 "coordinate_count": len(diagonal_coords),
 "sample_values": coord_values[:20], # Erste 20
 "value_range": {
 "min": min(v["value"] for v in coord_values if v["value"] is not None),
 "max": max(v["value"] for v in coord_values if v["value"] is not None),
 "mean": np.mean([v["value"] for v in coord_values if v["value"] is not None])
 }
 }

def main():
 """Hauptfunktion."""
 print("=" * 80)
 print("TRANSFORMATION FUNCTION RESEARCH")
 print("=" * 80)
 print()
 
 # Load Daten
 print("Loading mapping data...")
 db = load_mapping_data()
 if not db:
 print("❌ Mapping data not found")
 return
 
 print(f"✅ Loaded {len(db.get('seed_to_real_id', {}))} entries")
 print()
 
 # Load Matrix
 print("Loading Anna Matrix...")
 payload = load_anna_matrix()
 matrix = payload.matrix
 print(f"✅ Matrix loaded: {matrix.shape}")
 print()
 
 # Analyze Patterns
 print("Analyzing documented vs real patterns...")
 patterns = analyze_documented_vs_real_patterns(db)
 
 print("=" * 80)
 print("PATTERN ANALYSIS RESULTS")
 print("=" * 80)
 print()
 
 if patterns.get("difference_patterns"):
 print("Top Character Differences:")
 for diff, count in patterns["difference_patterns"].most_common(10):
 print(f" +{diff}: {count} occurrences")
 print()
 
 # Teste Hypothesen
 print("Testing transformation hypotheses...")
 hypotheses = test_transformation_hypotheses(db, matrix)
 
 print("Hypothesis Test Results:")
 for hyp in hypotheses:
 print(f" {hyp['name']}:")
 print(f" Matches: {hyp.get('matches', 0)}/{hyp.get('tested', 0)}")
 if 'success_rate' in hyp:
 print(f" Success Rate: {hyp['success_rate']:.1f}%")
 if 'note' in hyp:
 print(f" Note: {hyp['note']}")
 print()
 
 # Seed Characteristics
 print("Analyzing seed characteristics...")
 seed_chars = analyze_seed_characteristics(db)
 
 if seed_chars:
 print("Seed Characteristics:")
 print(f" Length distribution: {seed_chars.get('length_distribution', {})}")
 print(f" Unique chars: {seed_chars.get('unique_chars_count', 0)}")
 print(f" Top repeating patterns:")
 for pattern, count in list(seed_chars.get('repeating_patterns', {}).items())[:5]:
 print(f" '{pattern}': {count}")
 print()
 
 # Coordinate Patterns
 print("Analyzing coordinate patterns...")
 coord_patterns = find_coordinate_patterns(matrix, db)
 
 print(f"Coordinate analysis:")
 print(f" Coordinates analyzed: {coord_patterns.get('coordinate_count', 0)}")
 if 'value_range' in coord_patterns:
 vr = coord_patterns['value_range']
 print(f" Value range: {vr.get('min', 0):.2f} - {vr.get('max', 0):.2f}")
 print(f" Mean value: {vr.get('mean', 0):.2f}")
 print()
 
 # Speichere Ergebnisse
 OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
 results = {
 "patterns": {
 "difference_patterns": dict(patterns.get("difference_patterns", {}).most_common(26)),
 "position_analysis_summary": {str(k): len(v) for k, v in patterns.get("position_analysis", {}).items()}
 },
 "hypotheses": hypotheses,
 "seed_characteristics": seed_chars,
 "coordinate_patterns": coord_patterns
 }
 
 output_json = OUTPUT_DIR / "transformation_function_research.json"
 with output_json.open("w") as f:
 json.dump(results, f, indent=2)
 
 # Report
 REPORTS_DIR.mkdir(parents=True, exist_ok=True)
 output_md = REPORTS_DIR / "transformation_function_research_report.md"
 
 with output_md.open("w") as f:
 f.write("# Transformation Function Research Report\n\n")
 f.write("**Generated**: 2025-11-25\n\n")
 f.write("## Summary\n\n")
 f.write("Research into the true transformation function f(Matrix) = Seed.\n\n")
 
 f.write("## Hypothesis Testing\n\n")
 f.write("| Hypothesis | Matches | Tested | Success Rate |\n")
 f.write("|------------|---------|--------|--------------|\n")
 for hyp in hypotheses:
 matches = hyp.get('matches', 0)
 tested = hyp.get('tested', 0)
 rate = hyp.get('success_rate', 0)
 f.write(f"| {hyp['name']} | {matches} | {tested} | {rate:.1f}% |\n")
 f.write("\n")
 
 f.write("## Character Difference Patterns\n\n")
 if patterns.get("difference_patterns"):
 f.write("| Difference | Count |\n")
 f.write("|------------|-------|\n")
 for diff, count in patterns["difference_patterns"].most_common(20):
 f.write(f"| +{diff} | {count} |\n")
 f.write("\n")
 
 f.write("## Seed Characteristics\n\n")
 if seed_chars:
 f.write(f"- **Unique chars**: {seed_chars.get('unique_chars_count', 0)}\n")
 f.write(f"- **Length distribution**: {seed_chars.get('length_distribution', {})}\n\n")
 f.write("**Top Repeating Patterns:**\n\n")
 for pattern, count in list(seed_chars.get('repeating_patterns', {}).items())[:10]:
 f.write(f"- `{pattern}`: {count} occurrences\n")
 f.write("\n")
 
 print(f"💾 Results saved to: {output_json}")
 print(f"📄 Report saved to: {output_md}")
 print()
 
 return results

if __name__ == "__main__":
 main()

