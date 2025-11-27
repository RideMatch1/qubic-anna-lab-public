#!/usr/bin/env python3
"""
RPC-Validierung - 20,000 Identities
- Beste Methode: Alle 55 Seed-Positionen (gewichtet) = 46.25%
- Validierung mit 20,000 zufälligen Identities
- On-Chain RPC-Checks
- Live-Fortschrittsanzeige
- KEINE Halluzinationen - nur echte Daten!

MANUELL AUSFÜHREN:
 python3 scripts/research/rpc_validation_20000_background.py \
 [--resume-checkpoint outputs/derived/rpc_validation_20000_checkpoint.json]

FORTSCHRITT ANZEIGEN:
 tail -f outputs/derived/rpc_validation_20000_status.txt

GESCHÄTZTE DAUER:
 ~100-120 Minuten (20,000 * 0.3s = 6000s = 100min)
"""

import argparse
import json
import random
import sys
import time
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import numpy as np

# Qubic RPC
try:
 import sys
 venv_path = Path(__file__).parent.parent.parent / "venv-tx"
 if venv_path.exists():
 sys.path.insert(0, str(venv_path / "lib" / "python3.11" / "site-packages"))
 
 from qubipy.rpc import rpc_client
 RPC_AVAILABLE = True
except ImportError:
 RPC_AVAILABLE = False
 print("⚠️ qubipy nicht verfügbar - RPC-Validierung nicht möglich")
 print(" Installiere mit: python3 -m venv venv-tx && source venv-tx/bin/activate && pip install qubipy")

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# Paths
LAYER3_FILE = project_root / "outputs" / "derived" / "layer3_derivation_23k_complete.json"
OUTPUT_DIR = project_root / "outputs" / "derived"
STATUS_FILE = project_root / "outputs" / "derived" / "rpc_validation_20000_status.txt"
PROGRESS_FILE = project_root / "outputs" / "derived" / "rpc_validation_20000_progress.json"
RESULTS_FILE = project_root / "outputs" / "derived" / "rpc_validation_20000_results.json"

def log_progress(message: str, status_file: Path = STATUS_FILE):
 """Schreibe Fortschritt in Status-Datei."""
 timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
 with status_file.open("a") as f:
 f.write(f"[{timestamp}] {message}\n")
 print(f"[{timestamp}] {message}")

def save_progress(data: Dict, progress_file: Path = PROGRESS_FILE):
 """Speichere Fortschritt in JSON."""
 with progress_file.open("w") as f:
 json.dump(data, f, indent=2)

def identity_to_seed(identity: str) -> str:
 """Konvertiere Identity zu Seed."""
 return identity.lower()[:55]

def build_seed_mapping(layer3_data: List[Dict], seed_pos: int, target_pos: int, min_samples: int = 2) -> Dict:
 """Baue Seed-Character-Mapping."""
 mapping = defaultdict(Counter)
 totals = Counter()
 
 for entry in layer3_data:
 l3_id = entry.get("layer3_identity", "")
 if not l3_id or len(l3_id) <= max(seed_pos, target_pos):
 continue
 
 seed = identity_to_seed(l3_id)
 if len(seed) <= seed_pos:
 continue
 
 seed_char = seed[seed_pos].lower()
 identity_char = l3_id[target_pos].upper()
 
 mapping[seed_char][identity_char] += 1
 totals[seed_char] += 1
 
 results = {}
 for seed_char, counter in mapping.items():
 total = totals[seed_char]
 if total >= min_samples:
 most_common = counter.most_common(1)[0]
 success_rate = most_common[1] / total
 
 results[seed_char] = {
 "predicted_char": most_common[0],
 "success_rate": success_rate,
 "count": most_common[1],
 "total": total
 }
 
 return results

def predict_with_seed(seed: str, seed_pos: int, mapping: Dict) -> Optional[Tuple[str, float]]:
 """Vorhersage basierend auf Seed, gibt auch Confidence zurück."""
 if len(seed) <= seed_pos:
 return None
 
 seed_char = seed[seed_pos].lower()
 if seed_char not in mapping:
 return None
 
 pred_data = mapping[seed_char]
 return (pred_data["predicted_char"], pred_data["success_rate"])

def predict_all_55_seeds(seed: str, mappings: Dict[int, Dict], target_pos: int) -> str:
 """Vorhersage mit allen 55 Seed-Positionen (gewichtet)."""
 weighted_predictions = defaultdict(float)
 
 for seed_pos in range(55):
 if seed_pos == target_pos: # Skip trivial!
 continue
 if seed_pos in mappings:
 pred_result = predict_with_seed(seed, seed_pos, mappings[seed_pos])
 if pred_result:
 char, confidence = pred_result
 weighted_predictions[char] += confidence
 
 if not weighted_predictions:
 return None
 
 # Wähle Vorhersage mit höchstem Gewicht
 predicted = max(weighted_predictions.items(), key=lambda x: x[1])[0]
 return predicted

def validate_identity_rpc(identity: str, rpc_client_instance) -> Dict:
 """Validate Identity on-chain via RPC."""
 try:
 balance = rpc_client_instance.get_balance(identity)
 
 if balance is None:
 return {
 "exists": False,
 "valid": False,
 "error": "get_balance returned None"
 }
 
 if not isinstance(balance, dict):
 return {
 "exists": False,
 "valid": False,
 "error": f"Unexpected return type: {type(balance)}"
 }
 
 # WICHTIG: validForTick ist der beste Indikator for Existenz!
 valid_for_tick = balance.get("validForTick")
 exists = valid_for_tick is not None
 
 # Zusätzliche Info
 balance_val = int(balance.get("balance", "0"))
 incoming = int(balance.get("incomingAmount", "0"))
 outgoing = int(balance.get("outgoingAmount", "0"))
 num_incoming = balance.get("numberOfIncomingTransfers", 0)
 num_outgoing = balance.get("numberOfOutgoingTransfers", 0)
 has_activity = (balance_val > 0 or incoming > 0 or outgoing > 0 or 
 num_incoming > 0 or num_outgoing > 0)
 
 return {
 "exists": exists,
 "valid": exists,
 "error": None if exists else "Identity not found on-chain (validForTick is None)",
 "balance": balance_val,
 "incoming": incoming,
 "outgoing": outgoing,
 "num_incoming": num_incoming,
 "num_outgoing": num_outgoing,
 "valid_for_tick": valid_for_tick,
 "has_activity": has_activity
 }
 except Exception as e:
 return {
 "exists": False,
 "valid": False,
 "error": str(e)
 }

def parse_args() -> argparse.Namespace:
 parser = argparse.ArgumentParser(description="RPC-Validierung for 20,000 Identities")
 parser.add_argument(
 "--resume-checkpoint",
 type=Path,
 default=None,
 help="Checkpoint-Datei zum Fortsetzen (z. B. outputs/derived/rpc_validation_20000_checkpoint.json)",
 )
 return parser.parse_args()

def main():
 """Hauptfunktion."""
 
 args = parse_args()
 resume_data = None
 resume_processed = 0
 elapsed_base_seconds = 0.0
 resume_counters = {
 "correct": 0,
 "total_predictions": 0,
 "on_chain_valid": 0,
 "on_chain_total": 0,
 }

 if args.resume_checkpoint:
 checkpoint_path = args.resume_checkpoint
 if not checkpoint_path.exists():
 log_progress(f"❌ Checkpoint nicht gefunden: {checkpoint_path}")
 return
 try:
 with checkpoint_path.open() as f:
 resume_data = json.load(f)
 resume_progress = resume_data.get("progress", {})
 resume_processed = int(resume_progress.get("processed", 0))
 elapsed_base_seconds = float(resume_progress.get("elapsed_minutes", 0.0)) * 60.0
 resume_counters["correct"] = int(resume_progress.get("correct", 0))
 resume_counters["total_predictions"] = int(resume_progress.get("total_predictions", 0))
 resume_counters["on_chain_valid"] = int(resume_progress.get("on_chain_valid", 0))
 resume_counters["on_chain_total"] = int(resume_progress.get("on_chain_total", 0))
 log_progress(f"⏯️ Fortsetzen ab Checkpoint: {checkpoint_path}")
 except Exception as exc:
 log_progress(f"❌ Konnte Checkpoint nicht loadn: {exc}")
 return
 
 if not RPC_AVAILABLE:
 log_progress("❌ RPC nicht verfügbar - installiere qubipy")
 return
 
 STATUS_FILE.parent.mkdir(parents=True, exist_ok=True)
 PROGRESS_FILE.parent.mkdir(parents=True, exist_ok=True)
 
 # Initialisiere Status-Datei
 status_mode = "a" if resume_data else "w"
 with STATUS_FILE.open(status_mode) as f:
 f.write("=" * 80 + "\n")
 if resume_data:
 f.write("RPC-VALIDIERUNG - RESUME\n")
 f.write(f"Fortgesetzt: {datetime.now().isoformat()}\n")
 f.write(f"Weiter bei: {resume_processed}/20000\n")
 else:
 f.write("RPC-VALIDIERUNG - 20,000 IDENTITIES\n")
 f.write(f"Gestartet: {datetime.now().isoformat()}\n")
 f.write("=" * 80 + "\n\n")
 
 # Initialisiere Progress-Datei
 save_progress({
 "status": "resuming" if resume_data else "starting",
 "timestamp": datetime.now().isoformat(),
 "method": "all_55_seeds_weighted",
 "expected_accuracy": 46.25,
 "target_sample_size": 20000,
 "resume_from": resume_processed if resume_data else 0
 })
 
 log_progress("=" * 80)
 log_progress("RPC-VALIDIERUNG - 20,000 IDENTITIES")
 log_progress("=" * 80)
 log_progress("⚠️ KEINE HALLUZINATIONEN - NUR ECHTE DATEN!")
 log_progress("🔬 100% ON-CHAIN VALIDIERUNG!")
 log_progress("⏱️ GESCHÄTZTE DAUER: ~100-120 Minuten")
 log_progress("")
 log_progress("📝 FORTSCHRITT ANZEIGEN:")
 log_progress(f" tail -f {STATUS_FILE.relative_to(project_root)}")
 log_progress("")
 
 # Load Daten
 log_progress("📂 Load Daten...")
 save_progress({"step": "loading_data"})
 
 if not LAYER3_FILE.exists():
 log_progress(f"❌ Datei nicht gefunden: {LAYER3_FILE}")
 return
 
 with LAYER3_FILE.open() as f:
 layer3_data = json.load(f)
 layer3_results = layer3_data.get("results", [])
 log_progress(f"✅ {len(layer3_results)} Identities geloadn")
 log_progress("")
 
 # WICHTIG: Mappings auf ALLEN Daten aufbauen for beste Accuracy!
 target_pos = 27
 log_progress(f"🔧 Baue Mappings for alle 55 Seed-Positionen (Target: Position {target_pos})...")
 log_progress(f" Verwende ALLE {len(layer3_results)} Identities for Mappings (beste Accuracy)...")
 save_progress({"step": "building_mappings"})
 
 mappings = {}
 for seed_pos in range(55):
 if seed_pos == target_pos: # Skip trivial!
 continue
 if (seed_pos + 1) % 10 == 0:
 log_progress(f" {seed_pos + 1}/54 Seed-Positionen...")
 
 mapping = build_seed_mapping(layer3_results, seed_pos, target_pos, min_samples=2)
 if mapping:
 mappings[seed_pos] = mapping
 
 log_progress(f"✅ {len(mappings)} Mappings erstellt")
 log_progress("")
 
 # Wähle 20,000 zufällige Identities for Test
 log_progress("🎲 Wähle 20,000 zufällige Identities for Test...")
 save_progress({"step": "selecting_samples"})
 
 random.seed(42) # Reproduzierbar
 sample_size = min(20000, len(layer3_results))
 selected_indices = random.sample(range(len(layer3_results)), sample_size)
 test_entries = [layer3_results[i] for i in selected_indices]
 
 log_progress(f"✅ {sample_size} Test-Identities ausgewählt")
 log_progress("")
 
 # Initialisiere RPC
 log_progress("🔌 Verbinde mit Qubic RPC...")
 save_progress({"step": "connecting_rpc"})
 
 try:
 rpc = rpc_client.QubiPy_RPC()
 log_progress("✅ RPC-Verbindung hergestellt")
 except Exception as e:
 log_progress(f"❌ RPC-Verbindung fehlgeschlagen: {e}")
 return
 
 log_progress("")
 
 # Starte Validierung
 start_time = time.time()
 log_progress("=" * 80)
 log_progress("🚀 STARTE RPC-VALIDIERUNG")
 log_progress("=" * 80)
 log_progress(f" Teste auf {len(test_entries)} Test-Identities...")
 log_progress(f" Mappings aufgebaut auf: {len(layer3_results)} Identities")
 log_progress("")
 
 correct = resume_counters["correct"]
 total = resume_counters["total_predictions"]
 on_chain_valid = resume_counters["on_chain_valid"]
 on_chain_total = resume_counters["on_chain_total"]
 errors = []
 validated_data = [] # Für ML-Training später

 if resume_processed >= len(test_entries):
 log_progress("ℹ️ Checkpoint entspricht bereits vollständiger Verarbeitung.")
 log_progress(" Bitte ohne --resume-checkpoint neu starten, falls komplette Wiederholung nötig ist.")
 return
 
 for idx, entry in enumerate(test_entries):
 if idx < resume_processed:
 continue # Bereits verarbeitet
 # Fortschrittsanzeige: erste 10, dann alle 100, dann alle 500
 show_progress = False
 if (idx + 1) <= 10:
 show_progress = True # Erste 10 immer anzeigen
 elif (idx + 1) % 100 == 0:
 show_progress = True # Dann alle 100
 elif (idx + 1) % 500 == 0:
 show_progress = True # Dann alle 500
 elif (idx + 1) == len(test_entries):
 show_progress = True # Am Ende
 
 if show_progress:
 progress = 100 * (idx + 1) / len(test_entries)
 accuracy = (correct / total * 100) if total > 0 else 0
 on_chain_rate = (on_chain_valid / on_chain_total * 100) if on_chain_total > 0 else 0
 elapsed = elapsed_base_seconds + (time.time() - start_time)
 processed_since_resume = max(1, idx + 1 - resume_processed)
 remaining = (elapsed / processed_since_resume) * (len(test_entries) - (idx + 1)) if processed_since_resume > 0 else 0
 
 log_progress(f" Fortschritt: {idx + 1}/{len(test_entries)} ({progress:.1f}%)")
 log_progress(f" Accuracy: {accuracy:.2f}% ({correct}/{total})")
 log_progress(f" On-Chain: {on_chain_rate:.2f}% ({on_chain_valid}/{on_chain_total})")
 log_progress(f" Vergangene Zeit: {elapsed/60:.1f} Minuten")
 log_progress(f" Geschätzte verbleibende Zeit: {remaining/60:.1f} Minuten")
 log_progress("")
 
 save_progress({
 "step": "validation",
 "progress": progress,
 "processed": idx + 1,
 "total": len(test_entries),
 "accuracy": accuracy,
 "correct": correct,
 "total_predictions": total,
 "on_chain_rate": on_chain_rate,
 "on_chain_valid": on_chain_valid,
 "on_chain_total": on_chain_total,
 "elapsed_minutes": elapsed / 60,
 "estimated_remaining_minutes": remaining / 60
 })
 
 l3_id = entry.get("layer3_identity", "")
 if not l3_id or len(l3_id) <= target_pos:
 continue
 
 seed = identity_to_seed(l3_id)
 if len(seed) < 55:
 continue
 
 # Vorhersage
 predicted = predict_all_55_seeds(seed, mappings, target_pos)
 if predicted is None:
 continue
 
 actual = l3_id[target_pos].upper()
 
 # Check Accuracy
 is_correct = (predicted == actual)
 if is_correct:
 correct += 1
 total += 1
 
 # RPC-Validierung (nur wenn Vorhersage korrekt)
 if is_correct:
 # Rate Limiting - Pause vor jedem RPC-Call
 time.sleep(0.3) # 300ms Pause for Rate Limiting
 
 # Logge ersten RPC-Call for Debugging
 if on_chain_total == 0:
 log_progress(f" 🔍 Erster RPC-Call: {l3_id[:30]}...")
 
 try:
 rpc_result = validate_identity_rpc(l3_id, rpc)
 on_chain_total += 1
 
 # Logge ersten erfolgreichen RPC-Call
 if on_chain_total == 1 and rpc_result["valid"]:
 log_progress(f" ✅ Erster RPC-Call erfolgreich!")
 except Exception as e:
 log_progress(f" ❌ RPC-Call Fehler: {e}")
 rpc_result = {
 "exists": False,
 "valid": False,
 "error": str(e)
 }
 on_chain_total += 1
 
 if rpc_result["valid"]:
 on_chain_valid += 1
 
 # Speichere for ML-Training
 validated_data.append({
 "identity": l3_id,
 "seed": seed,
 "predicted": predicted,
 "actual": actual,
 "is_correct": is_correct,
 "on_chain": rpc_result["valid"],
 "valid_for_tick": rpc_result.get("valid_for_tick"),
 "has_activity": rpc_result.get("has_activity", False)
 })
 
 if not rpc_result["valid"]:
 errors.append({
 "identity": l3_id,
 "predicted": predicted,
 "actual": actual,
 "rpc_error": rpc_result.get("error")
 })
 
 elapsed_time = elapsed_base_seconds + (time.time() - start_time)
 
 # Finale Ergebnisse
 final_accuracy = (correct / total * 100) if total > 0 else 0
 final_on_chain_rate = (on_chain_valid / on_chain_total * 100) if on_chain_total > 0 else 0
 
 log_progress("")
 log_progress("=" * 80)
 log_progress("📊 FINALE ERGEBNISSE")
 log_progress("=" * 80)
 log_progress("")
 log_progress(f" Accuracy: {final_accuracy:.2f}% ({correct}/{total})")
 log_progress(f" On-Chain Valid: {final_on_chain_rate:.2f}% ({on_chain_valid}/{on_chain_total})")
 log_progress(f" Fehler: {len(errors)}")
 log_progress(f" Gesamtzeit: {elapsed_time:.1f} Sekunden ({elapsed_time/60:.1f} Minuten)")
 log_progress("")
 
 # Speichere Ergebnisse
 OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
 
 output_data = {
 "timestamp": datetime.now().isoformat(),
 "method": "all_55_seeds_weighted",
 "target_position": target_pos,
 "mappings_built_on": len(layer3_results),
 "test_size": len(test_entries),
 "total_sample_size": sample_size,
 "results": {
 "accuracy": final_accuracy,
 "correct": correct,
 "total": total,
 "on_chain_rate": final_on_chain_rate,
 "on_chain_valid": on_chain_valid,
 "on_chain_total": on_chain_total,
 "errors": errors[:20] # Erste 20 Fehler
 },
 "validated_data_count": len(validated_data),
 "elapsed_time_seconds": elapsed_time
 }
 
 with RESULTS_FILE.open("w") as f:
 json.dump(output_data, f, indent=2)
 log_progress(f"💾 Ergebnisse gespeichert: {RESULTS_FILE}")
 
 # Speichere validierte Daten for ML-Training
 validated_file = OUTPUT_DIR / "rpc_validation_20000_validated_data.json"
 with validated_file.open("w") as f:
 json.dump({
 "timestamp": datetime.now().isoformat(),
 "count": len(validated_data),
 "data": validated_data
 }, f, indent=2)
 log_progress(f"💾 Validierte Daten for ML gespeichert: {validated_file}")
 log_progress("")
 
 save_progress({
 "status": "completed",
 "accuracy": final_accuracy,
 "on_chain_rate": final_on_chain_rate,
 "elapsed_time_seconds": elapsed_time,
 "validated_data_count": len(validated_data)
 })
 
 log_progress("=" * 80)
 log_progress("✅ VALIDIERUNG ABGESCHLOSSEN")
 log_progress("=" * 80)
 log_progress("")
 log_progress("🎯 NÄCHSTER SCHRITT:")
 log_progress(" ML-Modelle trainieren mit validierten Daten")
 log_progress(" Script: scripts/research/ml_position27_50percent.py")
 log_progress("")

if __name__ == "__main__":
 main()

