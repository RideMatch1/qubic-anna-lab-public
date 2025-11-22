# QUBIC Anna Matrix — Found Keys & Identities

**Status**: Active Research

**Researcher**: Jordan  
**Discord**: @Jordan (Qubic community)  
**Contact**: Via Qubic Discord or GitHub issues

This repository documents the discovery of real Qubic identities and keys encoded in the Anna Matrix Excel file. These are actual on-chain identities that can be verified independently. We found valid keys and derived additional identities from them.

**What we found**: Real Qubic identities (public keys) and valid seeds encoded in the matrix. These are actual cryptographic keys that exist on the Qubic blockchain. We found 8 identities directly in the matrix, and discovered that each one contains a valid seed that derives an additional on-chain identity.

**Important**: We found seeds and identities in the matrix. We created a signed message to prove the seeds are cryptographically functional. The message text itself was not found in the matrix - it was created by us to demonstrate functionality.

## What We Found

| Discovery | Status | Evidence |
| --- | --- | --- |
| **8 Qubic identities** (public keys) extracted from matrix | Verified on-chain | `analysis/21_base26_identity_extraction.py`, `scripts/verify/rpc_check.py` |
| All 8 identities exist on-chain with valid ticks | Verified | RPC checks confirm they're live identities |
| **Seeds derived from identities** - each identity body yields a 55-char seed | Verified | `scripts/core/seed_candidate_scan.py`, `scripts/core/standardized_conversion.py` |
| **8 additional Layer-2 identities** derived from seeds also exist on-chain | Verified | `scripts/verify/identity_deep_scan.py` |
| Control group: 1,000 random matrices produced 0 hits | Verified | `scripts/verify/control_group.py` |
| **Comprehensive scan**: 22,801 identities checked, 22,522 on-chain (98.8% success rate) | In Progress | See `COMPREHENSIVE_SCAN_RESULTS.md` |

**All found identities are publicly documented:**
- **Initial 8 identities**: [`FOUND_IDENTITIES.md`](FOUND_IDENTITIES.md)
- **100 seeds and identities**: [`100_SEEDS_AND_IDENTITIES.md`](100_SEEDS_AND_IDENTITIES.md) - Sample from comprehensive scan

You can verify them yourself.

Everything here can be reproduced from the published Excel file (`data/anna-matrix/Anna_Matrix.xlsx`, SHA256 `bdee333b4006c1b7ab24a0dc61de76b60210c2db7bd8822c50e8509aff907c45`). The hash is important to ensure you're working with the exact same file.

**What this is**: We found 8 Qubic identities (public keys) in the matrix that exist on-chain. Each identity contains a seed that can derive additional valid identities. These are verifiable facts - you can check them yourself using the scripts provided.

**What this is NOT**: 
- This is not about AI training, model weights, or training logs
- We're not claiming Anna intentionally encoded these (we don't know)
- We're not claiming these are "private keys" or "secret keys" - they're public identities
- We're not claiming statistical proof of intentional encoding (see limitations below)

**Critical limitations**:
- We don't know if these were intentionally encoded or found by chance
- Statistical significance depends on unknown factors (total on-chain identities)
- The birthday paradox means random collisions are possible with enough attempts
- We only tested specific extraction patterns, not all possible methods
- **Multiple-testing problem**: We tested ~14 methods, only 2 found identities (see `METHODS_TESTED.md`)
- **Cherry-picking**: We show successful methods, not all attempts that found nothing
- **Logical inconsistency**: If intentional, why hide seeds in public scores? (See "Open Questions" below)

## Recent Research Updates

**Status**: Experimental / Active Research

Recent analyses have explored additional aspects of the matrix structure:

- **Qubic Stack Architecture**: Analysis of Anna's role in the 5-layer Qubic stack (see `outputs/derived/QUBIC_STACK_ANALYSIS.md`)
- **Aigarth Framework**: Investigation of Aigarth Intelligent Tissue connection (see `outputs/derived/AIGARTH_PAPER_ANALYSIS.md`)
- **Helix Gate Patterns**: 26,562 patterns found in matrix structure (see `outputs/reports/helix_gate_analysis_report.md`)
- **Evolutionary Signatures**: Analysis of identity patterns suggesting evolutionary selection (see `outputs/reports/evolutionary_signatures_analysis_report.md`)
- **26 Zero Values**: Analysis of "dark matter" control neurons (see `outputs/reports/26_zeros_dark_matter_analysis_report.md`)

**Note**: These are preliminary findings from ongoing research. Independent verification is recommended. See `RESEARCH_UPDATE_2025_11_22.md` for detailed summary.

**Important**: The matrix appears to be Aigarth Intelligent Tissue (ternary neural network weights), not encrypted data. This interpretation is based on repository analysis and statistical properties. However, this is still under investigation and requires further validation.

**What we can prove**: The identities exist on-chain, they're reproducible from the matrix, and random matrices don't produce the same results. Whether this is intentional or coincidence is unknown.

---

## Proof Pipeline

Here's basically how it works:

```
Anna_Matrix.xlsx
        |
        v
Base-26 extraction (diagonals + vortex)
        |
        v
60-char identities (body + checksum)
        |
        v
QubiPy RPC check (tick, balance, status)
        |
        v
Live evidence pack (reports + JSON)
        |
        v
Seed projection (56-letter body → 55-letter seed → Layer-2 identities) + deep scan
```

The full walkthrough with all the details is in **[`PROOF_OF_WORK.md`](PROOF_OF_WORK.md)** - hashes, exact commands, log excerpts, the whole thing. If you want to verify everything yourself, start there.

---

## On-Chain Verification (Dockerised)

A Docker container is provided because QubiPy dependencies can be tricky. Here's how to use it:

```bash
# build once
docker build -f Dockerfile.qubipy -t qubic-proof .

# quick connectivity ping (just to make sure RPC works)
docker run --rm -it -v "$PWD":/workspace -w /workspace qubic-proof \
  python scripts/verify/ping.py

# full identity verification (writes outputs/reports/qubipy_identity_check.md)
docker run --rm -it -v "$PWD":/workspace -w /workspace qubic-proof \
  python scripts/verify/rpc_check.py
```

Example output:

```
Connected to Qubic RPC. Latest tick: 37707442
Diagonal #1 ... EXISTS – Balance: 0 QU – ValidForTick: 37707446
...
Vortex #4 ... EXISTS – Balance: 0 QU – ValidForTick: 37707448
```

All eight identities exist on-chain. This can be verified independently using the scripts provided.

---

## Statistical Significance

### Control Group

To verify this wasn't just an artifact of the extraction method, 1,000 random 128x128 matrices were generated and processed with the same extraction:

`python scripts/verify/control_group.py --matrices 1000`  
4,000 random identities probed, **0** returned `status=exists`.

Results are in `outputs/reports/control_group_report.md`.

### Probability Analysis

**Critical question**: How likely is it to find 8 on-chain identities by chance?

We've calculated the statistical probability in `scripts/verify/statistical_significance.py`:

```bash
python scripts/verify/statistical_significance.py
```

This calculates:
- Total possible identity space (26^60 with checksum constraints)
- Estimated number of on-chain identities
- Probability of finding identities by chance

**Important limitations**:
- We don't know the exact number of on-chain identities
- Probability calculations are estimates
- The birthday paradox means collisions become likely with enough attempts
- **Multiple-testing problem**: We tested many methods (see `METHODS_TESTED.md`)
- **Method selection**: Methods were partially data-driven (see `METHOD_SELECTION_RATIONALE.md`)

**What this means**: The control group (0 hits in 1000 random matrices) and Monte-Carlo simulation (see below) provide evidence, but probability alone doesn't prove intentional encoding. The findings are reproducible and verifiable - you can check them yourself.

### Monte-Carlo Simulation

**Gold standard validation**: We run 10,000 random matrices with the same distribution as Anna Matrix:

```bash
python scripts/verify/monte_carlo_full_simulation.py --matrices 10000
```

This tests the null hypothesis directly: Do random matrices produce on-chain identities?

Results are in `outputs/reports/monte_carlo_simulation.md`. This is stronger evidence than Bonferroni correction alone.

---

## Seed Candidate Scan

The identities themselves aren't seeds (Qubic seeds need to be 55 lowercase characters). The script `scripts/core/seed_candidate_scan.py` tests various transformations and documents why the eight identities don't work as seeds directly. They're identity bodies with checksums, not seeds.

The script outputs both Markdown and JSON. If you run it with `--test-derivation`, it'll also derive the Layer-2 identities from the bodies (treating them as seeds) and check those on-chain.

---

## Dual-Layer Identity Cluster

Each 56-letter body from the matrix can be used as a seed (first 55 chars, lowercase). When you derive identities from those seeds, you get a second cluster of identities that also exist on-chain. So we have Layer-1 (the original 8 from the matrix) and Layer-2 (the 8 derived from seeds).

Run the deep scan to get everything:

```bash
docker run --rm -e PYTHONPATH=/workspace -v "$PWD":/workspace -w /workspace qubic-proof \
  python scripts/verify/identity_deep_scan.py
```

This spits out:

- `outputs/derived/identity_deep_scan.json` – all the data in JSON format (seeds, identities, ticks, balances, assets, etc.)
- `outputs/derived/identity_deep_scan.md` – human-readable table with the full seed inventory

---

## Repository Layout

Quick overview of what's where:

```
analysis/                   # Historical extraction & exploration scripts
scripts/
  core/                     # Core logic helpers (seed scan, derivations)
  verify/                   # RPC + control-group tools + deep scans
  utils/                    # Hash comparison helpers
data/anna-matrix/           # Source Excel (required input)
outputs/reports/            # Evidence artefacts (Markdown/JSON)
outputs/derived/            # Dual-layer identity exports (JSON/Markdown)
Dockerfile.qubipy           # Reproducible environment for QubiPy
PROOF_OF_WORK.md            # Narrative of the complete pipeline
```

The `analysis/` directory contains exploratory scripts - vortex density analysis, peptide projections, and similar experimental approaches. These are marked as hypothesis exploration in their reports, not proven facts. This is experimental work and findings may change as research continues.

---

## One-Click Verification

**Fastest way to verify everything:**

```bash
./run_all_verifications.sh
```

This script:
1. Verifies matrix file integrity (hash check)
2. Extracts all identities (diagonal + vortex)
3. Runs control group test
4. Calculates statistical significance
5. Performs on-chain verification (if Docker available)
6. Generates `verification_complete.txt` with hash

**No manual steps required** - just run the script and wait.

## Minimal Local Quickstart (without Docker)

If you don't want to use Docker, you can set up a local environment:

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Recreate the diagonal report and plot
python -m analysis.21_base26_identity_extraction

# Run the control group without RPC (structure-only)
python scripts/verify/control_group.py --matrices 200 --no-rpc
```

Note: For on-chain verification you'll need QubiPy. The Docker setup includes it automatically. For local setup, install QubiPy separately or use Docker (recommended).

---

## Verification Checklist

If you want to verify everything yourself, here's what to do:

1. **File integrity** – confirm the Excel hash (`bdee333b...`). Just run `shasum -a 256 data/anna-matrix/Anna_Matrix.xlsx` and compare.
2. **Extraction** – re-run the diagonal/vortex scripts to regenerate `outputs/reports/*.md`. Should match the documented results.
3. **On-chain proof** – execute `scripts/verify/rpc_check.py` (Docker or local). All 8 should exist.
4. **Control group** – run `scripts/verify/control_group.py` to confirm the anomaly. Random matrices should produce zero hits.
5. **Seed analysis** – review `outputs/reports/seed_candidate_scan.md` (and `outputs/derived/identity_deep_scan.md`) for seed eligibility + derived identities.

If all five steps work, you'll have verified the same facts documented here. Everything should be reproducible.

---

## Independent Verification

**We encourage independent verification**. Anyone can:

1. Download the matrix file (hash verified)
2. Run the extraction scripts (or use `./run_all_verifications.sh`)
3. Check identities on-chain using Qubic RPC
4. Run the control group test
5. Calculate statistical significance

**Submit your verification**: See `external_verifications/README.md` for how to submit independent verification results.

**Current verifications**: See `external_verifications/` directory (currently empty - be the first!)

External verification is essential for credibility. If multiple researchers can reproduce the findings, it strengthens the evidence significantly.

## Research Status

**Current Phase**: Active Research

We're continuing to:
- Improve statistical analysis
- Test additional extraction methods
- Validate findings on-chain
- Seek independent verification

**What we know**:
- 8 identities exist on-chain (verifiable fact)
- They're reproducible from the matrix (verifiable fact)
- Random matrices don't produce the same results (verifiable fact)

**What we don't know**:
- Whether these were intentionally encoded
- Whether this is statistically significant **after multiple-testing correction** (see `METHODS_TESTED.md`)
- Whether other extraction methods would find more identities
- **Why would someone hide seeds in public scores?** (Logical inconsistency - see "Open Questions")
- How many total extraction patterns are possible (we tested a tiny fraction)

**Critical limitation**: Methods were partially data-driven (see `METHOD_SELECTION_RATIONALE.md`). This means we cannot claim formal statistical significance - we treat findings as a strong anomaly, not a statistically proven event.

The core findings are reproducible and verifiable. Some exploratory analyses in `analysis/` are experimental and may evolve. 
