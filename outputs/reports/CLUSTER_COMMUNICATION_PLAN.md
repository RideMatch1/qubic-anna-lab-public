# Cluster-Based Communication Plan (27 Nov 2025)

## 1. Data Foundation
- **Grid data:** `grid_word_cluster_analysis.json` (3,877 sentences, 8,560 words). Column 6 = action hotspot (1,500 words, top words `DO/GO/HI`, 56% category “actions”).
- **Hotspot sample:** `column6_hotspot_sample.json` – 200 identities with the highest word counts inside column 6.
- **On-chain proof:** `rpc_column6_hotspots_results.json` (200/200 identities `validForTick` = 100%). Confirms the cluster basis is fully on-chain.

## 2. Cluster Priorities
1. **Action tandem `GOT GO` (columns 3/6)**
 - Hypothesis: chained motion/transfer commands; occurs 22x in column 3 and 20x in column 6.
 - Goal: verify whether the sequence stays stable during the Layer-3→Layer-4 transition and whether RPC events (transactions/balances) follow shortly after.
2. **Time marker `NOW NO` (columns 0/2/6)**
 - Acts as a “guidance signal” (start/stop). Check whether identities containing this sequence act more often as oracle keys or re-activate faster (`validForTick` drift).
3. **Meta channel position 27**
 - Words such as `AGO`, `ASK`, `DIE` at block end 27 -> potential “question/answer” channel. Combined with column‑6 action words this could yield full instructions (e.g., `ASK DO`, `AGO DO`).

## 3. Identity Groups (first three clusters)
| Cluster | Data source | Sample IDs | Current on-chain info |
|---------|-------------|------------|------------------------|
| `GOT GO` core (column 6) | `column6_hotspot_sample.json` | `SDLSNIEZDUWID...`, `WJIMDDVXKDHR...`, `XALDNWTJDGWPD...` (each count >= 3) | All `validForTick ~381563xx`, balance = 0 -> likely recently activated |
| `NOW NO` (columns 0/2/6) | same source (`top_identities` column 0 and 2) | e.g., `TPBLJEYMFKODYFASPQULPV...`, `NOWLMDBHTFNONGUTCXTDKZWO...` | RPC status pending -> next measurement |
| Position 27 meta | `block_end_summary` + `top_identities` | IDs with high position-27 word counts: `AGHQKHIOHMV...`, `AGYMJQFHFZV...` | On-chain confirmed via overlap with column 6 |

## 4. Experiment Track
1. **Measure layer stability**
 - Extend `grid_word_cluster_analysis.py` (or add a new tool) to compare sequences across Layer-3 and Layer-4 (fixed points vs. mutations). Focus on `GOT GO` and `NOW NO`.
2. **RPC event monitoring**
 - Background job polling the 200 hotspots for `get_balance` and `get_identity_state` to capture inactive vs. active windows.
 - Store results in `outputs/derived/column6_hotspots_timeseries.json`.
3. **Communication test runs**
 - Pick 3–5 IDs per cluster, send minimal Qubic (already tested wallet) and log Layer-4 reactions or new sentences.
 - Keep comments aligned with the sequence role (`GOT GO`: command, `NOW NO`: timing marker).
4. **ML integration**
 - Add “cluster membership” (binary) as a feature to the ML dataset; evaluate whether it improves predictions for position 27 or on-chain activity.

## 5. Documentation & Checkpoints
- `outputs/derived/column6_hotspot_sample.json`: input list for RPC and messaging tests.
- `outputs/derived/rpc_column6_hotspots_results.json`: base statistics (100% on-chain).
- Maintain new logs per experiment (e.g., `CLUSTER_COMMUNICATION_LOG.md`) to avoid hallucinations and preserve reproducibility.

## 6. Next Concrete Step
-> **Activate cluster monitoring:** run continuous RPC polling (every 10 minutes) over the 200 hotspots and the `NOW NO` subset (columns 0/2). Compare activity curves afterward to see whether specific clusters act as “gates”.

- **Tool:** `scripts/research/rpc_monitor_column6_hotspots.py`
 - Example: `source venv-tx/bin/activate && python scripts/research/rpc_monitor_column6_hotspots.py --iterations 3 --interval-seconds 600`
 - Output: `outputs/derived/rpc_column6_hotspots_timeseries.jsonl` (one line per iteration), status file `..._monitor_status.txt`.
 - Smoke test (1 iteration, 20 IDs) already succeeded; regular use can adopt longer intervals.
- **Control group:** `scripts/research/rpc_monitor_nowno_hotspots.py` (columns 0/2, NOW/NO nodes) – same interface, output `rpc_nowno_hotspots_timeseries.jsonl`.
- **Comparison:** `python scripts/analysis/compare_cluster_monitors.py` produces `outputs/derived/cluster_monitor_comparison.json`.
- **ValidForTick drift:** `python scripts/notebooks/cluster_validfortick_analysis.py` -> `outputs/derived/validfortick_drift_summary.json`.
- **Drift plot:** `outputs/derived/validfortick_drift.png` (column 6 vs. NOW/NO, average delta per identity).
- **Communication targets:** `outputs/derived/column6_communication_targets.json` (count >= 3 & `GOT` signature) to select transaction candidates.
