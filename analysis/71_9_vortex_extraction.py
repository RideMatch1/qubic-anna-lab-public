#!/usr/bin/env python3
"""
Extract Base-26 identities along the four 9-Vortex rings (18, 44, 66, 82).

This extracts identities by sampling cells in a circular pattern at specific radii.
The "9-Vortex" name comes from using digital root (mod 9) of matrix values.

Usage:
    python -m analysis.71_9_vortex_extraction

Outputs:
    - outputs/reports/9_vortex_identity_report.md
    - outputs/plots/9_vortex_paths.png
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import List, Sequence, Tuple

try:
    import matplotlib.pyplot as plt
    HAS_MATPLOTLIB = True
except ImportError:
    HAS_MATPLOTLIB = False
import numpy as np

from analysis.utils.data_loader import load_anna_matrix, ensure_directory
from analysis.utils.identity_tools import (
    IDENTITY_BODY_LENGTH,
    IdentityRecord,
    base26_char,
    identity_from_body,
    matrix_hash,
    public_key_from_identity,
)

BASE_DIR = Path(__file__).resolve().parents[1]
REPORT_PATH = BASE_DIR / "outputs" / "reports" / "9_vortex_identity_report.md"
PLOT_PATH = BASE_DIR / "outputs" / "plots" / "9_vortex_paths.png"
TARGET_RADII = (18, 44, 66, 82)

@dataclass(frozen=True)
class RingExtraction:
    radius: int
    identity: IdentityRecord | None
    letters: str
    checksum_valid: bool

def _digital_root(matrix: np.ndarray) -> np.ndarray:
    vals = np.abs(matrix) % 9
    vals = np.where(vals == 0, 9, vals)
    vals[matrix == 0] = 0
    return vals

def _prepare_matrix() -> Tuple[np.ndarray, Path]:
    payload = load_anna_matrix()
    matrix = payload.matrix
    # Keep the header row/column to remain consistent with the diag extraction.
    return matrix, payload.source_path

def _ring_positions(matrix: np.ndarray, radius: int, tolerance: float = 1.5) -> List[Tuple[int, int]]:
    """Find all positions on a ring at given radius from matrix center.
    
    Args:
        matrix: The matrix to sample from
        radius: Target radius in cells
        tolerance: How close to the radius we accept (default 1.5 cells)
    
    Returns:
        List of (row, col) positions ordered by angle (counter-clockwise from top)
    """
    size = matrix.shape[0]
    x_coords, y_coords = np.meshgrid(np.arange(size), np.arange(size), indexing="ij")
    center = ((size - 1) / 2, (size - 1) / 2)
    r = np.sqrt((x_coords - center[0]) ** 2 + (y_coords - center[1]) ** 2)
    mask = np.abs(r - radius) <= tolerance
    positions = list(zip(*np.where(mask)))

    # Sort by angle to get circular ordering
    angles = [
        np.arctan2(row - center[0], col - center[1]) if positions else 0 for row, col in positions
    ]
    ordered = [pos for _, pos in sorted(zip(angles, positions))]
    return ordered

def extract_rings(matrix: np.ndarray) -> List[RingExtraction]:
    results: List[RingExtraction] = []

    for radius in TARGET_RADII:
        positions = _ring_positions(matrix, radius)
        if len(positions) < IDENTITY_BODY_LENGTH:
            results.append(
                RingExtraction(
                    radius=radius,
                    identity=None,
                    letters="",
                    checksum_valid=False,
                )
            )
            continue

        letters = "".join(base26_char(matrix[r, c]) for r, c in positions[:IDENTITY_BODY_LENGTH])
        body = letters[:IDENTITY_BODY_LENGTH]
        identity_str = identity_from_body(body, msb_first=True)
        pk_hex, checksum_valid = public_key_from_identity(identity_str)

        record = IdentityRecord(
            label=f"Radius {radius}",
            identity=identity_str,
            public_key=pk_hex or "",
            checksum_valid=checksum_valid,
            path=tuple(positions[:IDENTITY_BODY_LENGTH]),
            note=f"First {IDENTITY_BODY_LENGTH} letters follow the ring angle ordering.",
        )
        results.append(
            RingExtraction(
                radius=radius,
                identity=record,
                letters=letters,
                checksum_valid=checksum_valid,
            )
        )
    return results

def _plot_ring_paths(matrix: np.ndarray, extractions: Sequence[RingExtraction], out_path: Path) -> None:
    if not HAS_MATPLOTLIB:
        print(f"[9-vortex] ⚠ Skipping plot generation (matplotlib not available)")
        return
    
    ensure_directory(out_path.parent)
    fig, axes = plt.subplots(2, 2, figsize=(10, 10))
    axes = axes.flatten()
    for ax, extraction in zip(axes, extractions):
        positions = extraction.identity.path if extraction.identity else ()
        if positions:
            rows = [pos[0] for pos in positions]
            cols = [pos[1] for pos in positions]
            order = np.linspace(0.0, 1.0, num=len(rows))
            ax.scatter(cols, rows, c=order, cmap="viridis", s=18)
            ax.plot(cols, rows, color="gray", alpha=0.4)
        ax.set_title(f"Radius {extraction.radius}")
        ax.invert_yaxis()
        ax.set_xticks([])
        ax.set_yticks([])
    fig.suptitle(f"Paths along the 9-Vortex rings (first {IDENTITY_BODY_LENGTH} points)", fontsize=14)
    fig.tight_layout()
    fig.savefig(out_path, dpi=180)
    plt.close(fig)

def _write_report(matrix: np.ndarray, source_path: Path, data: Sequence[RingExtraction], out_path: Path) -> None:
    ensure_directory(out_path.parent)
    lines: List[str] = [
        "# 9-Vortex Identity Report",
        "",
        f"- Matrix file: `{source_path}`",
        f"- Matrix hash: `{matrix_hash(matrix)}`",
        "",
        "| Radius | Identity | Public Key | Checksum valid |",
        "| --- | --- | --- | --- |",
    ]

    for item in data:
        if item.identity is None:
            lines.append(f"| {item.radius} | *(insufficient samples)* |  |  |")
            continue
        lines.append(
            f"| {item.radius} | `{item.identity.identity}` | `{item.identity.public_key}` | {item.identity.checksum_valid} |"
        )

    lines.extend(
        [
            "",
            "## Notes",
            "",
            f"- Only the first {IDENTITY_BODY_LENGTH} letters per ring are used as the identity body; the checksum is derived afterwards.",
            "- The published suffixes from the diagonal extraction do not apply here; all four rings produce auto-derived checksums.",
            "- The visualization highlights the angular ordering of the sampled cells.",
        ]
    )
    out_path.write_text("\n".join(lines), encoding="utf-8")

def main() -> None:
    """Main extraction routine."""
    matrix, source_path = _prepare_matrix()
    extractions = extract_rings(matrix)
    
    valid_count = sum(1 for e in extractions if e.identity is not None)
    if valid_count == 0:
        raise RuntimeError("No valid identities extracted from vortex rings.")
    
    _write_report(matrix, source_path, extractions, REPORT_PATH)
    _plot_ring_paths(matrix, extractions, PLOT_PATH)
    
    print(f"[9-vortex] ✓ report -> {REPORT_PATH}")
    print(f"[9-vortex] ✓ plot   -> {PLOT_PATH}")
    print(f"[9-vortex] Found {valid_count} identities from {len(extractions)} rings")

if __name__ == "__main__":
    main()

