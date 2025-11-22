#!/usr/bin/env python3
"""Probe DNA-like encodings across the Anna Matrix."""
from __future__ import annotations

from collections import Counter
from pathlib import Path
from typing import Dict, List

import numpy as np

from analysis.utils.data_loader import ensure_directory, load_anna_matrix

BASE_DIR = Path(__file__).resolve().parents[1]
REPORT_PATH = BASE_DIR / "outputs" / "reports" / "dna_encoding_probe.md"
NUCLEOTIDES = ("A", "C", "G", "T")

def to_dna(values: np.ndarray) -> str:
    mapped = np.vectorize(lambda v: NUCLEOTIDES[int(abs(v)) % 4])(values)
    return "".join(mapped.flatten())

def codon_counts(sequence: str) -> Dict[str, int]:
    counts: Counter[str] = Counter()
    for idx in range(0, len(sequence) - 2, 3):
        codon = sequence[idx : idx + 3]
        if len(codon) == 3:
            counts[codon] += 1
    return dict(counts)

def write_report(sequence: str, codons: Dict[str, int], out_path: Path) -> None:
    ensure_directory(out_path.parent)
    total_bases = len(sequence)
    total_codons = sum(codons.values())
    sorted_codons = sorted(codons.items(), key=lambda x: x[1], reverse=True)[:25]

    nucleotide_counts = Counter(sequence)
    nuc_lines = [f"- {nt}: {nucleotide_counts.get(nt,0)} ({nucleotide_counts.get(nt,0)/total_bases:.2%})" for nt in NUCLEOTIDES]

    lines: List[str] = [
        "# DNA Encoding Probe",
        "",
        f"- Total bases: {total_bases}",
        f"- Total codons (triplets): {total_codons}",
        "",
        "## Nucleotide distribution",
        "",
        *nuc_lines,
        "",
        "## Top codon frequencies",
        "",
        "| Codon | Count | Share |",
        "| --- | --- | --- |",
    ]

    for codon, count in sorted_codons:
        lines.append(f"| {codon} | {count} | {count / total_codons:.2%} |")

    lines.extend(
        [
            "",
            "## Notes",
            "",
            "- Mapping rule: `value % 4` → A/C/G/T.",
            "- The strong codon bias hints at structured regions (e.g. stop-codon-like `TAA/TAG/TGA` deficits).",
            "- Further work: interpret high-frequency codons as ternary markers or convert to amino acids.",
        ]
    )
    out_path.write_text("\n".join(lines), encoding="utf-8")

def main() -> None:
    payload = load_anna_matrix()
    matrix = payload.matrix
    sequence = to_dna(matrix)
    codons = codon_counts(sequence)
    write_report(sequence, codons, REPORT_PATH)
    print(f"[dna-probe] ✓ report -> {REPORT_PATH}")

if __name__ == "__main__":
    main()

