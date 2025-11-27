#!/usr/bin/env python3
"""
LightGBM-Training for Position 27 (Ziel: >50% Accuracy)
- nutzt dieselben Features wie ml_position27_50percent.py
- verwendet class-weighted Sample Weights
- meldet Live-Status + speichert Ergebnisse
"""

from __future__ import annotations

import json
import sys
import time
from collections import Counter
from datetime import datetime
from pathlib import Path
from typing import Dict, Tuple, Optional

import numpy as np

try:
 from lightgbm import LGBMClassifier
 from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
 from sklearn.model_selection import train_test_split, StratifiedKFold, cross_val_score
except ImportError:
 print("❌ lightgbm oder sklearn nicht installiert. Bitte vorher pip install lightgbm scikit-learn ausführen.")
 sys.exit(1)

PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from scripts.research.ml_position27_50percent import ( # type: ignore
 extract_features,
 load_anna_matrix,
 MATRIX_FILE,
)

DATA_FILE = PROJECT_ROOT / "outputs" / "derived" / "rpc_validation_pos27_extended_dataset.json"
STATUS_FILE = PROJECT_ROOT / "outputs" / "derived" / "ml_position27_lightgbm_status.txt"
RESULTS_FILE = PROJECT_ROOT / "outputs" / "derived" / "ml_position27_lightgbm_results.json"

def log(message: str) -> None:
 timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
 line = f"[{timestamp}] {message}"
 STATUS_FILE.parent.mkdir(parents=True, exist_ok=True)
 with STATUS_FILE.open("a") as fh:
 fh.write(line + "\n")
 print(line)

def load_dataset(target_pos: int, matrix: Optional[np.ndarray]) -> Tuple[np.ndarray, np.ndarray]:
 if not DATA_FILE.exists():
 raise FileNotFoundError(f"{DATA_FILE} fehlt.")
 with DATA_FILE.open() as fh:
 data = json.load(fh)
 entries = data.get("data", [])
 log(f"📦 Load {len(entries)} Einträge...")

 X_list = []
 y_list = []
 for idx, entry in enumerate(entries):
 if (idx + 1) % 2000 == 0:
 log(f" Feature-Extraction: {idx + 1}/{len(entries)}")
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
 STATUS_FILE.write_text("=" * 80 + "\nLIGHTGBM TRAINING POS 27\n" + "=" * 80 + "\n")

 matrix = load_anna_matrix(MATRIX_FILE) if MATRIX_FILE.exists() else None
 target_pos = 27
 X, y = load_dataset(target_pos, matrix)

 X_train, X_test, y_train, y_test = train_test_split(
 X, y, test_size=0.2, random_state=42, stratify=y
 )
 class_counts = Counter(y_train)
 total = sum(class_counts.values())
 weights = {cls: total / (len(class_counts) * count) for cls, count in class_counts.items()}
 sample_weight_train = np.array([weights[label] for label in y_train])

 log("🚀 Trainiere LightGBM...")
 params = {
 "n_estimators": 700,
 "learning_rate": 0.05,
 "max_depth": -1,
 "num_leaves": 63,
 "subsample": 0.8,
 "colsample_bytree": 0.8,
 "reg_lambda": 0.8,
 "random_state": 42,
 "verbose": -1,
 }
 model = LGBMClassifier(**params)
 start = time.time()
 model.fit(X_train, y_train, sample_weight=sample_weight_train)
 duration = time.time() - start

 y_pred = model.predict(X_test)
 accuracy = accuracy_score(y_test, y_pred) * 100
 log(f"✅ Test-Accuracy: {accuracy:.2f}% (Trainzeit {duration:.1f}s)")

 cv = StratifiedKFold(n_splits=3, shuffle=True, random_state=42)
 cv_scores = cross_val_score(model, X, y, cv=cv, scoring="accuracy")
 log(f"📊 Cross-Validation: {cv_scores.mean() * 100:.2f}% ± {cv_scores.std() * 100:.2f}%")

 report = classification_report(y_test, y_pred, output_dict=True, zero_division=0)
 cm = confusion_matrix(y_test, y_pred).tolist()

 RESULTS_FILE.parent.mkdir(parents=True, exist_ok=True)
 with RESULTS_FILE.open("w") as fh:
 json.dump(
 {
 "timestamp": datetime.now().isoformat(),
 "params": params,
 "test_accuracy": accuracy,
 "cv_mean": cv_scores.mean() * 100,
 "cv_std": cv_scores.std() * 100,
 "classification_report": report,
 "confusion_matrix": cm,
 "duration_seconds": duration,
 },
 fh,
 indent=2,
 )
 log(f"💾 Ergebnisse gespeichert: {RESULTS_FILE}")

if __name__ == "__main__":
 main()

