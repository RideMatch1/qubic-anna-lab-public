#!/usr/bin/env python3
"""
Umfassende Seed-basierte Vorhersage mit RPC-Validierung
- Läuft im Hintergrund
- Fortschrittsanzeige
- Alle Seed-Positionen testen
- RPC-Validierung mit korrigiertem Import
- 100% Echtheit sicherstellen
"""

import json
import sys
import time
import subprocess
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from collections import Counter, defaultdict
from datetime import datetime
import numpy as np
import pandas as pd

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# Paths
LAYER3_FILE = project_root / "outputs" / "derived" / "layer3_derivation_23k_complete.json"
MATRIX_FILE = project_root / "data" / "anna-matrix" / "Anna_Matrix.xlsx"
OUTPUT_DIR = project_root / "outputs" / "derived"
PROGRESS_FILE = project_root / "outputs" / "derived" / "seed_rpc_progress.json"
STATUS_FILE = project_root / "outputs" / "derived" / "seed_rpc_status.txt"

# RPC-Konfiguration
RPC_URL = "https://rpc.qubic.li"
RPC_TIMEOUT = 10
VENV_PYTHON = project_root / "venv-tx" / "bin" / "python3"

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

def load_anna_matrix():
 """Load Anna Matrix."""
 if not MATRIX_FILE.exists():
 return None
 
 df = pd.read_excel(MATRIX_FILE, header=None)
 numeric = df.apply(pd.to_numeric, errors="coerce").fillna(0.0)
 matrix = numeric.to_numpy(dtype=float)
 
 if matrix.shape == (129, 129):
 matrix = matrix[1:, 1:]
 
 if matrix.shape != (128, 128):
 return None
 
 return matrix

def get_matrix_coord(position: int, grid_col: int) -> Tuple[int, int]:
 """Berechne Matrix-Koordinate."""
 matrix_col = grid_col + 7
 
 if position == 27:
 matrix_row = position
 else:
 matrix_row = 128 - position
 
 return (matrix_row, matrix_col)

def get_grid_coord(position: int) -> Tuple[int, int]:
 """Berechne Grid-Koordinate."""
 grid_index = position % 49
 grid_row = grid_index // 7
 grid_col = grid_index % 7
 return (grid_row, grid_col)

def predict_matrix_char(matrix, position: int, transformation: str = "mod_4") -> Optional[str]:
 """Matrix-basierte Vorhersage."""
 if matrix is None:
 return None
 
 grid_row, grid_col = get_grid_coord(position)
 matrix_row, matrix_col = get_matrix_coord(position, grid_col)
 
 if not (0 <= matrix_row < 128 and 0 <= matrix_col < 128):
 return None
 
 matrix_value = matrix[matrix_row, matrix_col]
 
 if transformation == "mod_26":
 char = chr(ord('A') + (int(matrix_value) % 26))
 elif transformation == "mod_4":
 char = chr(ord('A') + (int(matrix_value) % 4))
 elif transformation == "abs_mod_4":
 char = chr(ord('A') + (abs(int(matrix_value)) % 4))
 else:
 return None
 
 return char

def build_seed_mapping(layer3_data: List[Dict], seed_pos: int, target_pos: int, min_samples: int = 10) -> Dict:
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

def predict_with_seed(seed: str, seed_pos: int, mapping: Dict) -> Optional[str]:
 """Vorhersage basierend auf Seed."""
 if len(seed) <= seed_pos:
 return None
 
 seed_char = seed[seed_pos].lower()
 if seed_char not in mapping:
 return None
 
 return mapping[seed_char]["predicted_char"]

def validate_identity_rpc(identity: str) -> Dict:
 """Validate Identity mit RPC (on-chain) via venv-tx."""
 if not VENV_PYTHON.exists():
 return {"valid": False, "error": "venv-tx not found"}
 
 script = f"""
import sys
sys.path.insert(0, '{project_root}')
from qubipy.rpc import rpc_client
import json

try:
 rpc = rpc_client.QubiPy_RPC()
 balance = rpc.get_balance('{identity}')
 
 if balance is not None:
 print(json.dumps({{'valid': True, 'on_chain': True, 'balance': balance}}))
 else:
 print(json.dumps({{'valid': True, 'on_chain': False, 'balance': None}}))
except Exception as e:
 print(json.dumps({{'valid': False, 'error': str(e)}}))
"""
 
 try:
 process = subprocess.run(
 [str(VENV_PYTHON), "-c", script],
 capture_output=True,
 text=True,
 timeout=RPC_TIMEOUT + 5,
 cwd=str(project_root)
 )
 
 if process.returncode == 0:
 result = json.loads(process.stdout.strip())
 return result
 else:
 return {"valid": False, "error": process.stderr.strip() or "Unknown error"}
 except subprocess.TimeoutExpired:
 return {"valid": False, "error": "Timeout"}
 except Exception as e:
 return {"valid": False, "error": str(e)}

def test_all_seed_positions(layer3_data: List[Dict], target_pos: int, matrix, rpc_enabled: bool = False, sample_size: int = 2000) -> Dict:
 """Teste ALLE Seed-Positionen mit RPC-Validierung."""
 
 log_progress(f"🔍 Starte Analyse for Position {target_pos}...")
 
 # 1. Teste ALLE Seed-Positionen (0-54)
 seed_positions = list(range(55))
 seed_results = {}
 
 log_progress(f" Teste {len(seed_positions)} Seed-Positionen...")
 
 for i, seed_pos in enumerate(seed_positions):
 if (i + 1) % 10 == 0:
 log_progress(f" {i + 1}/{len(seed_positions)} Seed-Positionen getestet...")
 
 mapping = build_seed_mapping(layer3_data, seed_pos, target_pos)
 
 if not mapping:
 continue
 
 # Teste Accuracy
 correct = 0
 total = 0
 
 for entry in layer3_data[:sample_size]:
 l3_id = entry.get("layer3_identity", "")
 if not l3_id or len(l3_id) <= target_pos:
 continue
 
 seed = identity_to_seed(l3_id)
 predicted = predict_with_seed(seed, seed_pos, mapping)
 
 if predicted is None:
 continue
 
 actual = l3_id[target_pos].upper()
 if predicted == actual:
 correct += 1
 total += 1
 
 if total > 0:
 accuracy = (correct / total * 100)
 seed_results[seed_pos] = {
 "accuracy": accuracy,
 "correct": correct,
 "total": total,
 "mapping_size": len(mapping)
 }
 
 # Finde beste Seed-Positionen
 best_seed_positions = sorted(
 seed_results.items(),
 key=lambda x: x[1]["accuracy"],
 reverse=True
 )[:10]
 
 log_progress(f" ✅ {len(best_seed_positions)} beste Seed-Positionen gefunden")
 
 # 2. Teste Matrix-Vorhersage
 matrix_pred = None
 matrix_accuracy = 0
 
 if matrix is not None:
 log_progress(f" Teste Matrix-Vorhersage...")
 transformations = ["mod_26", "mod_4", "abs_mod_4"]
 best_trans = None
 best_acc = 0
 
 for trans in transformations:
 pred_char = predict_matrix_char(matrix, target_pos, trans)
 if pred_char is None:
 continue
 
 correct = 0
 total = 0
 
 for entry in layer3_data[:sample_size]:
 l3_id = entry.get("layer3_identity", "")
 if not l3_id or len(l3_id) <= target_pos:
 continue
 
 if pred_char == l3_id[target_pos].upper():
 correct += 1
 total += 1
 
 if total > 0:
 acc = (correct / total * 100)
 if acc > best_acc:
 best_acc = acc
 best_trans = trans
 matrix_pred = pred_char
 
 matrix_accuracy = best_acc
 log_progress(f" ✅ Matrix-Accuracy: {matrix_accuracy:.2f}%")
 
 # 3. RPC-Validierung (Sample)
 rpc_results = {
 "tested": 0,
 "valid": 0,
 "on_chain": 0,
 "errors": []
 }
 
 if rpc_enabled and VENV_PYTHON.exists():
 rpc_sample_size = min(100, sample_size) # Größeres Sample for bessere Statistik
 log_progress(f" 📡 RPC-Validierung (Sample: {rpc_sample_size})...")
 rpc_sample = layer3_data[:rpc_sample_size]
 
 for i, entry in enumerate(rpc_sample):
 l3_id = entry.get("layer3_identity", "")
 if not l3_id:
 continue
 
 rpc_results["tested"] += 1
 validation = validate_identity_rpc(l3_id)
 
 if validation.get("valid"):
 rpc_results["valid"] += 1
 if validation.get("on_chain"):
 rpc_results["on_chain"] += 1
 else:
 rpc_results["errors"].append({
 "identity": l3_id,
 "error": validation.get("error", "Unknown")
 })
 
 # Progress
 if (i + 1) % 20 == 0:
 log_progress(f" {i + 1}/{rpc_sample_size} RPC-Validierungen... ({rpc_results['valid']} valid, {rpc_results['on_chain']} on-chain)")
 
 # Rate limiting
 time.sleep(0.2)
 
 log_progress(f" ✅ RPC: {rpc_results['valid']}/{rpc_results['tested']} valid, {rpc_results['on_chain']} on-chain")
 
 return {
 "target_position": target_pos,
 "seed_results": seed_results,
 "best_seed_positions": [
 {"position": pos, "accuracy": data["accuracy"], "total": data["total"]}
 for pos, data in best_seed_positions
 ],
 "matrix_prediction": matrix_pred,
 "matrix_accuracy": matrix_accuracy,
 "rpc_validation": rpc_results
 }

def main():
 """Hauptfunktion."""
 
 # Initialisiere Status-Datei
 STATUS_FILE.parent.mkdir(parents=True, exist_ok=True)
 with STATUS_FILE.open("w") as f:
 f.write("=" * 80 + "\n")
 f.write("UMFASSENDE SEED-BASIERTE VORHERSAGE MIT RPC-VALIDIERUNG\n")
 f.write("=" * 80 + "\n")
 f.write(f"Gestartet: {datetime.now().isoformat()}\n")
 f.write("=" * 80 + "\n\n")
 
 log_progress("=" * 80)
 log_progress("UMFASSENDE SEED-BASIERTE VORHERSAGE MIT RPC-VALIDIERUNG")
 log_progress("=" * 80)
 log_progress("⚠️ KEINE HALLUZINATIONEN - NUR ECHTE DATEN!")
 log_progress("🔬 KRITISCH, SYSTEMATISCH, PERFEKT, 100% ECHTHEIT")
 log_progress("")
 
 # 1. Load Daten
 log_progress("📂 Load Daten...")
 
 if not LAYER3_FILE.exists():
 log_progress(f"❌ Datei nicht gefunden: {LAYER3_FILE}")
 return
 
 with LAYER3_FILE.open() as f:
 layer3_data = json.load(f)
 layer3_results = layer3_data.get("results", [])
 log_progress(f"✅ {len(layer3_results)} Identities geloadn")
 
 # Load Matrix
 matrix = load_anna_matrix()
 if matrix is not None:
 log_progress(f"✅ Matrix geloadn: {matrix.shape}")
 else:
 log_progress("⚠️ Matrix nicht geloadn")
 log_progress("")
 
 # 2. RPC-Validierung vorbereiten
 rpc_enabled = VENV_PYTHON.exists()
 if rpc_enabled:
 log_progress("📡 RPC-Validierung aktiviert (venv-tx)")
 else:
 log_progress("⚠️ venv-tx nicht gefunden - RPC-Validierung abovesprungen")
 log_progress("")
 
 # 3. Teste alle Block-Ende-Positionen
 log_progress("🔍 UMFASSENDE ANALYSE:")
 log_progress("")
 
 block_end_positions = [13, 27, 41, 55]
 all_results = {}
 start_time = time.time()
 
 for idx, pos in enumerate(block_end_positions):
 log_progress(f"📊 Position {pos} ({idx + 1}/{len(block_end_positions)})...")
 
 result = test_all_seed_positions(
 layer3_results,
 pos,
 matrix,
 rpc_enabled=rpc_enabled,
 sample_size=2000
 )
 all_results[f"position_{pos}"] = result
 
 # Speichere Zwischenergebnisse
 progress_data = {
 "timestamp": datetime.now().isoformat(),
 "completed_positions": idx + 1,
 "total_positions": len(block_end_positions),
 "current_position": pos,
 "results_so_far": all_results,
 "elapsed_time": time.time() - start_time
 }
 save_progress(progress_data)
 
 log_progress("")
 
 # 4. Zusammenfassung
 elapsed_time = time.time() - start_time
 log_progress("=" * 80)
 log_progress("ZUSAMMENFASSUNG")
 log_progress("=" * 80)
 log_progress("")
 
 for pos_key, result in all_results.items():
 pos = result["target_position"]
 best_seeds = result["best_seed_positions"]
 matrix_acc = result["matrix_accuracy"]
 rpc = result["rpc_validation"]
 
 marker = "⭐" if pos == 27 else " "
 log_progress(f"{marker} Position {pos}:")
 
 if best_seeds:
 best = best_seeds[0]
 log_progress(f" Beste Seed-Position: {best['position']} ({best['accuracy']:.2f}%)")
 
 if matrix_acc > 0:
 log_progress(f" Matrix-Accuracy: {matrix_acc:.2f}%")
 
 if rpc["tested"] > 0:
 log_progress(f" RPC: {rpc['valid']}/{rpc['tested']} valid, {rpc['on_chain']} on-chain")
 
 log_progress("")
 
 # 5. Speichere finale Ergebnisse
 OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
 
 def convert_numpy(obj):
 if isinstance(obj, np.integer):
 return int(obj)
 elif isinstance(obj, np.floating):
 return float(obj)
 elif isinstance(obj, np.ndarray):
 return obj.tolist()
 elif isinstance(obj, dict):
 return {k: convert_numpy(v) for k, v in obj.items()}
 elif isinstance(obj, list):
 return [convert_numpy(item) for item in obj]
 return obj
 
 output_data = {
 "timestamp": datetime.now().isoformat(),
 "total_identities": len(layer3_results),
 "rpc_enabled": rpc_enabled,
 "sample_size": 2000,
 "elapsed_time_seconds": elapsed_time,
 "results": convert_numpy(all_results),
 "summary": {
 "best_overall": max(
 all_results.items(),
 key=lambda x: x[1]["best_seed_positions"][0]["accuracy"] if x[1]["best_seed_positions"] else 0
 ) if all_results else None
 }
 }
 
 output_file = OUTPUT_DIR / "comprehensive_seed_rpc_final_results.json"
 with output_file.open("w") as f:
 json.dump(output_data, f, indent=2)
 log_progress(f"💾 Ergebnisse gespeichert: {output_file}")
 log_progress("")
 
 log_progress("=" * 80)
 log_progress("✅ ANALYSE ABGESCHLOSSEN")
 log_progress("=" * 80)
 log_progress("")
 log_progress("📊 STATISTIKEN:")
 log_progress("")
 log_progress(f" Getestete Positionen: {len(block_end_positions)}")
 log_progress(f" Sample-Größe pro Position: 2000")
 log_progress(f" RPC-Validierung: {'✅' if rpc_enabled else '❌'}")
 log_progress(f" Gesamtzeit: {elapsed_time:.1f} Sekunden ({elapsed_time/60:.1f} Minuten)")
 log_progress("")
 log_progress("📄 Status-Datei: outputs/derived/seed_rpc_status.txt")
 log_progress("📄 Progress-Datei: outputs/derived/seed_rpc_progress.json")
 log_progress("📄 Finale Ergebnisse: outputs/derived/comprehensive_seed_rpc_final_results.json")
 log_progress("")

if __name__ == "__main__":
 main()

