#!/usr/bin/env python3
"""
Leite Layer-2 Identities for die 180 Comprehensive Scan Identities ab.

Prüft:
- Seed-Extraktion (identity.lower()[:55])
- Layer-2 Ableitung
- On-Chain Status der Layer-2 Identities
"""

import json
import subprocess
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime

OUTPUT_DIR = Path(__file__).parent.parent.parent / "outputs" / "derived"
SCAN_FILE = OUTPUT_DIR / "additional_identities_from_comprehensive_scan.json"
OUTPUT_FILE = OUTPUT_DIR / "comprehensive_scan_layer2_derivation.json"
REPORT_FILE = OUTPUT_DIR / "comprehensive_scan_layer2_derivation_report.md"
CHECKPOINT_FILE = OUTPUT_DIR / "comprehensive_scan_layer2_checkpoint.json"
VENV_PYTHON = Path(__file__).parent.parent.parent / "venv-tx" / "bin" / "python"

def identity_to_seed(identity: str) -> str:
 """Konvertiere Identity zu Seed."""
 return identity.lower()[:55]

def derive_identity_from_seed(seed: str) -> Optional[str]:
 """Leite Identity aus Seed ab."""
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

def check_identity_onchain(identity: str) -> Dict:
 """Check ob Identity on-chain existiert."""
 script = f"""
from qubipy.rpc import rpc_client
identity = "{identity}"
try:
 rpc = rpc_client.QubiPy_RPC()
 balance_data = rpc.get_balance(identity)
 if balance_data:
 print(f"EXISTS|{{balance_data.get('balance', '0')}}|{{balance_data.get('validForTick', 'N/A')}}")
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
 
 if "EXISTS" in result.stdout:
 parts = result.stdout.strip().split("|")
 return {
 "exists": True,
 "balance": parts[1] if len(parts) > 1 else "0",
 "validForTick": parts[2] if len(parts) > 2 else "N/A",
 }
 elif "NOT_FOUND" in result.stdout:
 return {"exists": False}
 else:
 return {"exists": False, "error": result.stdout.strip()}
 except Exception as e:
 return {"exists": False, "error": str(e)}

def load_checkpoint() -> Dict:
 """Load Checkpoint."""
 if CHECKPOINT_FILE.exists():
 try:
 with CHECKPOINT_FILE.open() as f:
 return json.load(f)
 except Exception:
 pass
 return {
 "processed": 0,
 "results": [],
 "last_processed_index": -1,
 }

def save_checkpoint(checkpoint: Dict):
 """Speichere Checkpoint."""
 OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
 with CHECKPOINT_FILE.open("w") as f:
 json.dump(checkpoint, f, indent=2)

def main():
 """Leite Layer-2 Identities ab."""
 
 print("=" * 80)
 print("LAYER-2 ABLEITUNG: COMPREHENSIVE SCAN IDENTITIES")
 print("=" * 80)
 print()
 
 if not SCAN_FILE.exists():
 print(f"❌ Datei nicht gefunden: {SCAN_FILE}")
 return
 
 if not VENV_PYTHON.exists():
 print(f"❌ venv-tx Python nicht gefunden: {VENV_PYTHON}")
 return
 
 # Load Identities
 print("Load Comprehensive Scan Identities...")
 with SCAN_FILE.open() as f:
 data = json.load(f)
 
 identities = data.get("identities", [])
 print(f"✅ {len(identities)} Identities geloadn")
 print()
 
 if not identities:
 print("❌ Keine Identities gefunden!")
 return
 
 # Load Checkpoint
 checkpoint = load_checkpoint()
 if checkpoint.get("processed", 0) > 0:
 print(f"✅ Checkpoint geloadn: {checkpoint['processed']:,} bereits verarbeitet")
 print()
 
 results = checkpoint.get("results", [])
 start_index = checkpoint.get("last_processed_index", -1) + 1
 
 # Verarbeite Identities
 print(f"Verarbeite {len(identities):,} Identities...")
 print(f"Starte ab Index: {start_index}")
 print()
 
 total = len(identities)
 
 for i, identity in enumerate(identities[start_index:], start_index):
 if i % 10 == 0:
 print(f" Progress: {i+1:,}/{total:,} ({(i+1)/total*100:.1f}%)")
 
 # Extrahiere Seed
 seed = identity_to_seed(identity)
 
 # Layer-2 Ableitung
 layer2_identity = derive_identity_from_seed(seed)
 
 # On-Chain Check
 layer2_onchain = False
 layer2_balance = "0"
 layer2_tick = "N/A"
 
 if layer2_identity:
 onchain_result = check_identity_onchain(layer2_identity)
 layer2_onchain = onchain_result.get("exists", False)
 if layer2_onchain:
 layer2_balance = onchain_result.get("balance", "0")
 layer2_tick = onchain_result.get("validForTick", "N/A")
 
 result = {
 "layer1_identity": identity,
 "seed": seed,
 "layer2_identity": layer2_identity,
 "layer2_onchain": layer2_onchain,
 "layer2_balance": layer2_balance,
 "layer2_tick": layer2_tick,
 }
 
 results.append(result)
 
 # Checkpoint alle 20 Identities
 if (i + 1) % 20 == 0:
 checkpoint["processed"] = i + 1
 checkpoint["last_processed_index"] = i
 checkpoint["results"] = results
 save_checkpoint(checkpoint)
 
 print()
 print("=" * 80)
 print("ZUSAMMENFASSUNG")
 print("=" * 80)
 print()
 
 total_processed = len(results)
 seeds_found = sum(1 for r in results if r.get("seed"))
 layer2_derivable = sum(1 for r in results if r.get("layer2_identity"))
 layer2_onchain = sum(1 for r in results if r.get("layer2_onchain"))
 
 print(f"Total verarbeitet: {total_processed:,}")
 print(f"Seeds extrahiert: {seeds_found:,} ({seeds_found/total_processed*100:.1f}%)")
 print(f"Layer-2 ableitbar: {layer2_derivable:,} ({layer2_derivable/total_processed*100:.1f}%)")
 print(f"Layer-2 on-chain: {layer2_onchain:,} ({layer2_onchain/layer2_derivable*100:.1f}% von ableitbaren)" if layer2_derivable > 0 else "Layer-2 on-chain: 0")
 print()
 
 # Speichere Ergebnisse
 output_data = {
 "timestamp": datetime.utcnow().isoformat() + "Z",
 "summary": {
 "total_processed": total_processed,
 "seeds_found": seeds_found,
 "layer2_derivable": layer2_derivable,
 "layer2_onchain": layer2_onchain,
 },
 "results": results,
 }
 
 OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
 with OUTPUT_FILE.open("w") as f:
 json.dump(output_data, f, indent=2)
 
 print(f"💾 Ergebnisse gespeichert in: {OUTPUT_FILE}")
 
 # Erstelle Report
 report_content = f"""# Layer-2 Ableitung: Comprehensive Scan Identities

**Datum**: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} 
**Total verarbeitet**: {total_processed}

## Zusammenfassung

- **Total Identities**: {total_processed}
- **Seeds extrahiert**: {seeds_found} ({seeds_found/total_processed*100:.1f}%)
- **Layer-2 ableitbar**: {layer2_derivable} ({layer2_derivable/total_processed*100:.1f}%)
- **Layer-2 on-chain**: {layer2_onchain} ({layer2_onchain/layer2_derivable*100:.1f}% von ableitbaren)

## Erkenntnisse

"""
 
 if layer2_onchain == layer2_derivable and layer2_derivable == total_processed:
 report_content += "✅ **PERFEKT**: Alle Comprehensive Scan Identities funktionieren als Seeds!\n"
 report_content += "✅ **PERFEKT**: Alle Layer-2 Identities existieren on-chain!\n"
 report_content += "\nDas bedeutet: Die Comprehensive Scan Identities folgen dem gleichen Pattern wie die systematischen Identities.\n"
 elif layer2_onchain > 0:
 report_content += f"⚠️ **TEILWEISE**: {layer2_onchain}/{layer2_derivable} Layer-2 Identities existieren on-chain.\n"
 report_content += "\nDas bedeutet: Nicht alle Comprehensive Scan Identities funktionieren als Seeds.\n"
 else:
 report_content += "❌ **KEINE**: Keine Layer-2 Identities existieren on-chain.\n"
 report_content += "\nDas bedeutet: Die Comprehensive Scan Identities funktionieren NICHT als Seeds.\n"
 
 report_content += "\n## Nächste Schritte\n\n"
 report_content += "- Vergleich mit systematischen Identities\n"
 report_content += "- Pattern-Analyse der Seeds\n"
 report_content += "- Layer-3 Ableitung (falls Layer-2 erfolgreich)\n"
 
 with REPORT_FILE.open("w") as f:
 f.write(report_content)
 
 print(f"📄 Report erstellt: {REPORT_FILE}")
 
 # Lösche Checkpoint wenn komplett
 if total_processed == len(identities):
 if CHECKPOINT_FILE.exists():
 CHECKPOINT_FILE.unlink()
 print("✅ Checkpoint gelöscht (Analyse komplett)")
 
 print()
 print("✅ Analyse abgeschlossen!")

if __name__ == "__main__":
 main()

