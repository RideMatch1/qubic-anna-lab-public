#!/usr/bin/env python3
"""
Teste Wallet-Zugriff for alle Identities mit Seeds

WICHTIG: Nur echte, nachgewiesene Erkenntnisse!
Testet ob wir Transaktionen signieren können (Wallet-Zugriff).
"""

import sys
import json
import subprocess
from pathlib import Path
from typing import Dict, List, Optional

VENV_PATH = Path(__file__).parent.parent.parent / "venv-tx"
OUTPUT_DIR = Path("outputs/derived")
SEEDS_FILE = OUTPUT_DIR / "all_identities_with_seeds_mapped.json"
OUTPUT_JSON = OUTPUT_DIR / "wallet_access_test_results.json"
OUTPUT_MD = OUTPUT_DIR / "WALLET_ACCESS_TEST_RESULTS.md"

def test_wallet_access(seed: str, identity: str) -> Dict:
 """Teste ob wir Zugriff auf das Wallet haben (können signieren)."""
 python_exe = VENV_PATH / "bin" / "python"
 
 script = f"""
from qubipy.crypto.utils import (
 get_subseed_from_seed,
 get_private_key_from_subseed,
 get_public_key_from_private_key,
 get_identity_from_public_key,
)
import json

seed = "{seed}"
identity = "{identity}"

try:
 seed_bytes = seed.encode('utf-8')
 subseed = get_subseed_from_seed(seed_bytes)
 private_key = get_private_key_from_subseed(subseed)
 public_key = get_public_key_from_private_key(private_key)
 derived_identity = get_identity_from_public_key(public_key)
 
 # Test: Check ob Identity aboveeinstimmt
 if derived_identity == identity:
 result = {{
 "can_sign": True,
 "seed_valid": True,
 "identity_match": True,
 "derived_identity": derived_identity,
 }}
 else:
 result = {{
 "can_sign": False,
 "seed_valid": True,
 "identity_match": False,
 "derived_identity": derived_identity,
 "expected_identity": identity,
 }}
 
 print(json.dumps(result))
except Exception as e:
 print(json.dumps({{
 "can_sign": False,
 "seed_valid": False,
 "error": str(e),
 }}))
"""
 
 try:
 result = subprocess.run(
 [str(python_exe), "-c", script],
 capture_output=True,
 text=True,
 timeout=10,
 cwd=Path(__file__).parent.parent.parent
 )
 
 if result.returncode != 0:
 return {"can_sign": False, "error": "subprocess_failed", "stderr": result.stderr}
 
 try:
 return json.loads(result.stdout.strip())
 except:
 return {"can_sign": False, "error": "parse_error", "stdout": result.stdout[:200]}
 except subprocess.TimeoutExpired:
 return {"can_sign": False, "error": "timeout"}
 except Exception as e:
 return {"can_sign": False, "error": str(e)}

def main():
 print("=" * 80)
 print("TEST WALLET ACCESS (BULK)")
 print("=" * 80)
 print()
 print("WICHTIG: Nur echte, nachgewiesene Erkenntnisse!")
 print()
 
 if not VENV_PATH.exists():
 print(f"❌ venv-tx not found at: {VENV_PATH}")
 return False
 
 if not SEEDS_FILE.exists():
 print(f"❌ Seeds file not found: {SEEDS_FILE}")
 return False
 
 # Load Identities mit Seeds
 print("Loading identities with seeds...")
 with SEEDS_FILE.open() as f:
 seeds_data = json.load(f)
 
 identities = seeds_data.get("identities", [])
 print(f"✅ Loaded {len(identities)} identities")
 print()
 
 # Teste Wallet-Zugriff
 print("=" * 80)
 print("TESTING WALLET ACCESS")
 print("=" * 80)
 print()
 
 results = []
 stats = {
 "total": len(identities),
 "tested": 0,
 "can_sign": 0,
 "seed_valid": 0,
 "identity_match": 0,
 "errors": 0,
 }
 
 # Teste nur Identities mit bekannten Seeds (schneller)
 identities_to_test = [i for i in identities if i.get("known_seed")]
 print(f"Testing {len(identities_to_test)} identities with known seeds...")
 print()
 
 batch_size = 50
 total_batches = (len(identities_to_test) + batch_size - 1) // batch_size
 
 for batch_idx in range(total_batches):
 start_idx = batch_idx * batch_size
 end_idx = min(start_idx + batch_size, len(identities_to_test))
 batch = identities_to_test[start_idx:end_idx]
 
 print(f"Batch {batch_idx + 1}/{total_batches} ({start_idx + 1}-{end_idx}/{len(identities_to_test)})...")
 
 for identity_data in batch:
 identity = identity_data.get("identity")
 known_seed = identity_data.get("known_seed")
 
 if not known_seed:
 continue
 
 stats["tested"] += 1
 
 # Teste Wallet-Zugriff
 wallet_test = test_wallet_access(known_seed, identity)
 
 can_sign = wallet_test.get("can_sign", False)
 seed_valid = wallet_test.get("seed_valid", False)
 identity_match = wallet_test.get("identity_match", False)
 
 if can_sign:
 stats["can_sign"] += 1
 if seed_valid:
 stats["seed_valid"] += 1
 if identity_match:
 stats["identity_match"] += 1
 if wallet_test.get("error"):
 stats["errors"] += 1
 
 # Speichere Ergebnis
 result = {
 "identity": identity,
 "known_seed": known_seed,
 "layer": identity_data.get("layer"),
 "balance": identity_data.get("balance", "0"),
 "wallet_test": wallet_test,
 "can_sign": can_sign,
 }
 results.append(result)
 
 if can_sign:
 print(f" ✅ {identity[:40]}... | Layer: {identity_data.get('layer')} | Wallet: ✅")
 elif seed_valid:
 print(f" ⚠️ {identity[:40]}... | Layer: {identity_data.get('layer')} | Wallet: ❌ (seed valid but no match)")
 else:
 print(f" ❌ {identity[:40]}... | Layer: {identity_data.get('layer')} | Error: {wallet_test.get('error', 'unknown')}")
 
 # Speichere Zwischenergebnisse
 checkpoint = {
 "stats": stats,
 "results": results,
 }
 checkpoint_file = OUTPUT_DIR / "wallet_access_checkpoint.json"
 with checkpoint_file.open("w") as f:
 json.dump(checkpoint, f, indent=2)
 
 print(f" Progress: {stats['can_sign']}/{stats['tested']} can sign ({stats['can_sign']/stats['tested']*100:.1f}%)")
 print()
 
 # Zusammenfassung
 print("=" * 80)
 print("SUMMARY")
 print("=" * 80)
 print()
 
 print(f"Total identities: {stats['total']}")
 print(f"Tested: {stats['tested']}")
 print(f"Can sign: {stats['can_sign']} ({stats['can_sign']/stats['tested']*100:.1f}%)")
 print(f"Seed valid: {stats['seed_valid']} ({stats['seed_valid']/stats['tested']*100:.1f}%)")
 print(f"Identity match: {stats['identity_match']} ({stats['identity_match']/stats['tested']*100:.1f}%)")
 print(f"Errors: {stats['errors']}")
 print()
 
 # Speichere finale Ergebnisse
 OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
 
 final_results = {
 "summary": stats,
 "results": results,
 }
 
 with OUTPUT_JSON.open("w") as f:
 json.dump(final_results, f, indent=2)
 
 # Erstelle Markdown Report
 with OUTPUT_MD.open("w") as f:
 f.write("# Wallet Access Test Results\n\n")
 f.write("## Summary\n\n")
 f.write(f"- **Total identities**: {stats['total']}\n")
 f.write(f"- **Tested**: {stats['tested']}\n")
 f.write(f"- **Can sign**: {stats['can_sign']} ({stats['can_sign']/stats['tested']*100:.1f}%)\n")
 f.write(f"- **Seed valid**: {stats['seed_valid']} ({stats['seed_valid']/stats['tested']*100:.1f}%)\n")
 f.write(f"- **Identity match**: {stats['identity_match']} ({stats['identity_match']/stats['tested']*100:.1f}%)\n")
 f.write(f"- **Errors**: {stats['errors']}\n\n")
 f.write("## Identities with Wallet Access\n\n")
 
 wallet_access_identities = [r for r in results if r.get("can_sign")]
 f.write(f"**Total**: {len(wallet_access_identities)}\n\n")
 f.write("| Identity | Layer | Seed | Balance |\n")
 f.write("|----------|-------|------|---------|\n")
 
 for result in wallet_access_identities[:100]: # Erste 100
 f.write(f"| {result['identity']} | {result.get('layer', '?')} | {result['known_seed']} | {result['balance']} QU |\n")
 
 if len(wallet_access_identities) > 100:
 f.write(f"\n... and {len(wallet_access_identities) - 100} more\n")
 
 print(f"💾 Results saved to: {OUTPUT_JSON}")
 print(f"📄 Report saved to: {OUTPUT_MD}")
 print()
 print("=" * 80)
 print("✅ WALLET ACCESS TEST COMPLETE")
 print("=" * 80)
 
 return True

if __name__ == "__main__":
 success = main()
 sys.exit(0 if success else 1)

