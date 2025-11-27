# ML Analysis of Block-End Positions (13/41/55)

## 1. Setup
- **Dataset:** `rpc_validation_20000_validated_data.json` (4,015 Layer-3 identities, identical to Position 27 run)
- **Features:** 91/92 per sample (all seed positions except target, block-end values, matrix, seed statistics, seed interactions)
- **Model:** Gradient Boosting (`n_estimators=100`, `max_depth=5`, `learning_rate=0.08`, `cv=3`)
- **Script:** `scripts/research/ml_block_end_positions.py`
- **Raw Data:** `outputs/derived/ml_block_end_positions_results.json`

## 2. Results
| Position | Classes | Test Acc | CV Mean ± Std | Comment |
|----------|---------|----------|---------------|---------|
| 13 | 8 | 12.58% | 13.50% ± 0.73% | ~Random (1/8 ≈ 12.5%) |
| 41 | 8 | 14.82% | 14.37% ± 1.08% | Only slightly better than random |
| 55 | 8 | 11.58% | 12.93% ± 0.56% | Slightly below random |

## 3. Feature Insights
- Top features are evenly distributed across various seed positions; seed interactions provide no clear peaks.
- Matrix and block features rarely appear in top lists → no clear mapping like position 27.
- All classes show approximately equal precision/recall (~0.1–0.18) → model cannot extract dominant patterns.

## 4. Interpretation
1. **Position 27 remains unique:** The 67% accuracy of the Position 27 model results from structural signals (seed min/std + specific seeds 12/17/24/32/35/37/45/51). For positions 13/41/55, these strong dependencies are missing.
2. **No hidden transformations:** Neither base-26/matrix combinations nor seed interactions explain the remaining block-end characters – aligns with the hypothesis that only position 27 (matrix column 13, mod4) has a special transformation.
3. **Next steps:** For positions 13/41/55, only a purely deterministic comparison with matrix column 13 is worthwhile (as in `BLOCK_END_TRANSFORMATION_ANALYSIS.md`). ML provides no added value, therefore focus on:
 - Completion of B/D RPC validation → complete class basis for position 27.
 - Extended feature engineering only if new transformations are discovered (e.g., block-specific seeds).

*Status: 27 Nov 2025, created after completion of script `ml_block_end_positions.py`.*
