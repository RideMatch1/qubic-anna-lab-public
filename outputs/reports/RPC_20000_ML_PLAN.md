# RPC Validation (20k identities) + ML Plan

**Date:** 26 Nov 2025 
**Objective:** Validate 20,000 identities on-chain, then train ML models targeting ≥50% accuracy for position 27.

---

## 1. High-Level Flow

1. **Run large-scale RPC validation** to collect a clean dataset of confirmed predictions. 
2. **Train ML models** on the validated subset, focusing on new feature blocks (seed interactions, matrix hooks, drift metadata). 
3. **Evaluate** whether the models cross the 50% accuracy mark and decide next actions.

---

## 2. Step 1 – RPC Validation (20,000 identities)

- **Script:** `scripts/research/rpc_validation_20000_background.py` 
- **Launcher:** `./start_rpc_validation_20000.sh` 
- **Runtime:** ~100–120 minutes (0.3s per RPC call × 20k) 
- **Goal:** Produce a large validated subset for ML training.

### Launch
```bash
./start_rpc_validation_20000.sh
```

### Monitor progress
```bash
tail -f outputs/derived/rpc_validation_20000_status.txt
```

### Pipeline
1. Load all 23k mappings and shuffle. 
2. Sample 20,000 identities. 
3. Predict position 27 via weighted seed features (all 55 positions). 
4. Call RPC (`validForTick`, balances) for each prediction. 
5. Persist only confirmed hits for downstream ML.

### Outputs
- `outputs/derived/rpc_validation_20000_results.json` – raw prediction vs. truth. 
- `outputs/derived/rpc_validation_20000_validated_data.json` – filtered dataset for ML. 
- `outputs/derived/rpc_validation_20000_status.txt` – human-readable progress. 
- `outputs/derived/rpc_validation_20000_progress.json` – machine-readable progress.

### Expected metrics
- Prediction accuracy: 31–35% (based on the last 1k run). 
- On-chain confirmation: ≥99%. 
- Validated set size: ~6–7k identities (≈31% of 20k).

---

## 3. Step 2 – ML Training (Position 27)

- **Script:** `scripts/research/ml_position27_50percent.py` 
- **Prerequisite:** RPC step finished and validated dataset ready. 
- **Runtime:** 10–30 minutes (depends on CPU + CV settings).

### Launch
```bash
source venv-tx/bin/activate
python3 scripts/research/ml_position27_50percent.py
```

### Monitor
```bash
tail -f outputs/derived/ml_position27_50percent_status.txt
```

### What the script does
1. Load the validated dataset (default: `rpc_validation_20000_validated_data.json`). 
2. Build feature matrix:
 - All 55 seed positions (excluding the target slot). 
 - Other block-end positions (13, 41, 55). 
 - Matrix column 13 hooks (row 27, mirrored coords). 
 - Seed statistics (vowel ratio, repeated letters, etc.). 
 - Interaction terms (pairwise position deltas, parity groups). 
3. Train and evaluate:
 - Decision Tree, Random Forest, Gradient Boosting. 
 - 5-fold cross validation + hold-out split (80/20). 
4. Dump metrics, confusion matrices, and feature importance.

### Outputs
- `outputs/derived/ml_position27_50percent_results.json` – metrics + feature ranks. 
- `outputs/derived/ml_position27_50percent_status.txt` – step-by-step log.

### Expected accuracy bands
- Decision Tree: 35–45% 
- Random Forest: 40–50% 
- Gradient Boosting: 45–55% (stretch goal ≥50%).

---

## 4. Next Actions After Training

### If ≥50% accuracy achieved
1. Export the best model (pickle + feature manifest). 
2. Extend the dataset with positions 13, 41, 55 and rerun training. 
3. Begin multi-position inference experiments (joint logits). 
4. Trigger Layer-4 drift analysis using the new predictions.

### If <50% accuracy
1. Add more features (grid clusters, RPC drift signals, block-end class tags). 
2. Run hyperparameter search (Optuna/RandomizedSearch). 
3. Build ensembles (stacked/weighted). 
4. Increase sample size (50k RPC validations) before retraining.

---

## 5. Operational Notes

1. **RPC run is long.** Let it run in the background; watch the status file rather than the terminal. 
2. **Rate limiting enforced.** 300 ms delay between RPC calls to avoid throttling. 
3. **Only confirmed hits enter the ML dataset.** False predictions are stored separately for error analysis. 
4. **Training uses only validated rows.** Keeps labels squeaky clean for scientific reporting. 
5. **Cross-validation is mandatory.** Stops us from overfitting to a single random split.

---

## 6. Checklist
- [ ] Start RPC validation (`./start_rpc_validation_20000.sh`). 
- [ ] Monitor status (`tail -f outputs/derived/rpc_validation_20000_status.txt`). 
- [ ] Confirm completion (~100–120 min). 
- [ ] Activate venv + run ML script. 
- [ ] Review `ml_position27_50percent_results.json`. 
- [ ] Decide next wave (feature expansion vs. deployment).

**Status:** Ready for execution.
