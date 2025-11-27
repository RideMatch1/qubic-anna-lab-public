#!/usr/bin/env python3
"""
Vorbereitung for 23k Seeds Derivation
Erstellt optimierte Pipeline for große Datensätze
"""

import json
import sys
from pathlib import Path
from typing import Dict, List
from datetime import datetime

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

OUTPUT_DIR = project_root / "outputs" / "derived"
MAPPING_FILE = project_root / "outputs" / "analysis" / "complete_mapping_database.json"
REPORTS_DIR = project_root / "outputs" / "reports"

def load_all_seeds() -> List[str]:
 """Load alle Seeds aus Mapping Database."""
 if not MAPPING_FILE.exists():
 raise FileNotFoundError(f"Mapping file not found: {MAPPING_FILE}")
 
 with MAPPING_FILE.open() as f:
 data = json.load(f)
 
 seeds = list(data.get("seed_to_real_id", {}).keys())
 print(f"✅ Loaded {len(seeds)} seeds from mapping database")
 return seeds

def create_derivation_plan(total_seeds: int, batch_size: int = 1000) -> Dict:
 """Erstelle Plan for schrittweise Derivation."""
 batches = []
 for i in range(0, total_seeds, batch_size):
 end = min(i + batch_size, total_seeds)
 batches.append({
 "batch": len(batches) + 1,
 "start": i,
 "end": end,
 "size": end - i
 })
 
 return {
 "total_seeds": total_seeds,
 "batch_size": batch_size,
 "total_batches": len(batches),
 "batches": batches,
 "created": datetime.now().isoformat()
 }

def main():
 """Hauptfunktion."""
 print("=" * 80)
 print("23K SEEDS DERIVATION PREPARATION")
 print("=" * 80)
 print()
 
 # Load Seeds
 seeds = load_all_seeds()
 total = len(seeds)
 
 # Erstelle Plan
 plan = create_derivation_plan(total, batch_size=1000)
 
 print(f"Total Seeds: {total}")
 print(f"Batch Size: {plan['batch_size']}")
 print(f"Total Batches: {plan['total_batches']}")
 print()
 
 # Speichere Plan
 plan_file = OUTPUT_DIR / "23k_derivation_plan.json"
 OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
 
 with plan_file.open("w") as f:
 json.dump(plan, f, indent=2)
 
 print(f"💾 Plan gespeichert: {plan_file}")
 print()
 
 # Erstelle Batch-Script Template
 script_template = f"""#!/usr/bin/env python3
\"\"\"
Batch Derivation Script for 23k Seeds
Verwendet: python3 scripts/core/derive_layer3_extended.py --count <batch_size> --skip-rpc
\"\"\"

import subprocess
import json
from pathlib import Path

project_root = Path(__file__).parent.parent.parent
plan_file = project_root / "outputs" / "derived" / "23k_derivation_plan.json"

with plan_file.open() as f:
 plan = json.load(f)

print("Starting batch derivation...")
print(f"Total batches: {{plan['total_batches']}}")

for batch_info in plan['batches']:
 batch_num = batch_info['batch']
 batch_size = batch_info['size']
 
 print(f"\\nProcessing batch {{batch_num}}/{{plan['total_batches']}} ({{batch_size}} identities)...")
 
 cmd = [
 "python3",
 str(project_root / "scripts" / "core" / "derive_layer3_extended.py"),
 "--count", str(batch_size),
 "--skip-rpc"
 ]
 
 result = subprocess.run(cmd, cwd=project_root)
 
 if result.returncode != 0:
 print(f"❌ Batch {{batch_num}} failed!")
 break
 
 print(f"✅ Batch {{batch_num}} completed")

print("\\n✅ All batches completed!")
"""
 
 script_file = project_root / "scripts" / "core" / "run_23k_derivation.py"
 with script_file.open("w") as f:
 f.write(script_template)
 
 script_file.chmod(0o755)
 print(f"💾 Batch-Script erstellt: {script_file}")
 print()
 
 # Report
 report_lines = [
 "# 23K Seeds Derivation Preparation",
 "",
 f"**Total Seeds**: {total}",
 f"**Batch Size**: {plan['batch_size']}",
 f"**Total Batches**: {plan['total_batches']}",
 "",
 "## Batch Plan",
 ""
 ]
 
 for batch in plan['batches']:
 report_lines.append(f"### Batch {batch['batch']}")
 report_lines.append(f"- Range: {batch['start']}-{batch['end']}")
 report_lines.append(f"- Size: {batch['size']}")
 report_lines.append("")
 
 report_lines.extend([
 "## Usage",
 "",
 "### Schritt 1: Batch Derivation (ohne RPC)",
 "```bash",
 "python3 scripts/core/run_23k_derivation.py",
 "```",
 "",
 "### Schritt 2: Position 30/4 Analysis",
 "```bash",
 "python3 scripts/analysis/position30_full_analysis.py",
 "```",
 "",
 "### Schritt 3: RPC Sample Validation",
 "```bash",
 "python3 scripts/verify/rpc_sample_validation.py --sample-size 500 --strategy unknown --delay 1.5",
 "```",
 "",
 "## Estimated Time",
 f"- Derivation (ohne RPC): ~{plan['total_batches'] * 2} Minuten",
 f"- RPC Validation (500 samples): ~12 Minuten",
 f"- Total: ~{plan['total_batches'] * 2 + 12} Minuten",
 ])
 
 report_file = REPORTS_DIR / "23K_DERIVATION_PREPARATION.md"
 REPORTS_DIR.mkdir(parents=True, exist_ok=True)
 
 with report_file.open("w") as f:
 f.write("\n".join(report_lines) + "\n")
 
 print(f"📝 Report gespeichert: {report_file}")
 print()
 print("✅ Preparation complete!")
 print()
 print("Nächste Schritte:")
 print("1. python3 scripts/core/run_23k_derivation.py")
 print("2. python3 scripts/analysis/position30_full_analysis.py")
 print("3. python3 scripts/verify/rpc_sample_validation.py --sample-size 500")

if __name__ == "__main__":
 main()

