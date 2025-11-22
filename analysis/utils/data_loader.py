"""Helper utilities for loading the Anna Matrix and related data."""
from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Iterable, List, Tuple

import numpy as np
import pandas as pd

BASE_DIR = Path(__file__).resolve().parents[2]
DEFAULT_MATRIX_PATHS: Tuple[Path, ...] = (
    BASE_DIR / "data" / "anna-matrix" / "Anna_Matrix.xlsx",
)
DEFAULT_COMPUTOR_PATH = BASE_DIR / "data" / "computor-data" / "computors.json"

@dataclass(frozen=True)
class MatrixPayload:
    """Container for the Anna matrix and metadata."""

    matrix: np.ndarray
    source_path: Path
    loaded_at: datetime

def load_anna_matrix(candidate_paths: Iterable[Path] | None = None) -> MatrixPayload:
    """Load the Anna matrix from Excel files.

    Args:
        candidate_paths: Optional list of alternative locations to search.

    Returns:
        MatrixPayload with a `(128, 128)` numpy array.

    Raises:
        FileNotFoundError: when no matrix file is available.
    
    The matrix is loaded as float32. Non-numeric cells are coerced to 0.0.
    """
    paths = tuple(candidate_paths) if candidate_paths else DEFAULT_MATRIX_PATHS
    for path in paths:
        if path.exists():
            df = pd.read_excel(path, header=None)
            # Convert to numeric, coerce errors to NaN, then fill NaN with 0.0
            numeric = df.apply(pd.to_numeric, errors="coerce").fillna(0.0)
            matrix = numeric.to_numpy(dtype=float)
            return MatrixPayload(matrix=matrix, source_path=path, loaded_at=datetime.utcnow())
    raise FileNotFoundError("Anna_Matrix.xlsx not found under data/anna-matrix/")

def load_or_generate_computor_positions(count: int = 676, seed: int = 42) -> List[dict]:
    """Load Computor GPS coordinates or generate deterministic placeholders."""

    DEFAULT_COMPUTOR_PATH.parent.mkdir(parents=True, exist_ok=True)
    if DEFAULT_COMPUTOR_PATH.exists():
        with DEFAULT_COMPUTOR_PATH.open("r", encoding="utf-8") as handle:
            data = json.load(handle)
            return data

    rng = np.random.default_rng(seed)
    lats = rng.uniform(-65.0, 65.0, size=count)
    lons = rng.uniform(-170.0, 170.0, size=count)
    data = [
        {"id": idx + 1, "latitude": float(lat), "longitude": float(lon)}
        for idx, (lat, lon) in enumerate(zip(lats, lons))
    ]
    with DEFAULT_COMPUTOR_PATH.open("w", encoding="utf-8") as handle:
        json.dump(data, handle, indent=2)
    return data

def normalize_coordinates(values: np.ndarray, min_val: float, max_val: float) -> np.ndarray:
    """Linearly scale values to the range [0, 127]."""

    clipped = np.clip(values, min_val, max_val)
    normed = (clipped - min_val) / (max_val - min_val)
    return normed * 127.0

def ensure_directory(path: Path) -> Path:
    """Ensure the directory exists and return the path."""

    path.mkdir(parents=True, exist_ok=True)
    return path

__all__ = [
    "MatrixPayload",
    "load_anna_matrix",
    "load_or_generate_computor_positions",
    "normalize_coordinates",
    "ensure_directory",
]
