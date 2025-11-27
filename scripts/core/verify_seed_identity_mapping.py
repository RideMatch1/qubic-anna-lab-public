#!/usr/bin/env python3
"""
Verifiziere Seed-Identity Mapping

WICHTIG: Nur echte, nachgewiesene Erkenntnisse!
"""

import json
from pathlib import Path
from typing import Dict, Optional

OUTPUT_DIR = Path("outputs/derived")
OUTPUT_JSON = OUTPUT_DIR / "seed_identity_mapping_verification.json"
OUTPUT_MD = OUTPUT_DIR / "SEED_IDENTITY_MAPPING_VERIFICATION.md"

from standardized_conversion import identity_to_seed

# Seed vom Benutzer
SEED = "aqiosqqmacybpqxqsjniuaylmxxiwqoxqmeqyxbbtbonsjjrcwpxxdd"

# Identities zum Testen
IDENTITIES = {
 "OBWIIPWFPOWIQCHGJHKFZNMSSYOBYNNDLUEXAELXKEROIUKIXEUXMLZBICUD": "Layer-2 Diagonal #1 (bekannt)",
 "CYTORJWZCJFCYXAHJPLPPCWPVOXTDZBWQYVWANQDYQCCIORJTVMPBIXBKIVP": "Neue Identity vom Benutzer",
 "AQIOSQQMACYBPQXQSJNIUAYLMXXIWQOXQMEQYXBBTBONSJJRCWPXXDDRDWOR": "Layer-1 Diagonal #1 (bekannt)",
}

def derive_seed_from_identity(identity: str) -> Optional[str]:
 """Leite Seed aus Identity ab."""
 try:
 return identity_to_seed(identity)
 except Exception as e:
 return None

def main():
 print("=" * 80)
 print("SEED-IDENTITY MAPPING VERIFICATION")
 print("=" * 80)
 print()
 print("WICHTIG: Nur echte, nachgewiesene Erkenntnisse!")
 print()
 
 print(f"Seed: {SEED}")
 print()
 
 results = []
 
 for identity, label in IDENTITIES.items():
 print(f"{label}:")
 print(f" Identity: {identity}")
 
 derived_seed = derive_seed_from_identity(identity)
 
 if derived_seed:
 print(f" Derived Seed: {derived_seed}")
 matches = (derived_seed == SEED)
 print(f" Matches known seed: {matches}")
 
 results.append({
 "identity": identity,
 "label": label,
 "derived_seed": derived_seed,
 "matches_known_seed": matches,
 })
 else:
 print(f" ❌ Could not derive seed")
 results.append({
 "identity": identity,
 "label": label,
 "derived_seed": None,
 "matches_known_seed": False,
 })
 
 print()
 
 # Zusammenfassung
 print("=" * 80)
 print("SUMMARY")
 print("=" * 80)
 print()
 
 matches = [r for r in results if r.get("matches_known_seed")]
 print(f"Identities matching seed: {len(matches)}/{len(results)}")
 
 if matches:
 print()
 print("✅ MATCHING IDENTITIES:")
 for match in matches:
 print(f" - {match['label']}: {match['identity'][:40]}...")
 
 # Speichere Ergebnisse
 OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
 
 final_results = {
 "seed": SEED,
 "identities_tested": results,
 "conclusion": {
 "matching_identities": len(matches),
 "matches": [m["label"] for m in matches],
 },
 }
 
 with OUTPUT_JSON.open("w") as f:
 json.dump(final_results, f, indent=2)
 
 # Erstelle Markdown Report
 with OUTPUT_MD.open("w") as f:
 f.write("# Seed-Identity Mapping Verification\n\n")
 f.write(f"**Seed**: `{SEED}`\n\n")
 f.write("## Results\n\n")
 
 for result in results:
 f.write(f"### {result['label']}\n\n")
 f.write(f"- Identity: `{result['identity']}`\n")
 if result.get("derived_seed"):
 f.write(f"- Derived Seed: `{result['derived_seed']}`\n")
 f.write(f"- Matches known seed: **{result['matches_known_seed']}**\n")
 else:
 f.write(f"- ❌ Could not derive seed\n")
 f.write("\n")
 
 f.write("## Conclusion\n\n")
 if matches:
 f.write(f"✅ **{len(matches)} identity/identities match the seed:**\n\n")
 for match in matches:
 f.write(f"- {match['label']}: `{match['identity']}`\n")
 else:
 f.write("❌ **No identities match the seed**\n")
 
 print("=" * 80)
 print("✅ VERIFICATION COMPLETE")
 print("=" * 80)
 print()
 print(f"💾 Results saved to: {OUTPUT_JSON}")
 print(f"📄 Report saved to: {OUTPUT_MD}")

if __name__ == "__main__":
 main()

