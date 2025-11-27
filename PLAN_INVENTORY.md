# Repository Inventory (2025‑11‑27)

Fresh clone inspected to understand existing public footprint. Status legend:

- **KEEP** – structure/content can stay as-is.
- **UPGRADE** – needs refreshed data, sanitization or rewritten narrative.
- **LEGACY** – consider replacing or archiving after confirmation.

| Path / File | Status | Notes |
|-----------------------------------------------|----------|-------|
| `README.md` | UPGRADE | Already detailed but German fragments, needs refreshed overview + curated links. |
| `RESEARCH_UPDATE_2025_11_22.md` | UPGRADE | Good baseline; rewrite into concise English + reference new work. |
| `PROOF_OF_WORK.md`, `VALIDATION_REPORT.md` | KEEP/UPGRADE | Keep structure, update stats + wording. |
| `100_SEEDS_AND_IDENTITIES.*` | KEEP | Serves as sample dataset; ensure sanitized references only. |
| `analysis/` scripts (21‑32, 70‑72, utils) | LEGACY | Many refer to older workflow; decide which ones remain relevant. |
| `data/anna-matrix/Anna_Matrix.xlsx` | KEEP | Core source; add README describing provenance. |
| `docs/internal/` | UPGRADE | Contains signed proof; ensure anonymized voice + context. |
| `external_verifications/` | KEEP | Encourage contributions; maybe add template. |
| `outputs/derived/*.md/json` | UPGRADE | Excellent analyses but German-heavy; need concise English versions + sanitized stats. |
| `outputs/derived/complete_24846_*.json` | KEEP | Core dataset; confirm formatting + mention verification steps. |
| `outputs/reports/*.md` | UPGRADE | Convert to English, remove redundant detail, keep math/figures. |
| `scripts/core`, `scripts/utils`, `scripts/verify` | KEEP/UPGRADE | Retain structure, modernize comments + instructions. |
| `run_all_verifications.sh`, `Dockerfile.qubipy`, `requirements.txt` | KEEP | Document usage in README. |
| `.github/` (workflows) | KEEP | Minimal; expand later if needed. |

Private backup of previous local fork stored at `../qubic-anna-lab-public_backup_<timestamp>/` for reference.

Next steps: sanitize existing docs, merge new research outputs (super-scan, RPC, signature lookup) and maintain this inventory as files transition from “UPGRADE” to “KEEP”.
