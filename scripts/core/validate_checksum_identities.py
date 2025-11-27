#!/usr/bin/env python3
"""
On-Chain Validierung der Identities mit Checksum.
"""

import json
import subprocess
from pathlib import Path
from typing import List, Dict

OUTPUT_DIR = Path("outputs/derived")
INPUT_FILE = OUTPUT_DIR / "candidates_with_checksums.json"
OUTPUT_FILE = OUTPUT_DIR / "checksum_identities_onchain_validation.json"
VENV_PYTHON = Path(__file__).parent.parent.parent / "venv-tx" / "bin" / "python"

def check_identity_onchain(identity: str) -> Dict:
 """Check ob Identity on-chain existiert."""
 script = f"""
from qubipy.rpc import rpc_client
import sys

identity = "{identity}"
try:
 rpc = rpc_client.QubiPy_RPC()
 balance = rpc.get_balance(identity)
 if balance is not None:
 print(f"EXISTS|{{balance}}")
 else:
 print("NOT_FOUND")
except Exception as e:
 print(f"ERROR|{{str(e)}}")
"""
 
 try:
 result = subprocess.run(
 [str(VENV_PYTHON), "-c", script],
 capture_output=True,
 text=True,
 timeout=10,
 cwd=Path(__file__).parent.parent.parent
 )
 
 if result.returncode != 0:
 return {"exists": False, "error": "RPC call failed"}
 
 output = result.stdout.strip()
 if output.startswith("EXISTS|"):
 balance = output.split("|")[1]
 return {"exists": True, "balance": balance}
 elif output == "NOT_FOUND":
 return {"exists": False}
 elif output.startswith("ERROR|"):
 error = output.split("|")[1]
 return {"exists": False, "error": error}
 else:
 return {"exists": False, "error": "Unknown response"}
 except subprocess.TimeoutExpired:
 return {"exists": False, "error": "Timeout"}
 except Exception as e:
 return {"exists": False, "error": str(e)}

def main():
 """Validate Identities mit Checksum on-chain."""
 
 print("=" * 80)
 print("ON-CHAIN VALIDIERUNG: IDENTITIES MIT CHECKSUM")
 print("=" * 80)
 print()
 
 # Load Identities mit Checksum
 if not INPUT_FILE.exists():
 print(f"❌ Input-Datei nicht gefunden: {INPUT_FILE}")
 return
 
 with INPUT_FILE.open() as f:
 data = json.load(f)
 
 valid_identities = data.get("all_valid_identities", [])
 print(f"Geloadn: {len(valid_identities)} Identities mit Checksum")
 print()
 
 if not VENV_PYTHON.exists():
 print(f"❌ venv-tx Python nicht gefunden: {VENV_PYTHON}")
 return
 
 # Check alle Identities
 results = []
 onchain_count = 0
 
 for i, identity in enumerate(valid_identities, 1):
 if i % 20 == 0:
 print(f" Progress: {i}/{len(valid_identities)}...")
 
 result = check_identity_onchain(identity)
 result["identity"] = identity
 results.append(result)
 
 if result.get("exists"):
 onchain_count += 1
 balance = result.get("balance", "0")
 print(f" ✅ On-chain gefunden: {identity[:40]}... (Balance: {balance})")
 
 print()
 print("=" * 80)
 print("ZUSAMMENFASSUNG")
 print("=" * 80)
 print()
 print(f"Geprüft: {len(results)} Identities")
 print(f"On-chain gefunden: {onchain_count}")
 print(f"Rate: {onchain_count/len(results)*100:.2f}%")
 print()
 
 # Speichere Ergebnisse
 output_data = {
 "summary": {
 "total_checked": len(results),
 "onchain_found": onchain_count,
 "onchain_rate": onchain_count/len(results)*100 if results else 0,
 },
 "onchain_identities": [r["identity"] for r in results if r.get("exists")],
 "results": results,
 }
 
 OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
 with OUTPUT_FILE.open("w") as f:
 json.dump(output_data, f, indent=2)
 
 print(f"💾 Ergebnisse gespeichert in: {OUTPUT_FILE}")
 
 if onchain_count > 0:
 print()
 print(f"🎉 {onchain_count} neue Identities on-chain gefunden!")
 print(" Diese könnten weitere Layer-1 Einstiegspunkte sein!")

if __name__ == "__main__":
 main()

