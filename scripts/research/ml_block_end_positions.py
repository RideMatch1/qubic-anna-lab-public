#!/usr/bin/env python3
"""
ML-Analyse for Block-Ende-Positionen (13, 41, 55)
-------------------------------------------------
Ziel:
 - Dieselbe Datenbasis wie Position 27 nutzen (4015 validierte Identities)
 - Gradient Boosting je Position trainieren/evaluieren
 - Feature-Importances & Confusion-Basics sichern

Ausführung:
 source venv-tx/bin/activate
 python3 scripts/research/ml_block_end_positions.py
"""

from __future__ import annotations

import json
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple, Optional

import numpy as np

try:
 from sklearn.ensemble import GradientBoostingClassifier
 from sklearn.metrics import accuracy_score, classification_report
 from sklearn.model_selection import KFold, cross_val_score, train_test_split
 SKLEARN_AVAILABLE = True
except ImportError:
 SKLEARN_AVAILABLE = False

PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from scripts.research.ml_position27_50percent import ( # type: ignore
 extract_features,
 load_anna_matrix,
 MATRIX_FILE,
)

VALIDATED_FILE = PROJECT_ROOT / "outputs" / "derived" / "rpc_validation_20000_validated_data.json"
STATUS_FILE = PROJECT_ROOT / "outputs" / "derived" / "ml_block_end_positions_status.txt"
RESULTS_FILE = PROJECT_ROOT / "outputs" / "derived" / "ml_block_end_positions_results.json"

TARGET_POSITIONS = [13, 41, 55]

def log(message: str) -> None:
 """Append message to status file + stdout."""
 timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
 line = f"[{timestamp}] {message}"
 with STATUS_FILE.open("a") as fh:
 fh.write(line + "\n")
 print(line)

def prepare_data(target_pos: int, matrix: Optional[np.ndarray]) -> Tuple[np.ndarray, np.ndarray]:
 with VALIDATED_FILE.open() as fh:
 validated = json.load(fh)["data"]

 X, y = [], []
 for entry in validated:
 identity = entry.get("identity", "")
 seed = entry.get("seed", "")
 if len(identity) <= target_pos or len(seed) < 55:
 continue
 feats = extract_features(identity, seed, target_pos, matrix)
 X.append(list(feats.values()))
 y.append(ord(identity[target_pos].upper()) - ord("A"))
 return np.array(X), np.array(y)

def run_model(X: np.ndarray, y: np.ndarray) -> Dict:
 X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
 model = GradientBoostingClassifier(
 n_estimators=100,
 max_depth=5,
 learning_rate=0.08,
 random_state=42,
 )
 model.fit(X_train, y_train)
 y_pred = model.predict(X_test)
 accuracy = accuracy_score(y_test, y_pred) * 100

 cv = KFold(n_splits=3, shuffle=True, random_state=42)
 cv_scores = cross_val_score(model, X, y, cv=cv, scoring="accuracy")

 report = classification_report(y_test, y_pred, output_dict=True, zero_division=0)
 top_idx = np.argsort(model.feature_importances_)[-10:][::-1]

 return {
 "test_accuracy": accuracy,
 "cv_mean": float(cv_scores.mean() * 100),
 "cv_std": float(cv_scores.std() * 100),
 "classification_report": report,
 "top_features": top_idx.tolist(),
 "feature_importance": model.feature_importances_.tolist(),
 }

def main() -> None:
 if not SKLEARN_AVAILABLE:
 print("❌ sklearn fehlt (pip install scikit-learn)")
 return

 STATUS_FILE.parent.mkdir(parents=True, exist_ok=True)
 with STATUS_FILE.open("w") as fh:
 fh.write("=" * 80 + "\n")
 fh.write("ML BLOCK-END POSITIONEN\n")
 fh.write("=" * 80 + "\n")

 if not VALIDATED_FILE.exists():
 log("❌ Validierte RPC-Daten fehlen – bitte zuerst 20k Validation ausführen.")
 return

 matrix = load_anna_matrix(MATRIX_FILE) if MATRIX_FILE.exists() else None
 if matrix is not None:
 log("✅ Anna-Matrix geloadn")

 results = {}
 start = time.time()
 for target in TARGET_POSITIONS:
 log("=" * 80)
 log(f"🔍 Position {target} – Vorbereitung")
 X, y = prepare_data(target, matrix)
 if len(X) == 0:
 log("⚠️ Keine Daten for diese Position gefunden – abovesprungen.")
 continue
 log(f"Samples: {len(X)}, Features: {X.shape[1]}")
 res = run_model(X, y)
 results[target] = res
 log(
 f"✅ Pos {target}: Acc {res['test_accuracy']:.2f}% | "
 f"CV {res['cv_mean']:.2f}% ± {res['cv_std']:.2f}%"
 )

 duration = time.time() - start
 log("=" * 80)
 log(f"Gesamtzeit: {duration:.1f}s")

 output = {
 "timestamp": datetime.now().isoformat(),
 "targets": TARGET_POSITIONS,
 "results": results,
 "elapsed_seconds": duration,
 }
 with RESULTS_FILE.open("w") as fh:
 json.dump(output, fh, indent=2)
 log(f"📝 Ergebnisse gespeichert: {RESULTS_FILE}")

if __name__ == "__main__":
 main()

