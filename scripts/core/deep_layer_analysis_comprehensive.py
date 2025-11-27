#!/usr/bin/env python3
"""
Deep Layer Analysis - Comprehensive

Analysiert die vollständige Layer-Struktur der Anna Matrix Identities:
- Layer-1 bis Layer-N Progression
- On-chain Rates pro Layer
- Patterns und Beziehungen
- Exit Points und spezielle Layers
"""

import json
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from collections import defaultdict
import subprocess

# Project root
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

OUTPUT_DIR = project_root / "outputs" / "derived"
REPORTS_DIR = project_root / "outputs" / "reports"
VENV_PATH = project_root / "venv-tx"

def derive_identity_from_seed(seed: str) -> Optional[str]:
 """Leite Identity aus Seed ab."""
 python_exe = VENV_PATH / "bin" / "python"
 
 if not python_exe.exists():
 return None
 
 script = f"""
from qubipy.crypto.utils import (
 get_subseed_from_seed,
 get_private_key_from_subseed,
 get_public_key_from_private_key,
 get_identity_from_public_key,
)

seed = "{seed}"
seed_bytes = seed.encode('utf-8')
subseed = get_subseed_from_seed(seed_bytes)
private_key = get_private_key_from_subseed(subseed)
public_key = get_public_key_from_private_key(private_key)
identity = get_identity_from_public_key(public_key)
print(identity)
"""
 
 try:
 result = subprocess.run(
 [str(python_exe), "-c", script],
 capture_output=True,
 text=True,
 timeout=10,
 cwd=project_root
 )
 
 if result.returncode != 0:
 return None
 
 identity = result.stdout.strip()
 if len(identity) == 60 and identity.isupper():
 return identity
 return None
 except Exception:
 return None

def check_identity_onchain(identity: str) -> Dict:
 """Check ob Identity on-chain existiert."""
 python_exe = VENV_PATH / "bin" / "python"
 
 if not python_exe.exists():
 return {"exists": False, "error": "venv not found"}
 
 script = f"""
from qubipy.rpc import rpc_client

rpc = rpc_client.QubiPy_RPC()
try:
 balance = rpc.get_balance("{identity}")
 if balance is not None:
 print("EXISTS")
 else:
 print("NOT_FOUND")
except Exception as e:
 print(f"ERROR: {{e}}")
"""
 
 try:
 result = subprocess.run(
 [str(python_exe), "-c", script],
 capture_output=True,
 text=True,
 timeout=10,
 cwd=project_root
 )
 
 if "EXISTS" in result.stdout:
 return {"exists": True}
 return {"exists": False}
 except Exception:
 return {"exists": False, "error": "RPC error"}

def load_complete_mapping_database() -> Dict:
 """Load die komplette Mapping-Datenbank."""
 db_file = project_root / "outputs" / "analysis" / "complete_mapping_database.json"
 
 if not db_file.exists():
 print(f"⚠️ Database file not found: {db_file}")
 return {}
 
 print(f"📂 Loading complete mapping database...")
 with db_file.open() as f:
 data = json.load(f)
 
 print(f"✅ Loaded database with {len(data.get('seed_to_real_id', {}))} entries")
 return data

def analyze_layer_progression_for_identity(seed: str, max_layers: int = 10) -> Dict:
 """Analyze Layer-Progression for einen Seed."""
 progression = {
 "seed": seed,
 "layers": [],
 "max_layer": 0,
 "onchain_layers": []
 }
 
 current_seed = seed
 
 for layer in range(1, max_layers + 1):
 identity = derive_identity_from_seed(current_seed)
 
 if not identity:
 break
 
 onchain = check_identity_onchain(identity)
 
 layer_data = {
 "layer": layer,
 "seed": current_seed,
 "identity": identity,
 "onchain": onchain.get("exists", False)
 }
 
 progression["layers"].append(layer_data)
 progression["max_layer"] = layer
 
 if onchain.get("exists"):
 progression["onchain_layers"].append(layer)
 
 # Für nächste Layer: Verwende identity.lower()[:55] als Seed
 if layer < max_layers:
 next_seed = identity.lower()[:55]
 current_seed = next_seed
 
 return progression

def analyze_all_layers_comprehensive():
 """Umfassende Layer-Analyse."""
 
 print("=" * 80)
 print("DEEP LAYER ANALYSIS - COMPREHENSIVE")
 print("=" * 80)
 print()
 
 # Load Mapping-Datenbank
 db = load_complete_mapping_database()
 
 if not db:
 print("❌ Could not load database. Using sample data...")
 # Fallback: Verwende bekannte Seeds
 known_seeds = [
 "aqiosqqmacybpqxqsjniuaylmxxiwqoxqmeqyxbbtbonsjjrcwpxxdd",
 "gwuxommmmfmtbwfzsngmukwbiltxqdknmmmnypeftamronjmablhtrr",
 "acgjgqqyilbpxdrborfgwfzbbbnlqnghddelvlxxxlbnnnfbllpbnnn",
 "giuvfgawcbbffkvbmfjeslhbbfbfwzwnnxcbqbbjrvfbnvjltjbbbht",
 ]
 
 seed_to_real_id = {}
 for seed in known_seeds:
 identity = derive_identity_from_seed(seed)
 if identity:
 seed_to_real_id[seed] = identity
 else:
 seed_to_real_id = db.get("seed_to_real_id", {})
 
 print(f"📊 Analyzing {len(seed_to_real_id)} seeds...")
 print()
 
 # Analyze Layer-Progression for Sample
 sample_size = min(100, len(seed_to_real_id))
 sample_seeds = list(seed_to_real_id.keys())[:sample_size]
 
 print(f"🔍 Analyzing Layer Progression for {sample_size} seeds...")
 print()
 
 all_progressions = []
 layer_stats = defaultdict(lambda: {
 "total": 0,
 "onchain": 0,
 "derivable": 0
 })
 
 for i, seed in enumerate(sample_seeds, 1):
 if i % 10 == 0:
 print(f" Progress: {i}/{sample_size} ({(i/sample_size*100):.1f}%)")
 
 progression = analyze_layer_progression_for_identity(seed, max_layers=8)
 all_progressions.append(progression)
 
 # Update Statistics
 for layer_data in progression["layers"]:
 layer = layer_data["layer"]
 layer_stats[layer]["total"] += 1
 layer_stats[layer]["derivable"] += 1
 if layer_data["onchain"]:
 layer_stats[layer]["onchain"] += 1
 
 print()
 print("=" * 80)
 print("LAYER STATISTICS")
 print("=" * 80)
 print()
 
 for layer in sorted(layer_stats.keys()):
 stats = layer_stats[layer]
 derivable_pct = (stats["derivable"] / stats["total"] * 100) if stats["total"] > 0 else 0
 onchain_pct = (stats["onchain"] / stats["derivable"] * 100) if stats["derivable"] > 0 else 0
 
 print(f"Layer {layer}:")
 print(f" Total: {stats['total']}")
 print(f" Derivable: {stats['derivable']} ({derivable_pct:.1f}%)")
 print(f" On-chain: {stats['onchain']} ({onchain_pct:.1f}% of derivable)")
 print()
 
 # Analyze Patterns
 print("=" * 80)
 print("PATTERN ANALYSIS")
 print("=" * 80)
 print()
 
 max_layer_distribution = defaultdict(int)
 for prog in all_progressions:
 max_layer_distribution[prog["max_layer"]] += 1
 
 print("Max Layer Distribution:")
 for layer in sorted(max_layer_distribution.keys()):
 count = max_layer_distribution[layer]
 pct = (count / len(all_progressions) * 100) if all_progressions else 0
 print(f" Layer {layer}: {count} seeds ({pct:.1f}%)")
 print()
 
 # On-chain Rate per Layer
 print("On-chain Rate per Layer:")
 for layer in sorted(layer_stats.keys()):
 stats = layer_stats[layer]
 if stats["derivable"] > 0:
 onchain_rate = (stats["onchain"] / stats["derivable"] * 100)
 print(f" Layer {layer}: {onchain_rate:.1f}%")
 print()
 
 # Speichere Ergebnisse
 results = {
 "summary": {
 "total_seeds_analyzed": len(all_progressions),
 "layer_statistics": dict(layer_stats),
 "max_layer_distribution": dict(max_layer_distribution)
 },
 "progressions": all_progressions[:20] # Nur erste 20 for JSON
 }
 
 OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
 output_json = OUTPUT_DIR / "deep_layer_analysis_comprehensive.json"
 with output_json.open("w") as f:
 json.dump(results, f, indent=2)
 
 # Erstelle Markdown Report
 output_md = REPORTS_DIR / "deep_layer_analysis_comprehensive_report.md"
 REPORTS_DIR.mkdir(parents=True, exist_ok=True)
 
 with output_md.open("w") as f:
 f.write("# Deep Layer Analysis - Comprehensive Report\n\n")
 f.write("## Summary\n\n")
 f.write(f"- **Total Seeds Analyzed**: {len(all_progressions)}\n")
 f.write(f"- **Max Layer Reached**: {max(layer_stats.keys()) if layer_stats else 0}\n\n")
 
 f.write("## Layer Statistics\n\n")
 f.write("| Layer | Total | Derivable | On-chain | Derivable % | On-chain % |\n")
 f.write("|-------|-------|-----------|----------|-------------|-------------|\n")
 
 for layer in sorted(layer_stats.keys()):
 stats = layer_stats[layer]
 derivable_pct = (stats["derivable"] / stats["total"] * 100) if stats["total"] > 0 else 0
 onchain_pct = (stats["onchain"] / stats["derivable"] * 100) if stats["derivable"] > 0 else 0
 f.write(f"| {layer} | {stats['total']} | {stats['derivable']} | {stats['onchain']} | {derivable_pct:.1f}% | {onchain_pct:.1f}% |\n")
 
 f.write("\n## Max Layer Distribution\n\n")
 for layer in sorted(max_layer_distribution.keys()):
 count = max_layer_distribution[layer]
 pct = (count / len(all_progressions) * 100) if all_progressions else 0
 f.write(f"- **Layer {layer}**: {count} seeds ({pct:.1f}%)\n")
 
 f.write("\n## Sample Progressions\n\n")
 f.write("First 10 seed progressions:\n\n")
 for i, prog in enumerate(all_progressions[:10], 1):
 f.write(f"### Seed {i}: {prog['seed'][:30]}...\n\n")
 f.write(f"- **Max Layer**: {prog['max_layer']}\n")
 f.write(f"- **On-chain Layers**: {prog['onchain_layers']}\n\n")
 f.write("| Layer | Identity | On-chain |\n")
 f.write("|-------|----------|----------|\n")
 for layer_data in prog["layers"]:
 onchain_mark = "✅" if layer_data["onchain"] else "❌"
 f.write(f"| {layer_data['layer']} | {layer_data['identity']} | {onchain_mark} |\n")
 f.write("\n")
 
 print(f"💾 Results saved to: {output_json}")
 print(f"📄 Report saved to: {output_md}")
 print()
 
 return results

if __name__ == "__main__":
 analyze_all_layers_comprehensive()

