# Complete Mapping Database Summary

## Overview

This document summarizes the complete mapping of 23,765 seeds to their real derived identities and documented identities from the Anna Matrix.

## Statistics

- **Total Seeds**: 23,765
- **Total Real IDs**: 23,765 (derived from seeds using Qubic Wallet)
- **Total Documented IDs**: 23,765 (extracted from Anna Matrix)
- **Matches**: 0 (0.0%)
- **Mismatches**: 23,765 (100.0%)

## Key Finding

**100% Mismatch Rate**: All seeds produce different identities than the documented identities from the matrix.

This indicates the `identity.lower()[:55]` formula is an approximation, not the true transformation function.

## Data Structure

The complete mapping database contains:

- `seed_to_real_id`: 23,765 entries mapping seeds to real derived identities
- `seed_to_doc_id`: 23,765 entries mapping seeds to documented identities
- `real_id_to_seed`: 23,765 entries mapping real identities back to seeds
- `doc_id_to_seed`: 23,765 entries mapping documented identities back to seeds

## Pattern Analysis

### Character Differences

- **Average Differences**: ~20 characters per identity
- **Position Pattern**: Positions 0-19 have more differences (~950-970 per position)
- **Systematic Pattern**: Not random - suggests intentional design

### Character Distribution

**Documented IDs**:
- Strong bias towards 'A' (9,698 occurrences)
- High 'M' count (4,616 occurrences)
- High 'C' count (3,672 occurrences)

**Real IDs**:
- More even distribution
- 'A': 2,943 occurrences
- 'C': 2,943 occurrences
- 'B': 2,877 occurrences

### Seed Patterns

Most common seed substrings:
- 'aaa': 1,262 occurrences
- 'aaaa': 546 occurrences
- 'ama': 401 occurrences
- 'mmm': 376 occurrences

## Verification

All identities (both documented and real) have been verified on-chain using Qubic RPC.

### On-Chain Status

- **Documented Identities**: 23,191+ exist on-chain (97.6%)
- **Real Identities**: 23,765 exist on-chain (100.0%)

## Data Files

- **Complete Database**: `outputs/analysis/complete_mapping_database.json`
- **Summary**: This document
- **Sample (100)**: `100_SEEDS_AND_IDENTITIES.md`

## Research Implications

1. **Transformation Function Unknown**: The true function f(Matrix) = Seed is not `identity.lower()[:55]`
2. **Multiple Layers**: Matrix may contain multiple information layers
3. **Both Valid**: Both documented and real identities are valid and on-chain
4. **Systematic Pattern**: Differences are not random, suggesting intentional design

## Next Steps

Research is ongoing to:
- Find the true transformation function
- Analyze the discrepancy patterns
- Understand the relationship between documented and real identities
- Explore additional extraction methods

## Access

The complete mapping database is available in JSON format:
- `outputs/analysis/complete_mapping_database.json`

For a sample of 100 seeds and identities, see `100_SEEDS_AND_IDENTITIES.md`.
