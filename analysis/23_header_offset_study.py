#!/usr/bin/env python3
"""Compare Base-26 sequences with and without trimming the Excel header row/column."""
from __future__ import annotations

from pathlib import Path
from typing import List, Tuple

from analysis.utils.data_loader import load_anna_matrix, ensure_directory
from analysis.utils.identity_tools import base26_char

BASE_DIR = Path(__file__).resolve().parents[1]
REPORT_PATH = BASE_DIR / "outputs" / "reports" / "header_offset_analysis.md"

def _extract_sequences(matrix) -> List[str]:
    size = matrix.shape[0]
    sequences: List[str] = []
    for gs in range(0, size, 32):
        chars: List[str] = []
        for g in range(4):
            r = gs + (g // 2) * 16
            c = (g % 2) * 16
            for j in range(14):
                row = r + j
                col = c + j
                if row < size and col < size:
                    chars.append(base26_char(matrix[row, col]))
        sequences.append("".join(chars[:56]))
    return sequences

def compare_sequences(raw: List[str], trimmed: List[str]) -> List[Tuple[str, str, int]]:
    """Return tuples of (raw, trimmed, hamming_distance)."""

    results: List[Tuple[str, str, int]] = []
    for r_seq, t_seq in zip(raw, trimmed):
        diff = sum(ch1 != ch2 for ch1, ch2 in zip(r_seq, t_seq))
        results.append((r_seq, t_seq, diff))
    return results

def write_report(entries: List[Tuple[str, str, int]], out_path: Path) -> None:
    ensure_directory(out_path.parent)
    lines = [
        "# Header Offset Analysis",
        "",
        "Comparison between diagonal Base-26 bodies when loading the matrix directly vs. "
        "skipping the Excel header row/column (`df.iloc[1:,1:]`).",
        "",
        "| Block | Raw body (with header) | Trimmed body | Hamming distance |",
        "| --- | --- | --- | --- |",
    ]

    for idx, (raw, trimmed, diff) in enumerate(entries, 1):
        lines.append(f"| #{idx} | `{raw}` | `{trimmed}` | {diff} |")

    lines.extend(
        [
            "",
            "## Notes",
            "",
            "- Raw loading preserves the `[0,0]` Excel header as `0`, which seeds the identities with `A`.",
            "- The critic's method removes that header, shifting every row/column by one and producing the "
            "trimmed variant.",
            "- Both approaches are deterministic; the difference is purely the starting offset.",
        ]
    )
    out_path.write_text("\n".join(lines), encoding="utf-8")

def main() -> None:
    payload = load_anna_matrix()
    raw_matrix = payload.matrix
    trimmed_matrix = raw_matrix[1:, 1:] if raw_matrix.shape == (129, 129) else raw_matrix[1:, 1:]

    raw_seq = _extract_sequences(raw_matrix)
    trimmed_seq = _extract_sequences(trimmed_matrix)
    comparison = compare_sequences(raw_seq, trimmed_seq)
    write_report(comparison, REPORT_PATH)
    print(f"[header-offset] ✓ report -> {REPORT_PATH}")

if __name__ == "__main__":
    main()

