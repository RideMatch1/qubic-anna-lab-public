#!/usr/bin/env python3
"""
Optimierte Batch On-Chain Validierung mit Checkpoint-System.

Features:
- Batch-Processing for Performance
- Checkpoint-System for Unterbrechungen
- Rate-Limiting for RPC-Calls
- Progress-Tracking
"""

import json
import subprocess
import time
from pathlib import Path
from typing import List, Dict, Optional

OUTPUT_DIR = Path("outputs/derived")
CHECKPOINT_FILE = OUTPUT_DIR / "onchain_validation_checkpoint.json"
OUTPUT_FILE = OUTPUT_DIR / "checksum_identities_onchain_validation_complete.json"
VENV_PYTHON = Path(__file__).parent.parent.parent / "venv-tx" / "bin" / "python"
BATCH_SIZE = 1000 # Verarbeite 1000 pro Batch
CHECKPOINT_INTERVAL = 100 # Speichere Checkpoint alle 100 Identities
RPC_DELAY = 0.1 # 0.1 Sekunden zwischen RPC-Calls (Rate-Limiting)

def check_identity_onchain(identity: str) -> Dict:
 """Check ob Identity on-chain existiert."""
 script = f"""
from qubipy.rpc import rpc_client
identity = "{identity}"
try:
 rpc = rpc_client.QubiPy_RPC()
 balance = rpc.get_balance(identity)
 if balance is not None:
 balance_str = str(balance.get('balance', '0')) if isinstance(balance, dict) else str(balance)
 print(f"EXISTS|{{balance_str}}")
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

def load_identities() -> List[str]:
 """Load alle Identities mit Checksum."""
 identities = []
 
 # Quelle 1: candidates_with_checksums_complete.json
 complete_file = OUTPUT_DIR / "candidates_with_checksums_complete.json"
 if complete_file.exists():
 with complete_file.open() as f:
 data = json.load(f)
 
 # Check ob Batch-Speicherung
 if "total_batches" in data:
 num_batches = data["total_batches"]
 print(f" Load {num_batches} Batches...")
 for i in range(num_batches):
 batch_file = OUTPUT_DIR / f"checksum_identities_batch_{i}.json"
 if batch_file.exists():
 with batch_file.open() as f:
 batch = json.load(f)
 # Batch enthält Dicts mit "identity_60"
 for item in batch:
 if isinstance(item, dict):
 identities.append(item.get("identity_60", ""))
 else:
 identities.append(item)
 print(f" Batch {i+1}/{num_batches}: {len(batch):,} Identities")
 else:
 # Normale Speicherung
 results = data.get("results", [])
 for item in results:
 if isinstance(item, dict):
 identities.append(item.get("identity_60", ""))
 else:
 identities.append(item)
 print(f" Normale Speicherung: {len(results):,} Identities")
 
 # Filtere leere Strings
 identities = [id for id in identities if id and len(id) == 60]
 
 return identities

def load_checkpoint() -> Dict:
 """Load Checkpoint falls vorhanden."""
 if CHECKPOINT_FILE.exists():
 try:
 with CHECKPOINT_FILE.open() as f:
 return json.load(f)
 except Exception as e:
 print(f"⚠️ Checkpoint konnte nicht geloadn werden: {e}")
 return {
 "processed": 0,
 "onchain_identities": [],
 "results": [],
 "last_processed_index": -1,
 }

def save_checkpoint(checkpoint: Dict):
 """Speichere Checkpoint."""
 OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
 with CHECKPOINT_FILE.open("w") as f:
 json.dump(checkpoint, f, indent=2)

def main():
 """Optimierte Batch On-Chain Validierung."""
 
 print("=" * 80)
 print("OPTIMIERTE BATCH ON-CHAIN VALIDIERUNG")
 print("=" * 80)
 print()
 
 # Load Identities
 print("Load Identities mit Checksum...")
 all_identities = load_identities()
 print(f"✅ {len(all_identities):,} Identities geloadn")
 print()
 
 if not all_identities:
 print("❌ Keine Identities gefunden!")
 return
 
 # Load Checkpoint
 checkpoint = load_checkpoint()
 if checkpoint.get("processed", 0) > 0:
 print(f"✅ Checkpoint geloadn: {checkpoint['processed']:,} bereits verarbeitet")
 print(f" On-chain gefunden: {len(checkpoint.get('onchain_identities', [])):,}")
 print(f" Fortsetzung ab Index: {checkpoint['last_processed_index'] + 1}")
 print()
 
 # Initialisiere Checkpoint
 if not checkpoint.get("onchain_identities"):
 checkpoint["onchain_identities"] = []
 checkpoint["results"] = []
 
 onchain_identities = checkpoint["onchain_identities"]
 results = checkpoint["results"]
 start_index = checkpoint.get("last_processed_index", -1) + 1
 
 # Check venv-tx Python
 if not VENV_PYTHON.exists():
 print(f"❌ venv-tx Python nicht gefunden: {VENV_PYTHON}")
 return
 
 # Verarbeite Identities
 print(f"Check {len(all_identities):,} Identities on-chain...")
 print(f"Starte ab Index: {start_index}")
 print(f"Rate-Limiting: {1/RPC_DELAY:.1f} RPC-Calls/Sekunde")
 print()
 
 total = len(all_identities)
 start_time = time.time()
 
 for i, identity in enumerate(all_identities[start_index:], start_index):
 if i % CHECKPOINT_INTERVAL == 0 and i > start_index:
 elapsed = time.time() - start_time
 rate = (i - start_index) / elapsed if elapsed > 0 else 0
 remaining = (total - i) / rate if rate > 0 else 0
 onchain_rate = len(onchain_identities) / (i - start_index + 1) * 100 if (i - start_index + 1) > 0 else 0
 print(f" Progress: {i:,}/{total:,} ({i/total*100:.1f}%) | "
 f"Rate: {rate:.1f}/s | On-chain: {len(onchain_identities):,} ({onchain_rate:.1f}%) | "
 f"ETA: {remaining/60:.1f} min")
 
 # Speichere Checkpoint
 checkpoint["processed"] = i + 1
 checkpoint["last_processed_index"] = i
 checkpoint["onchain_identities"] = onchain_identities
 checkpoint["results"] = results
 save_checkpoint(checkpoint)
 
 # Rate-Limiting
 if i > start_index:
 time.sleep(RPC_DELAY)
 
 result = check_identity_onchain(identity)
 result["identity"] = identity
 results.append(result)
 
 if result.get("exists"):
 onchain_identities.append(identity)
 if len(onchain_identities) % 100 == 0:
 print(f" ✅ On-chain gefunden: {identity[:40]}... (Total: {len(onchain_identities):,})")
 
 print()
 print("=" * 80)
 print("ZUSAMMENFASSUNG")
 print("=" * 80)
 print()
 
 print(f"Geprüft: {len(results):,} Identities")
 print(f"On-chain gefunden: {len(onchain_identities):,}")
 print(f"Erfolgsrate: {len(onchain_identities)/len(results)*100:.2f}%")
 print()
 
 # Speichere finale Ergebnisse
 print("Speichere finale Ergebnisse...")
 
 # Batch-Speicherung falls nötig
 if len(onchain_identities) > BATCH_SIZE:
 print(f" Datei will groß ({len(onchain_identities):,} Identities)")
 print(f" Verwende Batch-Speicherung (Batch-Size: {BATCH_SIZE:,})...")
 
 num_batches = (len(onchain_identities) + BATCH_SIZE - 1) // BATCH_SIZE
 for i in range(num_batches):
 batch = onchain_identities[i * BATCH_SIZE:(i + 1) * BATCH_SIZE]
 batch_file = OUTPUT_DIR / f"onchain_identities_batch_{i}.json"
 with batch_file.open("w") as f:
 json.dump(batch, f, indent=2)
 print(f" Batch {i+1}/{num_batches} gespeichert: {len(batch):,} Identities")
 
 # Speichere Summary
 summary_data = {
 "summary": {
 "total_checked": len(results),
 "onchain_found": len(onchain_identities),
 "onchain_rate": len(onchain_identities)/len(results)*100 if results else 0,
 },
 "total_batches": num_batches,
 "batch_size": BATCH_SIZE,
 }
 with OUTPUT_FILE.open("w") as f:
 json.dump(summary_data, f, indent=2)
 else:
 # Normale Speicherung
 output_data = {
 "summary": {
 "total_checked": len(results),
 "onchain_found": len(onchain_identities),
 "onchain_rate": len(onchain_identities)/len(results)*100 if results else 0,
 },
 "onchain_identities": onchain_identities,
 "results": results[:1000], # Nur erste 1000 for JSON
 }
 with OUTPUT_FILE.open("w") as f:
 json.dump(output_data, f, indent=2)
 
 print(f"💾 Ergebnisse gespeichert in: {OUTPUT_FILE}")
 
 # Lösche Checkpoint (Validierung komplett)
 if CHECKPOINT_FILE.exists():
 CHECKPOINT_FILE.unlink()
 print("✅ Checkpoint gelöscht (Validierung komplett)")
 
 print()
 print(f"🎉 {len(onchain_identities):,} Identities on-chain gefunden!")
 print(" Nächster Schritt: Identities-Analyse!")

if __name__ == "__main__":
 main()

