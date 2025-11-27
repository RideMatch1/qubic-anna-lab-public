# Multiple Testing Correction Analysis

**Date:** 27 Nov 2025 
**Purpose:** Apply multiple testing corrections for 60 position tests

---

## Problem Statement

When testing 60 positions (0-59), we face the **multiple testing problem**:
- Testing 60 hypotheses increases the chance of false positives
- Without correction, we expect ~3 false positives at α=0.05 (60 × 0.05 = 3)
- Need to control **family-wise error rate** (FWER) or **false discovery rate** (FDR)

---

## Correction Methods

### 1. Bonferroni Correction (FWER Control)

**Method:** Divide α by number of tests
- **Corrected α:** 0.05 / 60 = 0.00083
- **Interpretation:** Very conservative, controls probability of ANY false positive

**Results:**
- **Corrected α:** 0.000833
- **Significant positions after correction:** 0

### 2. FDR Correction (Benjamini-Hochberg)

**Method:** Less conservative than Bonferroni, controls expected proportion of false discoveries
- **Interpretation:** Allows some false positives, but controls their rate

**Results:**
- **Significant positions after correction:** 0

---

## Detailed Results

### Known Significant Positions (Before Correction)

#### Position 4

- **Original p-value:** 0.013768
- **Bonferroni:** Not significant (α = 0.000833)
- **FDR corrected p-value:** 0.500000
- **FDR:** Not significant

#### Position 27

- **Original p-value:** 0.028000
- **Bonferroni:** Not significant (α = 0.000833)
- **FDR corrected p-value:** 0.500000
- **FDR:** Not significant

#### Position 30

- **Original p-value:** 0.025547
- **Bonferroni:** Not significant (α = 0.000833)
- **FDR corrected p-value:** 0.500000
- **FDR:** Not significant

---

## Interpretation

### Bonferroni Correction

Bonferroni is **very conservative**:
- Position 4: p=0.013768 > 0.00083 **Not significant after correction**
- Position 27: p=0.028 > 0.00083 **Not significant after correction**
- Position 30: p=0.025547 > 0.00083 **Not significant after correction**

**Conclusion:** None of the positions are significant after Bonferroni correction.

### FDR Correction

FDR is **less conservative**:
- Position 4: FDR p = 0.500000 Not significant
- Position 27: FDR p = 0.500000 Not significant
- Position 30: FDR p = 0.500000 Not significant

---

## Recommendations

### For Position 27 ML Results (42.69% accuracy)

**Status:** Position 27 was **pre-specified** as the primary hypothesis:
- Position 27 constraint (only 4 characters) was discovered first
- ML analysis focused specifically on position 27
- Not part of exploratory 60-position scan

**Conclusion:** Multiple testing correction **may not apply** to position 27 ML results, as it was:
1. Pre-specified hypothesis
2. Independent validation (20k RPC calls)
3. Large sample size (n=14,697)

**However:** For full transparency, we report:
- Position 27 p-value: 1.83e-140 (vs. weighted seed predictor)
- Even with Bonferroni correction (α=0.00083), this is **highly significant**

### For Exploratory Position Tests (4, 30, 55, etc.)

**Status:** These were part of exploratory analysis:
- 60 positions tested
- Multiple testing correction **required**
- Bonferroni: None significant
- FDR: Check individual corrected p-values

**Recommendation:**
- Report both uncorrected and corrected p-values
- Clearly label as "exploratory" vs. "pre-specified"
- Use FDR for less conservative interpretation

---

## Limitations

1. **Incomplete p-value data:** Only 3 positions have documented p-values
2. **Conservative assumption:** Unknown positions assumed p=0.5
3. **Actual test count:** May be more than 60 if multiple methods per position

---

## Conclusion

**Multiple testing correction is critical** for exploratory analyses.

**For position 27 ML results:**
- Pre-specified hypothesis → correction may not apply
- But p=1.83e-140 is significant even with correction

**For exploratory position tests:**
- Bonferroni: None significant
- FDR: Check individual corrected p-values
- Report both corrected and uncorrected results

---

**Generated:** 27 Nov 2025 
**Method:** Bonferroni and FDR (Benjamini-Hochberg) corrections
