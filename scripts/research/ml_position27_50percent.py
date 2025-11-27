#!/usr/bin/env python3
"""
Machine Learning for Position 27 - Ziel: 50%+ Accuracy
- Nutzt validierte 20k RPC-Daten
- Alle 55 Seed-Positionen als Features
- Zusätzliche Features (Matrix-Werte, Block-Positionen, etc.)
- Verschiedene ML-Modelle (Decision Tree, Random Forest, Gradient Boosting)
- Cross-Validation
- Feature Importance
- KEINE Halluzinationen - nur echte Daten!

MANUELL AUSFÜHREN:
 python3 scripts/research/ml_position27_50percent.py

FORTSCHRITT ANZEIGEN:
 tail -f outputs/derived/ml_position27_50percent_status.txt
"""

import argparse
import json
import sys
import time
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from collections import Counter, defaultdict
from datetime import datetime
import numpy as np
import pandas as pd

# Machine Learning
try:
 from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
 from sklearn.tree import DecisionTreeClassifier
 from sklearn.model_selection import train_test_split, cross_val_score, KFold
 from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
 from sklearn.preprocessing import LabelEncoder
 SKLEARN_AVAILABLE = True
except ImportError:
 SKLEARN_AVAILABLE = False
 print("⚠️ sklearn nicht verfügbar - installiere mit: pip install scikit-learn")

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# Paths
VALIDATED_DATA_FILE = project_root / "outputs" / "derived" / "rpc_validation_pos27_extended_dataset.json"
LAYER3_FILE = project_root / "outputs" / "derived" / "layer3_derivation_23k_complete.json"
MATRIX_FILE = project_root / "data" / "anna-matrix" / "Anna_Matrix.xlsx"
OUTPUT_DIR = project_root / "outputs" / "derived"
STATUS_FILE = project_root / "outputs" / "derived" / "ml_position27_50percent_status.txt"
RESULTS_FILE = project_root / "outputs" / "derived" / "ml_position27_50percent_results.json"

def log_progress(message: str, status_file: Path = STATUS_FILE):
 """Schreibe Fortschritt in Status-Datei."""
 timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
 with status_file.open("a") as f:
 f.write(f"[{timestamp}] {message}\n")
 print(f"[{timestamp}] {message}")

def identity_to_seed(identity: str) -> str:
 """Konvertiere Identity zu Seed."""
 return identity.lower()[:55]

def load_anna_matrix(matrix_file: Path) -> Optional[np.ndarray]:
 """Load Anna Matrix."""
 try:
 df = pd.read_excel(matrix_file, header=None)
 df = df.apply(pd.to_numeric, errors="coerce").fillna(0)
 matrix = df.values.astype(float)
 if matrix.shape != (128, 128):
 matrix = matrix[:128, :128]
 return matrix
 except Exception as e:
 log_progress(f"⚠️ Matrix konnte nicht geloadn werden: {e}")
 return None

def extract_features(identity: str, seed: str, target_pos: int, matrix: Optional[np.ndarray] = None) -> Dict:
 """Extrahiere Features aus Identity und Seed."""
 features = {}
 
 # 1. Alle 55 Seed-Positionen (Hauptfeatures!) - OHNE triviale Position 27!
 for i in range(55):
 if i == target_pos: # Skip trivial!
 continue
 if i < len(seed):
 char = seed[i].upper()
 features[f"seed_{i}"] = ord(char) - ord('A')
 else:
 features[f"seed_{i}"] = -1
 
 # 2. Block-Positionen (13, 27, 41, 55) - OHNE triviale Position 27!
 block_positions = [13, 27, 41, 55]
 for i, block_pos in enumerate(block_positions):
 if block_pos == target_pos: # Skip trivial!
 continue
 if block_pos < len(identity):
 char = identity[block_pos].upper()
 features[f"block_end_{i}"] = ord(char) - ord('A')
 else:
 features[f"block_end_{i}"] = -1
 
 # 3. Position relativ zu Block
 block_num = target_pos // 14
 pos_in_block = target_pos % 14
 features["block_num"] = block_num
 features["pos_in_block"] = pos_in_block
 
 # 4. Matrix-Werte (wenn verfügbar)
 if matrix is not None:
 try:
 matrix_val = matrix[27, 13]
 features["matrix_27_13"] = matrix_val
 features["matrix_27_13_mod26"] = int(matrix_val) % 26
 features["matrix_27_13_mod4"] = int(matrix_val) % 4
 except:
 pass
 
 # 5. Seed-Statistiken
 seed_slice = seed[:55]
 seed_chars = [ord(c.upper()) - ord('A') for c in seed_slice]
 features["seed_mean"] = np.mean(seed_chars) if seed_chars else 0
 features["seed_std"] = np.std(seed_chars) if seed_chars else 0
 features["seed_min"] = np.min(seed_chars) if seed_chars else 0
 features["seed_max"] = np.max(seed_chars) if seed_chars else 0
 vowels = set("AEIOU")
 vowel_count = sum(1 for ch in seed_slice.upper() if ch in vowels)
 features["seed_vowel_ratio"] = vowel_count / 55
 features["seed_consonant_ratio"] = (55 - vowel_count) / 55
 unique_chars = len(set(seed_slice.upper()))
 features["seed_unique_ratio"] = unique_chars / 55
 features["seed_repeat_ratio"] = 1 - features["seed_unique_ratio"]
 features["seed_bigram_bd_count"] = seed_slice.upper().count("BD")

 # 5b. Block-Top-Char Features + letter fractions
 blocks = [(0, 14), (14, 28), (28, 42), (42, 55)]
 for idx, (start, end) in enumerate(blocks):
 block = seed[start:end]
 if block:
 counts = Counter(block.upper())
 top_char = max(counts.items(), key=lambda x: x[1])[0]
 features[f"block_{idx}_topchar"] = ord(top_char) - ord('A')
 block_len = len(block)
 block_upper = block.upper()
 features[f"block_{idx}_b_fraction"] = block_upper.count("B") / block_len
 features[f"block_{idx}_d_fraction"] = block_upper.count("D") / block_len
 features[f"block_{idx}_vowel_fraction"] = sum(1 for ch in block_upper if ch in vowels) / block_len
 else:
 features[f"block_{idx}_topchar"] = -1
 features[f"block_{idx}_b_fraction"] = 0
 features[f"block_{idx}_d_fraction"] = 0
 features[f"block_{idx}_vowel_fraction"] = 0

 
 # 6. Seed-Position Interaktionen (Top 10 Seed-Positionen)
 # Basierend auf vorherigen Analysen
 top_seed_positions = [33, 4, 30, 54, 0, 1, 2, 3, 5, 6]
 for i, pos1 in enumerate(top_seed_positions[:5]):
 for j, pos2 in enumerate(top_seed_positions[5:10]):
 if pos1 < len(seed) and pos2 < len(seed):
 char1 = ord(seed[pos1].upper()) - ord('A')
 char2 = ord(seed[pos2].upper()) - ord('A')
 features[f"seed_interaction_{i}_{j}"] = char1 * char2
 
 return features

def prepare_ml_data(validated_data: List[Dict], matrix: Optional[np.ndarray] = None, 
 target_pos: int = 27) -> Tuple[np.ndarray, np.ndarray]:
 """Bereite Daten for Machine Learning vor."""
 
 log_progress(f" Bereite ML-Daten vor (Target: Position {target_pos})...")
 
 X_list = []
 y_list = []
 
 total = len(validated_data)
 for idx, entry in enumerate(validated_data):
 if (idx + 1) % 1000 == 0:
 log_progress(f" Fortschritt: {idx + 1}/{total} ({100*(idx+1)/total:.1f}%)")
 
 identity = entry.get("identity", "")
 seed = entry.get("seed", "")
 
 if not identity or not seed or len(identity) <= target_pos or len(seed) < 55:
 continue
 
 # Extrahiere Features
 features = extract_features(identity, seed, target_pos, matrix)
 
 # Konvertiere zu Array
 feature_vector = list(features.values())
 X_list.append(feature_vector)
 
 # Target: Character an Position target_pos
 target_char = identity[target_pos].upper()
 y_list.append(ord(target_char) - ord('A'))
 
 X = np.array(X_list)
 y = np.array(y_list)
 
 log_progress(f" ✅ {len(X)} Samples, {X.shape[1]} Features")
 
 return X, y

def test_decision_tree(X: np.ndarray, y: np.ndarray, target_pos: int) -> Dict:
 """Teste Decision Tree."""
 
 log_progress(" Teste Decision Tree...")
 
 # Train/Test Split
 X_train, X_test, y_train, y_test = train_test_split(
 X, y, test_size=0.2, random_state=42, stratify=y
 )
 
 # Trainiere Model
 model = DecisionTreeClassifier(max_depth=30, min_samples_split=5, random_state=42)
 # class weights proportional to inverse frequency
 class_weights = Counter(y_train)
 total = sum(class_weights.values())
 weights = {cls: total / (len(class_weights) * count) for cls, count in class_weights.items()}
 sample_weight = np.array([weights[label] for label in y_train])
 model.fit(X_train, y_train, sample_weight=sample_weight)
 
 # Teste
 y_pred = model.predict(X_test)
 accuracy = accuracy_score(y_test, y_pred) * 100
 
 # Cross-Validation
 cv_scores = cross_val_score(model, X, y, cv=5, scoring='accuracy')
 cv_mean = cv_scores.mean() * 100
 cv_std = cv_scores.std() * 100
 
 # Feature Importance
 feature_importance = model.feature_importances_
 top_features = np.argsort(feature_importance)[-10:][::-1]
 
 return {
 "model": "DecisionTree",
 "test_accuracy": accuracy,
 "cv_mean": cv_mean,
 "cv_std": cv_std,
 "top_features": top_features.tolist(),
 "feature_importance": feature_importance.tolist()
 }

def test_random_forest(X: np.ndarray, y: np.ndarray, target_pos: int, best_params: Optional[Dict] = None) -> Dict:
 """Teste Random Forest."""
 
 log_progress(" Teste Random Forest...")
 
 # Train/Test Split
 X_train, X_test, y_train, y_test = train_test_split(
 X, y, test_size=0.2, random_state=42, stratify=y
 )
 
 # Trainiere Model
 rf_params = {
 "n_estimators": 200,
 "max_depth": 30,
 "min_samples_split": 5,
 "random_state": 42,
 "n_jobs": -1,
 }
 if best_params:
 rf_params.update(best_params)
 log_progress(f" ↳ Nutze abovegebene RF-Parameter: {best_params}")
 model = RandomForestClassifier(**rf_params)
 class_weights = Counter(y_train)
 total = sum(class_weights.values())
 weights = {cls: total / (len(class_weights) * count) for cls, count in class_weights.items()}
 sample_weight = np.array([weights[label] for label in y_train])
 model.fit(X_train, y_train, sample_weight=sample_weight)
 
 # Teste
 y_pred = model.predict(X_test)
 accuracy = accuracy_score(y_test, y_pred) * 100
 
 # Cross-Validation
 cv_scores = cross_val_score(model, X, y, cv=5, scoring='accuracy')
 cv_mean = cv_scores.mean() * 100
 cv_std = cv_scores.std() * 100
 
 # Feature Importance
 feature_importance = model.feature_importances_
 top_features = np.argsort(feature_importance)[-10:][::-1]
 
 return {
 "model": "RandomForest",
 "test_accuracy": accuracy,
 "cv_mean": cv_mean,
 "cv_std": cv_std,
 "top_features": top_features.tolist(),
 "feature_importance": feature_importance.tolist()
 }

def test_gradient_boosting(X: np.ndarray, y: np.ndarray, target_pos: int) -> Dict:
 """Teste Gradient Boosting."""
 
 log_progress(" Teste Gradient Boosting (optimierte Parameter)...")
 
 # Train/Test Split
 X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
 
 # Trainiere Model (kleiner & effizienter)
 model = GradientBoostingClassifier(
 n_estimators=100,
 max_depth=5,
 learning_rate=0.08,
 random_state=42
 )
 class_weights = Counter(y_train)
 total = sum(class_weights.values())
 weights = {cls: total / (len(class_weights) * count) for cls, count in class_weights.items()}
 sample_weight = np.array([weights[label] for label in y_train])
 model.fit(X_train, y_train, sample_weight=sample_weight)
 
 # Teste
 y_pred = model.predict(X_test)
 accuracy = accuracy_score(y_test, y_pred) * 100
 
 # Cross-Validation
 cv = KFold(n_splits=3, shuffle=True, random_state=42)
 cv_scores = cross_val_score(model, X, y, cv=cv, scoring='accuracy')
 cv_mean = cv_scores.mean() * 100
 cv_std = cv_scores.std() * 100
 
 # Feature Importance
 feature_importance = model.feature_importances_
 top_features = np.argsort(feature_importance)[-10:][::-1]
 
 return {
 "model": "GradientBoosting",
 "test_accuracy": accuracy,
 "cv_mean": cv_mean,
 "cv_std": cv_std,
 "top_features": top_features.tolist(),
 "feature_importance": feature_importance.tolist()
 }

def load_best_params(path: Optional[Path]) -> Optional[Dict]:
 if not path:
 return None
 if not path.exists():
 log_progress(f"⚠️ Best-Params Datei nicht gefunden: {path}")
 return None
 with path.open() as fh:
 data = json.load(fh)
 return data.get("best_params")

def main():
 """Hauptfunktion."""
 
 if not SKLEARN_AVAILABLE:
 log_progress("❌ sklearn nicht verfügbar - installiere mit: pip install scikit-learn")
 return
 
 parser = argparse.ArgumentParser(description="ML Training Pos27")
 parser.add_argument("--best-params", type=str, help="Pfad zu JSON mit RandomForest Best-Params", default=None)
 args = parser.parse_args()
 
 STATUS_FILE.parent.mkdir(parents=True, exist_ok=True)
 with STATUS_FILE.open("w") as f:
 f.write("=" * 80 + "\n")
 f.write("MACHINE LEARNING FÜR POSITION 27 - ZIEL: 50%+ ACCURACY\n")
 f.write("=" * 80 + "\n")
 f.write(f"Gestartet: {datetime.now().isoformat()}\n")
 f.write("=" * 80 + "\n\n")
 
 log_progress("=" * 80)
 log_progress("MACHINE LEARNING FÜR POSITION 27 - ZIEL: 50%+ ACCURACY")
 log_progress("=" * 80)
 log_progress("⚠️ KEINE HALLUZINATIONEN - NUR ECHTE DATEN!")
 log_progress("🔬 NUTZT ERWEITERTE POS-27-DATEN (20K + B/D Targeting)!")
 log_progress("")
 
 # Load validierte Daten
 log_progress("📂 Load validierte Daten...")
 
 if not VALIDATED_DATA_FILE.exists():
 log_progress(f"❌ Validierte Daten nicht gefunden: {VALIDATED_DATA_FILE}")
 log_progress(" Führe zuerst RPC-Validierung aus: ./start_rpc_validation_20000.sh")
 return
 
 with VALIDATED_DATA_FILE.open() as f:
 validated_data_json = json.load(f)
 validated_data = validated_data_json.get("data", [])
 log_progress(f"✅ {len(validated_data)} validierte Identities geloadn")
 log_progress("")
 
 # Load Matrix
 matrix = None
 if MATRIX_FILE.exists():
 matrix = load_anna_matrix(MATRIX_FILE)
 if matrix is not None:
 log_progress("✅ Anna Matrix geloadn")
 else:
 log_progress("⚠️ Matrix-Datei nicht gefunden - arbeite ohne Matrix-Features")
 
 log_progress("")
 
 start_time = time.time()
 
 target_pos = 27
 log_progress(f"🔍 POSITION {target_pos} - MACHINE LEARNING OPTIMIERUNG")
 log_progress("")
 
 # Bereite Daten vor
 log_progress(" 1. Bereite ML-Daten vor...")
 X, y = prepare_ml_data(validated_data, matrix, target_pos)
 log_progress("")
 
 if len(X) == 0:
 log_progress("❌ Keine Daten zum Trainieren!")
 return
 
 results = {}
 
 # 2. Teste verschiedene ML-Modelle
 log_progress(" 2. Teste verschiedene ML-Modelle...")
 log_progress("")
 
 # Decision Tree
 dt_result = test_decision_tree(X, y, target_pos)
 results["decision_tree"] = dt_result
 log_progress(f" ✅ Decision Tree: {dt_result['test_accuracy']:.2f}% (CV: {dt_result['cv_mean']:.2f}% ± {dt_result['cv_std']:.2f}%)")
 log_progress("")
 
 # Random Forest
 best_params = load_best_params(Path(args.best_params)) if args.best_params else None
 rf_result = test_random_forest(X, y, target_pos, best_params)
 results["random_forest"] = rf_result
 log_progress(f" ✅ Random Forest: {rf_result['test_accuracy']:.2f}% (CV: {rf_result['cv_mean']:.2f}% ± {rf_result['cv_std']:.2f}%)")
 log_progress("")
 
 # Gradient Boosting
 gb_result = test_gradient_boosting(X, y, target_pos)
 results["gradient_boosting"] = gb_result
 log_progress(f" ✅ Gradient Boosting: {gb_result['test_accuracy']:.2f}% (CV: {gb_result['cv_mean']:.2f}% ± {gb_result['cv_std']:.2f}%)")
 log_progress("")
 
 elapsed_time = time.time() - start_time
 
 # Finde bestes Model
 best_model = max(
 [("DecisionTree", dt_result), ("RandomForest", rf_result), ("GradientBoosting", gb_result)],
 key=lambda x: x[1]["test_accuracy"]
 )
 
 log_progress("=" * 80)
 log_progress("📊 ERGEBNISSE")
 log_progress("=" * 80)
 log_progress("")
 log_progress(f" 🏆 BESTES MODEL: {best_model[0]}")
 log_progress(f" 📈 Accuracy: {best_model[1]['test_accuracy']:.2f}%")
 log_progress(f" 📊 Cross-Validation: {best_model[1]['cv_mean']:.2f}% ± {best_model[1]['cv_std']:.2f}%")
 log_progress("")
 log_progress(f" Gesamtzeit: {elapsed_time:.1f} Sekunden ({elapsed_time/60:.1f} Minuten)")
 log_progress("")
 
 # Speichere Ergebnisse
 OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
 
 output_data = {
 "timestamp": datetime.now().isoformat(),
 "target_position": target_pos,
 "data_source": "rpc_validation_20000_validated_data",
 "samples_count": len(X),
 "features_count": X.shape[1],
 "results": results,
 "best_model": {
 "name": best_model[0],
 "accuracy": best_model[1]["test_accuracy"],
 "cv_mean": best_model[1]["cv_mean"],
 "cv_std": best_model[1]["cv_std"]
 },
 "elapsed_time_seconds": elapsed_time
 }
 
 with RESULTS_FILE.open("w") as f:
 json.dump(output_data, f, indent=2)
 log_progress(f"💾 Ergebnisse gespeichert: {RESULTS_FILE}")
 log_progress("")
 
 # Ziel erreicht?
 if best_model[1]["test_accuracy"] >= 50.0:
 log_progress("=" * 80)
 log_progress("🎉 ZIEL ERREICHT: 50%+ ACCURACY!")
 log_progress("=" * 80)
 else:
 log_progress("=" * 80)
 log_progress("⚠️ ZIEL NOCH NICHT ERREICHT - WEITER OPTIMIEREN")
 log_progress("=" * 80)
 log_progress(f" Aktuell: {best_model[1]['test_accuracy']:.2f}%")
 log_progress(f" Ziel: 50.00%")
 log_progress(f" Differenz: {50.0 - best_model[1]['test_accuracy']:.2f}%")
 log_progress("")
 
 log_progress("=" * 80)
 log_progress("✅ ML-TRAINING ABGESCHLOSSEN")
 log_progress("=" * 80)
 log_progress("")

if __name__ == "__main__":
 main()

