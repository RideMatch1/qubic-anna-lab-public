## Proof of Work: Anna Matrix → Found Keys & Identities

**Status**: Active Research

This document walks through the exact steps to extract real Qubic identities and keys from the Anna Matrix Excel file. All commands, hashes, and outputs are documented here so you can reproduce everything.

**What we found**: 8 Qubic identities (public keys) extracted from the matrix that exist on-chain. Each identity contains a seed that derives an additional valid identity. These are verifiable facts - see [`FOUND_IDENTITIES.md`](FOUND_IDENTITIES.md) for all identities.

**What we don't know**: Whether these were intentionally encoded or found by chance. Statistical significance depends on unknown factors (total on-chain identities). See limitations below.

---

### 1. Source Integrity

First thing - verify you have the right file. The hash is important because even a tiny change would break everything.

| File | Location | SHA256 |
| --- | --- | --- |
| Anna_Matrix.xlsx | `data/anna-matrix/Anna_Matrix.xlsx` | `bdee333b4006c1b7ab24a0dc61de76b60210c2db7bd8822c50e8509aff907c45` |
| Git commit (current) | `git rev-parse HEAD` | (varies by commit) |

To check the hash yourself:

```bash
shasum -a 256 data/anna-matrix/Anna_Matrix.xlsx
```

Should match the hash above. If it doesn't, you're working with a different file.

---

### 2. Extraction

Identities were extracted using two different patterns from the matrix - diagonals and a vortex pattern. The scripts are:

- `analysis/21_base26_identity_extraction.py` - extracts 4 identities from diagonal walks
- `analysis/71_9_vortex_extraction.py` - extracts 4 identities from a vortex pattern

These generate:

- `outputs/reports/base26_identity_report.md` - diagonal identities
- `outputs/reports/9_vortex_identity_report.md` - vortex identities
- `outputs/plots/base26_identity_paths.png` - visualization of diagonal paths
- `outputs/plots/9_vortex_paths.png` - visualization of vortex paths

Result: 8 valid 60-character identities total (4 diagonal, 4 vortex). Each one is a 56-letter body plus a 4-letter checksum.

---

### 3. On-Chain Verification

Checking if these identities actually exist on the Qubic blockchain. Tool: `scripts/verify/rpc_check.py` (docker or local)

Docker usage (recommended because QubiPy dependencies can be tricky):

```bash
docker build -f Dockerfile.qubipy -t qubic-proof .
docker run --rm -it -v "$PWD":/workspace -w /workspace qubic-proof \
 python scripts/verify/rpc_check.py
```

This writes to `outputs/reports/qubipy_identity_check.md`

Example output:

```
Connected to Qubic RPC. Latest tick: 37707442
Diagonal #1 ... EXISTS – Balance: 0 QU – ValidForTick: 37707446
...
Vortex #4 ... EXISTS – Balance: 0 QU – ValidForTick: 37707448
```

All eight extracted identities exist on the live network. These are real Qubic public keys (identities) that exist on-chain. They're not random strings - they're actual cryptographic keys.

---

### 4. Seed Candidate Audit

Testing whether the identities themselves could be used as seeds. Qubic seeds need to be exactly 55 lowercase characters. Tool: `scripts/core/seed_candidate_scan.py`

Purpose: check whether identities/bodies conform to the 55-char lowercase seed requirement

Outputs:

- `outputs/reports/seed_candidate_scan.md` - human readable report
- `outputs/reports/seed_candidate_scan.json` - machine readable data

Finding: The 60-char identities themselves aren't seeds, but their 56-char bodies can be converted to valid 55-char seeds. Formula: `identity.lower()[:55] = seed`. These seeds are valid and can be used to derive additional identities.

---

### 5. Layer-2 Identity Cluster (Seeds → Identities)

We discovered that the identity bodies can be converted to valid seeds. Each 56-char body yields a 55-char seed using the formula `identity.lower()[:55]`. These seeds are valid and derive additional on-chain identities. Tools:

- `scripts/core/seed_candidate_scan.py --test-derivation` - tests seed derivation
- `scripts/verify/identity_deep_scan.py` - full deep scan of both layers

Outputs:

- `outputs/reports/seed_candidate_scan.md` (seed derivation log)
- `outputs/derived/identity_deep_scan.md` - human readable table
- `outputs/derived/identity_deep_scan.json` - full data dump

Summary:

- Each 56-letter body (lowercase, first 55 chars) acts as a valid seed.
- The derived seeds generate a second cluster of 8 identities (Layer-2) at ticks `37709095-37709746`.
- Deep scan confirms all 16 identities exist on-chain (balance 0, no assets yet).
- The JSON inventory contains every seed, identity, tick, and asset list.

So we have Layer-1 (the original 8 from the matrix) and Layer-2 (the 8 derived from seeds). Both clusters exist on-chain.

---

### 6. Statistical Control Group

To verify this wasn't just an artifact of the extraction method, random matrices were generated and processed with the same extraction. Tool: `scripts/verify/control_group.py`

Command (example):

```bash
python scripts/verify/control_group.py --matrices 1000 --seed 42
```

Output: `outputs/reports/control_group_report.md`

Summary:

- Matrices tested: 1,000
- Identities generated: 4,000 (4 per matrix, same as Anna Matrix)
- RPC hits: 0

**What this proves**: Random matrices don't produce on-chain identities with our extraction method.

**What this doesn't prove**: That the Anna Matrix identities were intentionally encoded. The birthday paradox means random collisions are possible with enough attempts.

### 7. Statistical Significance Analysis

Tool: `scripts/verify/statistical_significance.py`

```bash
python scripts/verify/statistical_significance.py
```

Output: `outputs/reports/statistical_significance.md`

This calculates the probability of finding identities by chance, but has critical limitations:
- We don't know the exact number of on-chain identities
- Probability calculations are estimates
- The birthday paradox means collisions become likely with enough attempts

**Conclusion**: Probability alone doesn't prove intentional encoding. The control group provides additional evidence, but the question remains open.

### 8. Monte-Carlo Simulation

**Gold standard validation**: We run 10,000 random matrices with the same distribution as Anna Matrix:

```bash
python scripts/verify/monte_carlo_full_simulation.py --matrices 10000
```

This tests the null hypothesis directly: Do random matrices produce on-chain identities?

Results are in `outputs/reports/monte_carlo_simulation.md`. This is stronger evidence than Bonferroni correction alone.

---

By reproducing the steps above you can independently confirm (or falsify) every claim made in this repository. Everything should be verifiable on-chain and reproducible from the source Excel file.

---

## Limitations and Open Questions

**What we can prove**:
- 8 identities exist on-chain (verifiable fact)
- They're reproducible from the matrix (verifiable fact)
- Random matrices don't produce the same results (verifiable fact)

**What we cannot prove**:
- Whether these were intentionally encoded
- Whether this is statistically significant **after multiple-testing correction** (see `METHODS_TESTED.md`)
- Whether other extraction methods would find more identities
- **Why someone would hide seeds in public scores** (logical inconsistency - see "Open Questions")

**Critical limitation**: Methods were partially data-driven (see `METHOD_SELECTION_RATIONALE.md`). This means we cannot claim formal statistical significance - we treat findings as a strong anomaly, not a statistically proven event.

**Critical questions**:
- How many identities exist on-chain total? (We don't know)
- What's the probability of finding 8 by chance **after multiple-testing correction**? (See `METHODS_TESTED.md`)
- Are there other extraction methods that would find more? (We tested ~14, only 2 found identities)
- **Why would someone hide seeds in public scores?** (Logical inconsistency - if intentional, why public?)

**We encourage independent verification**. If you verify these findings, please share your results.

---

## Research Status

**Current Phase**: Active Research

This is ongoing experimental work. Research continues on:
- Statistical significance analysis
- Additional extraction methods
- On-chain verification
- Independent verification

Core extraction and verification methods are stable and reproducible. Some exploratory analyses are experimental and findings may evolve.
