#!/usr/bin/env python3
"""Map amino-acid peptides to candidate ASCII/Base-26 messages."""
from __future__ import annotations

import string
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Tuple

from analysis.utils.data_loader import ensure_directory, load_anna_matrix
from analysis.utils.dna_tools import matrix_to_dna, translate, split_peptides

BASE_DIR = Path(__file__).resolve().parents[1]
REPORT_PATH = BASE_DIR / "outputs" / "reports" / "peptide_ascii_decoder.md"

Printable = set(string.printable) - set("\x0b\x0c")

@dataclass
class DecodeAttempt:
    frame: int
    peptide_len: int
    method: str
    printable_ratio: float
    preview: str

def letter_value(ch: str) -> int:
    return ord(ch) - ord("A")

def normalize_text(raw: str, max_len: int = 120) -> str:
    trimmed = raw[:max_len]
    return trimmed + ("…" if len(raw) > max_len else "")

def pairwise_decode(peptide: str) -> Tuple[str, float]:
    chars: List[str] = []
    printable_count = 0
    total = 0
    for idx in range(0, len(peptide) - 1, 2):
        value = letter_value(peptide[idx]) * 26 + letter_value(peptide[idx + 1])
        byte = value % 256
        ch = chr(byte) if chr(byte) in Printable else "."
        if ch != ".":
            printable_count += 1
        chars.append(ch)
        total += 1
    ratio = printable_count / total if total else 0.0
    return "".join(chars), ratio

def triplet_decode(peptide: str) -> Tuple[str, float]:
    chars: List[str] = []
    printable_count = 0
    total = 0
    for idx in range(0, len(peptide) - 2, 3):
        value = (
            letter_value(peptide[idx]) * 26 * 26
            + letter_value(peptide[idx + 1]) * 26
            + letter_value(peptide[idx + 2])
        )
        byte = value % 256
        ch = chr(byte) if chr(byte) in Printable else "."
        if ch != ".":
            printable_count += 1
        chars.append(ch)
        total += 1
    ratio = printable_count / total if total else 0.0
    return "".join(chars), ratio

def direct_letter_probe(peptide: str) -> Tuple[str, float]:
    mapped = peptide
    printable_count = sum(1 for ch in mapped if ch in Printable)
    ratio = printable_count / len(mapped) if mapped else 0.0
    return mapped, ratio

def build_attempts(peptides_by_frame: Dict[int, List[str]]) -> List[DecodeAttempt]:
    attempts: List[DecodeAttempt] = []
    for frame, peptides in peptides_by_frame.items():
        for peptide in peptides:
            if len(peptide) < 40:
                continue
            pair_text, pair_ratio = pairwise_decode(peptide)
            attempts.append(
                DecodeAttempt(
                    frame=frame,
                    peptide_len=len(peptide),
                    method="pairwise",
                    printable_ratio=pair_ratio,
                    preview=normalize_text(pair_text),
                )
            )
            triple_text, triple_ratio = triplet_decode(peptide)
            attempts.append(
                DecodeAttempt(
                    frame=frame,
                    peptide_len=len(peptide),
                    method="triplet",
                    printable_ratio=triple_ratio,
                    preview=normalize_text(triple_text),
                )
            )
            direct_text, direct_ratio = direct_letter_probe(peptide)
            attempts.append(
                DecodeAttempt(
                    frame=frame,
                    peptide_len=len(peptide),
                    method="direct",
                    printable_ratio=direct_ratio,
                    preview=normalize_text(direct_text),
                )
            )
    return attempts

def write_report(attempts: List[DecodeAttempt]) -> None:
    ensure_directory(REPORT_PATH.parent)
    attempts.sort(key=lambda att: att.printable_ratio, reverse=True)
    top_entries = attempts[:15]

    lines: List[str] = [
        "# Peptide ASCII Decoder",
        "",
        "Drei Mapping-Strategien (Pairwise, Triplet, Direct) zur Projektion der längsten "
        "peptidischen Sequenzen in ASCII-Räume.",
        "",
        "| Frame | Peptid-Länge | Methode | Printable-Anteil | Vorschau |",
        "| --- | --- | --- | --- | --- |",
    ]
    for attempt in top_entries:
        lines.append(
            f"| {attempt.frame} | {attempt.peptide_len} | {attempt.method} | "
            f"{attempt.printable_ratio:.2%} | `{attempt.preview}` |"
        )

    REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")
    print(f"[peptide-ascii] ✓ report -> {REPORT_PATH}")

def main() -> None:
    payload = load_anna_matrix()
    dna_seq = matrix_to_dna(payload.matrix)
    peptides_by_frame: Dict[int, List[str]] = {}
    for frame in range(3):
        amino_seq = translate(dna_seq, frame)
        peptides_by_frame[frame] = split_peptides(amino_seq, min_length=40)
    attempts = build_attempts(peptides_by_frame)
    write_report(attempts)

if __name__ == "__main__":
    main()

