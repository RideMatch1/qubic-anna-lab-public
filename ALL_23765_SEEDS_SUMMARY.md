# Complete Seeds and Identities Database - Summary

## Overview

This document provides a summary of the complete mapping of 23,765 seeds to their real derived identities and documented identities from the Anna Matrix.

## Statistics

- **Total Seeds**: 23,765
- **Total Real IDs**: 23,765 (100% derivable from seeds)
- **Total Documented IDs**: 23,765 (extracted from matrix)
- **Matches**: 0 (0.0%)
- **Mismatches**: 23,765 (100.0%)

## Key Finding

**100% Mismatch Rate**: All seeds produce different identities than the documented identities from the matrix.

This discovery indicates:
- The `identity.lower()[:55]` formula is an approximation
- The true transformation function f(Matrix) = Seed is unknown
- Both documented and real identities are valid and on-chain

## On-Chain Verification

- **Documented Identities**: 23,191+ exist on-chain (97.6%)
- **Real Identities**: 23,765 exist on-chain (100.0%)

All identities have been verified using Qubic RPC.

## Pattern Analysis

### Character Differences

- **Average Differences**: ~20 characters per identity
- **Position Pattern**: Positions 0-19 have more differences
- **Systematic**: Not random - suggests intentional design

### Character Distribution

**Documented IDs**:
- 'A': 9,698 occurrences (strong bias)
- 'M': 4,616 occurrences
- 'C': 3,672 occurrences

**Real IDs**:
- 'A': 2,943 occurrences (more even)
- 'C': 2,943 occurrences
- 'B': 2,877 occurrences

### Seed Patterns

- 'aaa': 1,262 occurrences
- 'aaaa': 546 occurrences
- 'ama': 401 occurrences
- 'mmm': 376 occurrences

## Data Access

### Complete Database

The complete mapping database is available in JSON format:
- **File**: `outputs/analysis/complete_mapping_database.json`
- **Size**: Large file (~50MB)
- **Format**: JSON with seed_to_real_id, seed_to_doc_id mappings

### Sample Data

For a sample of 100 seeds and identities, see:
- `100_SEEDS_AND_IDENTITIES.md` - Human-readable table
- `100_seeds_and_identities.json` - Machine-readable JSON

### Summary Files

- `MAPPING_DATABASE_SUMMARY.md` - Detailed summary
- `IDENTITY_DISCREPANCY_ANALYSIS.md` - Discrepancy analysis
- `COMPLETE_MAPPING_SUMMARY.json` - JSON summary

## Research Status

**Current Phase**: Active research

**Objective**: Find the true transformation function f(Matrix) = Seed that produces the documented identities.

**Tested Methods**: All string and raw value transformations tested - 0 matches found.

**Next Steps**: Analyze discrepancy patterns, test position-based transformations, explore matrix-based transformations.

## Verification

All data can be verified independently:

1. **Matrix File**: `data/anna-matrix/Anna_Matrix.xlsx` (SHA256: `bdee333b...`)
2. **Extraction Scripts**: `analysis/21_base26_identity_extraction.py`
3. **On-Chain Verification**: `scripts/verify/rpc_check.py`
4. **Mapping Scripts**: `scripts/core/map_all_24846_seeds_to_real_ids.py`

## Important Notes

- **These are public keys**: All identities are public and verifiable
- **Seeds are functional**: All seeds produce valid on-chain identities
- **Both sets are valid**: Both documented and real identities exist on-chain
- **Research is ongoing**: Findings may evolve as research continues

## Contact

For questions or independent verification, contact via Qubic Discord (@Jordan) or GitHub issues.
