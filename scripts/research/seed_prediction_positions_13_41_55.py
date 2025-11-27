#!/usr/bin/env python3
"""
Seed-basierte Vorhersage for Position 13, 41, 55
- Gleiche Methode wie Position 27 (alle 55 Seed-Positionen gewichtet)
- Teste alle 3 Block-Ende-Positionen
- Finde beste Seed-Kombinationen
- KEINE RPC-Calls - nur lokale Analyse
- KEINE Halluzinationen - nur echte Daten!

MANUELL AUSFÜHREN:
 python3 scripts/research/seed_prediction_positions_13_41_55.py
"""

import json
import sys
import time
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from collections import Counter, defaultdict
from datetime import datetime
import numpy as np

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# Paths
LAYER3_FILE = project_root / "outputs" / "derived" / "layer3_derivation_23k_complete.json"
OUTPUT_DIR = project_root / "outputs" / "derived"
RESULTS_FILE = project_root / "outputs" / "derived" / "seed_prediction_positions_13_41_55_results.json"
STATUS_FILE = project_root / "outputs" / "derived" / "seed_prediction_positions_13_41_55_status.txt"

def log_progress(message: str, status_file: Path = STATUS_FILE):
 """Schreibe Fortschritt in Status-Datei."""
 timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
 with status_file.open("a") as f:
 f.write(f"[{timestamp}] {message}\n")
 print(f"[{timestamp}] {message}")

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

def test_position(layer3_data: List[Dict], target_pos: int, sample_size: int = 10000) -> Dict:
 """Teste seed-basierte Vorhersage for eine Position."""
 
 log_progress(f" Teste Position {target_pos}...")
 
 # Baue Mappings for alle 55 Seed-Positionen
 mappings = {}
 for seed_pos in range(55):
 if seed_pos == target_pos: # Skip trivial!
 continue
 if (seed_pos + 1) % 10 == 0:
 log_progress(f" {seed_pos + 1}/54 Seed-Positionen...")
 
 mapping = build_seed_mapping(layer3_data, seed_pos, target_pos, min_samples=2)
 if mapping:
 mappings[seed_pos] = mapping
 
 log_progress(f" ✅ {len(mappings)} Mappings erstellt")
 
 # Teste auf Sample
 random_indices = np.random.choice(len(layer3_data), min(sample_size, len(layer3_data)), replace=False)
 test_entries = [layer3_data[i] for i in random_indices]
 
 correct = 0
 total = 0
 
 for entry in test_entries:
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
 
 if predicted == actual:
 correct += 1
 total += 1
 
 accuracy = (correct / total * 100) if total > 0 else 0
 
 # Finde beste Seed-Positionen
 seed_accuracies = {}
 for seed_pos in range(55):
 if seed_pos == target_pos:
 continue
 if seed_pos not in mappings:
 continue
 
 # Teste einzelne Seed-Position
 seed_correct = 0
 seed_total = 0
 for entry in test_entries:
 l3_id = entry.get("layer3_identity", "")
 if not l3_id or len(l3_id) <= target_pos:
 continue
 seed = identity_to_seed(l3_id)
 if len(seed) <= seed_pos:
 continue
 
 pred_result = predict_with_seed(seed, seed_pos, mappings[seed_pos])
 if pred_result:
 char, _ = pred_result
 if char == l3_id[target_pos].upper():
 seed_correct += 1
 seed_total += 1
 
 if seed_total > 0:
 seed_accuracies[seed_pos] = (seed_correct / seed_total * 100)
 
 # Top 10 Seed-Positionen
 top_seeds = sorted(seed_accuracies.items(), key=lambda x: x[1], reverse=True)[:10]
 
 return {
 "target_position": target_pos,
 "accuracy": accuracy,
 "correct": correct,
 "total": total,
 "mappings_count": len(mappings),
 "top_10_seed_positions": [{"position": pos, "accuracy": acc} for pos, acc in top_seeds]
 }

def main():
 """Hauptfunktion."""
 
 STATUS_FILE.parent.mkdir(parents=True, exist_ok=True)
 with STATUS_FILE.open("w") as f:
 f.write("=" * 80 + "\n")
 f.write("SEED-BASIERTE VORHERSAGE - POSITION 13, 41, 55\n")
 f.write("=" * 80 + "\n")
 f.write(f"Gestartet: {datetime.now().isoformat()}\n")
 f.write("=" * 80 + "\n\n")
 
 log_progress("=" * 80)
 log_progress("SEED-BASIERTE VORHERSAGE - POSITION 13, 41, 55")
 log_progress("=" * 80)
 log_progress("⚠️ KEINE HALLUZINATIONEN - NUR ECHTE DATEN!")
 log_progress("🔬 GLEICHE METHODE WIE POSITION 27!")
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
 
 # Teste alle 3 Positionen
 target_positions = [13, 41, 55]
 results = {}
 
 for target_pos in target_positions:
 log_progress(f"🔍 POSITION {target_pos}")
 log_progress("")
 
 result = test_position(layer3_results, target_pos, sample_size=10000)
 results[f"position_{target_pos}"] = result
 
 log_progress(f" ✅ Accuracy: {result['accuracy']:.2f}% ({result['correct']}/{result['total']})")
 log_progress(f" 📊 Top Seed-Position: {result['top_10_seed_positions'][0]['position']} ({result['top_10_seed_positions'][0]['accuracy']:.2f}%)")
 log_progress("")
 
 elapsed_time = time.time() - start_time
 
 # Zusammenfassung
 log_progress("=" * 80)
 log_progress("📊 ZUSAMMENFASSUNG")
 log_progress("=" * 80)
 log_progress("")
 
 for target_pos in target_positions:
 result = results[f"position_{target_pos}"]
 log_progress(f" Position {target_pos}: {result['accuracy']:.2f}% Accuracy")
 
 log_progress("")
 log_progress(f" Gesamtzeit: {elapsed_time:.1f} Sekunden ({elapsed_time/60:.1f} Minuten)")
 log_progress("")
 
 # Speichere Ergebnisse
 OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
 
 output_data = {
 "timestamp": datetime.now().isoformat(),
 "method": "all_55_seeds_weighted",
 "target_positions": target_positions,
 "results": results,
 "elapsed_time_seconds": elapsed_time
 }
 
 with RESULTS_FILE.open("w") as f:
 json.dump(output_data, f, indent=2)
 log_progress(f"💾 Ergebnisse gespeichert: {RESULTS_FILE}")
 log_progress("")
 
 log_progress("=" * 80)
 log_progress("✅ ANALYSE ABGESCHLOSSEN")
 log_progress("=" * 80)
 log_progress("")

if __name__ == "__main__":
 import random
 np.random.seed(42)
 random.seed(42)
 main()

