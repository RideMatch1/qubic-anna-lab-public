#!/usr/bin/env python3
"""Translate the matrix-derived DNA sequence into amino-acid strings across frames."""
from __future__ import annotations

from collections import Counter
from pathlib import Path
from typing import Dict, List

from analysis.utils.data_loader import load_anna_matrix, ensure_directory
from analysis.utils.dna_tools import matrix_to_dna, translate

BASE_DIR = Path(__file__).resolve().parents[1]
REPORT_PATH = BASE_DIR / "outputs" / "reports" / "amino_acid_translation.md"

def summarize(amino_seq: str) -> Dict[str, float]:
 counts = Counter(amino_seq)
 total = sum(counts.values())
 return {aa: counts[aa] / total for aa in sorted(counts)}

def longest_peptides(amino_seq: str, top_k: int = 5) -> List[str]:
 peptides = [pep for pep in amino_seq.split("*") if pep]
 peptides.sort(key=len, reverse=True)
 return peptides[:top_k]

def write_report(frames: Dict[int, str], out_path: Path) -> None:
 ensure_directory(out_path.parent)
 lines: List[str] = [
 "# Amino-Acid Translation",
 "",
 "Forward strand reading frames based on the matrix→DNA mapping (`value % 4`).",
 ]

 for frame, amino_seq in frames.items():
 summary = summarize(amino_seq)
 peptides = longest_peptides(amino_seq)
 lines.extend(
 [
 "",
 f"## Frame {frame}",
 "",
 f"- Length (aa): {len(amino_seq)}",
 f"- Stop codons: {amino_seq.count('*')}",
 f"- Unknown codons (`?`): {amino_seq.count('?')}",
 "",
 "### Amino-acid distribution",
 "",
 "| Amino acid | Share |",
 "| --- | --- |",
 ]
 )
 for aa, share in sorted(summary.items(), key=lambda kv: kv[1], reverse=True):
 lines.append(f"| {aa} | {share:.2%} |")

 lines.extend(
 [
 "",
 "### Longest peptides (no stop)",
 "",
 ]
 )
 if peptides:
 for idx, pep in enumerate(peptides, 1):
 lines.append(f"{idx}. `{pep}` (len {len(pep)})")
 else:
 lines.append("_None_")

 out_path.write_text("\n".join(lines), encoding="utf-8")

def main() -> None:
 payload = load_anna_matrix()
 dna_seq = matrix_to_dna(payload.matrix)
 frames = {frame: translate(dna_seq, frame) for frame in range(3)}
 write_report(frames, REPORT_PATH)
 print(f"[amino-translation] ✓ report -> {REPORT_PATH}")

if __name__ == "__main__":
 main()

