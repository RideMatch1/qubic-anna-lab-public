#!/usr/bin/env python3
"""
Machine Learning Accuracy-Optimierung - Background Script
- Alle 55 Seed-Positionen als Features (OHNE triviale Position 27!)
- Zusätzliche Features (Block-Positionen, etc.)
- Verschiedene ML-Modelle (Decision Tree, Random Forest, Gradient Boosting)
- Cross-Validation
- Feature Importance
- Live-Fortschrittsanzeige
- KEINE Halluzinationen - nur echte Daten!

MANUELL AUSFÜHREN:
 python3 scripts/research/ml_accuracy_optimization_background.py

FORTSCHRITT ANZEIGEN:
 tail -f outputs/derived/ml_accuracy_optimization_status.txt
"""

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
 sys.exit(1)

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# Paths
LAYER3_FILE = project_root / "outputs" / "derived" / "layer3_derivation_23k_complete.json"
MATRIX_FILE = project_root / "data" / "anna-matrix" / "Anna_Matrix.xlsx"
OUTPUT_DIR = project_root / "outputs" / "derived"
STATUS_FILE = project_root / "outputs" / "derived" / "ml_accuracy_optimization_status.txt"
PROGRESS_FILE = project_root / "outputs" / "derived" / "ml_accuracy_optimization_progress.json"

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

def load_anna_matrix(matrix_file: Path) -> np.ndarray:
 """Load Anna Matrix."""
 try:
 df = pd.read_excel(matrix_file, header=None)
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
 # Konvertiere zu numerisch (A=0, B=1, ..., Z=25)
 char = seed[i].upper()
 features[f"seed_{i}"] = ord(char) - ord('A')
 else:
 features[f"seed_{i}"] = -1
 
 # 2. Block-Positionen (0-13, 14-27, 28-41, 42-55) - OHNE triviale Position 27!
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
 # Position 27 könnte zu Matrix(27, 13) mappen
 try:
 matrix_val = matrix[27, 13]
 features["matrix_27_13"] = matrix_val
 features["matrix_27_13_mod26"] = int(matrix_val) % 26
 features["matrix_27_13_mod4"] = int(matrix_val) % 4
 except:
 pass
 
 # 5. Seed-Statistiken
 seed_chars = [ord(c.upper()) - ord('A') for c in seed[:55]]
 features["seed_mean"] = np.mean(seed_chars) if seed_chars else 0
 features["seed_std"] = np.std(seed_chars) if seed_chars else 0
 features["seed_min"] = np.min(seed_chars) if seed_chars else 0
 features["seed_max"] = np.max(seed_chars) if seed_chars else 0
 
 return features

def prepare_ml_data(layer3_data: List[Dict], target_pos: int, matrix: Optional[np.ndarray] = None, 
 max_samples: Optional[int] = None) -> Tuple[np.ndarray, np.ndarray]:
 """Bereite Daten for Machine Learning vor."""
 
 log_progress(f" Bereite ML-Daten vor (Target: Position {target_pos})...")
 
 X_list = []
 y_list = []
 
 data_to_use = layer3_data[:max_samples] if max_samples else layer3_data
 total = len(data_to_use)
 
 for idx, entry in enumerate(data_to_use):
 if (idx + 1) % 1000 == 0:
 progress = 100*(idx+1)/total
 log_progress(f" Fortschritt: {idx + 1}/{total} ({progress:.1f}%)")
 save_progress({
 "step": "prepare_data",
 "progress": progress,
 "processed": idx + 1,
 "total": total
 })
 
 l3_id = entry.get("layer3_identity", "")
 if not l3_id or len(l3_id) <= target_pos:
 continue
 
 seed = identity_to_seed(l3_id)
 if len(seed) < 55:
 continue
 
 # Extrahiere Features
 features = extract_features(l3_id, seed, target_pos, matrix)
 
 # Konvertiere zu Array
 feature_vector = list(features.values())
 X_list.append(feature_vector)
 
 # Target: Character an Position target_pos
 target_char = l3_id[target_pos].upper()
 y_list.append(ord(target_char) - ord('A'))
 
 X = np.array(X_list)
 y = np.array(y_list)
 
 log_progress(f" ✅ {len(X)} Samples, {X.shape[1]} Features")
 
 return X, y

def test_decision_tree(X: np.ndarray, y: np.ndarray, target_pos: int) -> Dict:
 """Teste Decision Tree."""
 
 log_progress(" Teste Decision Tree...")
 log_progress(" Train/Test Split...")
 save_progress({"step": "decision_tree", "status": "train_test_split"})
 
 # Train/Test Split
 X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
 
 log_progress(" Trainiere Model...")
 save_progress({"step": "decision_tree", "status": "training"})
 # Trainiere Model
 model = DecisionTreeClassifier(max_depth=20, min_samples_split=10, random_state=42)
 model.fit(X_train, y_train)
 
 log_progress(" Teste Model...")
 save_progress({"step": "decision_tree", "status": "testing"})
 # Teste
 y_pred = model.predict(X_test)
 accuracy = accuracy_score(y_test, y_pred) * 100
 
 log_progress(" Cross-Validation (5-Fold)...")
 save_progress({"step": "decision_tree", "status": "cross_validation"})
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

def test_random_forest(X: np.ndarray, y: np.ndarray, target_pos: int) -> Dict:
 """Teste Random Forest."""
 
 log_progress(" Teste Random Forest...")
 log_progress(" Train/Test Split...")
 save_progress({"step": "random_forest", "status": "train_test_split"})
 
 # Train/Test Split
 X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
 
 log_progress(" Trainiere Model (100 Bäume, kann etwas dauern)...")
 save_progress({"step": "random_forest", "status": "training", "note": "100 Bäume"})
 # Trainiere Model
 model = RandomForestClassifier(n_estimators=100, max_depth=20, min_samples_split=10, 
 random_state=42, n_jobs=-1)
 model.fit(X_train, y_train)
 
 log_progress(" Teste Model...")
 save_progress({"step": "random_forest", "status": "testing"})
 # Teste
 y_pred = model.predict(X_test)
 accuracy = accuracy_score(y_test, y_pred) * 100
 
 log_progress(" Cross-Validation (5-Fold)...")
 save_progress({"step": "random_forest", "status": "cross_validation"})
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
 
 log_progress(" Teste Gradient Boosting...")
 log_progress(" Train/Test Split...")
 save_progress({"step": "gradient_boosting", "status": "train_test_split"})
 
 # Train/Test Split
 X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
 
 log_progress(" Trainiere Model (100 Estimators, kann länger dauern)...")
 save_progress({"step": "gradient_boosting", "status": "training", "note": "100 Estimators"})
 # Trainiere Model
 model = GradientBoostingClassifier(n_estimators=100, max_depth=10, learning_rate=0.1, 
 random_state=42)
 model.fit(X_train, y_train)
 
 log_progress(" Teste Model...")
 save_progress({"step": "gradient_boosting", "status": "testing"})
 # Teste
 y_pred = model.predict(X_test)
 accuracy = accuracy_score(y_test, y_pred) * 100
 
 log_progress(" Cross-Validation (5-Fold)...")
 save_progress({"step": "gradient_boosting", "status": "cross_validation"})
 # Cross-Validation
 cv_scores = cross_val_score(model, X, y, cv=5, scoring='accuracy')
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

def main():
 """Hauptfunktion."""
 
 STATUS_FILE.parent.mkdir(parents=True, exist_ok=True)
 PROGRESS_FILE.parent.mkdir(parents=True, exist_ok=True)
 
 # Initialisiere Status-Datei
 with STATUS_FILE.open("w") as f:
 f.write("=" * 80 + "\n")
 f.write("MACHINE LEARNING ACCURACY-OPTIMIERUNG - BACKGROUND SCRIPT\n")
 f.write("=" * 80 + "\n")
 f.write(f"Gestartet: {datetime.now().isoformat()}\n")
 f.write("=" * 80 + "\n\n")
 
 # Initialisiere Progress-Datei
 save_progress({
 "status": "starting",
 "timestamp": datetime.now().isoformat()
 })
 
 log_progress("=" * 80)
 log_progress("MACHINE LEARNING ACCURACY-OPTIMIERUNG - BACKGROUND SCRIPT")
 log_progress("=" * 80)
 log_progress("⚠️ KEINE HALLUZINATIONEN - NUR ECHTE DATEN!")
 log_progress("🔬 SYSTEMATISCH, PERFEKT, ZIEL: 90-99% ACCURACY!")
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
 save_progress({"step": "prepare_ml_data"})
 X, y = prepare_ml_data(layer3_results, target_pos, matrix, max_samples=10000)
 log_progress("")
 
 results = {}
 
 # 2. Teste verschiedene ML-Modelle
 log_progress(" 2. Teste verschiedene ML-Modelle...")
 log_progress("")
 
 # Decision Tree
 dt_result = test_decision_tree(X, y, target_pos)
 results["decision_tree"] = dt_result
 log_progress(f" ✅ Decision Tree: {dt_result['test_accuracy']:.2f}% (CV: {dt_result['cv_mean']:.2f}% ± {dt_result['cv_std']:.2f}%)")
 save_progress({
 "step": "decision_tree",
 "status": "completed",
 "accuracy": dt_result['test_accuracy'],
 "cv_mean": dt_result['cv_mean']
 })
 log_progress("")
 
 # Random Forest
 rf_result = test_random_forest(X, y, target_pos)
 results["random_forest"] = rf_result
 log_progress(f" ✅ Random Forest: {rf_result['test_accuracy']:.2f}% (CV: {rf_result['cv_mean']:.2f}% ± {rf_result['cv_std']:.2f}%)")
 save_progress({
 "step": "random_forest",
 "status": "completed",
 "accuracy": rf_result['test_accuracy'],
 "cv_mean": rf_result['cv_mean']
 })
 log_progress("")
 
 # Gradient Boosting
 gb_result = test_gradient_boosting(X, y, target_pos)
 results["gradient_boosting"] = gb_result
 log_progress(f" ✅ Gradient Boosting: {gb_result['test_accuracy']:.2f}% (CV: {gb_result['cv_mean']:.2f}% ± {gb_result['cv_std']:.2f}%)")
 save_progress({
 "step": "gradient_boosting",
 "status": "completed",
 "accuracy": gb_result['test_accuracy'],
 "cv_mean": gb_result['cv_mean']
 })
 log_progress("")
 
 # Zusammenfassung
 log_progress("=" * 80)
 log_progress("📊 ZUSAMMENFASSUNG - ALLE ML-MODELLE:")
 log_progress("=" * 80)
 log_progress("")
 
 all_results = [
 ("Decision Tree", dt_result["test_accuracy"], dt_result["cv_mean"]),
 ("Random Forest", rf_result["test_accuracy"], rf_result["cv_mean"]),
 ("Gradient Boosting", gb_result["test_accuracy"], gb_result["cv_mean"])
 ]
 
 best_model = max(all_results, key=lambda x: x[1])
 
 log_progress(" Alle Modelle (Test Accuracy):")
 for name, test_acc, cv_acc in sorted(all_results, key=lambda x: x[1], reverse=True):
 marker = "⭐" if (name, test_acc, cv_acc) == best_model else " "
 log_progress(f" {marker} {name}: {test_acc:.2f}% (CV: {cv_acc:.2f}%)")
 
 log_progress("")
 log_progress(f" 🏆 BESTES MODELL: {best_model[0]} ({best_model[1]:.2f}%)")
 
 if best_model[1] >= 90:
 log_progress(" 🎉 ZIEL 90% ERREICHT!")
 else:
 log_progress(f" 📊 Noch {90 - best_model[1]:.2f}% bis Ziel 90%")
 log_progress(f" 📊 Aktuell: {best_model[1]:.2f}% / 90% = {best_model[1]/90*100:.1f}% des Ziels")
 
 log_progress("")
 
 # Feature Importance
 log_progress("📊 TOP 10 FEATURES (Random Forest):")
 log_progress("")
 feature_names = [f"seed_{i}" for i in range(55) if i != target_pos] + ["block_end_0", "block_end_2", "block_end_3",
 "block_num", "pos_in_block"]
 if matrix is not None:
 feature_names.extend(["matrix_27_13", "matrix_27_13_mod26", "matrix_27_13_mod4"])
 feature_names.extend(["seed_mean", "seed_std", "seed_min", "seed_max"])
 
 top_features = rf_result["top_features"]
 log_progress(" Top 10 wichtigste Features:")
 for i, feat_idx in enumerate(top_features[:10], 1):
 feat_name = feature_names[feat_idx] if feat_idx < len(feature_names) else f"feature_{feat_idx}"
 importance = rf_result["feature_importance"][feat_idx]
 log_progress(f" {i}. {feat_name}: {importance:.4f}")
 
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
 "num_samples": len(X),
 "num_features": X.shape[1],
 "feature_names": feature_names,
 "results": convert_numpy(results),
 "best_model": {
 "name": best_model[0],
 "test_accuracy": best_model[1],
 "cv_mean": best_model[2]
 },
 "elapsed_time_seconds": elapsed_time
 }
 
 output_file = OUTPUT_DIR / "ml_accuracy_optimization_results.json"
 with output_file.open("w") as f:
 json.dump(output_data, f, indent=2)
 log_progress(f"💾 Ergebnisse gespeichert: {output_file}")
 log_progress("")
 
 save_progress({
 "status": "completed",
 "best_model": best_model[0],
 "best_accuracy": best_model[1],
 "elapsed_time_seconds": elapsed_time
 })
 
 log_progress("=" * 80)
 log_progress("✅ ANALYSE ABGESCHLOSSEN")
 log_progress("=" * 80)
 log_progress(f" Gesamtzeit: {elapsed_time:.1f} Sekunden ({elapsed_time/60:.1f} Minuten)")
 log_progress("")

if __name__ == "__main__":
 main()

