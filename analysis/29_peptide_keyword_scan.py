#!/usr/bin/env python3
"""Search direct peptide strings for Qubic/CFB-related keywords."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List

from analysis.utils.data_loader import ensure_directory, load_anna_matrix
from analysis.utils.dna_tools import matrix_to_dna, translate, split_peptides

BASE_DIR = Path(__file__).resolve().parents[1]
REPORT_PATH = BASE_DIR / "outputs" / "reports" / "peptide_keyword_scan.md"

KEY_TERMS = [
    "CFB",
    "BASE",
    "MATRIX",
    "SHIFT",
    "KEY",
    "QUBIC",
    "IDENTITY",
    "PUBLIC",
    "COMPUTOR",
    "NINE",
]

@dataclass
class MatchRecord:
    frame: int
    peptide_len: int
    term: str
    count: int
    positions: List[int]

def find_matches(sequence: str, term: str) -> List[int]:
    positions: List[int] = []
    start = sequence.find(term)
    while start != -1:
        positions.append(start)
        start = sequence.find(term, start + 1)
    return positions

def scan_peptides(peptides_by_frame: Dict[int, List[str]]) -> List[MatchRecord]:
    records: List[MatchRecord] = []
    for frame, peptides in peptides_by_frame.items():
        for peptide in peptides:
            if len(peptide) < len(min(KEY_TERMS, key=len)):
                continue
            for term in KEY_TERMS:
                positions = find_matches(peptide, term)
                if positions:
                    records.append(
                        MatchRecord(
                            frame=frame,
                            peptide_len=len(peptide),
                            term=term,
                            count=len(positions),
                            positions=positions,
                        )
                    )
    return records

def write_report(records: List[MatchRecord], total_peptides: Dict[int, int]) -> None:
    ensure_directory(REPORT_PATH.parent)
    records.sort(key=lambda rec: (rec.term, rec.frame, -rec.count))

    lines = [
        "# Peptide Keyword Scan",
        "",
        "Direkte Peptidstrings (Frame 0–2) wurden nach Qubic/CFB-relevanten Stichwörtern durchsucht.",
        "",
        "## Peptidübersicht",
        "",
        "| Frame | Anzahl Peptide (>=40 aa) |",
        "| --- | --- |",
    ]
    for frame in sorted(total_peptides):
        lines.append(f"| {frame} | {total_peptides[frame]} |")

    lines.extend(
        [
            "",
            "## Treffer",
            "",
            "| Term | Frame | Peptid-Länge | Treffer | Positionen |",
            "| --- | --- | --- | --- | --- |",
        ]
    )

    if records:
        for rec in records:
            pos_str = ", ".join(str(pos) for pos in rec.positions[:6])
            if len(rec.positions) > 6:
                pos_str += ", …"
            lines.append(
                f"| {rec.term} | {rec.frame} | {rec.peptide_len} | {rec.count} | {pos_str} |"
            )
    else:
        lines.append("| _no matches_ | | | | |")

    REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")
    print(f"[peptide-keyword] ✓ report -> {REPORT_PATH}")

def main() -> None:
    payload = load_anna_matrix()
    dna_seq = matrix_to_dna(payload.matrix)
    peptides_by_frame: Dict[int, List[str]] = {}
    for frame in range(3):
        amino_seq = translate(dna_seq, frame)
        peptides_by_frame[frame] = split_peptides(amino_seq, min_length=40)

    total_peptides = {frame: len(peps) for frame, peps in peptides_by_frame.items()}
    records = scan_peptides(peptides_by_frame)
    write_report(records, total_peptides)

if __name__ == "__main__":
    main()

