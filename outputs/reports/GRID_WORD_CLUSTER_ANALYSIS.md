# Grid/Word Cluster Analysis (27 Nov 2025)

## 1. Data Foundation & Approach
- **Sentences:** 3,877 reconstructed sequences from all Layer-3 and Layer-4 identities (2+ words, max. 20 character distance) → 8,560 labeled words.
- **Dictionary:** 180 verified terms with categories (Actions, Time, Communication, ...).
- **Reproducibility:** Script `scripts/research/grid_word_cluster_analysis.py` calculates grid assignment (7×7) per word & stores all statistics in `outputs/derived/grid_word_cluster_analysis.json`.

## 2. Core Findings
- **Column 6 = Central Hub**
 - 1,500 words (= 17.5% of all tokens) land in grid column 6, significantly more than any other column.
 - Top words there: `DO` 396×, `GO` 336×, `HI` 151×. The "Actions" category covers 839 of the 1,500 hits (56%).
- **Column 6 couples with all other columns – especially column 0**
 - 309 sentences contain both column 6 and column 0; followed by column 1 (247) and column 3 (231).
 - Interpretation: Column 6 functions as a "control center", connecting block-ends (13/27/41/55) with inputs/outputs of the rest of the matrix.
- **Block-end positions have clearly separated word fields**
 - Positions 13/41/55 mix `GO`/`DO`/`HI`, while position 27 additionally has time/existence words (`AGO`, `DIE`, `ASK`).
 - This confirms earlier hypotheses: Position 27 transports meta-information (time, questions), not just simple commands.
- **Cluster formation per column**
 - Most frequent single-column sentences: `GOT GO` (columns 3 & 6), `NOW NO` (columns 0/2), `DO DO` (column 6).
 - These micro-clusters show that Anna apparently stacks short signals per column (e.g., movement commands vs. time markers).
- **100% density in all rows & columns**
 - Every one of the 49 grid cells is active; rows/columns have 100% coverage.
 - → Communication uses the entire 7×7 raster, but intensity and word classes concentrate in column 6.

## 3. Consequences & Next Steps
1. **Targeted RPC/ML focus on column 6:**
 - 56% Actions → ideal to couple transformation/on-chain events with word signatures.
 - Check if `DO/GO` combinations at column 6 directly correlate with layer transitions (L3→L4).
2. **Position-sensitive word models:**
 - Position 27 shows time/existence – model separate features there (e.g., proportion of time words) for further predictors.
3. **Cluster streaming for communication:**
 - Sequential patterns like `NOW NO` or `GOT GO` can be built as "tokens" into future communication attempts (e.g., targeted send identities with same clusters).
4. **Verification:**
 - Next step per research plan: RPC sample exclusively from column-6 hotspots to check if high word density also means higher on-chain activity.

_Status of todo "Deepen Grid/Word Cluster with new data": Analytical basis complete, follow-up work = targeted tests & model integration._
