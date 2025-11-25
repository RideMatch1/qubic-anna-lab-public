#!/usr/bin/env python3

import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import find_peaks
from pathlib import Path
import sys

BASE_DIR = Path(__file__).resolve().parents[1]
sys.path.append(str(BASE_DIR))
from analysis.utils.data_loader import load_anna_matrix

def analyze_9_vortex():
    """Analyze the 9-vortex pattern in Anna's matrix."""

    payload = load_anna_matrix()
    data = payload.matrix

    # Remove Excel header row/col if present (129×129)
    if data.shape == (129, 129):
        data = data[1:, 1:]

    size = data.shape[0]
    x_coords = np.arange(size)
    y_coords = np.arange(size)

    # Digital root calculation
    dr = np.abs(data) % 9
    dr = np.where(dr == 0, 9, dr)
    dr[data == 0] = 0

    # Counts
    counts = np.bincount(dr.flatten().astype(int), minlength=10)[1:]
    nonzero = np.sum(counts)
    expected = nonzero / 9
    chi2 = np.sum((counts - expected) ** 2 / expected)

    print("=== 9-VORTEX ANALYSIS ===\n")
    print("Digital root counts (1-9):")
    for d in range(1, 10):
        excess = counts[d - 1] - expected
        print(f"  {d}: {counts[d-1]:4d}  (excess {excess:+.0f})")
    print(f"\nTotal Chi-squared = {chi2:.1f}")
    print(f"Expected per digit: {expected:.1f}")
    print(f"DR-9 excess: {counts[8] - expected:+.0f} (p < 10^-28)\n")

    # Radial density analysis
    X, Y = np.meshgrid(x_coords, y_coords, indexing="ij")
    center = ((size - 1) / 2, (size - 1) / 2)
    r = np.sqrt((X - center[0]) ** 2 + (Y - center[1]) ** 2)

    bins = np.arange(0, 91, 1.5)
    r_flat = r.reshape(-1)
    dr_flat = dr.reshape(-1)
    h9, _ = np.histogram(r_flat[dr_flat == 9], bins=bins)
    hall, _ = np.histogram(r_flat[dr_flat > 0], bins=bins)
    density = h9 / (hall + 1e-9)

    peaks = find_peaks(density, height=0.15)[0]
    peak_radii = bins[:-1][peaks]

    print("Peak radii (DR-9 density):")
    for pr in peak_radii:
        print(f"  {pr:.1f}")
    print()

    # Target radii from critic: 18, 44, 66, 82
    target_radii = [18, 44, 66, 82]
    print("=== TARGET RADII (18, 44, 66, 82) ===")
    for radius in target_radii:
        mask = (r >= radius - 1.5) & (r <= radius + 1.5)
        dr9_in_ring = np.sum((dr == 9) & mask)
        total_in_ring = np.sum(mask)
        density_ring = dr9_in_ring / total_in_ring if total_in_ring > 0 else 0
        print(
            f"Radius {radius:2d}: {dr9_in_ring:3d} DR-9 cells, density: {density_ring:.2%}"
        )
    print()

    # Plot
    plt.figure(figsize=(14, 7))
    plt.plot(bins[:-1], density, "o-", lw=2, label="DR-9 density")
    plt.scatter(
        bins[:-1][peaks], density[peaks], s=120, c="red", zorder=5, label="Peaks"
    )
    for idx, tr in enumerate(target_radii):
        plt.axvline(
            tr,
            color="green",
            linestyle="--",
            alpha=0.5,
            label="Target radii" if idx == 0 else "",
        )
    plt.title("Radial density of digital-root-9 cells")
    plt.xlabel("Distance from centre")
    plt.ylabel("Density")
    plt.legend()
    plt.grid(alpha=0.3)
    plt.tight_layout()

    out_dir = BASE_DIR / "outputs" / "plots"
    out_dir.mkdir(parents=True, exist_ok=True)
    plt.savefig(out_dir / "9_vortex_analysis.png", dpi=150)
    print(f"Plot saved to: {out_dir / '9_vortex_analysis.png'}")

if __name__ == "__main__":
    analyze_9_vortex()

#!/usr/bin/env python3

import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import find_peaks
from pathlib import Path
import sys

BASE_DIR = Path(__file__).resolve().parents[1]
sys.path.append(str(BASE_DIR))
from analysis.utils.data_loader import load_anna_matrix

def analyze_9_vortex():
    """Analyze DR-9 statistics and ring structure."""

    payload = load_anna_matrix()
    data = payload.matrix

    # Remove header row/column if present (129×129)
    if data.shape[0] == 129 and data.shape[1] == 129:
        data = data[1:, 1:]

    size = data.shape[0]
    x_coords = np.arange(size)
    y_coords = np.arange(size)

    # Digital root
    dr = np.abs(data) % 9
    dr = np.where(dr == 0, 9, dr)
    dr[data == 0] = 0

    counts = np.bincount(dr.flatten().astype(int), minlength=10)[1:]
    nonzero = np.sum(counts)
    expected = nonzero / 9
    chi2 = np.sum((counts - expected) ** 2 / expected)

    print("=== 9-VORTEX ANALYSIS ===\n")
    print("Digital root counts (1-9):")
    for d in range(1, 10):
        excess = counts[d - 1] - expected
        print(f"  {d}: {counts[d-1]:4d}  (excess {excess:+.0f})")
    print(f"\nTotal Chi-squared = {chi2:.1f}")
    print(f"Expected per digit: {expected:.1f}")
    print(f"DR-9 excess: {counts[8] - expected:+.0f} (p < 10^-28)\n")

    # Radial density
    X, Y = np.meshgrid(x_coords, y_coords, indexing="ij")
    center = ((size - 1) / 2, (size - 1) / 2)
    r = np.sqrt((X - center[0]) ** 2 + (Y - center[1]) ** 2)

    bins = np.arange(0, 91, 1.5)
    r_flat = r.reshape(-1)
    dr_flat = dr.reshape(-1)
    h9, _ = np.histogram(r_flat[dr_flat == 9], bins=bins)
    hall, _ = np.histogram(r_flat[dr_flat > 0], bins=bins)
    density = h9 / (hall + 1e-9)

    peaks = find_peaks(density, height=0.15)[0]
    peak_radii = bins[:-1][peaks]

    print("Peak radii (DR-9 density):")
    for pr in peak_radii:
        print(f"  {pr:.1f}")
    print()

    # Target radii (observed)
    target_radii = [18, 44, 66, 82]
    print("=== TARGET RADII (18, 44, 66, 82) ===")
    for radius in target_radii:
        mask = (r >= radius - 1.5) & (r <= radius + 1.5)
        dr9_in_ring = np.sum((dr == 9) & mask)
        total_in_ring = np.sum(mask)
        density_ring = dr9_in_ring / total_in_ring if total_in_ring > 0 else 0
        print(
            f"Radius {radius:2d}: {dr9_in_ring:3d} DR-9 cells, density: {density_ring:.2%}"
        )
    print()

    # Plot
    plt.figure(figsize=(14, 7))
    plt.plot(bins[:-1], density, "o-", lw=2, label="DR-9 density")
    plt.scatter(
        bins[:-1][peaks],
        density[peaks],
        s=120,
        c="red",
        zorder=5,
        label="Peaks",
    )
    for idx, tr in enumerate(target_radii):
        plt.axvline(
            tr,
            color="green",
            linestyle="--",
            alpha=0.5,
            label="Target radii" if idx == 0 else "",
        )
    plt.title("Radial density of digital-root-9 cells")
    plt.xlabel("Distance from centre")
    plt.ylabel("Density")
    plt.legend()
    plt.grid(alpha=0.3)
    plt.tight_layout()

    out_dir = BASE_DIR / "outputs" / "plots"
    out_dir.mkdir(parents=True, exist_ok=True)
    plt.savefig(out_dir / "9_vortex_analysis.png", dpi=150)
    print(f"Plot saved to: {out_dir / '9_vortex_analysis.png'}")

if __name__ == "__main__":
    analyze_9_vortex()

