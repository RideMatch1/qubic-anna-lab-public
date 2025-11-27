#!/usr/bin/env python3
"""
Maximale Accuracy - Nur nicht-triviale Kombinationen
- Teste Kombinationen OHNE triviale Seed-Positionen
- Fokus auf Position 27 mit Seed-Position 33
- Teste weitere Optimierungen
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

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# Paths
LAYER3_FILE = project_root / "outputs" / "derived" / "layer3_derivation_23k_complete.json"
OUTPUT_DIR = project_root / "outputs" / "derived"
STATUS_FILE = project_root / "outputs" / "derived" / "maximize_accuracy_non_trivial_status.txt"

def log_progress(message: str, status_file: Path = STATUS_FILE):
 """Schreibe Fortschritt in Status-Datei."""
 timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
 with status_file.open("a") as f:
 f.write(f"[{timestamp}] {message}\n")
 print(f"[{timestamp}] {message}")

def identity_to_seed(identity: str) -> str:
 """Konvertiere Identity zu Seed."""
 return identity.lower()[:55]

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

def test_non_trivial_combinations(layer3_data: List[Dict], target_pos: int, top_seed_positions: List[int], sample_size: int = 2000) -> Dict:
 """Teste nicht-triviale Kombinationen (ohne target_pos)."""
 
 # Filtere triviale Positionen
 non_trivial_seeds = [pos for pos in top_seed_positions if pos != target_pos]
 
 if len(non_trivial_seeds) < 2:
 return {}
 
 # Baue Mappings
 mappings = {}
 for seed_pos in non_trivial_seeds:
 mapping = build_seed_mapping(layer3_data, seed_pos, target_pos)
 if mapping:
 mappings[seed_pos] = mapping
 
 if len(mappings) < 2:
 return {}
 
 results = {}
 
 # Teste 2-Position-Kombinationen
 log_progress(f" Teste 2-Position-Kombinationen ({len(non_trivial_seeds)} Positionen)...")
 for combo in combinations(non_trivial_seeds[:10], 2): # Nur Top 10 for Geschwindigkeit
 if combo[0] not in mappings or combo[1] not in mappings:
 continue
 
 correct = 0
 total = 0
 
 for entry in layer3_data[:sample_size]:
 l3_id = entry.get("layer3_identity", "")
 if not l3_id or len(l3_id) <= target_pos:
 continue
 
 seed = identity_to_seed(l3_id)
 
 pred1 = predict_with_seed(seed, combo[0], mappings[combo[0]])
 pred2 = predict_with_seed(seed, combo[1], mappings[combo[1]])
 
 if pred1 is None or pred2 is None:
 continue
 
 # Mehrheitsentscheidung
 if pred1 == pred2:
 predicted = pred1
 else:
 # Bei Uneinigkeit: verwende die mit höherer Erfolgsrate
 # Vereinfacht: verwende erste
 predicted = pred1
 
 actual = l3_id[target_pos].upper()
 if predicted == actual:
 correct += 1
 total += 1
 
 if total > 0:
 accuracy = (correct / total * 100)
 combo_key = f"{combo[0]}_{combo[1]}"
 results[combo_key] = {
 "positions": list(combo),
 "accuracy": accuracy,
 "correct": correct,
 "total": total
 }
 
 # Teste 3-Position-Kombinationen (Top 5)
 log_progress(f" Teste 3-Position-Kombinationen (Top 5)...")
 for combo in combinations(non_trivial_seeds[:5], 3):
 if not all(pos in mappings for pos in combo):
 continue
 
 correct = 0
 total = 0
 
 for entry in layer3_data[:sample_size]:
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
 
 # Mehrheitsentscheidung
 prediction_counter = Counter(predictions)
 predicted = prediction_counter.most_common(1)[0][0]
 
 actual = l3_id[target_pos].upper()
 if predicted == actual:
 correct += 1
 total += 1
 
 if total > 0:
 accuracy = (correct / total * 100)
 combo_key = "_".join(map(str, combo))
 results[combo_key] = {
 "positions": list(combo),
 "accuracy": accuracy,
 "correct": correct,
 "total": total
 }
 
 return results

def main():
 """Hauptfunktion."""
 
 STATUS_FILE.parent.mkdir(parents=True, exist_ok=True)
 with STATUS_FILE.open("w") as f:
 f.write("=" * 80 + "\n")
 f.write("MAXIMALE ACCURACY - NUR NICHT-TRIVIALE KOMBINATIONEN\n")
 f.write("=" * 80 + "\n")
 f.write(f"Gestartet: {datetime.now().isoformat()}\n")
 f.write("=" * 80 + "\n\n")
 
 log_progress("=" * 80)
 log_progress("MAXIMALE ACCURACY - NUR NICHT-TRIVIALE KOMBINATIONEN")
 log_progress("=" * 80)
 log_progress("⚠️ KEINE HALLUZINATIONEN - NUR ECHTE DATEN!")
 log_progress("🔬 KRITISCH, SYSTEMATISCH, PERFEKT")
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
 
 # Fokus auf Position 27
 target_pos = 27
 log_progress(f"🔍 POSITION {target_pos} - NICHT-TRIVIALE KOMBINATIONEN")
 log_progress("")
 
 # Beste Seed-Positionen (aus vorheriger Analyse)
 top_seed_positions = [33, 26, 14, 0, 10, 13, 6, 16, 18, 15] # Top 10 ohne 27
 
 log_progress(f" Top Seed-Positionen: {top_seed_positions}")
 log_progress("")
 
 # Teste nicht-triviale Kombinationen
 combo_results = test_non_trivial_combinations(
 layer3_results,
 target_pos,
 top_seed_positions,
 sample_size=2000
 )
 
 # Finde beste Kombinationen
 if combo_results:
 best_combo2 = max(
 [r for k, r in combo_results.items() if len(r["positions"]) == 2],
 key=lambda x: x["accuracy"],
 default=None
 )
 
 best_combo3 = max(
 [r for k, r in combo_results.items() if len(r["positions"]) == 3],
 key=lambda x: x["accuracy"],
 default=None
 )
 
 log_progress("")
 log_progress("📊 ERGEBNISSE:")
 log_progress("")
 
 if best_combo2:
 log_progress(f" Beste 2-Position-Kombination: {best_combo2['positions']} ({best_combo2['accuracy']:.2f}%)")
 
 if best_combo3:
 log_progress(f" Beste 3-Position-Kombination: {best_combo3['positions']} ({best_combo3['accuracy']:.2f}%)")
 
 # Zeige Top 5 Kombinationen
 all_combos = sorted(combo_results.items(), key=lambda x: x[1]["accuracy"], reverse=True)
 log_progress("")
 log_progress(" Top 5 Kombinationen:")
 for i, (key, data) in enumerate(all_combos[:5], 1):
 log_progress(f" {i}. {data['positions']}: {data['accuracy']:.2f}%")
 
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
 "top_seed_positions": top_seed_positions,
 "combo_results": convert_numpy(combo_results),
 "elapsed_time_seconds": elapsed_time
 }
 
 output_file = OUTPUT_DIR / "maximize_accuracy_non_trivial_results.json"
 with output_file.open("w") as f:
 json.dump(output_data, f, indent=2)
 log_progress(f"💾 Ergebnisse gespeichert: {output_file}")
 log_progress("")
 
 log_progress("=" * 80)
 log_progress("✅ ANALYSE ABGESCHLOSSEN")
 log_progress("=" * 80)
 log_progress(f" Gesamtzeit: {elapsed_time:.1f} Sekunden")
 log_progress("")

if __name__ == "__main__":
 main()

