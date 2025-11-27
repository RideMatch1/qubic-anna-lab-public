#!/usr/bin/env python3
"""
Analyze Layer-4 Sample (5000 Identities)
"""

import json
from pathlib import Path
from collections import Counter, defaultdict
from typing import Dict, List

project_root = Path(__file__).parent.parent.parent
LAYER4_FILE = project_root / "outputs" / "derived" / "layer4_derivation_sample_5000.json"
LAYER3_FILE = project_root / "outputs" / "derived" / "layer3_derivation_23k_complete.json"
REPORTS_DIR = project_root / "outputs" / "reports"

def load_layer4_data() -> List[Dict]:
 """Load Layer-4 Daten."""
 if not LAYER4_FILE.exists():
 return []
 
 with LAYER4_FILE.open() as f:
 data = json.load(f)
 
 return data.get("results", [])

def load_layer3_sample() -> Dict[str, str]:
 """Load Layer-3 Sample for Vergleich."""
 layer3_map = {}
 
 if LAYER3_FILE.exists():
 with LAYER3_FILE.open() as f:
 data = json.load(f)
 
 for result in data.get("results", []):
 layer3_id = result.get("layer3_identity", "")
 if layer3_id:
 layer3_map[layer3_id] = layer3_id
 
 return layer3_map

def analyze_layer4_patterns():
 """Analyze Layer-4 Patterns."""
 print("=" * 80)
 print("LAYER-4 SAMPLE ANALYSIS (5000 Identities)")
 print("=" * 80)
 print()
 
 layer4_data = load_layer4_data()
 
 if not layer4_data:
 print("❌ No Layer-4 data found!")
 return
 
 print(f"✅ Loaded {len(layer4_data)} Layer-4 identities")
 print()
 
 # Basis-Statistiken
 derivable = sum(1 for r in layer4_data if r.get("layer4_derivable"))
 print(f"Layer-4 derivable: {derivable}/{len(layer4_data)} ({derivable/len(layer4_data)*100:.1f}%)")
 print()
 
 # Position 30/4 Distribution
 pos30 = Counter()
 pos4 = Counter()
 
 for entry in layer4_data:
 identity = entry.get("layer4_identity", "")
 if len(identity) > 30:
 pos30[identity[30].upper()] += 1
 if len(identity) > 4:
 pos4[identity[4].upper()] += 1
 
 print("## Position 30 Distribution (Top 10)")
 for char, count in pos30.most_common(10):
 pct = (count / len(layer4_data)) * 100
 print(f" {char}: {count} ({pct:.1f}%)")
 print()
 
 print("## Position 4 Distribution (Top 10)")
 for char, count in pos4.most_common(10):
 pct = (count / len(layer4_data)) * 100
 print(f" {char}: {count} ({pct:.1f}%)")
 print()
 
 # Vergleich mit Layer-3 (Position 30/4)
 print("## Vergleich Layer-3 vs. Layer-4 (Position 30)")
 layer3_map = load_layer3_sample()
 
 # Finde Layer-3 Position 30 for gleiche Identities
 layer3_pos30 = Counter()
 for entry in layer4_data:
 layer3_id = entry.get("layer3_identity", "")
 if len(layer3_id) > 30:
 layer3_pos30[layer3_id[30].upper()] += 1
 
 print("Layer-3 Position 30 (Top 10):")
 for char, count in layer3_pos30.most_common(10):
 pct = (count / len(layer4_data)) * 100
 print(f" {char}: {count} ({pct:.1f}%)")
 print()
 
 print("Layer-4 Position 30 (Top 10):")
 for char, count in pos30.most_common(10):
 pct = (count / len(layer4_data)) * 100
 print(f" {char}: {count} ({pct:.1f}%)")
 print()
 
 # Character Distribution (alle Positionen)
 print("## Character Distribution Analysis")
 all_chars = Counter()
 for entry in layer4_data:
 identity = entry.get("layer4_identity", "")
 for char in identity[:56]: # Body ohne Checksum
 all_chars[char.upper()] += 1
 
 print("Top 10 Characters (in Body):")
 for char, count in all_chars.most_common(10):
 pct = (count / (len(layer4_data) * 56)) * 100
 print(f" {char}: {count} ({pct:.2f}%)")
 print()
 
 # Sample Identities
 print("## Sample Layer-4 Identities")
 for i, entry in enumerate(layer4_data[:5], 1):
 layer3 = entry.get("layer3_identity", "")
 layer4 = entry.get("layer4_identity", "")
 seed = entry.get("seed", "")
 print(f"{i}. Layer-3: {layer3[:30]}...")
 print(f" Seed: {seed[:30]}...")
 print(f" Layer-4: {layer4[:30]}...")
 print()
 
 # Report
 report_lines = [
 "# Layer-4 Sample Analysis (5000 Identities)",
 "",
 f"**Total Layer-4 identities**: {len(layer4_data)}",
 f"**Layer-4 derivable**: {derivable} ({derivable/len(layer4_data)*100:.1f}%)",
 "",
 "## Position 30 Distribution",
 ""
 ]
 
 for char, count in pos30.most_common(10):
 pct = (count / len(layer4_data)) * 100
 report_lines.append(f"- {char}: {count} ({pct:.1f}%)")
 
 report_lines.extend([
 "",
 "## Position 4 Distribution",
 ""
 ])
 
 for char, count in pos4.most_common(10):
 pct = (count / len(layer4_data)) * 100
 report_lines.append(f"- {char}: {count} ({pct:.1f}%)")
 
 report_lines.extend([
 "",
 "## Next Steps",
 "",
 "1. RPC Validation: Check on-chain Status for Layer-4 Sample",
 "2. Pattern Analysis: Vergleiche Layer-3 vs. Layer-4 Patterns",
 "3. Full Derivation: Leite alle 23k Layer-4 Identities ab (falls nötig)"
 ])
 
 report_file = REPORTS_DIR / "layer4_sample_analysis.md"
 REPORTS_DIR.mkdir(parents=True, exist_ok=True)
 
 with report_file.open("w") as f:
 f.write("\n".join(report_lines) + "\n")
 
 print(f"📝 Report gespeichert: {report_file}")

if __name__ == "__main__":
 analyze_layer4_patterns()

