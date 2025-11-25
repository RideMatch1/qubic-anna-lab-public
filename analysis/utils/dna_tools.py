"""Utility helpers for matrix→DNA→amino-acid conversions."""
from __future__ import annotations

from typing import Dict, List

import numpy as np

NUCLEOTIDES = ("A", "C", "G", "T")

CODON_TABLE: Dict[str, str] = {
    "TTT": "F",
    "TTC": "F",
    "TTA": "L",
    "TTG": "L",
    "CTT": "L",
    "CTC": "L",
    "CTA": "L",
    "CTG": "L",
    "ATT": "I",
    "ATC": "I",
    "ATA": "I",
    "ATG": "M",
    "GTT": "V",
    "GTC": "V",
    "GTA": "V",
    "GTG": "V",
    "TCT": "S",
    "TCC": "S",
    "TCA": "S",
    "TCG": "S",
    "CCT": "P",
    "CCC": "P",
    "CCA": "P",
    "CCG": "P",
    "ACT": "T",
    "ACC": "T",
    "ACA": "T",
    "ACG": "T",
    "GCT": "A",
    "GCC": "A",
    "GCA": "A",
    "GCG": "A",
    "TAT": "Y",
    "TAC": "Y",
    "TAA": "*",
    "TAG": "*",
    "CAT": "H",
    "CAC": "H",
    "CAA": "Q",
    "CAG": "Q",
    "AAT": "N",
    "AAC": "N",
    "AAA": "K",
    "AAG": "K",
    "GAT": "D",
    "GAC": "D",
    "GAA": "E",
    "GAG": "E",
    "TGT": "C",
    "TGC": "C",
    "TGA": "*",
    "TGG": "W",
    "CGT": "R",
    "CGC": "R",
    "CGA": "R",
    "CGG": "R",
    "AGT": "S",
    "AGC": "S",
    "AGA": "R",
    "AGG": "R",
    "GGT": "G",
    "GGC": "G",
    "GGA": "G",
    "GGG": "G",
}

def matrix_to_dna(matrix: np.ndarray) -> str:
    mapper = np.vectorize(lambda v: NUCLEOTIDES[int(abs(v)) % 4])
    seq = mapper(matrix).flatten()
    return "".join(seq)

def translate(sequence: str, frame: int) -> str:
    amino = []
    for idx in range(frame, len(sequence) - 2, 3):
        codon = sequence[idx : idx + 3]
        amino.append(CODON_TABLE.get(codon, "?"))
    return "".join(amino)

def split_peptides(amino_sequence: str, min_length: int = 1) -> List[str]:
    return [chunk for chunk in amino_sequence.split("*") if len(chunk) >= min_length]

