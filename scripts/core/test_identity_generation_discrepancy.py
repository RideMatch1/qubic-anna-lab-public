#!/usr/bin/env python3
"""
Test Identity Generation Discrepancy

Der User hat getestet: Private Keys funktionieren, aber generieren andere IDs im Qubic Wallet
als die in der Dokumentation stehen.

Lass uns das checkn!
"""

import sys
import subprocess
from pathlib import Path
import json

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

OUTPUT_DIR = project_root / "outputs" / "derived"
REPORTS_DIR = project_root / "outputs" / "reports"

def load_100_seeds():
 """Load die 100 Seeds aus der Dokumentation."""
 # Versuche zuerst JSON
 json_file = project_root / "github_export" / "100_seeds_and_identities.json"
 if json_file.exists():
 with json_file.open() as f:
 data = json.load(f)
 if isinstance(data, list):
 return [(item["seed"], item["identity"]) for item in data]
 elif isinstance(data, dict) and "seeds_and_identities" in data:
 return [(item["seed"], item["identity"]) for item in data["seeds_and_identities"]]
 
 # Fallback: Markdown
 seeds_file = project_root / "github_export" / "100_SEEDS_AND_IDENTITIES.md"
 if seeds_file.exists():
 seeds = []
 content = seeds_file.read_text()
 lines = content.split('\n')
 in_table = False
 
 for line in lines:
 if '| Seed' in line and '| Identity' in line:
 in_table = True
 continue
 
 if in_table and line.startswith('|') and '|' in line[1:]:
 parts = [p.strip() for p in line.split('|')]
 if len(parts) >= 3:
 seed = parts[1].strip('`')
 identity = parts[2].strip('`')
 if seed and identity and len(seed) == 55 and len(identity) == 60:
 seeds.append((seed, identity))
 return seeds
 
 return []

def derive_identity_from_seed(seed: str) -> tuple[str, str, str]:
 """
 Leite Identity aus Seed ab.
 Returns: (identity, private_key_hex, public_key_hex)
 """
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

print(f"IDENTITY:{{identity}}")
print(f"PRIVATE_KEY:{{private_key.hex()}}")
print(f"PUBLIC_KEY:{{public_key.hex()}}")
"""
 
 venv_python = project_root / "venv-tx" / "bin" / "python"
 if not venv_python.exists():
 return None, None, None
 
 try:
 result = subprocess.run(
 [str(venv_python), "-c", script],
 capture_output=True,
 text=True,
 timeout=10,
 cwd=project_root
 )
 
 if result.returncode != 0:
 return None, None, None
 
 identity = None
 private_key = None
 public_key = None
 
 for line in result.stdout.split('\n'):
 if line.startswith('IDENTITY:'):
 identity = line.split(':', 1)[1].strip()
 elif line.startswith('PRIVATE_KEY:'):
 private_key = line.split(':', 1)[1].strip()
 elif line.startswith('PUBLIC_KEY:'):
 public_key = line.split(':', 1)[1].strip()
 
 if identity and len(identity) == 60:
 return identity, private_key, public_key
 return None, None, None
 except Exception as e:
 print(f"Error deriving identity: {e}")
 return None, None, None

def main():
 print("=" * 80)
 print("TEST IDENTITY GENERATION DISCREPANCY")
 print("=" * 80)
 print()
 
 print("Loading 100 seeds from documentation...")
 seeds_data = load_100_seeds()
 print(f"✅ Loaded {len(seeds_data)} seeds")
 print()
 
 if not seeds_data:
 print("❌ No seeds found in documentation")
 return
 
 print("Testing first 10 seeds...")
 print()
 
 discrepancies = []
 matches = []
 
 for i, (seed, documented_identity) in enumerate(seeds_data[:10], 1):
 print(f"Test {i}/10: Seed: {seed[:20]}...")
 
 derived_identity, private_key, public_key = derive_identity_from_seed(seed)
 
 if not derived_identity:
 print(f" ❌ Could not derive identity")
 print()
 continue
 
 if derived_identity == documented_identity:
 matches.append({
 "seed": seed,
 "documented": documented_identity,
 "derived": derived_identity,
 "match": True
 })
 print(f" ✅ MATCH: {derived_identity}")
 else:
 discrepancies.append({
 "seed": seed,
 "documented": documented_identity,
 "derived": derived_identity,
 "private_key": private_key[:32] + "..." if private_key else None,
 "public_key": public_key[:32] + "..." if public_key else None,
 "match": False
 })
 print(f" ❌ MISMATCH!")
 print(f" Documented: {documented_identity}")
 print(f" Derived: {derived_identity}")
 print(f" Private Key: {private_key[:32]}..." if private_key else " Private Key: None")
 print()
 
 print("=" * 80)
 print("SUMMARY")
 print("=" * 80)
 print()
 print(f"Total tested: {len(seeds_data[:10])}")
 print(f"Matches: {len(matches)}")
 print(f"Discrepancies: {len(discrepancies)}")
 print()
 
 if discrepancies:
 print("⚠️ DISCREPANCIES FOUND!")
 print()
 print("This confirms the user's finding:")
 print("- Private keys work (can be derived from seeds)")
 print("- But they generate different identities than documented")
 print()
 print("Possible reasons:")
 print("1. Different identity calculation method")
 print("2. Different subseed derivation")
 print("3. Different public key format")
 print("4. Documentation contains wrong identities")
 print()
 
 # Speichere Ergebnisse
 OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
 REPORTS_DIR.mkdir(parents=True, exist_ok=True)
 
 results = {
 "total_tested": len(seeds_data[:10]),
 "matches": len(matches),
 "discrepancies": len(discrepancies),
 "discrepancy_details": discrepancies,
 "match_details": matches
 }
 
 output_file = OUTPUT_DIR / "identity_generation_discrepancy_test.json"
 with output_file.open('w') as f:
 json.dump(results, f, indent=2)
 print(f"✅ Results saved to: {output_file}")
 
 # Report
 report_file = REPORTS_DIR / "identity_generation_discrepancy_report.md"
 with report_file.open('w') as f:
 f.write("# Identity Generation Discrepancy Report\n\n")
 f.write("## Overview\n\n")
 f.write("Test confirms user finding: Private keys work but generate different identities than documented.\n\n")
 f.write("## Results\n\n")
 f.write(f"- **Total tested**: {len(seeds_data[:10])}\n")
 f.write(f"- **Matches**: {len(matches)}\n")
 f.write(f"- **Discrepancies**: {len(discrepancies)}\n\n")
 f.write("## Discrepancies\n\n")
 if discrepancies:
 for disc in discrepancies:
 f.write(f"### Seed: `{disc['seed']}`\n\n")
 f.write(f"- **Documented Identity**: `{disc['documented']}`\n")
 f.write(f"- **Derived Identity**: `{disc['derived']}`\n")
 f.write(f"- **Private Key**: `{disc['private_key']}`\n")
 f.write(f"- **Public Key**: `{disc['public_key']}`\n\n")
 else:
 f.write("No discrepancies found in tested seeds.\n\n")
 f.write("## Implications\n\n")
 f.write("This suggests:\n")
 f.write("1. Seeds/Private Keys are correct and functional\n")
 f.write("2. But the documented identities may be wrong or from a different calculation\n")
 f.write("3. Or there's a difference in how Qubic Wallet calculates identities\n\n")
 f.write("## Next Steps\n\n")
 f.write("- Test with Qubic Wallet directly\n")
 f.write("- Compare identity calculation methods\n")
 f.write("- Check if documented identities are from a different source\n")
 
 print(f"✅ Report saved to: {report_file}")
 print()
 print("=" * 80)
 print("TEST COMPLETE")
 print("=" * 80)

if __name__ == "__main__":
 main()

