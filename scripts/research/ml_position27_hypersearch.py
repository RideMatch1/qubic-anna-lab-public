#!/usr/bin/env python3
"""
Hyperparameter-Suche for Pos-27 (Random Forest, class-weighted)
- nutzt den erweiterten Datensatz (20k + B/D Targeting)
- gibt Live-Fortschritt aus und speichert Ergebnisse
"""

from __future__ import annotations

import json
import sys
import time
from collections import Counter
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import RandomizedSearchCV, StratifiedKFold, train_test_split
from sklearn.metrics import accuracy_score

PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from scripts.research.ml_position27_50percent import ( # type: ignore
 extract_features,
 load_anna_matrix,
 MATRIX_FILE,
)

DATA_FILE = PROJECT_ROOT / "outputs" / "derived" / "rpc_validation_pos27_extended_dataset.json"
STATUS_FILE = PROJECT_ROOT / "outputs" / "derived" / "ml_position27_hypersearch_status.txt"
RESULTS_FILE = PROJECT_ROOT / "outputs" / "derived" / "ml_position27_hypersearch_results.json"

def log(msg: str) -> None:
 timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
 line = f"[{timestamp}] {msg}"
 STATUS_FILE.parent.mkdir(parents=True, exist_ok=True)
 with STATUS_FILE.open("a") as fh:
 fh.write(line + "\n")
 print(line)

def load_data(target_pos: int, matrix: Optional[np.ndarray]) -> Tuple[np.ndarray, np.ndarray]:
 with DATA_FILE.open() as fh:
 data = json.load(fh)
 entries = data.get("data", [])
 log(f"📦 Load {len(entries)} Einträge...")

 X_list: List[List[float]] = []
 y_list: List[int] = []
 for idx, entry in enumerate(entries):
 if (idx + 1) % 2000 == 0:
 log(f" Fortschritt Feature-Extraction: {idx + 1}/{len(entries)}")
 identity = entry.get("identity", "")
 seed = entry.get("seed", "")
 if len(identity) <= target_pos or len(seed) < 55:
 continue
 feats = extract_features(identity, seed, target_pos, matrix)
 X_list.append(list(feats.values()))
 y_list.append(ord(identity[target_pos].upper()) - ord("A"))
 log(f"✅ Features fertig: {len(X_list)} Samples, {len(X_list[0]) if X_list else 0} Features")
 return np.array(X_list), np.array(y_list)

def main() -> None:
 STATUS_FILE.write_text("=" * 80 + "\nHYPERPARAMETER-SUCHE POS 27\n" + "=" * 80 + "\n")

 if not DATA_FILE.exists():
 log(f"❌ Datendatei fehlt: {DATA_FILE}")
 return

 matrix = load_anna_matrix(MATRIX_FILE) if MATRIX_FILE.exists() else None
 target_pos = 27
 X, y = load_data(target_pos, matrix)

 X_train, X_test, y_train, y_test = train_test_split(
 X, y, test_size=0.2, random_state=42, stratify=y
 )
 class_weights = Counter(y_train)
 total = sum(class_weights.values())
 weights = {cls: total / (len(class_weights) * count) for cls, count in class_weights.items()}
 sample_weight_train = np.array([weights[label] for label in y_train])

 log("🔍 Starte Randomized Search (Random Forest)...")
 rf = RandomForestClassifier(random_state=42, n_jobs=-1)
 param_dist = {
 "n_estimators": [300, 400, 500, 600],
 "max_depth": [20, 25, 30, 35],
 "min_samples_split": [2, 5, 10],
 "min_samples_leaf": [1, 2, 4],
 "max_features": ["sqrt", "log2", 0.4],
 "bootstrap": [True, False],
 }
 search = RandomizedSearchCV(
 rf,
 param_distributions=param_dist,
 n_iter=25,
 scoring="accuracy",
 cv=StratifiedKFold(n_splits=3, shuffle=True, random_state=42),
 verbose=2,
 random_state=42,
 n_jobs=-1,
 )
 start = time.time()
 search.fit(X_train, y_train, sample_weight=sample_weight_train)
 duration = time.time() - start

 log("✅ Suche beendet")
 log(f" Beste Params: {search.best_params_}")
 log(f" CV-Score: {search.best_score_ * 100:.2f}%")

 best_model = search.best_estimator_
 y_pred = best_model.predict(X_test)
 test_accuracy = accuracy_score(y_test, y_pred) * 100
 log(f"💡 Test-Accuracy: {test_accuracy:.2f}%")

 output = {
 "timestamp": datetime.now().isoformat(),
 "best_params": search.best_params_,
 "cv_best_score": search.best_score_ * 100,
 "test_accuracy": test_accuracy,
 "duration_seconds": duration,
 }
 with RESULTS_FILE.open("w") as fh:
 json.dump(output, fh, indent=2)
 log(f"💾 Ergebnisse gespeichert: {RESULTS_FILE}")

if __name__ == "__main__":
 main()

