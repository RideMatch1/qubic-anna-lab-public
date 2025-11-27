# Repository Organization

## File Organization

This repository has been organized for clarity:

### Root Level (Main Documentation)

- `README.md` - Main documentation and research timeline
- `PROOF_OF_WORK.md` - Complete proof pipeline
- `FOUND_IDENTITIES.md` - Initial 8 identities
- `100_SEEDS_AND_IDENTITIES.md` - Sample of 100 seeds with real IDs
- `100_seeds_and_identities.json` - Machine-readable format
- `RESEARCH_OVERVIEW.md` - Current research status
- `IDENTITY_DISCREPANCY_ANALYSIS.md` - Detailed discrepancy analysis
- `MAPPING_DATABASE_SUMMARY.md` - Summary of 23,765 seeds
- `ALL_23765_SEEDS_SUMMARY.md` - Complete seeds database summary
- `COMPLETE_DATA_INDEX.md` - Index to all data files
- `COMPREHENSIVE_SCAN_RESULTS.md` - Comprehensive scan results
- `METHODS_TESTED.md` - All methods tested
- `METHOD_SELECTION_RATIONALE.md` - Method selection rationale
- `RESEARCH_UPDATE_2025_11_22.md` - Research update summary

### Data Files

- `outputs/reports/` - Analysis reports (created by verification scripts)
- `outputs/derived/` - Derived data and analysis reports
- `outputs/plots/` - Visualization plots (created if matplotlib installed)

**Note**: The complete mapping database (`complete_mapping_database.json`, ~50MB) is not included in this repository due to size. See `MAPPING_DATABASE_SUMMARY.md` and `ALL_23765_SEEDS_SUMMARY.md` for summaries.

### Internal Documentation

- `docs/internal/` - Internal documentation and audit reports

### Scripts and Tools

- `analysis/` - Extraction and exploration scripts
- `scripts/` - Core logic, verification, and utilities
- `data/anna-matrix/` - Source Excel file

## Quick Access

- **Start here**: `README.md`
- **Sample data**: `100_SEEDS_AND_IDENTITIES.md`
- **Complete database summaries**: `MAPPING_DATABASE_SUMMARY.md` and `ALL_23765_SEEDS_SUMMARY.md`
- **Verification**: `./run_all_verifications.sh`
