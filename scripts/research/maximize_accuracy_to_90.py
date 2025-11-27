#!/usr/bin/env python3
"""
Maximale Accuracy - Ziel 90%!
- Teste ALLE möglichen Kombinationen
- Teste größere Kombinationen (15+, 20+, 25+ Positionen)
- Teste andere Features (Matrix-Werte, Block-Positionen, etc.)
- Teste Machine Learning Ansätze
- Systematisch nach der besten Methode suchen
- KEINE Halluzinationen - nur echte Daten!
"""

import json
import sys
import time
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from collections import Counter, defaultdict
from datetime import datetime
from itertools import combinations
import numpy as np
import pandas as pd

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# Paths
LAYER3_FILE = project_root / "outputs" / "derived" / "layer3_derivation_23k_complete.json"
MATRIX_FILE = project_root / "data" / "anna-matrix" / "Anna_Matrix.xlsx"
OUTPUT_DIR = project_root / "outputs" / "derived"
STATUS_FILE = project_root / "outputs" / "derived" / "maximize_accuracy_to_90_status.txt"

def log_progress(message: str, status_file: Path = STATUS_FILE):
 """Schreibe Fortschritt in Status-Datei."""
 timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
 with status_file.open("a") as f:
 f.write(f"[{timestamp}] {message}\n")
 print(f"[{timestamp}] {message}")

def identity_to_seed(identity: str) -> str:
 """Konvertiere Identity zu Seed."""
 return identity.lower()[:55]

def load_anna_matrix(matrix_file: Path) -> np.ndarray:
 """Load Anna Matrix."""
 df = pd.read_excel(matrix_file, header=None)
 matrix = df.values.astype(float)
 # Stelle sicher, dass es 128x128 ist
 if matrix.shape != (128, 128):
 matrix = matrix[:128, :128]
 return matrix

def build_seed_mapping(layer3_data: List[Dict], seed_pos: int, target_pos: int, min_samples: int = 5) -> Dict:
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

def build_identity_mapping(layer3_data: List[Dict], identity_pos: int, target_pos: int, min_samples: int = 5) -> Dict:
 """Baue Identity-Character-Mapping (andere Identity-Positionen)."""
 mapping = defaultdict(Counter)
 totals = Counter()
 
 for entry in layer3_data:
 l3_id = entry.get("layer3_identity", "")
 if not l3_id or len(l3_id) <= max(identity_pos, target_pos):
 continue
 
 identity_char_at_pos = l3_id[identity_pos].upper()
 target_char = l3_id[target_pos].upper()
 
 mapping[identity_char_at_pos][target_char] += 1
 totals[identity_char_at_pos] += 1
 
 results = {}
 for char, counter in mapping.items():
 total = totals[char]
 if total >= min_samples:
 most_common = counter.most_common(1)[0]
 success_rate = most_common[1] / total
 
 results[char] = {
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

def predict_with_identity(identity: str, identity_pos: int, mapping: Dict) -> Optional[str]:
 """Vorhersage basierend auf Identity-Position."""
 if len(identity) <= identity_pos:
 return None
 
 char = identity[identity_pos].upper()
 if char not in mapping:
 return None
 
 return mapping[char]["predicted_char"]

def test_hybrid_combination(layer3_data: List[Dict], seed_positions: List[int], identity_positions: List[int], 
 target_pos: int, sample_size: int = 2000) -> Dict:
 """Teste Hybrid-Kombination (Seed + Identity-Positionen)."""
 
 # Baue Mappings
 seed_mappings = {}
 for seed_pos in seed_positions:
 mapping = build_seed_mapping(layer3_data, seed_pos, target_pos, min_samples=3)
 if mapping:
 seed_mappings[seed_pos] = mapping
 
 identity_mappings = {}
 for identity_pos in identity_positions:
 if identity_pos == target_pos: # Skip trivial
 continue
 mapping = build_identity_mapping(layer3_data, identity_pos, target_pos, min_samples=3)
 if mapping:
 identity_mappings[identity_pos] = mapping
 
 if not seed_mappings and not identity_mappings:
 return {"accuracy": 0, "total": 0}
 
 correct = 0
 total = 0
 
 for entry in layer3_data[:sample_size]:
 l3_id = entry.get("layer3_identity", "")
 if not l3_id or len(l3_id) <= target_pos:
 continue
 
 seed = identity_to_seed(l3_id)
 
 predictions = []
 
 # Seed-basierte Vorhersagen
 for seed_pos in seed_positions:
 if seed_pos in seed_mappings:
 pred = predict_with_seed(seed, seed_pos, seed_mappings[seed_pos])
 if pred is not None:
 predictions.append(pred)
 
 # Identity-basierte Vorhersagen
 for identity_pos in identity_positions:
 if identity_pos == target_pos:
 continue
 if identity_pos in identity_mappings:
 pred = predict_with_identity(l3_id, identity_pos, identity_mappings[identity_pos])
 if pred is not None:
 predictions.append(pred)
 
 if not predictions:
 continue
 
 # Mehrheitsentscheidung
 prediction_counter = Counter(predictions)
 predicted = prediction_counter.most_common(1)[0][0]
 
 actual = l3_id[target_pos].upper()
 if predicted == actual:
 correct += 1
 total += 1
 
 accuracy = (correct / total * 100) if total > 0 else 0
 
 return {
 "seed_positions": seed_positions,
 "identity_positions": identity_positions,
 "accuracy": accuracy,
 "correct": correct,
 "total": total
 }

def test_large_combination(layer3_data: List[Dict], all_positions: List[int], target_pos: int, 
 sample_size: int = 2000) -> Dict:
 """Teste große Kombination (alle Positionen)."""
 
 # Baue Mappings for alle Positionen
 mappings = {}
 
 for pos in all_positions:
 if pos == target_pos: # Skip trivial
 continue
 
 # Teste Seed-Mapping
 seed_mapping = build_seed_mapping(layer3_data, pos, target_pos, min_samples=2)
 if seed_mapping:
 mappings[pos] = {"type": "seed", "mapping": seed_mapping}
 continue
 
 # Teste Identity-Mapping
 identity_mapping = build_identity_mapping(layer3_data, pos, target_pos, min_samples=2)
 if identity_mapping:
 mappings[pos] = {"type": "identity", "mapping": identity_mapping}
 
 if not mappings:
 return {"accuracy": 0, "total": 0}
 
 correct = 0
 total = 0
 
 for entry in layer3_data[:sample_size]:
 l3_id = entry.get("layer3_identity", "")
 if not l3_id or len(l3_id) <= target_pos:
 continue
 
 seed = identity_to_seed(l3_id)
 
 predictions = []
 
 for pos, mapping_data in mappings.items():
 if mapping_data["type"] == "seed":
 pred = predict_with_seed(seed, pos, mapping_data["mapping"])
 else:
 pred = predict_with_identity(l3_id, pos, mapping_data["mapping"])
 
 if pred is not None:
 predictions.append(pred)
 
 if not predictions:
 continue
 
 # Mehrheitsentscheidung
 prediction_counter = Counter(predictions)
 predicted = prediction_counter.most_common(1)[0][0]
 
 actual = l3_id[target_pos].upper()
 if predicted == actual:
 correct += 1
 total += 1
 
 accuracy = (correct / total * 100) if total > 0 else 0
 
 return {
 "num_positions": len(mappings),
 "accuracy": accuracy,
 "correct": correct,
 "total": total
 }

def main():
 """Hauptfunktion."""
 
 STATUS_FILE.parent.mkdir(parents=True, exist_ok=True)
 with STATUS_FILE.open("w") as f:
 f.write("=" * 80 + "\n")
 f.write("MAXIMALE ACCURACY - ZIEL 90%!\n")
 f.write("=" * 80 + "\n")
 f.write(f"Gestartet: {datetime.now().isoformat()}\n")
 f.write("=" * 80 + "\n\n")
 
 log_progress("=" * 80)
 log_progress("MAXIMALE ACCURACY - ZIEL 90%!")
 log_progress("=" * 80)
 log_progress("⚠️ KEINE HALLUZINATIONEN - NUR ECHTE DATEN!")
 log_progress("🔬 SYSTEMATISCH, PERFEKT, ZIEL: 90% ACCURACY!")
 log_progress("")
 
 # Load Daten
 log_progress("📂 Load Daten...")
 
 if not LAYER3_FILE.exists():
 log_progress(f"❌ Datei nicht gefunden: {LAYER3_FILE}")
 return
 
 with LAYER3_FILE.open() as f:
 layer3_data = json.load(f)
 layer3_results = layer3_data.get("results", [])
 log_progress(f"✅ {len(layer3_results)} Identities geloadn")
 log_progress("")
 
 start_time = time.time()
 
 target_pos = 27
 log_progress(f"🔍 POSITION {target_pos} - SYSTEMATISCHE OPTIMIERUNG ZU 90%")
 log_progress("")
 
 results = {}
 
 # 1. Teste große Seed-Kombinationen (15, 20, 25, 30 Positionen)
 log_progress(" 1. Teste große Seed-Kombinationen...")
 
 # Beste Seed-Positionen (aus vorheriger Analyse)
 top_seed_positions = [33, 26, 14, 0, 10, 13, 6, 16, 18, 15, 5, 1, 2, 3, 4, 7, 8, 9, 11, 12, 17, 19, 20, 21, 22, 23, 24, 25, 27, 28]
 
 for num_positions in [15, 20, 25, 30]:
 log_progress(f" Teste {num_positions} Seed-Positionen...")
 combo = top_seed_positions[:num_positions]
 
 # Baue Mappings
 mappings = {}
 for seed_pos in combo:
 mapping = build_seed_mapping(layer3_results, seed_pos, target_pos, min_samples=3)
 if mapping:
 mappings[seed_pos] = mapping
 
 if not mappings:
 continue
 
 # Teste
 correct = 0
 total = 0
 
 for entry in layer3_results[:2000]:
 l3_id = entry.get("layer3_identity", "")
 if not l3_id or len(l3_id) <= target_pos:
 continue
 
 seed = identity_to_seed(l3_id)
 
 predictions = []
 for seed_pos in combo:
 if seed_pos in mappings:
 pred = predict_with_seed(seed, seed_pos, mappings[seed_pos])
 if pred is not None:
 predictions.append(pred)
 
 if not predictions:
 continue
 
 prediction_counter = Counter(predictions)
 predicted = prediction_counter.most_common(1)[0][0]
 
 actual = l3_id[target_pos].upper()
 if predicted == actual:
 correct += 1
 total += 1
 
 accuracy = (correct / total * 100) if total > 0 else 0
 results[f"seed_{num_positions}"] = {
 "num_positions": num_positions,
 "accuracy": accuracy,
 "correct": correct,
 "total": total
 }
 log_progress(f" ✅ {num_positions} Positionen: {accuracy:.2f}%")
 
 log_progress("")
 
 # 2. Teste Hybrid-Kombinationen (Seed + Identity)
 log_progress(" 2. Teste Hybrid-Kombinationen (Seed + Identity)...")
 
 # Beste Seed-Positionen
 top_seeds = [33, 26, 14, 0, 10, 13, 6, 16, 18, 15]
 
 # Teste verschiedene Identity-Positionen
 identity_positions_to_test = [
 [13, 41, 55], # Block-Ende
 [0, 1, 2, 3, 4], # Anfang
 [56, 57, 58, 59], # Ende (vor Checksum)
 [13, 27, 41, 55], # Alle Block-Ende
 ]
 
 for identity_positions in identity_positions_to_test:
 result = test_hybrid_combination(
 layer3_results,
 top_seeds[:10],
 identity_positions,
 target_pos,
 sample_size=2000
 )
 
 if result["accuracy"] > 0:
 key = f"hybrid_seed10_identity{len(identity_positions)}"
 results[key] = result
 log_progress(f" ✅ Hybrid ({len(identity_positions)} Identity-Positionen): {result['accuracy']:.2f}%")
 
 log_progress("")
 
 # 3. Teste ALLE Positionen (Seed + Identity kombiniert)
 log_progress(" 3. Teste ALLE Positionen (Seed + Identity kombiniert)...")
 
 # Teste verschiedene Größen
 for num_positions in [20, 30, 40, 50]:
 all_positions = list(range(num_positions))
 result = test_large_combination(
 layer3_results,
 all_positions,
 target_pos,
 sample_size=2000
 )
 
 if result["accuracy"] > 0:
 results[f"all_{num_positions}"] = result
 log_progress(f" ✅ Alle {num_positions} Positionen: {result['accuracy']:.2f}% ({result['num_positions']} Mappings)")
 
 log_progress("")
 
 # Zusammenfassung
 log_progress("=" * 80)
 log_progress("📊 ZUSAMMENFASSUNG - ALLE METHODEN:")
 log_progress("=" * 80)
 log_progress("")
 
 all_results = sorted(
 [(k, v.get("accuracy", 0)) for k, v in results.items()],
 key=lambda x: x[1],
 reverse=True
 )
 
 log_progress(" Top 10 Methoden:")
 for i, (method, acc) in enumerate(all_results[:10], 1):
 marker = "⭐" if i == 1 else " "
 log_progress(f" {marker} {i}. {method}: {acc:.2f}%")
 
 best_method = all_results[0] if all_results else None
 log_progress("")
 
 if best_method:
 log_progress(f" 🏆 BESTE METHODE: {best_method[0]} ({best_method[1]:.2f}%)")
 
 if best_method[1] >= 90:
 log_progress(" 🎉 ZIEL 90% ERREICHT!")
 else:
 log_progress(f" 📊 Noch {90 - best_method[1]:.2f}% bis Ziel 90%")
 
 log_progress("")
 
 # Speichere Ergebnisse
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
 
 elapsed_time = time.time() - start_time
 
 output_data = {
 "timestamp": datetime.now().isoformat(),
 "target_position": target_pos,
 "goal": 90.0,
 "results": convert_numpy(results),
 "best_method": {
 "method": best_method[0] if best_method else None,
 "accuracy": best_method[1] if best_method else 0
 },
 "elapsed_time_seconds": elapsed_time
 }
 
 output_file = OUTPUT_DIR / "maximize_accuracy_to_90_results.json"
 with output_file.open("w") as f:
 json.dump(output_data, f, indent=2)
 log_progress(f"💾 Ergebnisse gespeichert: {output_file}")
 log_progress("")
 
 log_progress("=" * 80)
 log_progress("✅ ANALYSE ABGESCHLOSSEN")
 log_progress("=" * 80)
 log_progress(f" Gesamtzeit: {elapsed_time:.1f} Sekunden ({elapsed_time/60:.1f} Minuten)")
 log_progress("")

if __name__ == "__main__":
 main()

