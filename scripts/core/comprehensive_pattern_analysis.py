#!/usr/bin/env python3
"""
Comprehensive Pattern Analysis

Analysiert alle Patterns systematisch:
- Identity Discrepancy Patterns
- Seed Patterns
- Layer-3 On-chain Patterns
- Coordinate Relationships
- 26 Zeros Analysis
"""

import json
import sys
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from collections import defaultdict, Counter
import re

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

OUTPUT_DIR = project_root / "outputs" / "derived"
REPORTS_DIR = project_root / "outputs" / "reports"

def load_complete_mapping_database() -> Dict:
 """Load die komplette Mapping-Datenbank."""
 db_file = project_root / "outputs" / "analysis" / "complete_mapping_database.json"
 
 if not db_file.exists():
 print(f"⚠️ Database file not found: {db_file}")
 return {}
 
 print(f"📂 Loading complete mapping database...")
 with db_file.open() as f:
 data = json.load(f)
 
 print(f"✅ Loaded {len(data.get('seed_to_real_id', {}))} entries")
 return data

def analyze_identity_discrepancy_patterns(db: Dict) -> Dict:
 """Analyze Identity Discrepancy Patterns."""
 print("\n" + "=" * 80)
 print("IDENTITY DISCREPANCY PATTERN ANALYSIS")
 print("=" * 80)
 
 seed_to_doc_id = db.get("seed_to_doc_id", {})
 seed_to_real_id = db.get("seed_to_real_id", {})
 
 if not seed_to_doc_id or not seed_to_real_id:
 return {}
 
 # Analyze Character-Differenzen pro Position
 position_differences = defaultdict(int)
 char_diff_patterns = defaultdict(int)
 total_analyzed = 0
 
 for seed in list(seed_to_doc_id.keys())[:1000]: # Sample for Performance
 doc_id = seed_to_doc_id.get(seed)
 real_id = seed_to_real_id.get(seed)
 
 if not doc_id or not real_id:
 continue
 
 total_analyzed += 1
 
 # Position-by-Position Analyse
 for pos in range(min(len(doc_id), len(real_id))):
 if doc_id[pos] != real_id[pos]:
 position_differences[pos] += 1
 
 # Char-Differenz Pattern
 doc_char = doc_id[pos]
 real_char = real_id[pos]
 diff = (ord(real_char) - ord(doc_char)) % 26
 char_diff_patterns[diff] += 1
 
 # Analyze Seed Patterns
 seed_patterns = analyze_seed_patterns(list(seed_to_real_id.keys())[:1000])
 
 results = {
 "total_analyzed": total_analyzed,
 "position_differences": dict(position_differences),
 "char_diff_patterns": dict(char_diff_patterns),
 "seed_patterns": seed_patterns
 }
 
 print(f"\n✅ Analyzed {total_analyzed} identity pairs")
 print(f" Position differences: {len(position_differences)} positions differ")
 print(f" Most common char diff: {max(char_diff_patterns.items(), key=lambda x: x[1]) if char_diff_patterns else 'N/A'}")
 
 return results

def analyze_seed_patterns(seeds: List[str]) -> Dict:
 """Analyze Seed Patterns."""
 print("\n" + "=" * 80)
 print("SEED PATTERN ANALYSIS")
 print("=" * 80)
 
 # Wiederholende Patterns
 repeating_patterns = Counter()
 char_distribution = Counter()
 substring_patterns = Counter()
 
 for seed in seeds:
 if not seed or len(seed) < 3:
 continue
 
 # Char Distribution
 char_distribution.update(seed)
 
 # 2-char Patterns
 for i in range(len(seed) - 1):
 pattern = seed[i:i+2]
 if pattern[0] == pattern[1]: # Repeating
 repeating_patterns[pattern] += 1
 
 # 3-char Patterns
 for i in range(len(seed) - 2):
 pattern = seed[i:i+3]
 substring_patterns[pattern] += 1
 
 results = {
 "repeating_patterns": dict(repeating_patterns.most_common(20)),
 "char_distribution": dict(char_distribution.most_common(10)),
 "top_substrings": dict(substring_patterns.most_common(20))
 }
 
 print(f"\n✅ Analyzed {len(seeds)} seeds")
 print(f" Top repeating pattern: {repeating_patterns.most_common(1)[0] if repeating_patterns else 'N/A'}")
 print(f" Most common char: {char_distribution.most_common(1)[0] if char_distribution else 'N/A'}")
 
 return results

def analyze_layer3_patterns() -> Dict:
 """Analyze Layer-3 On-chain Patterns."""
 print("\n" + "=" * 80)
 print("LAYER-3 ON-CHAIN PATTERN ANALYSIS")
 print("=" * 80)
 
 layer3_file = OUTPUT_DIR / "layer3_derivation_complete.json"
 
 if not layer3_file.exists():
 print("⚠️ Layer-3 data not found")
 return {}
 
 with layer3_file.open() as f:
 data = json.load(f)
 
 results_data = data.get("results", [])
 
 onchain_ids = []
 offchain_ids = []
 
 for result in results_data:
 layer3_id = result.get("layer3_identity")
 is_onchain = result.get("layer3_onchain", False)
 
 if not layer3_id:
 continue
 
 if is_onchain:
 onchain_ids.append(layer3_id)
 else:
 offchain_ids.append(layer3_id)
 
 # Analyze Patterns
 onchain_patterns = analyze_id_patterns(onchain_ids)
 offchain_patterns = analyze_id_patterns(offchain_ids)
 
 results = {
 "total_layer3": len(results_data),
 "onchain_count": len(onchain_ids),
 "offchain_count": len(offchain_ids),
 "onchain_rate": len(onchain_ids) / len(results_data) * 100 if results_data else 0,
 "onchain_patterns": onchain_patterns,
 "offchain_patterns": offchain_patterns
 }
 
 print(f"\n✅ Analyzed {len(results_data)} Layer-3 identities")
 print(f" On-chain: {len(onchain_ids)} ({results['onchain_rate']:.1f}%)")
 print(f" Off-chain: {len(offchain_ids)}")
 
 return results

def analyze_id_patterns(identities: List[str]) -> Dict:
 """Analyze Patterns in Identities."""
 if not identities:
 return {}
 
 char_distribution = Counter()
 position_patterns = defaultdict(Counter)
 
 for identity in identities:
 char_distribution.update(identity)
 
 for pos, char in enumerate(identity):
 position_patterns[pos][char] += 1
 
 # Finde konsistente Patterns
 consistent_positions = {}
 for pos, char_counts in position_patterns.items():
 if len(char_counts) > 0:
 most_common = char_counts.most_common(1)[0]
 if most_common[1] / len(identities) > 0.3: # >30% konsistent
 consistent_positions[pos] = {
 "char": most_common[0],
 "frequency": most_common[1] / len(identities) * 100
 }
 
 return {
 "char_distribution": dict(char_distribution.most_common(10)),
 "consistent_positions": consistent_positions
 }

def analyze_coordinate_relationships() -> Dict:
 """Analyze Coordinate Relationships."""
 print("\n" + "=" * 80)
 print("COORDINATE RELATIONSHIP ANALYSIS")
 print("=" * 80)
 
 # Load bekannte Zero-Koordinaten
 known_zeros = [
 (4, 23), (6, 19), (35, 80), (36, 19), (36, 114), (37, 19), (44, 19),
 (44, 67), (44, 115), (46, 83), (68, 51), (68, 55), (70, 49), (70, 51),
 (70, 115), (78, 115), (78, 119), (100, 51), (100, 115), (101, 51),
 ]
 
 # Identity Extraction Regions
 identity_regions = [
 {"name": "Identity #1", "rows": (0, 13), "cols": (0, 13)},
 {"name": "Identity #2", "rows": (0, 13), "cols": (16, 29)},
 {"name": "Identity #3", "rows": (16, 29), "cols": (0, 13)},
 {"name": "Identity #4", "rows": (16, 29), "cols": (16, 29)},
 {"name": "Identity #5", "rows": (32, 45), "cols": (0, 13)},
 {"name": "Identity #6", "rows": (32, 45), "cols": (16, 29)},
 {"name": "Identity #7", "rows": (48, 61), "cols": (0, 13)},
 {"name": "Identity #8", "rows": (48, 61), "cols": (16, 29)},
 ]
 
 # Finde Zeros in/near Identity Regions
 zero_proximity = []
 for zero_r, zero_c in known_zeros:
 for region in identity_regions:
 r_min, r_max = region["rows"]
 c_min, c_max = region["cols"]
 
 # Check ob Zero in Region oder nah dran
 in_region = (r_min <= zero_r <= r_max) and (c_min <= zero_c <= c_max)
 near_region = (abs(zero_r - r_min) <= 5 or abs(zero_r - r_max) <= 5) and \
 (abs(zero_c - c_min) <= 5 or abs(zero_c - c_max) <= 5)
 
 if in_region or near_region:
 zero_proximity.append({
 "zero": (zero_r, zero_c),
 "region": region["name"],
 "in_region": in_region,
 "near_region": near_region
 })
 
 # Column Patterns
 column_patterns = defaultdict(list)
 for zero_r, zero_c in known_zeros:
 column_patterns[zero_c].append(zero_r)
 
 results = {
 "known_zeros": known_zeros,
 "zero_count": len(known_zeros),
 "expected_zeros": 26,
 "missing_zeros": 26 - len(known_zeros),
 "zero_proximity": zero_proximity,
 "column_patterns": {str(k): v for k, v in column_patterns.items()}
 }
 
 print(f"\n✅ Analyzed {len(known_zeros)} known zeros")
 print(f" Zeros near identity regions: {len(zero_proximity)}")
 print(f" Column clusters: {len([k for k, v in column_patterns.items() if len(v) > 1])}")
 
 return results

def main():
 """Hauptfunktion."""
 print("=" * 80)
 print("COMPREHENSIVE PATTERN ANALYSIS")
 print("=" * 80)
 print()
 
 # Load Daten
 db = load_complete_mapping_database()
 
 # Führe Analysen durch
 all_results = {
 "identity_discrepancy": {},
 "seed_patterns": {},
 "layer3_patterns": {},
 "coordinate_relationships": {}
 }
 
 if db:
 all_results["identity_discrepancy"] = analyze_identity_discrepancy_patterns(db)
 all_results["seed_patterns"] = analyze_seed_patterns(
 list(db.get("seed_to_real_id", {}).keys())[:1000]
 )
 
 all_results["layer3_patterns"] = analyze_layer3_patterns()
 all_results["coordinate_relationships"] = analyze_coordinate_relationships()
 
 # Speichere Ergebnisse
 OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
 output_json = OUTPUT_DIR / "comprehensive_pattern_analysis.json"
 with output_json.open("w") as f:
 json.dump(all_results, f, indent=2)
 
 # Erstelle Report
 REPORTS_DIR.mkdir(parents=True, exist_ok=True)
 output_md = REPORTS_DIR / "comprehensive_pattern_analysis_report.md"
 
 with output_md.open("w") as f:
 f.write("# Comprehensive Pattern Analysis Report\n\n")
 f.write("**Generated**: 2025-11-25\n\n")
 f.write("## Summary\n\n")
 f.write("This report provides comprehensive pattern analysis across multiple dimensions.\n\n")
 
 # Identity Discrepancy
 if all_results["identity_discrepancy"]:
 f.write("## Identity Discrepancy Patterns\n\n")
 disc = all_results["identity_discrepancy"]
 f.write(f"- **Total Analyzed**: {disc.get('total_analyzed', 0)}\n")
 f.write(f"- **Positions with Differences**: {len(disc.get('position_differences', {}))}\n")
 f.write(f"- **Most Common Char Diff**: {max(disc.get('char_diff_patterns', {}).items(), key=lambda x: x[1]) if disc.get('char_diff_patterns') else 'N/A'}\n\n")
 
 # Seed Patterns
 if all_results["seed_patterns"]:
 f.write("## Seed Patterns\n\n")
 seed = all_results["seed_patterns"]
 f.write("### Top Repeating Patterns\n\n")
 for pattern, count in list(seed.get("repeating_patterns", {}).items())[:10]:
 f.write(f"- `{pattern}`: {count} occurrences\n")
 f.write("\n")
 
 # Layer-3 Patterns
 if all_results["layer3_patterns"]:
 f.write("## Layer-3 On-chain Patterns\n\n")
 l3 = all_results["layer3_patterns"]
 f.write(f"- **Total Layer-3**: {l3.get('total_layer3', 0)}\n")
 f.write(f"- **On-chain**: {l3.get('onchain_count', 0)} ({l3.get('onchain_rate', 0):.1f}%)\n")
 f.write(f"- **Off-chain**: {l3.get('offchain_count', 0)}\n\n")
 
 # Coordinate Relationships
 if all_results["coordinate_relationships"]:
 f.write("## Coordinate Relationships\n\n")
 coord = all_results["coordinate_relationships"]
 f.write(f"- **Known Zeros**: {coord.get('zero_count', 0)}/{coord.get('expected_zeros', 26)}\n")
 f.write(f"- **Missing Zeros**: {coord.get('missing_zeros', 0)}\n")
 f.write(f"- **Zeros Near Identity Regions**: {len(coord.get('zero_proximity', []))}\n\n")
 
 print(f"\n💾 Results saved to: {output_json}")
 print(f"📄 Report saved to: {output_md}")
 print()
 
 return all_results

if __name__ == "__main__":
 main()

