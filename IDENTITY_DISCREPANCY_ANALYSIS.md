# Identity Discrepancy Analysis

## Overview

This document analyzes the discrepancy between documented identities (extracted from Anna Matrix) and real identities (derived from seeds using Qubic Wallet).

## Discovery

**Date**: 2025-11-22

**Finding**: Seeds derived using `identity.lower()[:55]` generate different Qubic identities than the original documented identities from the matrix.

## Statistics

- **Total Seeds Analyzed**: 23,765
- **Matches**: 0 (0.0%)
- **Mismatches**: 23,765 (100.0%)
- **Average Character Differences**: ~20 per identity

## Analysis

### Character Difference Distribution

- **Positions 0-19**: ~950-970 differences per position
- **Positions 20+**: Significantly fewer differences
- **Most Common Differences**: +1 (792), +4 (716), +3 (735), +2 (755)

### Character Pattern Analysis

**Documented Identities**:
- Strong bias towards 'A' (9,698 occurrences)
- High 'M' count (4,616 occurrences)
- High 'C' count (3,672 occurrences)

**Real Identities**:
- More even distribution
- 'A': 2,943 occurrences
- 'C': 2,943 occurrences
- 'B': 2,877 occurrences

### Seed Pattern Analysis

Most common seed substrings:
- 'aaa': 1,262 occurrences
- 'aaaa': 546 occurrences
- 'ama': 401 occurrences
- 'mmm': 376 occurrences

## Interpretation

### What This Means

1. **Formula is Approximation**: `identity.lower()[:55]` is not the true transformation
2. **Matrix Contains Final Identities**: The matrix contains the final identities, not the seeds that generate them
3. **Both Are Valid**: Both documented and real identities exist on-chain
4. **Systematic Pattern**: Differences are not random, suggesting intentional design

### Possible Explanations

1. **Multiple Layers**: Matrix may contain multiple information layers
2. **Unknown Transformation**: True transformation function f(Matrix) = Seed is unknown
3. **Different Extraction**: Documented identities may use different extraction method
4. **Layer Mismatch**: Documented identities may be from different layer

## Research Status

**Current Phase**: Active research to find the true transformation function

**Tested Methods**:
- String transformations (reverse, rotate, XOR, etc.)
- Raw value transformations (mod 26, absolute, etc.)
- Coordinate pattern variations
- All methods tested: 0 matches found

**Next Steps**:
- Analyze discrepancy patterns in depth
- Test position-based transformations
- Test character-based transformations
- Explore matrix-based transformations

## Data Files

- **Complete Mapping**: `outputs/analysis/complete_mapping_database.json`
- **Pattern Analysis**: `outputs/analysis/documented_vs_real_pattern_analysis.json`
- **Pattern Discovery**: `outputs/analysis/pattern_discovery_results.json`
- **Sample (100)**: `100_SEEDS_AND_IDENTITIES.md`

## Verification

All identities (both documented and real) have been verified on-chain:
- **Documented Identities**: 23,191+ on-chain (97.6%)
- **Real Identities**: 23,765 on-chain (100.0%)

## Conclusion

The discrepancy between documented and real identities is systematic and non-random. This suggests intentional design, but the true transformation function remains unknown. Research is ongoing to find the function f(Matrix) = Seed that produces the documented identities.
