#!/usr/bin/env python3
"""
Extrahiere alle Seeds/Private Keys aus On-Chain validierten Identities

WICHTIG: Nur echte, nachgewiesene Erkenntnisse!
1. Bereinigt Duplikate
2. Leitet Seeds ab (identity.lower()[:55])
3. Validiert Seeds mit Crypto
4. Testet Wallet-Zugriff
"""

import sys
import json
import subprocess
from pathlib import Path
from typing import Dict, List, Set, Optional
from collections import defaultdict

VENV_PATH = Path(__file__).parent.parent.parent / "venv-tx"
OUTPUT_DIR = Path("outputs/derived")
VALIDATION_FILE = OUTPUT_DIR / "onchain_validation_all_identities.json"
OUTPUT_JSON = OUTPUT_DIR / "all_identities_with_seeds.json"
OUTPUT_MD = OUTPUT_DIR / "ALL_IDENTITIES_WITH_SEEDS.md"

# Import standardized conversion
sys.path.insert(0, str(Path(__file__).parent))
from standardized_conversion import identity_to_seed, validate_identity, validate_seed

def derive_identity_from_seed(seed: str) -> Optional[str]:
 """Leite Identity aus Seed ab (mit venv-tx)."""
 python_exe = VENV_PATH / "bin" / "python"
 
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
 [str(python_exe), "-c", script],
 capture_output=True,
 text=True,
 timeout=10,
 cwd=Path(__file__).parent.parent.parent
 )
 
 if result.returncode != 0:
 return None
 
 identity = result.stdout.strip()
 if len(identity) == 60 and identity.isupper():
 return identity
 return None
 except Exception:
 return None

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
 print(json.dumps({{
 "can_sign": True,
 "seed_valid": True,
 "identity_match": True,
 }}))
 else:
 print(json.dumps({{
 "can_sign": False,
 "seed_valid": True,
 "identity_match": False,
 "derived_identity": derived_identity,
 }}))
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
 return {"can_sign": False, "error": "subprocess_failed"}
 
 try:
 return json.loads(result.stdout.strip())
 except:
 return {"can_sign": False, "error": "parse_error"}
 except Exception as e:
 return {"can_sign": False, "error": str(e)}

def deduplicate_results(results: List[Dict]) -> List[Dict]:
 """Bereinige Duplikate aus den Ergebnissen."""
 seen = set()
 unique_results = []
 
 for result in results:
 identity = result.get("identity")
 if identity and identity not in seen:
 seen.add(identity)
 unique_results.append(result)
 
 return unique_results

def main():
 print("=" * 80)
 print("EXTRACT ALL SEEDS FROM IDENTITIES")
 print("=" * 80)
 print()
 print("WICHTIG: Nur echte, nachgewiesene Erkenntnisse!")
 print()
 
 if not VENV_PATH.exists():
 print(f"❌ venv-tx not found at: {VENV_PATH}")
 return False
 
 if not VALIDATION_FILE.exists():
 print(f"❌ Validation file not found: {VALIDATION_FILE}")
 return False
 
 # Load On-Chain Validierungs-Ergebnisse
 print("Loading on-chain validation results...")
 with VALIDATION_FILE.open() as f:
 validation_data = json.load(f)
 
 results = validation_data.get("results", [])
 print(f"✅ Loaded {len(results)} results")
 
 # Bereinige Duplikate
 print("Deduplicating results...")
 unique_results = deduplicate_results(results)
 print(f"✅ {len(unique_results)} unique identities (removed {len(results) - len(unique_results)} duplicates)")
 print()
 
 # Extrahiere Seeds und validate
 print("=" * 80)
 print("EXTRACTING SEEDS & VALIDATING")
 print("=" * 80)
 print()
 
 identities_with_seeds = []
 stats = {
 "total": len(unique_results),
 "seeds_extracted": 0,
 "seeds_valid": 0,
 "crypto_validated": 0,
 "wallet_access": 0,
 "errors": 0,
 }
 
 batch_size = 50
 total_batches = (len(unique_results) + batch_size - 1) // batch_size
 
 for batch_idx in range(total_batches):
 start_idx = batch_idx * batch_size
 end_idx = min(start_idx + batch_size, len(unique_results))
 batch = unique_results[start_idx:end_idx]
 
 print(f"Batch {batch_idx + 1}/{total_batches} ({start_idx + 1}-{end_idx}/{len(unique_results)})...")
 
 for result in batch:
 identity = result.get("identity")
 if not identity:
 continue
 
 # Extrahiere Seed
 seed = identity_to_seed(identity)
 if not seed:
 stats["errors"] += 1
 continue
 
 stats["seeds_extracted"] += 1
 
 # Validate Seed-Format
 if not validate_seed(seed):
 stats["errors"] += 1
 continue
 
 stats["seeds_valid"] += 1
 
 # Crypto-Validierung: Check ob Seed zu Identity führt
 derived_identity = derive_identity_from_seed(seed)
 crypto_valid = (derived_identity == identity)
 
 if crypto_valid:
 stats["crypto_validated"] += 1
 
 # Teste Wallet-Zugriff
 wallet_test = test_wallet_access(seed, identity)
 can_sign = wallet_test.get("can_sign", False)
 
 if can_sign:
 stats["wallet_access"] += 1
 
 # Speichere Ergebnis
 identity_data = {
 "identity": identity,
 "seed": seed,
 "balance": result.get("balance", "0"),
 "validForTick": result.get("validForTick"),
 "incomingAmount": result.get("incomingAmount", "0"),
 "outgoingAmount": result.get("outgoingAmount", "0"),
 "crypto_validated": crypto_valid,
 "derived_identity": derived_identity,
 "wallet_access": can_sign,
 "wallet_test": wallet_test,
 }
 
 identities_with_seeds.append(identity_data)
 
 if crypto_valid and can_sign:
 print(f" ✅ {identity[:40]}... | Seed: {seed[:30]}... | Wallet: ✅")
 elif crypto_valid:
 print(f" ⚠️ {identity[:40]}... | Seed: {seed[:30]}... | Wallet: ❌")
 else:
 print(f" ❌ {identity[:40]}... | Seed: {seed[:30]}... | Crypto: ❌")
 
 # Speichere Zwischenergebnisse
 checkpoint = {
 "stats": stats,
 "identities": identities_with_seeds,
 }
 checkpoint_file = OUTPUT_DIR / "identities_seeds_checkpoint.json"
 with checkpoint_file.open("w") as f:
 json.dump(checkpoint, f, indent=2)
 
 print(f" Progress: {stats['crypto_validated']}/{stats['seeds_valid']} crypto-validated, {stats['wallet_access']} wallet access")
 print()
 
 # Zusammenfassung
 print("=" * 80)
 print("SUMMARY")
 print("=" * 80)
 print()
 
 print(f"Total identities: {stats['total']}")
 print(f"Seeds extracted: {stats['seeds_extracted']}")
 print(f"Seeds valid: {stats['seeds_valid']}")
 print(f"Crypto validated: {stats['crypto_validated']} ({stats['crypto_validated']/stats['seeds_valid']*100:.1f}%)")
 print(f"Wallet access: {stats['wallet_access']} ({stats['wallet_access']/stats['seeds_valid']*100:.1f}%)")
 print(f"Errors: {stats['errors']}")
 print()
 
 # Speichere finale Ergebnisse
 OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
 
 final_results = {
 "summary": stats,
 "identities": identities_with_seeds,
 }
 
 with OUTPUT_JSON.open("w") as f:
 json.dump(final_results, f, indent=2)
 
 # Erstelle Markdown Report
 with OUTPUT_MD.open("w") as f:
 f.write("# All Identities with Seeds\n\n")
 f.write(f"**Date**: {Path(__file__).stat().st_mtime}\n\n")
 f.write("## Summary\n\n")
 f.write(f"- **Total identities**: {stats['total']}\n")
 f.write(f"- **Seeds extracted**: {stats['seeds_extracted']}\n")
 f.write(f"- **Seeds valid**: {stats['seeds_valid']}\n")
 f.write(f"- **Crypto validated**: {stats['crypto_validated']} ({stats['crypto_validated']/stats['seeds_valid']*100:.1f}%)\n")
 f.write(f"- **Wallet access**: {stats['wallet_access']} ({stats['wallet_access']/stats['seeds_valid']*100:.1f}%)\n")
 f.write(f"- **Errors**: {stats['errors']}\n\n")
 f.write("## Identities with Wallet Access\n\n")
 
 wallet_access_identities = [i for i in identities_with_seeds if i.get("wallet_access")]
 f.write(f"**Total**: {len(wallet_access_identities)}\n\n")
 f.write("| Identity | Seed | Balance | Crypto Valid |\n")
 f.write("|----------|------|---------|--------------|\n")
 
 for identity_data in wallet_access_identities[:100]: # Erste 100
 f.write(f"| {identity_data['identity']} | {identity_data['seed']} | {identity_data['balance']} QU | ✅ |\n")
 
 if len(wallet_access_identities) > 100:
 f.write(f"\n... and {len(wallet_access_identities) - 100} more\n")
 
 print(f"💾 Results saved to: {OUTPUT_JSON}")
 print(f"📄 Report saved to: {OUTPUT_MD}")
 print()
 print("=" * 80)
 print("✅ EXTRACTION COMPLETE")
 print("=" * 80)
 
 return True

if __name__ == "__main__":
 success = main()
 sys.exit(0 if success else 1)

