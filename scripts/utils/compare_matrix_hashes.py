#!/usr/bin/env python3
"""
Compare matrix files by hashing raw bytes and (optionally) numeric content.

Usage:
 python scripts/compare_matrix_hashes.py file_a.xlsx file_b.csv

For each input it prints:
- SHA-256 of the raw file bytes
- SHA-256 of the normalized numeric payload (if the file can be parsed)
"""

from __future__ import annotations

import argparse
import hashlib
import sys
from pathlib import Path
from typing import Iterable

import numpy as np
import pandas as pd

def sha256_bytes(path: Path) -> str:
 digest = hashlib.sha256()
 with path.open("rb") as handle:
 for chunk in iter(lambda: handle.read(1 << 20), b""):
 digest.update(chunk)
 return digest.hexdigest()

def load_numeric_matrix(path: Path) -> np.ndarray:
 suffix = path.suffix.lower()
 if suffix in {".xlsx", ".xlsm", ".xls"}:
 frame = pd.read_excel(path, header=None)
 elif suffix == ".csv":
 frame = pd.read_csv(path, header=None)
 else:
 raise ValueError(f"Unsupported file type: {path.suffix}")
 numeric = frame.apply(pd.to_numeric, errors="coerce").fillna(0.0)
 return numeric.to_numpy(dtype=np.float32)

def sha256_matrix(path: Path) -> str | None:
 try:
 matrix = load_numeric_matrix(path)
 except Exception as exc: # noqa: BLE001
 print(f"[warn] Could not parse numeric matrix from {path.name}: {exc}")
 return None
 normalized = np.asarray(matrix, dtype=np.float32)
 return hashlib.sha256(normalized.tobytes()).hexdigest()

def print_report(paths: Iterable[Path]) -> None:
 for path in paths:
 print("=" * 72)
 print(f"File: {path}")
 if not path.exists():
 print(" [error] file not found")
 continue
 byte_hash = sha256_bytes(path)
 print(f" SHA256 (raw bytes): {byte_hash}")
 matrix_hash = sha256_matrix(path)
 if matrix_hash:
 print(f" SHA256 (numeric data): {matrix_hash}")
 else:
 print(" SHA256 (numeric data): unavailable")
 print("=" * 72)

def main(argv: list[str] | None = None) -> int:
 parser = argparse.ArgumentParser(description=__doc__)
 parser.add_argument(
 "paths",
 nargs="+",
 type=Path,
 help="Matrix files (XLSX or CSV) to hash.",
 )
 args = parser.parse_args(argv)
 print_report(args.paths)
 return 0

if __name__ == "__main__":
 raise SystemExit(main())

