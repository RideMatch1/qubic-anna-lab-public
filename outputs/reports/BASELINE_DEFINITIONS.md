# Baseline Definitions - Complete Clarification

**Date:** 27 Nov 2025 
**Purpose:** Clarify all baseline definitions to resolve contradictions

---

## Problem Statement

Multiple baseline definitions exist in the documentation, causing confusion:
- 3.85% (random baseline)
- 25.10% (matrix mod 4 baseline)
- 32.72% (weighted seed predictor)
- 33.30% (weighted top 10)

**Question:** Which baseline is correct for which comparison?

---

## Complete Baseline Taxonomy

### Category 1: Position 27 Character Prediction

#### 1.1 Random Baseline (3.85%)
- **Definition:** Theoretical random chance if all 26 letters were equally likely
- **Calculation:** 1/26 = 3.85%
- **Relevance:** **NOT RELEVANT** - Position 27 is constrained to 4 characters (A/B/C/D), not 26
- **Use Case:** Only for theoretical comparison, not practical baseline
- **Status:** **Misleading** - Should not be used as primary baseline

#### 1.2 Random Baseline (25.00%)
- **Definition:** Random chance for 4 equally likely classes
- **Calculation:** 1/4 = 25.00%
- **Relevance:** **RELEVANT** - Position 27 uses only 4 characters (A/B/C/D)
- **Use Case:** Theoretical lower bound for position 27
- **Status:** **Valid baseline** for theoretical comparison

#### 1.3 Matrix Mod 4 Baseline (25.10%)
- **Definition:** Simplest method using only matrix coordinate (27, 13) mod 4
- **Calculation:** `matrix[27, 13] % 4` → character A/B/C/D
- **Relevance:** **RELEVANT** - Simplest practical method
- **Use Case:** Baseline for simple methods (no seed information)
- **Status:** **Valid baseline** for simple method comparison
- **Source:** `POSITION27_ACCURACY_BREAKTHROUGH.md`

#### 1.4 Weighted Seed Predictor (32.72%)
- **Definition:** Weighted seed-based predictor using all 55 seed positions
- **Calculation:** Weighted combination of seed positions (from 20k RPC validation)
- **Relevance:** **RELEVANT** - Best non-ML method using seed information
- **Use Case:** **PRIMARY BASELINE** for ML model comparison
- **Status:** **Valid baseline** - This is the correct baseline for ML comparison
- **Source:** `ML_POSITION27_RESULTS.md`
- **Dataset:** 20,000 RPC validation run

#### 1.5 Weighted Top 10 (33.30%)
- **Definition:** Weighted combination of top 10 seed positions
- **Calculation:** Weighted top 10 seed positions
- **Relevance:** **RELEVANT** - Best simple seed-based method
- **Use Case:** Baseline for simple seed-based methods
- **Status:** **Valid baseline** - Alternative baseline for seed-based methods
- **Source:** `POSITION27_ACCURACY_BREAKTHROUGH.md`

---

## Recommended Baseline Selection

### For ML Model Comparison (Position 27)

**PRIMARY BASELINE:** **32.72% (Weighted Seed Predictor)**

**Reasoning:**
1. Uses same dataset (20k RPC validation)
2. Uses same seed information (all 55 positions)
3. Represents best non-ML method
4. Fair comparison (same features, different algorithm)

**Statistical Comparison:**
- ML Accuracy: 42.69%
- Baseline: 32.72%
- Improvement: +9.97% (30.5% relative)
- p-value: 1.83e-140 (highly significant)
- Effect size (Cohen's h): 0.21 (small effect)

**See:** `ML_POSITION27_STATISTICAL_VALIDATION.md`

### For Simple Method Comparison

**BASELINE:** **25.10% (Matrix Mod 4)**

**Reasoning:**
1. Simplest practical method
2. No seed information required
3. Represents minimal knowledge baseline

**Comparison:**
- Matrix Mod 4: 25.10%
- Weighted Top 10: 33.30%
- ML Random Forest: 42.69%

---

## Category 2: Position 4/55 On-Chain Prediction

### 2.1 Naive Majority Class Baseline (66.0%)
- **Definition:** Always predict majority class (on-chain vs off-chain)
- **Calculation:** `max(onchain_count, offchain_count) / total * 100`
- **Relevance:** **RELEVANT** - Standard baseline for binary classification
- **Use Case:** Baseline for on-chain prediction tasks
- **Status:** **Valid baseline** for position 4/55
- **Source:** `validate_selection_mechanism.py` (for Position 4/55 tests)

**Note:** This is a **different task** than position 27 character prediction!

---

## Baseline Comparison Table

| Baseline | Value | Task | Relevance | Status |
|----------|-------|------|-----------|--------|
| Random (26 classes) | 3.85% | Position 27 | Not relevant | Misleading |
| Random (4 classes) | 25.00% | Position 27 | Theoretical | Valid |
| Matrix Mod 4 | 25.10% | Position 27 | Simple method | Valid |
| Weighted Seed Predictor | 32.72% | Position 27 | **PRIMARY** | **RECOMMENDED** |
| Weighted Top 10 | 33.30% | Position 27 | Simple seed | Valid |
| Naive Majority | 66.0% | Position 4/55 | Binary classification | Valid |

---

## Recommendations

### For Position 27 ML Results

**Use:** 32.72% (Weighted Seed Predictor) as primary baseline

**Justification:**
- Same dataset
- Same features (seed positions)
- Fair comparison
- Statistically validated (p = 1.83e-140)

**Also report:**
- vs. 25.10% (Matrix Mod 4) - shows improvement over simplest method
- vs. 33.30% (Weighted Top 10) - shows improvement over best simple seed method

### For Documentation

**Clarify in all reports:**
- Which baseline is used for which comparison
- Why that baseline is appropriate
- Context of the comparison

---

## Conclusion

**Single Source of Truth:**

For **Position 27 ML Model (42.69% accuracy)**:
- **Primary Baseline:** 32.72% (Weighted Seed Predictor)
- **Improvement:** +9.97% (30.5% relative)
- **Statistical Significance:** p = 1.83e-140 (highly significant)
- **Effect Size:** Cohen's h = 0.21 (small effect)

**All other baselines are valid** for different contexts, but **32.72% is the correct baseline** for ML model comparison.

---

**Generated:** 27 Nov 2025 
**Purpose:** Resolve baseline definition contradictions for peer review
