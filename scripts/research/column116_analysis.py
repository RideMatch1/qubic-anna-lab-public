#!/usr/bin/env python3
"""
Column 116 Deep Analysis

Warum hat Column 116 die meisten Zeros (7)?
Analysiert Column 116 und ihre Beziehung zu Identity Extraction.
"""

import sys
import numpy as np
from pathlib import Path
from typing import Dict, List, Tuple
from collections import Counter

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from analysis.utils.data_loader import load_anna_matrix

OUTPUT_DIR = project_root / "outputs" / "derived"
REPORTS_DIR = project_root / "outputs" / "reports"

def analyze_column116(matrix: np.ndarray) -> Dict:
 """Analyze Column 116 im Detail."""
 col = 116
 
 # Alle Werte in Column 116
 column_values = matrix[:, col]
 
 # Statistiken
 zero_positions = []
 value_distribution = Counter()
 
 for row in range(128):
 value = matrix[row, col]
 
 if abs(value) < 0.0001:
 zero_positions.append(row)
 
 # Value distribution
 int_value = int(value) if not np.isnan(value) else None
 if int_value is not None:
 value_distribution[int_value] += 1
 
 # Base-26 Analysis
 base26_chars = []
 for row in range(128):
 value = matrix[row, col]
 if not np.isnan(value):
 base26_val = int(value) % 26
 base26_char = chr(ord('A') + base26_val)
 base26_chars.append(base26_char)
 
 base26_dist = Counter(base26_chars)
 
 return {
 "column": col,
 "zero_count": len(zero_positions),
 "zero_positions": zero_positions,
 "value_distribution": dict(value_distribution.most_common(20)),
 "base26_chars": base26_chars,
 "base26_distribution": dict(base26_dist.most_common(26)),
 "mean_value": float(np.nanmean(column_values)),
 "std_value": float(np.nanstd(column_values)),
 "min_value": float(np.nanmin(column_values)),
 "max_value": float(np.nanmax(column_values))
 }

def analyze_column116_identity_relationship(matrix: np.ndarray) -> Dict:
 """Analyze Beziehung zwischen Column 116 und Identity Extraction."""
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
 
 # Column 116 Zeros
 col116_zeros = [37, 45, 71, 79, 101, 109, 111, 112]
 
 # Finde Beziehungen
 relationships = []
 for zero_row in col116_zeros:
 for region in identity_regions:
 r_min, r_max = region["rows"]
 distance = min(abs(zero_row - r_min), abs(zero_row - r_max))
 
 if distance <= 10: # Within 10 rows
 relationships.append({
 "zero_row": zero_row,
 "region": region["name"],
 "distance": distance,
 "in_region": r_min <= zero_row <= r_max
 })
 
 return {
 "col116_zeros": col116_zeros,
 "identity_relationships": relationships,
 "total_relationships": len(relationships)
 }

def analyze_column116_patterns(matrix: np.ndarray) -> Dict:
 """Analyze Patterns in Column 116."""
 col = 116
 
 # Analyze Werte-Muster
 patterns = {
 "consecutive_zeros": [],
 "value_clusters": [],
 "base26_sequences": []
 }
 
 # Finde consecutive zeros
 consecutive = []
 for row in range(128):
 value = matrix[row, col]
 if abs(value) < 0.0001:
 consecutive.append(row)
 else:
 if len(consecutive) > 1:
 patterns["consecutive_zeros"].append(consecutive)
 consecutive = []
 
 if len(consecutive) > 1:
 patterns["consecutive_zeros"].append(consecutive)
 
 # Base-26 Sequence
 base26_seq = []
 for row in range(128):
 value = matrix[row, col]
 if not np.isnan(value):
 base26_val = int(value) % 26
 base26_char = chr(ord('A') + base26_val)
 base26_seq.append(base26_char)
 
 patterns["base26_sequence"] = ''.join(base26_seq)
 
 # Finde wiederholende Patterns in Base-26
 seq = patterns["base26_sequence"]
 repeating_patterns = []
 for pattern_len in [2, 3, 4]:
 for i in range(len(seq) - pattern_len + 1):
 pattern = seq[i:i+pattern_len]
 if seq.count(pattern) > 1:
 repeating_patterns.append((pattern, seq.count(pattern)))
 
 patterns["repeating_base26"] = list(set(repeating_patterns))[:20]
 
 return patterns

def main():
 """Hauptfunktion."""
 print("=" * 80)
 print("COLUMN 116 DEEP ANALYSIS")
 print("=" * 80)
 print()
 
 # Load Matrix
 print("Loading Anna Matrix...")
 payload = load_anna_matrix()
 matrix = payload.matrix
 print(f"✅ Matrix loaded: {matrix.shape}")
 print()
 
 # Analyze Column 116
 print("Analyzing Column 116...")
 col116_analysis = analyze_column116(matrix)
 
 print("=" * 80)
 print("COLUMN 116 ANALYSIS RESULTS")
 print("=" * 80)
 print()
 print(f"Zero count: {col116_analysis['zero_count']}")
 print(f"Zero positions: {col116_analysis['zero_positions']}")
 print(f"Mean value: {col116_analysis['mean_value']:.2f}")
 print(f"Std value: {col116_analysis['std_value']:.2f}")
 print()
 
 print("Top 10 values in Column 116:")
 for value, count in list(col116_analysis['value_distribution'].items())[:10]:
 print(f" Value {value}: {count} occurrences")
 print()
 
 print("Top 10 Base-26 characters in Column 116:")
 for char, count in list(col116_analysis['base26_distribution'].items())[:10]:
 print(f" '{char}': {count} occurrences")
 print()
 
 # Identity Relationships
 print("Analyzing Column 116 - Identity Relationships...")
 relationships = analyze_column116_identity_relationship(matrix)
 
 print(f"Column 116 zeros: {relationships['col116_zeros']}")
 print(f"Identity relationships found: {relationships['total_relationships']}")
 if relationships['identity_relationships']:
 print("\nRelationships:")
 for rel in relationships['identity_relationships'][:5]:
 print(f" Row {rel['zero_row']} near {rel['region']} (distance: {rel['distance']})")
 print()
 
 # Patterns
 print("Analyzing Column 116 Patterns...")
 patterns = analyze_column116_patterns(matrix)
 
 if patterns['consecutive_zeros']:
 print("Consecutive zero sequences:")
 for seq in patterns['consecutive_zeros']:
 print(f" Rows {seq[0]}-{seq[-1]}: {len(seq)} consecutive zeros")
 print()
 
 if patterns['repeating_base26']:
 print("Top repeating Base-26 patterns:")
 for pattern, count in sorted(patterns['repeating_base26'], key=lambda x: x[1], reverse=True)[:10]:
 print(f" '{pattern}': {count} occurrences")
 print()
 
 # Speichere Ergebnisse
 OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
 import json
 
 results = {
 "column116_analysis": col116_analysis,
 "identity_relationships": relationships,
 "patterns": patterns
 }
 
 output_json = OUTPUT_DIR / "column116_deep_analysis.json"
 with output_json.open("w") as f:
 json.dump(results, f, indent=2)
 
 # Report
 REPORTS_DIR.mkdir(parents=True, exist_ok=True)
 output_md = REPORTS_DIR / "column116_deep_analysis_report.md"
 
 with output_md.open("w") as f:
 f.write("# Column 116 Deep Analysis Report\n\n")
 f.write("**Generated**: 2025-11-25\n\n")
 f.write("## Summary\n\n")
 f.write(f"Column 116 contains **{col116_analysis['zero_count']} zeros** - the strongest cluster!\n\n")
 
 f.write("## Column 116 Statistics\n\n")
 f.write(f"- **Zero count**: {col116_analysis['zero_count']}\n")
 f.write(f"- **Zero positions**: {col116_analysis['zero_positions']}\n")
 f.write(f"- **Mean value**: {col116_analysis['mean_value']:.2f}\n")
 f.write(f"- **Std value**: {col116_analysis['std_value']:.2f}\n\n")
 
 f.write("## Identity Relationships\n\n")
 f.write(f"Column 116 zeros near identity extraction regions: {relationships['total_relationships']}\n\n")
 if relationships['identity_relationships']:
 f.write("| Zero Row | Region | Distance | In Region |\n")
 f.write("|----------|--------|----------|-----------|\n")
 for rel in relationships['identity_relationships']:
 f.write(f"| {rel['zero_row']} | {rel['region']} | {rel['distance']} | {'✅' if rel['in_region'] else '❌'} |\n")
 f.write("\n")
 
 f.write("## Patterns\n\n")
 if patterns['consecutive_zeros']:
 f.write("### Consecutive Zero Sequences\n\n")
 for seq in patterns['consecutive_zeros']:
 f.write(f"- Rows {seq[0]}-{seq[-1]}: {len(seq)} consecutive zeros\n")
 f.write("\n")
 
 print(f"💾 Results saved to: {output_json}")
 print(f"📄 Report saved to: {output_md}")
 print()
 
 return results

if __name__ == "__main__":
 main()

