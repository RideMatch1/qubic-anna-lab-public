#!/usr/bin/env python3
"""
Explore alternative extraction patterns (reverse diagonals, strides, snakes).
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Dict, List, Sequence, Tuple

import numpy as np

from analysis.utils.data_loader import ensure_directory, load_anna_matrix
from analysis.utils.identity_tools import (
    IDENTITY_BODY_LENGTH,
    IdentityRecord,
    base26_char,
    identity_from_body,
    matrix_hash,
    public_key_from_identity,
)

Position = Tuple[int, int]
PatternFunc = Callable[[int, int], Sequence[Position]]

OUTPUT_PATH = Path("outputs/reports/alternative_pattern_scan.md")

def diag_main(base_r: int, base_c: int) -> Sequence[Position]:
    return [(base_r + j, base_c + j) for j in range(14)]

def diag_reverse(base_r: int, base_c: int) -> Sequence[Position]:
    return [(base_r + j, base_c + (13 - j)) for j in range(14)]

def vertical_stride(base_r: int, base_c: int) -> Sequence[Position]:
    return [(base_r + j, base_c + (j % 4)) for j in range(14)]

def horizontal_stride(base_r: int, base_c: int) -> Sequence[Position]:
    return [(base_r + (j % 4), base_c + j) for j in range(14)]

def zigzag_snake(base_r: int, base_c: int) -> Sequence[Position]:
    coords: List[Position] = []
    for j in range(14):
        row = base_r + j
        col = base_c + (j if j % 2 == 0 else 13 - j)
        coords.append((row, col))
    return coords

PATTERNS: Dict[str, PatternFunc] = {
    "diag_main": diag_main,
    "diag_reverse": diag_reverse,
    "vertical_stride": vertical_stride,
    "horizontal_stride": horizontal_stride,
    "zigzag_snake": zigzag_snake,
}

def extract_with_pattern(matrix: np.ndarray, builder: PatternFunc) -> List[IdentityRecord]:
    records: List[IdentityRecord] = []
    for idx, start_row in enumerate(range(0, 128, 32), start=1):
        chars: List[str] = []
        path: List[Position] = []
        for block in range(4):
            base_r = start_row + (block // 2) * 16
            base_c = (block % 2) * 16
            for (row, col) in builder(base_r, base_c):
                if row >= 128 or col >= 128:
                    continue
                val = matrix[row, col]
                chars.append(base26_char(val))
                path.append((row, col))
        if len(chars) < IDENTITY_BODY_LENGTH:
            continue
        body = "".join(chars[:IDENTITY_BODY_LENGTH])
        identity = identity_from_body(body)
        public_key, checksum_valid = public_key_from_identity(identity)
        records.append(
            IdentityRecord(
                label=f"pattern-{idx}",
                identity=identity,
                public_key=public_key or "",
                checksum_valid=checksum_valid,
                path=tuple(path[:IDENTITY_BODY_LENGTH]),
                note="",
            )
        )
    return records

def main() -> None:
    payload = load_anna_matrix()
    matrix = payload.matrix
    digest = matrix_hash(matrix)

    ensure_directory(OUTPUT_PATH.parent)

    lines: List[str] = []
    lines.append("# Alternative Pattern Scan")
    lines.append("")
    lines.append(f"- Matrix source: `{payload.source_path}`")
    lines.append(f"- Matrix hash: `{digest}`")
    lines.append("")

    for name, builder in PATTERNS.items():
        records = extract_with_pattern(matrix, builder)
        unique_keys = {record.public_key for record in records}
        lines.append(f"## Pattern: {name}")
        lines.append(f"- Identities extracted: {len(records)}")
        lines.append(f"- Unique public keys: {len(unique_keys)}")
        for record in records:
            lines.append(
                f"  - {record.label}: checksum={record.checksum_valid} key={record.public_key[:16]}…"
            )
        lines.append("")

    OUTPUT_PATH.write_text("\n".join(lines), encoding="utf-8")
    print("[alt-pattern-scan] ✓ report ->", OUTPUT_PATH.resolve())

if __name__ == "__main__":
    main()

