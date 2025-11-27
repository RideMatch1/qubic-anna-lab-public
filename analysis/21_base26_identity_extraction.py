#!/usr/bin/env python3
"""
Extract the four Base-26 Qubic identities hidden in the Anna Matrix diagonals.

This is the core extraction script. It walks diagonally through 4 different 32x32 blocks
in the matrix, extracts 56 letters from each, and constructs valid Qubic identities.

Usage:
 python -m analysis.21_base26_identity_extraction

Outputs:
 - outputs/reports/base26_identity_report.md
 - outputs/plots/base26_identity_paths.png
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List, Sequence, Tuple

try:
 import matplotlib.pyplot as plt
 HAS_MATPLOTLIB = True
except ImportError:
 HAS_MATPLOTLIB = False
import numpy as np

from analysis.utils.data_loader import load_anna_matrix, ensure_directory
from analysis.utils.identity_tools import (
 IdentityRecord,
 IDENTITY_BODY_LENGTH,
 base26_char,
 identity_from_body,
 matrix_hash,
 public_key_from_identity,
)

BASE_DIR = Path(__file__).resolve().parents[1]
REPORT_PATH = BASE_DIR / "outputs" / "reports" / "base26_identity_report.md"
PLOT_PATH = BASE_DIR / "outputs" / "plots" / "base26_identity_paths.png"

# manual suffixes from public discourse (intentional invalid checksums)
MANUAL_SUFFIXES = ("MDCK", "DGKC", "DPHO", "XMTI")

@dataclass(frozen=True)
class ExtractionResult:
 body: str
 valid_identity: IdentityRecord
 manual_identity: IdentityRecord

def _prepare_matrix(drop_header: bool = False) -> Tuple[np.ndarray, Path]:
 payload = load_anna_matrix()
 matrix = payload.matrix
 if drop_header and matrix.shape == (129, 129):
 matrix = matrix[1:, 1:]
 return matrix, payload.source_path

def _diagonal_positions(start_row: int, block_idx: int, size: int) -> List[Tuple[int, int]]:
 """Generate diagonal coordinates for one 32x32 block.
 
 Walks through 4 sub-diagonals within the block. Each sub-diagonal gives us
 14 coordinates, so we get 56 total (which is exactly what we need for an identity body).
 """
 coords: List[Tuple[int, int]] = []
 for g in range(4):
 row = start_row + (g // 2) * 16
 col = (g % 2) * 16
 for j in range(14):
 r = row + j
 c = col + j
 if r < size and c < size:
 coords.append((r, c))
 return coords

def extract_diagonal_identities(
 matrix: np.ndarray, suffix_overrides: Sequence[str] | None = None
) -> List[ExtractionResult]:
 size = matrix.shape[0]
 overrides = list(suffix_overrides or [])
 results: List[ExtractionResult] = []

 for idx, base_row in enumerate(range(0, size, 32), start=1):
 coords = _diagonal_positions(base_row, idx - 1, size)
 if len(coords) < IDENTITY_BODY_LENGTH:
 continue

 letters = "".join(base26_char(matrix[r, c]) for r, c in coords[:IDENTITY_BODY_LENGTH])
 valid_identity_str = identity_from_body(letters, msb_first=True)
 pk_hex, checksum_valid = public_key_from_identity(valid_identity_str)

 manual_suffix = overrides[idx - 1] if idx - 1 < len(overrides) else None
 manual_identity_str = identity_from_body(letters, suffix=manual_suffix, msb_first=True)
 manual_pk, manual_valid = public_key_from_identity(manual_identity_str)

 valid_record = IdentityRecord(
 label=f"Diagonal #{idx} (valid checksum)",
 identity=valid_identity_str,
 public_key=pk_hex or "",
 checksum_valid=checksum_valid,
 path=tuple(coords[:IDENTITY_BODY_LENGTH]),
 note="Checksum derived directly from the 56-letter body.",
 )

 manual_record = IdentityRecord(
 label=f"Diagonal #{idx} (CFB published)",
 identity=manual_identity_str,
 public_key=manual_pk or pk_hex or "",
 checksum_valid=manual_valid,
 path=tuple(coords[:IDENTITY_BODY_LENGTH]),
 note="Suffix supplied from public release; intentionally invalid.",
 )

 results.append(ExtractionResult(body=letters, valid_identity=valid_record, manual_identity=manual_record))
 return results

def _plot_paths(matrix: np.ndarray, records: Sequence[IdentityRecord], out_path: Path) -> None:
 if not HAS_MATPLOTLIB:
 print(f"[base26-identities] ⚠ Skipping plot generation (matplotlib not available)")
 return
 
 ensure_directory(out_path.parent)
 fig, axes = plt.subplots(2, 2, figsize=(10, 10))
 axes = axes.flatten()

 for ax, record in zip(axes, records):
 rows = [pos[0] for pos in record.path]
 cols = [pos[1] for pos in record.path]
 order = np.linspace(0.0, 1.0, num=len(rows))
 ax.scatter(cols, rows, c=order, cmap="plasma", s=25)
 ax.plot(cols, rows, color="gray", alpha=0.4, linewidth=1)
 ax.set_title(record.label, fontsize=10)
 ax.invert_yaxis()
 ax.set_xlim(-1, matrix.shape[1])
 ax.set_ylim(matrix.shape[0], -1)
 ax.set_xticks([])
 ax.set_yticks([])

 fig.suptitle("Matrix positions for the four diagonal Base-26 identities", fontsize=14)
 fig.tight_layout()
 fig.savefig(out_path, dpi=180)
 plt.close(fig)

def _write_report(
 matrix: np.ndarray,
 source_path: Path,
 extractions: Sequence[ExtractionResult],
 out_path: Path,
) -> None:
 ensure_directory(out_path.parent)
 lines: List[str] = [
 "# Base-26 Diagonal Identity Report",
 "",
 f"- Matrix file: `{source_path}`",
 f"- Matrix hash: `{matrix_hash(matrix)}`",
 f"- Total identities: {len(extractions)}",
 "",
 "## Manual (CFB) identities",
 "",
 "| Label | Identity | Public Key | Checksum valid |",
 "| --- | --- | --- | --- |",
 ]

 for item in extractions:
 record = item.manual_identity
 lines.append(
 f"| {record.label} | `{record.identity}` | `{record.public_key}` | {record.checksum_valid} |"
 )

 lines.extend(["", "## Auto-derived checksums", "", "| Label | Identity | Public Key | Checksum valid |", "| --- | --- | --- | --- |"])
 for item in extractions:
 record = item.valid_identity
 lines.append(
 f"| {record.label} | `{record.identity}` | `{record.public_key}` | {record.checksum_valid} |"
 )

 lines.extend(
 [
 "",
 "## Notes",
 "",
 f"- Each identity body ({IDENTITY_BODY_LENGTH} letters) comes from the diagonal walk inside one 32×32 window.",
 "- Suffixes published by CFB do not match the KangarooTwelve checksum, thus wallet validation fails.",
 "- Auto-derived variants keep the same public key but reintroduce a valid checksum for reference.",
 ]
 )

 out_path.write_text("\n".join(lines), encoding="utf-8")

def main() -> None:
 """Main extraction routine."""
 matrix, source_path = _prepare_matrix(drop_header=False)
 extractions = extract_diagonal_identities(matrix, MANUAL_SUFFIXES)
 
 if not extractions:
 raise RuntimeError("No identities extracted. Check matrix file and extraction logic.")

 _plot_paths(matrix, [item.manual_identity for item in extractions], PLOT_PATH)
 _write_report(matrix, source_path, extractions, REPORT_PATH)
 
 print(f"[base26-identities] ✓ report -> {REPORT_PATH}")
 print(f"[base26-identities] ✓ plot -> {PLOT_PATH}")
 print(f"[base26-identities] Found {len(extractions)} identities")

if __name__ == "__main__":
 main()

