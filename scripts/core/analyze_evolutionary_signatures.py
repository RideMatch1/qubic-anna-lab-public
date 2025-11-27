#!/usr/bin/env python3
"""
Analyze Identity Patterns auf evolutionäre Signaturen.

Evolutionäre Signaturen:
- Selection pressure indicators
- Fitness function traces
- Mutation patterns
- Convergence indicators
"""

import json
from pathlib import Path
from typing import List, Dict
from collections import Counter, defaultdict
import statistics

import sys
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from scripts.core.identity_constants import SEED_LENGTH

OUTPUT_DIR = Path("outputs/derived")
REPORTS_DIR = Path("outputs/reports")

def load_seeds() -> List[str]:
 """Load alle Seeds aus on-chain validation."""
 
 seeds = []
 
 # Load aus complete file
 complete_file = OUTPUT_DIR / "checksum_identities_onchain_validation_complete.json"
 if complete_file.exists():
 with complete_file.open() as f:
 data = json.load(f)
 
 # Load Batches
 total_batches = data.get("total_batches", 0)
 for i in range(total_batches):
 batch_file = OUTPUT_DIR / f"onchain_identities_batch_{i}.json"
 if batch_file.exists():
 with batch_file.open() as f:
 batch_data = json.load(f)
 if isinstance(batch_data, list):
 for item in batch_data:
 if isinstance(item, str):
 # Item ist Identity, konvertiere zu Seed
 seed = item.lower()[:SEED_LENGTH]
 if len(seed) == SEED_LENGTH:
 seeds.append(seed)
 elif isinstance(item, dict):
 identity = item.get("identity", "")
 if identity:
 seed = identity.lower()[:SEED_LENGTH]
 if len(seed) == SEED_LENGTH:
 seeds.append(seed)
 
 return seeds

def analyze_selection_pressure(seeds: List[str]) -> Dict:
 """Analyze Selection Pressure Indicators."""
 
 # Charakter-Verteilung
 char_distribution = Counter()
 for seed in seeds:
 char_distribution.update(seed)
 
 # Entropie (niedrige Entropie = hohe Selection Pressure)
 import math
 total_chars = sum(char_distribution.values())
 entropy = 0
 for count in char_distribution.values():
 prob = count / total_chars
 if prob > 0:
 entropy -= prob * math.log2(prob)
 
 # Diversity (Anzahl unique Seeds)
 unique_seeds = len(set(seeds))
 diversity_ratio = unique_seeds / len(seeds) if seeds else 0
 
 return {
 "char_distribution": dict(char_distribution.most_common(26)),
 "entropy": entropy,
 "diversity_ratio": diversity_ratio,
 "unique_seeds": unique_seeds,
 "total_seeds": len(seeds),
 }

def analyze_fitness_traces(seeds: List[str]) -> Dict:
 """Analyze Fitness Function Traces."""
 
 # Wiederholende Patterns (könnten Fitness-Indikatoren sein)
 pattern_lengths = [2, 3, 4, 5]
 pattern_counts = defaultdict(int)
 
 for seed in seeds:
 for length in pattern_lengths:
 for i in range(len(seed) - length + 1):
 pattern = seed[i:i+length]
 if len(set(pattern)) == 1: # Repeating pattern
 pattern_counts[pattern] += 1
 
 # Häufigste Patterns
 top_patterns = dict(Counter(pattern_counts).most_common(20))
 
 # Sequential patterns (könnten Mutation-Indikatoren sein)
 sequential_patterns = []
 for seed in seeds[:1000]: # Sample
 for i in range(len(seed) - 2):
 chars = [ord(c) for c in seed[i:i+3]]
 if chars[1] == chars[0] + 1 and chars[2] == chars[1] + 1:
 sequential_patterns.append(seed[i:i+3])
 elif chars[1] == chars[0] - 1 and chars[2] == chars[1] - 1:
 sequential_patterns.append(seed[i:i+3])
 
 return {
 "repeating_patterns": top_patterns,
 "sequential_patterns": dict(Counter(sequential_patterns).most_common(20)),
 "total_repeating_patterns": sum(pattern_counts.values()),
 }

def analyze_mutation_patterns(seeds: List[str]) -> Dict:
 """Analyze Mutation Patterns."""
 
 # Charakter-Änderungen zwischen ähnlichen Seeds
 mutations = defaultdict(int)
 
 # Vergleiche Seeds paarweise (Sample)
 sample_size = min(1000, len(seeds))
 for i in range(sample_size):
 for j in range(i + 1, min(i + 10, sample_size)):
 seed1 = seeds[i]
 seed2 = seeds[j]
 
 # Zähle Unterschiede
 differences = sum(1 for c1, c2 in zip(seed1, seed2) if c1 != c2)
 if differences < 10: # Ähnliche Seeds
 # Finde Mutation-Positionen
 for pos, (c1, c2) in enumerate(zip(seed1, seed2)):
 if c1 != c2:
 mutations[f"{c1}->{c2}"] += 1
 
 return {
 "mutation_counts": dict(Counter(mutations).most_common(50)),
 "total_mutations_analyzed": sum(mutations.values()),
 }

def analyze_convergence(seeds: List[str]) -> Dict:
 """Analyze Convergence Indicators."""
 
 # Cluster-Analyse (einfach: nach ersten N Zeichen)
 clusters = defaultdict(list)
 
 for seed in seeds:
 # Cluster nach ersten 10 Zeichen
 cluster_key = seed[:10]
 clusters[cluster_key].append(seed)
 
 # Cluster-Größen
 cluster_sizes = [len(cluster) for cluster in clusters.values()]
 
 return {
 "total_clusters": len(clusters),
 "avg_cluster_size": statistics.mean(cluster_sizes) if cluster_sizes else 0,
 "max_cluster_size": max(cluster_sizes) if cluster_sizes else 0,
 "convergence_ratio": max(cluster_sizes) / len(seeds) if seeds and cluster_sizes else 0,
 }

def main():
 """Hauptfunktion."""
 
 print("=" * 80)
 print("ANALYZE EVOLUTIONARY SIGNATURES IN IDENTITIES")
 print("=" * 80)
 print()
 
 print("Loading seeds...")
 seeds = load_seeds()
 print(f"✅ Loaded {len(seeds):,} seeds")
 print()
 
 if not seeds:
 print("⚠️ No seeds found. Check on-chain validation data.")
 return
 
 print("Analyzing selection pressure...")
 selection = analyze_selection_pressure(seeds)
 print(f"✅ Entropy: {selection['entropy']:.2f}")
 print(f"✅ Diversity ratio: {selection['diversity_ratio']:.4f}")
 print()
 
 print("Analyzing fitness traces...")
 fitness = analyze_fitness_traces(seeds)
 print(f"✅ Found {fitness['total_repeating_patterns']} repeating patterns")
 print()
 
 print("Analyzing mutation patterns...")
 mutations = analyze_mutation_patterns(seeds)
 print(f"✅ Analyzed {mutations['total_mutations_analyzed']} mutations")
 print()
 
 print("Analyzing convergence...")
 convergence = analyze_convergence(seeds)
 print(f"✅ Found {convergence['total_clusters']} clusters")
 print(f"✅ Max cluster size: {convergence['max_cluster_size']}")
 print()
 
 # Speichere Ergebnisse
 OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
 json_file = OUTPUT_DIR / "evolutionary_signatures_analysis.json"
 with json_file.open("w") as f:
 json.dump({
 "selection_pressure": selection,
 "fitness_traces": fitness,
 "mutation_patterns": mutations,
 "convergence": convergence,
 }, f, indent=2)
 
 print(f"💾 Results saved to: {json_file}")
 
 # Erstelle Report
 REPORTS_DIR.mkdir(parents=True, exist_ok=True)
 report_file = REPORTS_DIR / "evolutionary_signatures_analysis_report.md"
 
 with report_file.open("w") as f:
 f.write("# Evolutionary Signatures Analysis Report\n\n")
 f.write("## Overview\n\n")
 f.write("This report analyzes identity patterns for evolutionary signatures.\n\n")
 
 f.write("## Selection Pressure\n\n")
 f.write(f"- **Entropy**: {selection['entropy']:.2f} (lower = higher selection pressure)\n")
 f.write(f"- **Diversity ratio**: {selection['diversity_ratio']:.4f}\n")
 f.write(f"- **Unique seeds**: {selection['unique_seeds']:,} / {selection['total_seeds']:,}\n\n")
 
 f.write("### Top Character Distribution\n\n")
 for char, count in list(selection['char_distribution'].items())[:10]:
 f.write(f"- **{char}**: {count:,} occurrences\n")
 f.write("\n")
 
 f.write("## Fitness Traces\n\n")
 f.write(f"- **Total repeating patterns**: {fitness['total_repeating_patterns']:,}\n\n")
 f.write("### Top Repeating Patterns\n\n")
 for pattern, count in list(fitness['repeating_patterns'].items())[:10]:
 f.write(f"- **{pattern}**: {count} occurrences\n")
 f.write("\n")
 
 f.write("## Mutation Patterns\n\n")
 f.write(f"- **Total mutations analyzed**: {mutations['total_mutations_analyzed']:,}\n\n")
 f.write("### Top Mutations\n\n")
 for mutation, count in list(mutations['mutation_counts'].items())[:10]:
 f.write(f"- **{mutation}**: {count} occurrences\n")
 f.write("\n")
 
 f.write("## Convergence\n\n")
 f.write(f"- **Total clusters**: {convergence['total_clusters']}\n")
 f.write(f"- **Average cluster size**: {convergence['avg_cluster_size']:.2f}\n")
 f.write(f"- **Max cluster size**: {convergence['max_cluster_size']}\n")
 f.write(f"- **Convergence ratio**: {convergence['convergence_ratio']:.4f}\n\n")
 
 f.write("## Interpretation\n\n")
 f.write("If evolutionary signatures are present:\n")
 f.write("- Low entropy suggests strong selection pressure\n")
 f.write("- Repeating patterns could indicate fitness function preferences\n")
 f.write("- Mutation patterns show how identities evolved\n")
 f.write("- Convergence indicates successful evolutionary paths\n\n")
 
 print(f"📄 Report saved to: {report_file}")
 print()
 print("=" * 80)
 print("✅ EVOLUTIONARY SIGNATURES ANALYSIS COMPLETE")
 print("=" * 80)

if __name__ == "__main__":
 main()

