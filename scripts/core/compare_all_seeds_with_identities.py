#!/usr/bin/env python3
"""
Compare All Seeds with Derived Identities

Nimmt alle 100 Seeds aus der Dokumentation, leitet die Identities ab,
und vergleicht sie mit den dokumentierten Identities, um Muster zu erkennen.
"""

import sys
import subprocess
import json
from pathlib import Path
from typing import Dict, List, Optional
from collections import defaultdict

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

OUTPUT_DIR = project_root / "outputs" / "derived"
REPORTS_DIR = project_root / "outputs" / "reports"
VENV_PYTHON = project_root / "venv-tx" / "bin" / "python"

def load_100_seeds() -> List[Dict]:
 """Load die 100 Seeds aus der Dokumentation."""
 json_file = project_root / "github_export" / "100_seeds_and_identities.json"
 
 if json_file.exists():
 with json_file.open() as f:
 data = json.load(f)
 if isinstance(data, list):
 return data
 elif isinstance(data, dict) and "seeds_and_identities" in data:
 return data["seeds_and_identities"]
 
 return []

def derive_identity_from_seed(seed: str) -> Optional[str]:
 """Leite Identity aus Seed ab."""
 if not VENV_PYTHON.exists():
 return None
 
 script = f"""
from qubipy.crypto.utils import (
 get_subseed_from_seed,
 get_private_key_from_subseed,
 get_public_key_from_private_key,
 get_identity_from_public_key,
)

seed = "{seed}"
seed_bytes = seed.encode('utf-8')
subseed = get_subseed_from_seed(seed_bytes)
private_key = get_private_key_from_subseed(subseed)
public_key = get_public_key_from_private_key(private_key)
identity = get_identity_from_public_key(public_key)
print(identity)
"""
 
 try:
 result = subprocess.run(
 [str(VENV_PYTHON), "-c", script],
 capture_output=True,
 text=True,
 timeout=10,
 cwd=project_root
 )
 
 if result.returncode == 0:
 identity = result.stdout.strip()
 if len(identity) == 60 and identity.isupper():
 return identity
 return None
 except Exception as e:
 return None

def analyze_patterns(comparisons: List[Dict]) -> Dict:
 """Analyze Muster in den Seed-Identity-Vergleichen."""
 patterns = {
 "character_differences": defaultdict(int),
 "position_differences": [],
 "common_prefix_length": [],
 "common_suffix_length": [],
 "seed_identity_overlap": [],
 }
 
 for comp in comparisons:
 seed = comp["seed"]
 documented = comp["documented_identity"]
 derived = comp["derived_identity"]
 
 if not derived:
 continue
 
 # Charakter-Unterschiede
 for i, (doc_char, der_char) in enumerate(zip(documented, derived)):
 if doc_char != der_char:
 patterns["character_differences"][i] += 1
 
 # Position der ersten Differenz
 first_diff = None
 for i, (doc_char, der_char) in enumerate(zip(documented, derived)):
 if doc_char != der_char:
 first_diff = i
 break
 if first_diff is not None:
 patterns["position_differences"].append(first_diff)
 
 # Gemeinsame Präfix-Länge
 prefix_len = 0
 for i, (doc_char, der_char) in enumerate(zip(documented, derived)):
 if doc_char == der_char:
 prefix_len += 1
 else:
 break
 patterns["common_prefix_length"].append(prefix_len)
 
 # Gemeinsame Suffix-Länge
 suffix_len = 0
 for i in range(min(len(documented), len(derived))):
 if documented[-(i+1)] == derived[-(i+1)]:
 suffix_len += 1
 else:
 break
 patterns["common_suffix_length"].append(suffix_len)
 
 # Seed-Identity Overlap
 seed_lower = seed.upper() # Seeds sind lowercase, Identities uppercase
 overlap = sum(1 for s, d in zip(seed_lower, documented) if s == d)
 patterns["seed_identity_overlap"].append(overlap)
 
 # Berechne Statistiken
 stats = {
 "avg_first_diff_position": sum(patterns["position_differences"]) / len(patterns["position_differences"]) if patterns["position_differences"] else 0,
 "avg_prefix_length": sum(patterns["common_prefix_length"]) / len(patterns["common_prefix_length"]) if patterns["common_prefix_length"] else 0,
 "avg_suffix_length": sum(patterns["common_suffix_length"]) / len(patterns["common_suffix_length"]) if patterns["common_suffix_length"] else 0,
 "avg_seed_overlap": sum(patterns["seed_identity_overlap"]) / len(patterns["seed_identity_overlap"]) if patterns["seed_identity_overlap"] else 0,
 "most_common_diff_positions": sorted(patterns["character_differences"].items(), key=lambda x: x[1], reverse=True)[:10],
 }
 
 return {
 "raw_patterns": patterns,
 "statistics": stats,
 }

def main():
 print("=" * 80)
 print("COMPARE ALL SEEDS WITH DERIVED IDENTITIES")
 print("=" * 80)
 print()
 
 print("Loading 100 seeds from documentation...")
 seeds_data = load_100_seeds()
 print(f"✅ Loaded {len(seeds_data)} seeds")
 print()
 
 if not seeds_data:
 print("❌ No seeds found")
 return
 
 print("Deriving identities from seeds...")
 print("(This may take a while...)")
 print()
 
 comparisons = []
 matches = 0
 mismatches = 0
 
 for idx, item in enumerate(seeds_data, 1):
 seed = item["seed"]
 documented_identity = item["identity"]
 
 if idx % 10 == 0:
 print(f"Progress: {idx}/{len(seeds_data)} ({idx/len(seeds_data)*100:.1f}%)")
 
 derived_identity = derive_identity_from_seed(seed)
 
 comparison = {
 "index": idx,
 "seed": seed,
 "documented_identity": documented_identity,
 "derived_identity": derived_identity,
 "match": derived_identity == documented_identity if derived_identity else False,
 }
 
 comparisons.append(comparison)
 
 if comparison["match"]:
 matches += 1
 elif derived_identity:
 mismatches += 1
 
 print()
 print("=" * 80)
 print("RESULTS")
 print("=" * 80)
 print()
 print(f"Total seeds tested: {len(seeds_data)}")
 print(f"Matches: {matches}")
 print(f"Mismatches: {mismatches}")
 print(f"Could not derive: {len(seeds_data) - matches - mismatches}")
 print()
 
 if mismatches > 0:
 print("Analyzing patterns in mismatches...")
 patterns = analyze_patterns(comparisons)
 
 print()
 print("Pattern Analysis:")
 print(f" Average first difference position: {patterns['statistics']['avg_first_diff_position']:.1f}")
 print(f" Average common prefix length: {patterns['statistics']['avg_prefix_length']:.1f}")
 print(f" Average common suffix length: {patterns['statistics']['avg_suffix_length']:.1f}")
 print(f" Average seed-identity overlap: {patterns['statistics']['avg_seed_overlap']:.1f}")
 print()
 print("Most common difference positions:")
 for pos, count in patterns['statistics']['most_common_diff_positions']:
 print(f" Position {pos}: {count} differences")
 print()
 
 # Speichere Ergebnisse
 OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
 REPORTS_DIR.mkdir(parents=True, exist_ok=True)
 
 results = {
 "total_tested": len(seeds_data),
 "matches": matches,
 "mismatches": mismatches,
 "comparisons": comparisons,
 "patterns": patterns if mismatches > 0 else None,
 }
 
 output_file = OUTPUT_DIR / "seed_identity_comparison.json"
 with output_file.open('w') as f:
 json.dump(results, f, indent=2)
 print(f"✅ Results saved to: {output_file}")
 
 # Report
 report_file = REPORTS_DIR / "seed_identity_comparison_report.md"
 with report_file.open('w') as f:
 f.write("# Seed-Identity Comparison Report\n\n")
 f.write("## Overview\n\n")
 f.write(f"Comparison of {len(seeds_data)} seeds with their derived and documented identities.\n\n")
 f.write("## Results\n\n")
 f.write(f"- **Total tested**: {len(seeds_data)}\n")
 f.write(f"- **Matches**: {matches}\n")
 f.write(f"- **Mismatches**: {mismatches}\n")
 f.write(f"- **Could not derive**: {len(seeds_data) - matches - mismatches}\n\n")
 
 if mismatches > 0:
 f.write("## Pattern Analysis\n\n")
 f.write("### Statistics\n\n")
 f.write(f"- **Average first difference position**: {patterns['statistics']['avg_first_diff_position']:.1f}\n")
 f.write(f"- **Average common prefix length**: {patterns['statistics']['avg_prefix_length']:.1f}\n")
 f.write(f"- **Average common suffix length**: {patterns['statistics']['avg_suffix_length']:.1f}\n")
 f.write(f"- **Average seed-identity overlap**: {patterns['statistics']['avg_seed_overlap']:.1f}\n\n")
 f.write("### Most Common Difference Positions\n\n")
 for pos, count in patterns['statistics']['most_common_diff_positions']:
 f.write(f"- Position {pos}: {count} differences\n")
 f.write("\n")
 
 f.write("## Sample Mismatches (First 10)\n\n")
 f.write("| Seed (excerpt) | Documented Identity (excerpt) | Derived Identity (excerpt) | Match |\n")
 f.write("| --- | --- | --- | --- |\n")
 
 for comp in comparisons[:10]:
 if not comp["match"] and comp["derived_identity"]:
 f.write(f"| `{comp['seed'][:20]}...` | `{comp['documented_identity'][:20]}...` | `{comp['derived_identity'][:20]}...` | ❌ |\n")
 
 f.write("\n## Implications\n\n")
 if matches == 0:
 f.write("**All seeds produce different identities than documented.**\n\n")
 f.write("This confirms:\n")
 f.write("1. The documented identities are from the matrix (not derived from seeds)\n")
 f.write("2. The extracted seeds (`identity.lower()[:55]`) are approximations\n")
 f.write("3. The real seeds that generate the documented identities are different\n\n")
 else:
 f.write(f"**{matches} seeds match, {mismatches} don't.**\n\n")
 f.write("This suggests a mixed situation - some seeds might be correct, others not.\n\n")
 
 print(f"✅ Report saved to: {report_file}")
 print()
 print("=" * 80)
 print("COMPARISON COMPLETE")
 print("=" * 80)

if __name__ == "__main__":
 main()

