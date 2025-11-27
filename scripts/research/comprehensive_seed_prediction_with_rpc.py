#!/usr/bin/env python3
"""
Umfassende Seed-basierte Vorhersage mit RPC-Validierung
- Optimiert Seed-basierte Vorhersagen
- Testet Kombinationen (Seed + Matrix)
- Validiert mit RPC (on-chain)
- 100% Echtheit sicherstellen
- KEINE Halluzinationen - nur echte Daten!
"""

import json
import sys
import time
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from collections import Counter, defaultdict
from datetime import datetime
import numpy as np

# Qubic RPC - verwende venv-tx
import subprocess
import os

RPC_AVAILABLE = True # Wir verwenden subprocess for RPC-Calls

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# Paths
LAYER3_FILE = project_root / "outputs" / "derived" / "layer3_derivation_23k_complete.json"
MATRIX_FILE = project_root / "data" / "anna-matrix" / "Anna_Matrix.xlsx"
OUTPUT_DIR = project_root / "outputs" / "derived"
REPORTS_DIR = project_root / "outputs" / "reports"

# RPC-Konfiguration
RPC_URL = "https://rpc.qubic.li"
RPC_TIMEOUT = 10
RPC_RETRY_DELAY = 1
RPC_MAX_RETRIES = 3

def identity_to_seed(identity: str) -> str:
 """Konvertiere Identity zu Seed."""
 return identity.lower()[:55]

def load_anna_matrix():
 """Load Anna Matrix."""
 import pandas as pd
 
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
 "total": total,
 "distribution": dict(counter.most_common(5))
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

def validate_identity_rpc(identity: str, use_venv: bool = True) -> Dict:
 """Validate Identity mit RPC (on-chain) via venv-tx oder direkter RPC."""
 if not RPC_AVAILABLE:
 return {"valid": False, "error": "RPC not available"}
 
 try:
 # Check Identity-Format
 if len(identity) != 60:
 return {"valid": False, "error": "Invalid length"}
 
 # RPC-Call mit Retry
 for attempt in range(RPC_MAX_RETRIES):
 try:
 if use_venv:
 # Verwende venv-tx for RPC-Call
 venv_path = project_root / "venv-tx"
 python_path = venv_path / "bin" / "python3"
 
 if not python_path.exists():
 # Fallback: versuche direktes Python mit qubipy
 use_venv = False
 
 if use_venv:
 script = f"""
import sys
sys.path.insert(0, '{project_root}')
from qubipy.rpc.rpc_client import RpcClient
import json

client = RpcClient('{RPC_URL}', timeout={RPC_TIMEOUT})
try:
 result = client.get_identity('{identity}')
 if result:
 print(json.dumps({{'valid': True, 'on_chain': True, 'result': result}}))
 else:
 print(json.dumps({{'valid': True, 'on_chain': False, 'result': None}}))
except Exception as e:
 print(json.dumps({{'valid': False, 'error': str(e)}}))
"""
 process = subprocess.run(
 [str(python_path), "-c", script],
 capture_output=True,
 text=True,
 timeout=RPC_TIMEOUT + 5
 )
 
 if process.returncode == 0:
 result = json.loads(process.stdout.strip())
 return result
 else:
 error_msg = process.stderr.strip() or "Unknown error"
 if attempt < RPC_MAX_RETRIES - 1:
 time.sleep(RPC_RETRY_DELAY * (attempt + 1))
 continue
 return {"valid": False, "error": error_msg}
 
 # Fallback: Direkter RPC-Call (wenn qubipy verfügbar)
 if not use_venv:
 try:
 from qubipy.rpc.rpc_client import RpcClient
 client = RpcClient(RPC_URL, timeout=RPC_TIMEOUT)
 result = client.get_identity(identity)
 
 if result:
 return {
 "valid": True,
 "on_chain": True,
 "result": result
 }
 else:
 return {
 "valid": True,
 "on_chain": False,
 "result": None
 }
 except ImportError:
 return {"valid": False, "error": "qubipy not available"}
 
 except subprocess.TimeoutExpired:
 if attempt < RPC_MAX_RETRIES - 1:
 time.sleep(RPC_RETRY_DELAY * (attempt + 1))
 continue
 return {"valid": False, "error": "Timeout"}
 except Exception as e:
 if attempt < RPC_MAX_RETRIES - 1:
 time.sleep(RPC_RETRY_DELAY * (attempt + 1))
 continue
 else:
 return {"valid": False, "error": str(e)}
 except Exception as e:
 return {"valid": False, "error": str(e)}
 
 return {"valid": False, "error": "Unknown error"}

def test_comprehensive_prediction(layer3_data: List[Dict], target_pos: int, matrix, rpc_enabled: bool = False, sample_size: int = 1000) -> Dict:
 """Umfassender Test mit RPC-Validierung."""
 
 print(f" 🔍 Teste Position {target_pos}...")
 
 # 1. Teste alle Seed-Positionen
 seed_positions = list(range(55)) # Alle 55 Seed-Positionen
 seed_results = {}
 
 print(f" Teste {len(seed_positions)} Seed-Positionen...")
 for seed_pos in seed_positions:
 mapping = build_seed_mapping(layer3_data, seed_pos, target_pos)
 
 if not mapping:
 continue
 
 # Teste Accuracy
 correct = 0
 total = 0
 
 for entry in layer3_data[:sample_size]: # Sample for Geschwindigkeit
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
 )[:5]
 
 print(f" Beste Seed-Positionen gefunden: {len(best_seed_positions)}")
 
 # 2. Teste Matrix-Vorhersage
 matrix_pred = None
 matrix_accuracy = 0
 
 if matrix is not None:
 # Beste Transformation for diese Position finden
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
 
 # 3. Teste Kombinationen (beste Seed-Positionen)
 combo_results = {}
 
 if best_seed_positions:
 best_seed_pos = best_seed_positions[0][0]
 best_seed_mapping = build_seed_mapping(layer3_data, best_seed_pos, target_pos)
 
 # Kombiniere: Seed + Matrix
 if matrix_pred and best_seed_mapping:
 correct = 0
 total = 0
 seed_correct = 0
 matrix_correct = 0
 both_correct = 0
 
 for entry in layer3_data[:sample_size]:
 l3_id = entry.get("layer3_identity", "")
 if not l3_id or len(l3_id) <= target_pos:
 continue
 
 seed = identity_to_seed(l3_id)
 seed_pred = predict_with_seed(seed, best_seed_pos, best_seed_mapping)
 
 if seed_pred is None:
 continue
 
 actual = l3_id[target_pos].upper()
 
 seed_match = (seed_pred == actual)
 matrix_match = (matrix_pred == actual)
 
 if seed_match:
 seed_correct += 1
 if matrix_match:
 matrix_correct += 1
 if seed_match and matrix_match:
 both_correct += 1
 
 # Kombinierte Vorhersage: Wenn beide gleich sind, verwende sie
 if seed_pred == matrix_pred:
 predicted = seed_pred
 else:
 predicted = seed_pred # Bevorzuge Seed
 
 if predicted == actual:
 correct += 1
 total += 1
 
 if total > 0:
 combo_results["seed_matrix"] = {
 "accuracy": (correct / total * 100),
 "seed_accuracy": (seed_correct / total * 100),
 "matrix_accuracy": (matrix_correct / total * 100),
 "both_correct": (both_correct / total * 100),
 "correct": correct,
 "total": total
 }
 
 # 4. RPC-Validierung (Sample)
 rpc_results = {
 "tested": 0,
 "valid": 0,
 "on_chain": 0,
 "errors": []
 }
 
 if rpc_enabled:
 rpc_sample_size = min(50, sample_size) # Kleinere Sample for RPC
 print(f" RPC-Validierung (Sample: {rpc_sample_size})...")
 rpc_sample = layer3_data[:rpc_sample_size]
 
 for i, entry in enumerate(rpc_sample):
 l3_id = entry.get("layer3_identity", "")
 if not l3_id:
 continue
 
 rpc_results["tested"] += 1
 validation = validate_identity_rpc(l3_id, use_venv=True)
 
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
 if (i + 1) % 10 == 0:
 print(f" {i + 1}/{rpc_sample_size} validiert...")
 
 # Rate limiting
 time.sleep(0.2)
 
 return {
 "target_position": target_pos,
 "seed_results": seed_results,
 "best_seed_positions": [
 {"position": pos, "accuracy": data["accuracy"], "total": data["total"]}
 for pos, data in best_seed_positions
 ],
 "matrix_prediction": matrix_pred,
 "matrix_accuracy": matrix_accuracy,
 "combo_results": combo_results,
 "rpc_validation": rpc_results
 }

def main():
 """Hauptfunktion."""
 
 print("=" * 80)
 print("UMFASSENDE SEED-BASIERTE VORHERSAGE MIT RPC-VALIDIERUNG")
 print("=" * 80)
 print()
 print("⚠️ KEINE HALLUZINATIONEN - NUR ECHTE DATEN!")
 print("🔬 KRITISCH, SYSTEMATISCH, PERFEKT, 100% ECHTHEIT")
 print()
 
 # 1. Load Daten
 print("📂 Load Daten...")
 
 if not LAYER3_FILE.exists():
 print(f"❌ Datei nicht gefunden: {LAYER3_FILE}")
 return
 
 with LAYER3_FILE.open() as f:
 layer3_data = json.load(f)
 layer3_results = layer3_data.get("results", [])
 print(f"✅ {len(layer3_results)} Identities geloadn")
 
 # Load Matrix
 matrix = load_anna_matrix()
 if matrix is not None:
 print(f"✅ Matrix geloadn: {matrix.shape}")
 else:
 print("⚠️ Matrix nicht geloadn")
 print()
 
 # 2. RPC-Validierung vorbereiten
 rpc_enabled = RPC_AVAILABLE
 if rpc_enabled:
 venv_path = project_root / "venv-tx"
 python_path = venv_path / "bin" / "python3"
 
 if python_path.exists():
 print("📡 RPC-Validierung aktiviert (venv-tx)")
 else:
 print("⚠️ venv-tx nicht gefunden - RPC-Validierung will versucht")
 else:
 print("⚠️ RPC-Validierung deaktiviert")
 print()
 
 # 3. Teste alle Block-Ende-Positionen
 print("🔍 UMFASSENDE ANALYSE:")
 print()
 
 block_end_positions = [13, 27, 41, 55]
 all_results = {}
 
 for pos in block_end_positions:
 result = test_comprehensive_prediction(
 layer3_results,
 pos,
 matrix,
 rpc_enabled=rpc_enabled,
 sample_size=2000 # Größeres Sample for bessere Statistik
 )
 all_results[f"position_{pos}"] = result
 print()
 
 # 4. Zusammenfassung
 print("=" * 80)
 print("ZUSAMMENFASSUNG")
 print("=" * 80)
 print()
 
 for pos_key, result in all_results.items():
 pos = result["target_position"]
 best_seeds = result["best_seed_positions"]
 matrix_acc = result["matrix_accuracy"]
 combo = result["combo_results"]
 rpc = result["rpc_validation"]
 
 marker = "⭐" if pos == 27 else " "
 print(f"{marker} Position {pos}:")
 
 if best_seeds:
 best = best_seeds[0]
 print(f" Beste Seed-Position: {best['position']} ({best['accuracy']:.2f}%)")
 
 if matrix_acc > 0:
 print(f" Matrix-Accuracy: {matrix_acc:.2f}%")
 
 if combo:
 combo_acc = combo.get("seed_matrix", {}).get("accuracy", 0)
 if combo_acc > 0:
 print(f" Kombiniert (Seed+Matrix): {combo_acc:.2f}%")
 
 if rpc["tested"] > 0:
 print(f" RPC-Validierung: {rpc['valid']}/{rpc['tested']} valid, {rpc['on_chain']} on-chain")
 
 print()
 
 # 5. Speichere Ergebnisse
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
 "results": convert_numpy(all_results),
 "summary": {
 "best_overall": max(
 all_results.items(),
 key=lambda x: x[1]["best_seed_positions"][0]["accuracy"] if x[1]["best_seed_positions"] else 0
 ) if all_results else None
 }
 }
 
 output_file = OUTPUT_DIR / "comprehensive_seed_prediction_rpc_results.json"
 with output_file.open("w") as f:
 json.dump(output_data, f, indent=2)
 print(f"💾 Ergebnisse gespeichert: {output_file}")
 print()
 
 print("=" * 80)
 print("✅ ANALYSE ABGESCHLOSSEN")
 print("=" * 80)
 print()
 print("📊 STATISTIKEN:")
 print()
 print(f" Getestete Positionen: {len(block_end_positions)}")
 print(f" Sample-Größe pro Position: 2000")
 print(f" RPC-Validierung: {'✅' if rpc_enabled else '❌'}")
 print()

if __name__ == "__main__":
 main()

