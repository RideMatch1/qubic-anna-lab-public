#!/usr/bin/env python3
"""Cross-check diagonal/vortex identity layers for structural overlap."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Sequence, Tuple

import numpy as np

from analysis.utils.data_loader import load_anna_matrix, ensure_directory

BASE_DIR = Path(__file__).resolve().parents[1]
REPORT_PATH = BASE_DIR / "outputs" / "reports" / "layer_crossprobe.md"

@dataclass
class SequenceBundle:
    label: str
    body: str

def to_char(val: float) -> str:
    return chr(ord("A") + int(abs(val)) % 26)

def diag_sequences(matrix: np.ndarray) -> List[SequenceBundle]:
    bundles: List[SequenceBundle] = []
    for idx, gs in enumerate(range(0, matrix.shape[0], 32), 1):
        chars: List[str] = []
        for block in range(4):
            r = gs + (block // 2) * 16
            c = (block % 2) * 16
            for offset in range(14):
                row = r + offset
                col = c + offset
                if row < matrix.shape[0] and col < matrix.shape[1]:
                    chars.append(to_char(matrix[row, col]))
        bundles.append(SequenceBundle(label=f"Diag#{idx}", body="".join(chars)))
    return bundles

def vortex_sequences(matrix: np.ndarray) -> List[SequenceBundle]:
    center = (matrix.shape[0] - 1) / 2
    targets = [18, 44, 66, 82]
    bundles: List[SequenceBundle] = []
    for idx, radius in enumerate(targets, 1):
        chars: List[str] = []
        for row in range(matrix.shape[0]):
            for col in range(matrix.shape[1]):
                dist = np.hypot(row - center, col - center)
                if abs(dist - radius) < 0.5:
                    chars.append(to_char(matrix[row, col]))
        bundles.append(SequenceBundle(label=f"Vortex#{idx}", body="".join(chars)))
    return bundles

def hamming(a: str, b: str) -> Tuple[int, float]:
    length = min(len(a), len(b))
    mismatches = sum(ch1 != ch2 for ch1, ch2 in zip(a[:length], b[:length]))
    return mismatches, 1 - mismatches / length if length else 0.0

def ternary_profile(seq: str) -> List[int]:
    return [((ord(ch) - ord("A")) % 3) - 1 for ch in seq]

def ternary_alignment(a: str, b: str) -> float:
    ta = ternary_profile(a)
    tb = ternary_profile(b)
    length = min(len(ta), len(tb))
    if length == 0:
        return 0.0
    matches = sum(1 for i in range(length) if ta[i] == tb[i])
    return matches / length

def summarize_pairs(lhs: SequenceBundle, rhs: SequenceBundle) -> str:
    mismatches, similarity = hamming(lhs.body, rhs.body)
    ternary_sim = ternary_alignment(lhs.body, rhs.body)
    return (
        f"| {lhs.label} | {rhs.label} | {len(lhs.body)} | {len(rhs.body)} | "
        f"{mismatches} | {similarity:.2%} | {ternary_sim:.2%} |"
    )

def write_report(diag_raw: List[SequenceBundle], diag_trim: List[SequenceBundle], vortex: List[SequenceBundle]) -> None:
    ensure_directory(REPORT_PATH.parent)
    lines = [
        "# Layer Crossprobe",
        "",
        "Vergleich von diagonalen 56-Zeichen-Körpern (roh vs. getrimmt) und den vier 9-Vortex-Ringen.",
        "",
        "## Diagonal (raw vs. trimmed)",
        "",
        "| Raw | Trimmed | Len Raw | Len Trim | Hamming | Similarität | Ternär-Overlap |",
        "| --- | --- | --- | --- | --- | --- | --- |",
    ]
    for raw, trimmed in zip(diag_raw, diag_trim):
        lines.append(summarize_pairs(raw, trimmed))

    lines.extend(
        [
            "",
            "## Diagonal vs. Vortex",
            "",
            "| Diagonal | Vortex | Len D | Len V | Hamming | Similarität | Ternär-Overlap |",
            "| --- | --- | --- | --- | --- | --- | --- |",
        ]
    )
    for diag_bundle, vortex_bundle in zip(diag_raw, vortex):
        lines.append(summarize_pairs(diag_bundle, vortex_bundle))

    REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")
    print(f"[layer-crossprobe] ✓ report -> {REPORT_PATH}")

def main() -> None:
    payload = load_anna_matrix()
    mat = payload.matrix
    diag_raw = diag_sequences(mat)
    trimmed = mat[1:, 1:] if mat.shape[0] == 129 else mat
    diag_trim = diag_sequences(trimmed)
    vortex = vortex_sequences(mat)
    write_report(diag_raw, diag_trim, vortex)

if __name__ == "__main__":
    main()

