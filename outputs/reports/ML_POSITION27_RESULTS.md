# ML Position 27 Results - 20k Validation

**Date:** 27 Nov 2025 
**Status:** Completed 
**Target:** 50%+ Accuracy for Position 27 prediction

---

## Summary

- **Dataset:** 14,697 validated identities from 20k RPC validation
- **Features:** 112 features (55 seed positions + matrix values + block positions)
- **Best Model:** Random Forest
- **Accuracy:** 42.69% (test), 41.86% ± 0.17% (cross-validation)
- **Baseline:** 32.72% (weighted seed predictor)

---

## Model Comparison

### Decision Tree
- **Test Accuracy:** 32.07%
- **CV Score:** 32.96% ± 0.69%
- **Status:** Below baseline

### Random Forest **BEST**
- **Test Accuracy:** 42.69%
- **CV Score:** 41.86% ± 0.17%
- **Status:** 9.97% improvement over baseline
- **Top Features:** 78, 63, 62, 75, 106, 111, 90, 100, 91, 88

### Gradient Boosting
- **Test Accuracy:** 39.49%
- **CV Score:** 43.42% ± 0.69%
- **Status:** Higher CV variance, lower test accuracy

---

## Feature Analysis

### Top 10 Most Important Features (Random Forest)

1. **Feature 78** - Importance: 0.0149
2. **Feature 63** - Importance: 0.0134
3. **Feature 62** - Importance: 0.0122
4. **Feature 75** - Importance: 0.0110
5. **Feature 106** - Importance: 0.0108
6. **Feature 111** - Importance: 0.0106
7. **Feature 90** - Importance: 0.0104
8. **Feature 100** - Importance: 0.0103
9. **Feature 91** - Importance: 0.0103
10. **Feature 88** - Importance: 0.0102

**Note:** Feature mapping:
- Features 0-54: Seed positions (excluding position 27)
- Features 55-58: Block-end positions (13, 41, 55, excluding 27)
- Features 59+: Matrix values, interactions, etc.

---

## Accuracy Gap Analysis

**Current:** 42.69% 
**Target:** 50%+ 
**Gap:** 7.31 percentage points

### Potential Improvements

1. **Feature Engineering:**
 - Add seed position interactions (e.g., position 4 × position 30)
 - Include modulo operations (mod 4, mod 26)
 - Add grid coordinates (7×7 grid mapping)

2. **Model Tuning:**
 - Hyperparameter optimization (n_estimators, max_depth, etc.)
 - Ensemble methods (combine Random Forest + Gradient Boosting)
 - Deep learning models (if dataset size allows)

3. **Data Quality:**
 - Increase validation dataset (currently 14,697 from 20k)
 - Filter out low-confidence predictions
 - Add Layer-4 data for comparison

---

## Next Steps

1. **Hyperparameter Tuning:**
 - Run `ml_position27_hypersearch.py` for optimized parameters
 - Target: 45%+ accuracy

2. **Feature Engineering:**
 - Add seed interaction features
 - Include grid coordinate features
 - Test modulo-based features

3. **Ensemble Methods:**
 - Combine Random Forest + Gradient Boosting
 - Weighted voting based on confidence scores

4. **Layer-4 Analysis:**
 - Compare Layer-3 vs Layer-4 predictions
 - Test if Layer-4 improves accuracy

---

## Statistical Validation

**See:** `ML_POSITION27_STATISTICAL_VALIDATION.md` for complete statistical analysis.

### Key Statistical Results

- **95% Confidence Interval:** [41.89%, 43.49%]
- **99% Confidence Interval:** [41.64%, 43.74%]
- **vs. Random (4 classes):** p < 0.001, Cohen's h = 0.38 (small-medium effect)
- **vs. Weighted seed predictor:** p = 1.83e-140, Cohen's h = 0.21 (small effect)
- **Statistical Significance:** Very highly significant (p < 0.001) against all baselines

---

## Files

- **Results:** `outputs/derived/ml_position27_50percent_results.json`
- **Status Log:** `outputs/derived/ml_position27_50percent_status.txt`
- **Validated Data:** `outputs/derived/rpc_validation_20000_validated_data.json`
- **Statistical Validation:** `outputs/reports/ML_POSITION27_STATISTICAL_VALIDATION.md`

---

**Status:** ML training completed. Accuracy improved from 32.72% to 42.69%, but still below 50% target. **Statistically validated** - all improvements are highly significant (p < 0.001). Next: hyperparameter tuning and feature engineering.
