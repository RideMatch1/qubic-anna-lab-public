#!/usr/bin/env python3
"""
Vergleiche Layer-3 und Layer-4 Patterns
"""

import json
from pathlib import Path
from collections import Counter, defaultdict
from typing import Dict, List

project_root = Path(__file__).parent.parent.parent
LAYER4_FILE = project_root / "outputs" / "derived" / "layer4_derivation_sample_5000.json"
LAYER3_EXTENDED = project_root / "outputs" / "derived" / "layer3_derivation_extended.json"
REPORTS_DIR = project_root / "outputs" / "reports"

def load_data():
 """Load Layer-3 und Layer-4 Daten."""
 layer4_data = []
 if LAYER4_FILE.exists():
 with LAYER4_FILE.open() as f:
 data = json.load(f)
 layer4_data = data.get("results", [])
 
 layer3_data = []
 if LAYER3_EXTENDED.exists():
 with LAYER3_EXTENDED.open() as f:
 data = json.load(f)
 layer3_data = data.get("results", [])
 
 return layer3_data, layer4_data

def compare_patterns():
 """Vergleiche Layer-3 und Layer-4 Patterns."""
 print("=" * 80)
 print("LAYER-3 vs. LAYER-4 COMPARISON")
 print("=" * 80)
 print()
 
 layer3_data, layer4_data = load_data()
 
 if not layer3_data:
 print("⚠️ No Layer-3 data found (using sample)")
 if not layer4_data:
 print("❌ No Layer-4 data found!")
 return
 
 print(f"✅ Layer-3: {len(layer3_data)} identities")
 print(f"✅ Layer-4: {len(layer4_data)} identities")
 print()
 
 # Position 30/4 Vergleich
 layer3_pos30 = Counter()
 layer3_pos4 = Counter()
 layer4_pos30 = Counter()
 layer4_pos4 = Counter()
 
 for entry in layer3_data:
 identity = entry.get("layer3_identity", "")
 if len(identity) > 30:
 layer3_pos30[identity[30].upper()] += 1
 if len(identity) > 4:
 layer3_pos4[identity[4].upper()] += 1
 
 for entry in layer4_data:
 identity = entry.get("layer4_identity", "")
 if len(identity) > 30:
 layer4_pos30[identity[30].upper()] += 1
 if len(identity) > 4:
 layer4_pos4[identity[4].upper()] += 1
 
 print("## Position 30 Comparison")
 print()
 print("Layer-3 (Top 10):")
 for char, count in layer3_pos30.most_common(10):
 pct = (count / len(layer3_data)) * 100 if layer3_data else 0
 print(f" {char}: {count} ({pct:.1f}%)")
 print()
 
 print("Layer-4 (Top 10):")
 for char, count in layer4_pos30.most_common(10):
 pct = (count / len(layer4_data)) * 100 if layer4_data else 0
 print(f" {char}: {count} ({pct:.1f}%)")
 print()
 
 print("## Position 4 Comparison")
 print()
 print("Layer-3 (Top 10):")
 for char, count in layer3_pos4.most_common(10):
 pct = (count / len(layer3_data)) * 100 if layer3_data else 0
 print(f" {char}: {count} ({pct:.1f}%)")
 print()
 
 print("Layer-4 (Top 10):")
 for char, count in layer4_pos4.most_common(10):
 pct = (count / len(layer4_data)) * 100 if layer4_data else 0
 print(f" {char}: {count} ({pct:.1f}%)")
 print()
 
 # Character Distribution Vergleich
 print("## Character Distribution Comparison")
 print()
 
 layer3_chars = Counter()
 layer4_chars = Counter()
 
 for entry in layer3_data:
 identity = entry.get("layer3_identity", "")
 for char in identity[:56]:
 layer3_chars[char.upper()] += 1
 
 for entry in layer4_data:
 identity = entry.get("layer4_identity", "")
 for char in identity[:56]:
 layer4_chars[char.upper()] += 1
 
 print("Layer-3 Top 10 Characters:")
 total_l3 = sum(layer3_chars.values())
 for char, count in layer3_chars.most_common(10):
 pct = (count / total_l3 * 100) if total_l3 > 0 else 0
 print(f" {char}: {count} ({pct:.2f}%)")
 print()
 
 print("Layer-4 Top 10 Characters:")
 total_l4 = sum(layer4_chars.values())
 for char, count in layer4_chars.most_common(10):
 pct = (count / total_l4 * 100) if total_l4 > 0 else 0
 print(f" {char}: {count} ({pct:.2f}%)")
 print()
 
 # Report
 report_lines = [
 "# Layer-3 vs. Layer-4 Comparison",
 "",
 f"**Layer-3 identities**: {len(layer3_data)}",
 f"**Layer-4 identities**: {len(layer4_data)}",
 "",
 "## Position 30 Comparison",
 "",
 "### Layer-3",
 ""
 ]
 
 for char, count in layer3_pos30.most_common(10):
 pct = (count / len(layer3_data)) * 100 if layer3_data else 0
 report_lines.append(f"- {char}: {count} ({pct:.1f}%)")
 
 report_lines.extend([
 "",
 "### Layer-4",
 ""
 ])
 
 for char, count in layer4_pos30.most_common(10):
 pct = (count / len(layer4_data)) * 100 if layer4_data else 0
 report_lines.append(f"- {char}: {count} ({pct:.1f}%)")
 
 report_file = REPORTS_DIR / "layer3_layer4_comparison.md"
 REPORTS_DIR.mkdir(parents=True, exist_ok=True)
 
 with report_file.open("w") as f:
 f.write("\n".join(report_lines) + "\n")
 
 print(f"📝 Report gespeichert: {report_file}")

if __name__ == "__main__":
 compare_patterns()

