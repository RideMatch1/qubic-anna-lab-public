#!/usr/bin/env python3
"""
Teste ob Seed als Private Key for verschiedene Identities funktioniert

WICHTIG: Nur echte, nachgewiesene Erkenntnisse!
"""

import json
import sys
from pathlib import Path
from typing import Dict, Optional

OUTPUT_DIR = Path("outputs/derived")
OUTPUT_JSON = OUTPUT_DIR / "seed_as_private_key_test.json"
OUTPUT_MD = OUTPUT_DIR / "SEED_AS_PRIVATE_KEY_TEST.md"

# Seed vom Benutzer
SEED = "aqiosqqmacybpqxqsjniuaylmxxiwqoxqmeqyxbbtbonsjjrcwpxxdd"

# Identities zum Testen
IDENTITIES = {
 "OBWIIPWFPOWIQCHGJHKFZNMSSYOBYNNDLUEXAELXKEROIUKIXEUXMLZBICUD": "Layer-2 Diagonal #1",
 "CYTORJWZCJFCYXAHJPLPPCWPVOXTDZBWQYVWANQDYQCCIORJTVMPBIXBKIVP": "Neue Identity vom Benutzer",
 "AQIOSQQMACYBPQXQSJNIUAYLMXXIWQOXQMEQYXBBTBONSJJRCWPXXDDRDWOR": "Layer-1 Diagonal #1",
}

def derive_identity_from_seed(seed: str) -> Optional[str]:
 """
 Derive identity from seed using native crypto functions.
 
 Returns: Identity oder None bei Fehler
 """
 try:
 sys.path.insert(0, "venv-tx/lib/python3.11/site-packages")
 from qubipy.crypto.utils import (
 get_subseed_from_seed,
 get_private_key_from_subseed,
 get_public_key_from_private_key,
 get_identity_from_public_key,
 )
 
 seed_bytes = seed.encode('utf-8')
 subseed = get_subseed_from_seed(seed_bytes)
 private_key = get_private_key_from_subseed(subseed)
 public_key = get_public_key_from_private_key(private_key)
 identity = get_identity_from_public_key(public_key)
 return identity
 except Exception as e:
 return None

def main():
 print("=" * 80)
 print("SEED AS PRIVATE KEY TEST")
 print("=" * 80)
 print()
 print("WICHTIG: Nur echte, nachgewiesene Erkenntnisse!")
 print()
 
 print(f"Seed: {SEED}")
 print()
 
 # Leite Identity aus Seed ab (mit crypto functions)
 print("=" * 80)
 print("DERIVING IDENTITY FROM SEED (CRYPTO FUNCTIONS)")
 print("=" * 80)
 print()
 
 derived_identity = derive_identity_from_seed(SEED)
 
 if derived_identity:
 print(f"✅ Derived Identity: {derived_identity}")
 else:
 print("❌ Could not derive identity from seed (crypto.so problem)")
 
 print()
 
 # Teste gegen alle Identities
 print("=" * 80)
 print("TESTING AGAINST TARGET IDENTITIES")
 print("=" * 80)
 print()
 
 results = []
 
 for identity, label in IDENTITIES.items():
 print(f"{label}:")
 print(f" Target Identity: {identity}")
 
 if derived_identity:
 matches = (derived_identity == identity)
 print(f" Derived Identity: {derived_identity}")
 print(f" Matches: {matches}")
 
 results.append({
 "identity": identity,
 "label": label,
 "derived_identity": derived_identity,
 "matches": matches,
 })
 else:
 print(f" ⚠️ Could not test (crypto.so problem)")
 results.append({
 "identity": identity,
 "label": label,
 "derived_identity": None,
 "matches": False,
 "error": "crypto.so problem",
 })
 
 print()
 
 # Zusammenfassung
 print("=" * 80)
 print("SUMMARY")
 print("=" * 80)
 print()
 
 if derived_identity:
 matches = [r for r in results if r.get("matches")]
 print(f"Identities matching derived identity: {len(matches)}/{len(results)}")
 
 if matches:
 print()
 print("✅ MATCHING IDENTITIES:")
 for match in matches:
 print(f" - {match['label']}: {match['identity'][:40]}...")
 else:
 print()
 print("❌ NO MATCHING IDENTITIES")
 print(f" Derived identity: {derived_identity}")
 else:
 print("❌ Could not derive identity from seed")
 print(" This is likely due to the crypto.so problem in Docker")
 
 # Speichere Ergebnisse
 OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
 
 final_results = {
 "seed": SEED,
 "derived_identity": derived_identity,
 "tests": results,
 "conclusion": {
 "seed_is_private_key_for": [r["label"] for r in results if r.get("matches")],
 },
 }
 
 with OUTPUT_JSON.open("w") as f:
 json.dump(final_results, f, indent=2)
 
 # Erstelle Markdown Report
 with OUTPUT_MD.open("w") as f:
 f.write("# Seed as Private Key Test\n\n")
 f.write(f"**Seed**: `{SEED}`\n\n")
 
 if derived_identity:
 f.write(f"**Derived Identity (from seed via crypto functions)**: `{derived_identity}`\n\n")
 else:
 f.write("❌ **Could not derive identity from seed (crypto.so problem)**\n\n")
 
 f.write("## Test Results\n\n")
 
 for result in results:
 f.write(f"### {result['label']}\n\n")
 f.write(f"- Target Identity: `{result['identity']}`\n")
 if result.get("derived_identity"):
 f.write(f"- Derived Identity: `{result['derived_identity']}`\n")
 f.write(f"- Matches: **{result['matches']}**\n")
 else:
 f.write(f"- ❌ Could not test: {result.get('error', 'Unknown error')}\n")
 f.write("\n")
 
 f.write("## Conclusion\n\n")
 if derived_identity:
 matches = [r for r in results if r.get("matches")]
 if matches:
 f.write(f"✅ **Seed is Private Key for {len(matches)} identity/identities:**\n\n")
 for match in matches:
 f.write(f"- {match['label']}: `{match['identity']}`\n")
 else:
 f.write("❌ **Seed is NOT Private Key for any of the tested identities**\n\n")
 f.write(f"Derived identity: `{derived_identity}`\n")
 else:
 f.write("❌ **Could not test (crypto.so problem)**\n")
 
 print("=" * 80)
 print("✅ TEST COMPLETE")
 print("=" * 80)
 print()
 print(f"💾 Results saved to: {OUTPUT_JSON}")
 print(f"📄 Report saved to: {OUTPUT_MD}")

if __name__ == "__main__":
 main()

