#!/usr/bin/env python3
"""Visualize similarity matrices between diagonal and vortex layers."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import List, Tuple

import matplotlib.pyplot as plt
import numpy as np

from analysis.utils.data_loader import ensure_directory, load_anna_matrix

PLOT_PATH = Path(__file__).resolve().parents[1] / "outputs" / "plots" / "layer_crossprobe.png"

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
 radii = [18, 44, 66, 82]
 bundles: List[SequenceBundle] = []
 for idx, radius in enumerate(radii, 1):
 chars: List[str] = []
 for row in range(matrix.shape[0]):
 for col in range(matrix.shape[1]):
 dist = np.hypot(row - center, col - center)
 if abs(dist - radius) < 0.5:
 chars.append(to_char(matrix[row, col]))
 bundles.append(SequenceBundle(label=f"Vortex#{idx}", body="".join(chars)))
 return bundles

def similarity(a: str, b: str) -> float:
 length = min(len(a), len(b))
 if length == 0:
 return 0.0
 matches = sum(ch1 == ch2 for ch1, ch2 in zip(a[:length], b[:length]))
 return matches / length

def ternary_profile(seq: str) -> List[int]:
 return [((ord(ch) - ord("A")) % 3) - 1 for ch in seq]

def ternary_similarity(a: str, b: str) -> float:
 ta = ternary_profile(a)
 tb = ternary_profile(b)
 length = min(len(ta), len(tb))
 if length == 0:
 return 0.0
 matches = sum(1 for i in range(length) if ta[i] == tb[i])
 return matches / length

def build_matrices(diag_raw: List[SequenceBundle], diag_trim: List[SequenceBundle], vortex: List[SequenceBundle]) -> Tuple[np.ndarray, np.ndarray]:
 diag_matrix = np.zeros((len(diag_raw), len(diag_trim)))
 for i, raw in enumerate(diag_raw):
 for j, trimmed in enumerate(diag_trim):
 diag_matrix[i, j] = similarity(raw.body, trimmed.body)

 cross_matrix = np.zeros((len(diag_raw), len(vortex)))
 for i, raw in enumerate(diag_raw):
 for j, vortex_bundle in enumerate(vortex):
 cross_matrix[i, j] = ternary_similarity(raw.body, vortex_bundle.body)

 return diag_matrix, cross_matrix

def plot_matrices(diag_matrix: np.ndarray, cross_matrix: np.ndarray, diag_labels: List[str], vortex_labels: List[str]) -> None:
 ensure_directory(PLOT_PATH.parent)
 fig, axes = plt.subplots(1, 2, figsize=(12, 5))

 im0 = axes[0].imshow(diag_matrix, vmin=0, vmax=1, cmap="viridis")
 axes[0].set_title("Raw vs Trimmed Similarity")
 axes[0].set_xticks(range(len(diag_labels)))
 axes[0].set_xticklabels(diag_labels)
 axes[0].set_yticks(range(len(diag_labels)))
 axes[0].set_yticklabels(diag_labels)
 fig.colorbar(im0, ax=axes[0], fraction=0.046, pad=0.04)

 im1 = axes[1].imshow(cross_matrix, vmin=0, vmax=1, cmap="magma")
 axes[1].set_title("Ternary Overlap: Diagonal vs Vortex")
 axes[1].set_xticks(range(len(vortex_labels)))
 axes[1].set_xticklabels(vortex_labels, rotation=45)
 axes[1].set_yticks(range(len(diag_labels)))
 axes[1].set_yticklabels(diag_labels)
 fig.colorbar(im1, ax=axes[1], fraction=0.046, pad=0.04)

 fig.tight_layout()
 fig.savefig(PLOT_PATH, dpi=300)
 plt.close(fig)
 print(f"[layer-crossprobe-plot] ✓ plot -> {PLOT_PATH}")

def main() -> None:
 payload = load_anna_matrix()
 mat = payload.matrix
 diag_raw = diag_sequences(mat)
 trimmed_mat = mat[1:, 1:] if mat.shape[0] == 129 else mat
 diag_trim = diag_sequences(trimmed_mat)
 vortex = vortex_sequences(mat)
 diag_matrix, cross_matrix = build_matrices(diag_raw, diag_trim, vortex)
 plot_matrices(diag_matrix, cross_matrix, [bundle.label for bundle in diag_raw], [bundle.label for bundle in vortex])

if __name__ == "__main__":
 main()

