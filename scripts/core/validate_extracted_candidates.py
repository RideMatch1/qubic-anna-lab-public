#!/usr/bin/env python3
"""
On-Chain Validierung der extrahierten Kandidaten.

Prüft eine Stichprobe der extrahierten Kandidaten on-chain.
"""

import json
import sys
import subprocess
from pathlib import Path
from typing import List, Dict

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

VENV_PYTHON = project_root / "venv-tx" / "bin" / "python"

OUTPUT_DIR = Path("outputs/derived")
INPUT_FILE = OUTPUT_DIR / "systematic_matrix_extraction.json"
OUTPUT_FILE = OUTPUT_DIR / "extracted_candidates_onchain_validation.json"

def check_identity_onchain(identity_body: str) -> Dict:
 """Check ob Identity on-chain existiert."""
 # Verwende venv-tx Python for qubipy
 script = f"""
from qubipy.rpc import rpc_client
import sys

identity = "{identity_body}"
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
 cwd=project_root
 )
 
 if result.returncode != 0:
 return {"exists": False, "error": "RPC call failed"}
 
 output = result.stdout.strip()
 if output.startswith("EXISTS|"):
 balance = output.split("|")[1]
 return {
 "exists": True,
 "balance": balance,
 }
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
 """Validate extrahierte Kandidaten on-chain."""
 
 print("=" * 80)
 print("ON-CHAIN VALIDIERUNG DER EXTRAHIERTEN KANDIDATEN")
 print("=" * 80)
 print()
 
 # Load Kandidaten
 if not INPUT_FILE.exists():
 print(f"❌ Input-Datei nicht gefunden: {INPUT_FILE}")
 return
 
 with INPUT_FILE.open() as f:
 data = json.load(f)
 
 all_candidates = data.get("all_candidates", [])
 print(f"Geloadn: {len(all_candidates)} Kandidaten")
 print()
 
 # Für jetzt: Check nur eine Stichprobe (erste 100)
 # TODO: Später alle checkn mit Checkpoint-System
 sample_size = min(100, len(all_candidates))
 sample = all_candidates[:sample_size]
 
 print(f"Check Stichprobe: {sample_size} Kandidaten")
 print()
 
 # Check venv-tx Python
 if not VENV_PYTHON.exists():
 print(f"❌ venv-tx Python nicht gefunden: {VENV_PYTHON}")
 print(" Bitte venv-tx erstellen oder qubipy installieren.")
 return
 
 # Check Kandidaten
 results = []
 onchain_count = 0
 
 for i, candidate in enumerate(sample, 1):
 if i % 10 == 0:
 print(f" Progress: {i}/{sample_size}...")
 
 result = check_identity_onchain(candidate)
 result["candidate"] = candidate
 results.append(result)
 
 if result.get("exists"):
 onchain_count += 1
 balance = result.get("balance", "0")
 print(f" ✅ On-chain gefunden: {candidate[:40]}... (Balance: {balance})")
 
 print()
 print("=" * 80)
 print("ZUSAMMENFASSUNG")
 print("=" * 80)
 print()
 print(f"Geprüft: {len(results)} Kandidaten")
 print(f"On-chain gefunden: {onchain_count}")
 print(f"Rate: {onchain_count/len(results)*100:.2f}%")
 print()
 
 # Speichere Ergebnisse
 output_data = {
 "summary": {
 "total_candidates": len(all_candidates),
 "sample_size": sample_size,
 "checked": len(results),
 "onchain_found": onchain_count,
 "onchain_rate": onchain_count/len(results)*100 if results else 0,
 },
 "results": results,
 }
 
 OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
 with OUTPUT_FILE.open("w") as f:
 json.dump(output_data, f, indent=2)
 
 print(f"💾 Ergebnisse gespeichert in: {OUTPUT_FILE}")
 print()
 print("⚠️ HINWEIS: Diese Validierung prüft nur Balance-Abfragen.")
 print(" Für vollständige Validierung müsste Checksum berechnet werden.")

if __name__ == "__main__":
 main()

