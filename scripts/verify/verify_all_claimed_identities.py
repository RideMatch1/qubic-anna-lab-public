#!/usr/bin/env python3
"""
Verify All Claimed Identities

Kritische Prüfung: Verifiziere ALLE behaupteten Identitäten on-chain.
Dies will zeigen, wer recht hat: Grok (nur 16) oder unsere Scripts (195+).
"""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Set

try:
 from qubipy.rpc import rpc_client
 HAS_QUBIPY = True
except ImportError:
 HAS_QUBIPY = False
 print("⚠️ QubiPy nicht verfügbar - verwende Docker")

OUTPUT_DIR = Path("outputs/derived")
OUTPUT_JSON = OUTPUT_DIR / "all_identities_rpc_verification.json"

def load_all_claimed_identities() -> Set[str]:
 """Load alle behaupteten Identitäten aus allen Quellen."""
 all_identities = set()
 
 files = [
 ("identity_deep_scan.json", "outputs/derived/identity_deep_scan.json"),
 ("comprehensive_matrix_scan.json", "outputs/derived/comprehensive_matrix_scan.json"),
 ("recursive_layer_map.json", "outputs/derived/recursive_layer_map.json"),
 ]
 
 for name, file_path in files:
 path = Path(file_path)
 if not path.exists():
 continue
 
 try:
 with path.open() as f:
 data = json.load(f)
 
 if isinstance(data, dict):
 # identity_deep_scan.json
 if "records" in data:
 for record in data["records"]:
 identity = record.get("identity")
 if identity:
 all_identities.add(identity)
 
 # comprehensive_matrix_scan.json
 if "all_on_chain_identities" in data:
 all_identities.update(data["all_on_chain_identities"])
 
 # recursive_layer_map.json
 for key in ["known_8_exploration", "new_seeds_exploration"]:
 if key in data:
 exp = data[key]
 if "all_identities" in exp:
 all_identities.update(exp["all_identities"])
 
 except Exception as e:
 print(f"⚠️ Fehler beim Loadn von {name}: {e}")
 
 return all_identities

def check_on_chain(rpc, identity: str) -> tuple[bool, dict]:
 """Check ob Identität on-chain existiert."""
 try:
 time.sleep(0.3) # Rate limiting
 balance_data = rpc.get_balance(identity)
 if balance_data:
 return True, {
 "exists": True,
 "balance": balance_data.get("balance", "0"),
 "valid_for_tick": balance_data.get("validForTick"),
 }
 else:
 return False, {"exists": False}
 except Exception as e:
 return False, {"exists": False, "error": str(e)}

def main() -> None:
 OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
 
 print("=" * 80)
 print("KRITISCHE VERIFIZIERUNG: ALLE BEHAUPTETEN IDENTITÄTEN")
 print("=" * 80)
 print()
 
 if not HAS_QUBIPY:
 print("❌ QubiPy nicht verfügbar")
 print(" Bitte in Docker ausführen: docker run ...")
 return
 
 print("Load alle behaupteten Identitäten...")
 all_identities = load_all_claimed_identities()
 print(f"✅ {len(all_identities)} eindeutige Identitäten gefunden")
 print()
 
 print("Starte RPC-Verifizierung...")
 print("(Dies kann einige Minuten dauern)")
 print()
 
 rpc = rpc_client.QubiPy_RPC()
 
 results = {}
 verified = []
 not_found = []
 errors = []
 
 for i, identity in enumerate(sorted(all_identities), 1):
 if i % 50 == 0:
 print(f" Geprüft: {i}/{len(all_identities)}, Verifiziert: {len(verified)}, Nicht gefunden: {len(not_found)}")
 
 exists, data = check_on_chain(rpc, identity)
 results[identity] = data
 
 if exists:
 verified.append(identity)
 elif "error" in data:
 errors.append(identity)
 else:
 not_found.append(identity)
 
 print()
 print("=" * 80)
 print("ERGEBNISSE")
 print("=" * 80)
 print()
 print(f"✅ On-chain verifiziert: {len(verified)}")
 print(f"❌ Nicht gefunden: {len(not_found)}")
 print(f"⚠️ Fehler: {len(errors)}")
 print()
 
 # Vergleich mit Grok's Behauptung
 print("=" * 80)
 print("VERGLEICH MIT GROK'S BEHAUPTUNG")
 print("=" * 80)
 print()
 print(f"Grok behauptet: 16 Identitäten")
 print(f"Wir haben verifiziert: {len(verified)} Identitäten")
 print()
 
 if len(verified) == 16:
 print("✅ GROK HAT RECHT: Nur 16 Identitäten sind wirklich on-chain")
 elif len(verified) > 16:
 print(f"❌ GROK HAT UNRECHT: {len(verified)} Identitäten sind on-chain")
 print(f" → {len(verified) - 16} zusätzliche Identitäten gefunden!")
 else:
 print(f"⚠️ WENIGER ALS 16: {len(verified)} Identitäten gefunden")
 print(f" → Möglicherweise RPC-Fehler")
 
 # Speichere Ergebnisse
 output = {
 "total_checked": len(all_identities),
 "verified_count": len(verified),
 "not_found_count": len(not_found),
 "error_count": len(errors),
 "verified_identities": verified,
 "not_found_identities": not_found,
 "error_identities": errors,
 "all_results": results,
 }
 
 with OUTPUT_JSON.open("w", encoding="utf-8") as f:
 json.dump(output, f, indent=2)
 
 print()
 print(f"Ergebnisse gespeichert in: {OUTPUT_JSON}")

if __name__ == "__main__":
 main()

