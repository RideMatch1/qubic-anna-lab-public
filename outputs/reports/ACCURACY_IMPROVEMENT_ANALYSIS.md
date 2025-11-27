# Accuracy Improvement Analysis

**Generated:** 26 Nov 2025 
**Status:** Validated, data-only, no speculation

---

## Executive Summary

**Experiments covered:**
1. Alternative transformations (modulo variants) for all block-end positions (13/27/41/55). 
2. Two-position combinations (simple intersections). 
3. Multiple modulo families (`mod_4`, `mod_8`, `mod_13`, `mod_26`, `mod_29`).

**Key outcomes:**
- Position 27 delivers the strongest ratio under `mod_8` (2.17× expected) but the same absolute accuracy as `mod_4` (27.11%). 
- Position 55 peaks at `mod_29` ratio (3.73×) yet the raw accuracy stays lower (12.86%). 
- Two-position combinations sit around 3–4% accuracy, matching the product of the individual probabilities.

---

## Critical Findings

### 1. Best transformation per block-end position

| Position | Best modulo | Accuracy | Ratio (Accuracy / expected) | Expected |
|----------|-------------|----------|------------------------------|----------|
| 13 | mod 26 | 13.57% | 3.53× | 3.85% |
| **27** | mod 8 | 27.11% | 2.17× | 12.50% |
| 41 | mod 26 | 13.63% | 3.54× | 3.85% |
| 55 | mod 29 | 12.86% | 3.73× | 3.45% |

- Position 27: `mod_8` owns the best ratio, yet `mod_4` yields the **same** 27.11% accuracy. 
- Position 55: `mod_29` has the highest ratio, but `mod_26` still beats it in absolute accuracy (13.74%). 
- Ratios reflect the expected base rate: smaller denominators inflate the ratio even if accuracy stays flat.

### 2. Position combinations

Top intersections:
1. Position 27 (`mod_4`) ∧ Position 41 (`mod_4`): 3.92% 
2. Position 27 (`mod_4`) ∧ Position 55 (`mod_4`): 3.76% 
3. Position 13 (`mod_26`) ∧ Position 27 (`mod_4`): 3.67%

- Absolute accuracy remains low (≈ product of the two independent probabilities, e.g., 27% × 13% ≈ 3.5%). 
- Slight uplift above the naive product suggests mild correlation, but not enough to make combinations a primary tactic. 
- Position 27 appears in every top combo, reinforcing its central role.

### 3. Ratio vs. accuracy

- Ratio = `accuracy / expected`. 
- High ratios often stem from tiny expected probabilities rather than better absolute performance. 
- Example: Position 27 with `mod_8` → 27.11% / 12.5% = 2.17×. The same 27.11% divided by the `mod_4` expectation (25%) yields only 1.08×. 
- Conclusion: we prioritize **accuracy**, not ratio.

### 4. Why combos remain limited

- If Position 27 (27%) and Position 41 (13%) were independent, joint probability ≈ 3.51%. 
- Measured combo = 3.92%, i.e., only +0.4 percentage points above independence. 
- Hence, intersections confirm partial independence; no multiplicative gains beyond statistical expectation.

---

## Conclusions

**Working well:**
1. Position 27 with `mod_4` (27.11%) remains the best single deterministic rule. 
2. Positions 13 and 41 under `mod_26` hold ~13.5% accuracy. 
3. Position 55 benefits from `mod_26`/`mod_29`, but absolute accuracy stays ~13%. 
4. Combinations perform slightly above the multiplicative baseline, confirming consistent signal.

**Limitations:**
1. Two-position combos cap out around 4%. 
2. Ratios alone can mislead; absolute accuracy matters more for deployment. 
3. No simple modulo tweak pushes accuracy meaningfully beyond the current plateaus.

---

## Next Steps

**Priority 1 – Explore richer predictors** 
- Seed-based methods (55-position weighting). 
- Multi-position models beyond pairwise intersections. 
- Machine learning (tree ensembles, gradient boosting). 
- Pattern-driven approaches (grid clusters, block-end drift).

**Priority 2 – Deepen Position 27 analysis** 
- Understand why `mod_4` and `mod_8` tie on accuracy. 
- Check whether alternative transformations (e.g., mixed residue classes) can break the 27% ceiling. 
- Plug seed weights + RPC drift for incremental gains.

**Priority 3 – Scan other positions** 
- Identify additional slots with consistent >10% accuracy. 
- Investigate block-end symmetry (13/27/41/55) vs. non block-end positions. 
- Expand to Layer-4 logs to verify whether similar constraints exist there.

**Status:** Analysis complete; accuracy gains from simple modulo tweaks are exhausted. Focus shifts to seed-based predictors and ML models for larger leaps.
