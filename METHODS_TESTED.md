# Methods Tested - Complete Inventory

This document lists ALL extraction and decoding methods we tested, not just the successful ones. This is important for understanding the multiple-testing problem.

## Successful Methods (Found On-Chain Identities)

### 1. Base-26 Diagonal Extraction
- **Script**: `analysis/21_base26_identity_extraction.py`
- **Method**: Extract 56 characters along diagonal paths, Base-26 encode, add checksum
- **Pattern**: 4 diagonal patterns starting at rows 0, 32, 64, 96
- **Result**: 4 identities found, all on-chain
- **Success rate**: 4/4 (100% of tested patterns)

### 2. Base-26 Vortex Extraction
- **Script**: `analysis/71_9_vortex_extraction.py`
- **Method**: Extract along 9-vortex ring patterns, Base-26 encode, add checksum
- **Pattern**: 4 vortex rings
- **Result**: 4 identities found, all on-chain
- **Success rate**: 4/4 (100% of tested patterns)

**Total successful**: 8 identities from 2 methods, 8 patterns tested

## Methods Tested (No On-Chain Results)

### 3. Repeating Block Decoder
- **Script**: `analysis/22_repeating_block_decoder.py`
- **Method**: Look for repeating patterns in Base-26 encoded identities
- **Result**: Patterns found, but no additional on-chain identities
- **Status**: Explored, no hits

### 4. Header Offset Study
- **Script**: `analysis/23_header_offset_study.py`
- **Method**: Test different header offsets in Base-26 decoding
- **Result**: Various offsets tested, no on-chain identities found
- **Status**: Explored, no hits

### 5. DNA Encoding Probe
- **Script**: `analysis/24_dna_encoding_probe.py`
- **Method**: Map matrix values to DNA sequences (A, T, G, C)
- **Result**: DNA sequences generated, but no meaningful patterns or on-chain identities
- **Status**: Explored, no hits

### 6. Amino Acid Translation
- **Script**: `analysis/25_amino_acid_translation.py`
- **Method**: Translate DNA sequences to amino acids
- **Result**: Amino acid sequences generated, no on-chain identities
- **Status**: Explored, no hits

### 7. Layer Crossprobe
- **Script**: `analysis/26_layer_crossprobe.py`
- **Method**: Test cross-layer relationships
- **Result**: Patterns explored, no additional on-chain identities
- **Status**: Explored, no hits

### 8. Peptide ASCII Decoder
- **Script**: `analysis/27_peptide_ascii_decoder.py`
- **Method**: Decode peptide sequences to ASCII
- **Result**: ASCII strings generated, no on-chain identities
- **Status**: Explored, no hits

### 9. Layer Crossprobe Visual
- **Script**: `analysis/28_layer_crossprobe_visual.py`
- **Method**: Visual analysis of layer relationships
- **Result**: Visualizations created, no additional findings
- **Status**: Explored, no hits

### 10. Peptide Keyword Scan
- **Script**: `analysis/29_peptide_keyword_scan.py`
- **Method**: Search for keywords in peptide sequences
- **Result**: No meaningful keywords found
- **Status**: Explored, no hits

### 11. Base-26 Word Probe
- **Script**: `analysis/30_base26_word_probe.py`
- **Method**: Search for English words in Base-26 encoded strings
- **Result**: No meaningful words found
- **Status**: Explored, no hits

### 12. Alternative Pattern Scan
- **Script**: `analysis/31_alternative_pattern_scan.py`
- **Method**: Test alternative extraction patterns (spirals, zigzags, etc.)
- **Result**: Various patterns tested, no on-chain identities found
- **Status**: Explored, no hits

### 13. Layer-3 Seed Probe
- **Script**: `analysis/32_layer3_seed_probe.py`
- **Method**: Derive Layer-3 identities from Layer-2 seeds
- **Result**: Layer-3 identities derived, but not verified on-chain (or no hits)
- **Status**: Explored, limited results

### 14. 9-Vortex Analysis
- **Script**: `analysis/70_9_vortex_analysis.py`
- **Method**: Analyze vortex patterns in detail
- **Result**: Analysis completed, but extraction already done in #2
- **Status**: Redundant with successful method

## Summary Statistics

- **Total methods tested**: 14
- **Methods with on-chain hits**: 2 (14.3%)
- **Methods with no hits**: 12 (85.7%)
- **Total patterns tested**: ~50+ (including variations within methods)
- **On-chain identities found**: 8

## Multiple-Testing Problem

**Critical issue**: We tested many methods, but only report the successful ones. This is a classic multiple-testing problem (also called p-hacking or cherry-picking).

**What this means**:
- If you test 100 different methods, you expect some to produce "significant" results by chance
- The probability of finding 8 identities by chance increases with the number of methods tested
- Our statistical analysis in `statistical_significance.py` doesn't account for this

**Bonferroni correction** (rough estimate):
- If we tested ~50 different patterns/methods
- Adjusted significance level: 0.05 / 50 = 0.001
- Our findings would need to be significant at p < 0.001 to be considered statistically significant after correction

**We don't have exact p-values**, but the multiple-testing problem is real and reduces the statistical significance of our findings.

## What We Don't Know

1. **How many other extraction methods would also find identities?**
 - We only tested specific patterns
 - Other researchers might find different patterns that also work

2. **Are our successful methods special, or just the first ones we tried?**
 - We tested diagonal and vortex early
 - Would other methods have worked if we tried them first?

3. **How many total extraction patterns are possible?**
 - With a 128×128 matrix, there are millions of possible paths
 - We tested a tiny fraction

4. **Is the success rate (2/14 methods) higher than expected by chance?**
 - This depends on how many on-chain identities exist
 - We don't know the baseline success rate for random extraction

## Conclusion

**We found 8 on-chain identities using 2 specific extraction methods.**

**We tested 12 other methods that found nothing.**

**This is important context for evaluating the statistical significance of our findings.**

The multiple-testing problem means our findings are less statistically significant than they appear at first glance. However, the control group (0 hits in 1000 random matrices) still provides some evidence that our successful methods are not purely random.
