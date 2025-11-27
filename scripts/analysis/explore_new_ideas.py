#!/usr/bin/env python3
"""
Explore New Ideas

Erkundet neue Ideen und Ansätze mit der großen Datenmenge:
- Machine Learning Ansätze
- Clustering
- Anomaly Detection
- Network Analysis
"""

import json
import sys
from pathlib import Path
from collections import defaultdict
from typing import Dict, List

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

INPUT_FILE = project_root / "outputs" / "analysis" / "complete_mapping_database.json"
OUTPUT_DIR = project_root / "outputs" / "analysis"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

def cluster_by_similarity(mismatches: List[Dict]) -> Dict:
 """Clustere ähnliche Transformationen."""
 clusters = defaultdict(list)
 
 for item in mismatches[:500]:
 doc_id = item.get("documented_identity", "")
 real_id = item.get("real_identity", "")
 
 if len(doc_id) == 60 and len(real_id) == 60:
 # Calculate similarity signature
 diff_signature = []
 for i in range(60):
 if doc_id[i] != real_id[i]:
 diff = ord(real_id[i]) - ord(doc_id[i])
 diff_signature.append(f"{i}:{diff}")
 
 signature = ",".join(diff_signature[:10]) # First 10 differences
 clusters[signature].append(item)
 
 # Find largest clusters
 largest_clusters = sorted(clusters.items(), key=lambda x: len(x[1]), reverse=True)[:10]
 
 return {
 "total_clusters": len(clusters),
 "largest_clusters": [(sig, len(items)) for sig, items in largest_clusters],
 "cluster_samples": {sig: items[:5] for sig, items in largest_clusters}
 }

def network_analysis(database: Dict) -> Dict:
 """Analyze Netzwerk-Verbindungen."""
 seed_to_real = database.get("seed_to_real_id", {})
 seed_to_doc = database.get("seed_to_doc_id", {})
 
 # Build network
 nodes = set()
 edges = []
 
 for seed, real_id in seed_to_real.items():
 nodes.add(seed)
 nodes.add(real_id)
 edges.append(("seed", seed, real_id))
 
 for seed, doc_id in seed_to_doc.items():
 nodes.add(doc_id)
 edges.append(("seed", seed, doc_id))
 
 # Find connections
 connections = defaultdict(list)
 for edge_type, source, target in edges:
 connections[source].append(target)
 connections[target].append(source)
 
 # Find hubs (nodes with many connections)
 hubs = sorted(connections.items(), key=lambda x: len(x[1]), reverse=True)[:20]
 
 return {
 "total_nodes": len(nodes),
 "total_edges": len(edges),
 "hubs": [(node, len(conns)) for node, conns in hubs]
 }

def anomaly_detection(mismatches: List[Dict]) -> Dict:
 """Erkenne Anomalien in den Daten."""
 anomalies = {
 "very_similar": [],
 "very_different": [],
 "unusual_seeds": []
 }
 
 for item in mismatches[:1000]:
 doc_id = item.get("documented_identity", "")
 real_id = item.get("real_identity", "")
 seed = item.get("seed", "")
 
 if len(doc_id) == 60 and len(real_id) == 60:
 # Calculate similarity
 same_chars = sum(1 for i in range(60) if doc_id[i] == real_id[i])
 similarity = same_chars / 60
 
 if similarity > 0.9:
 anomalies["very_similar"].append({
 "item": item,
 "similarity": similarity
 })
 elif similarity < 0.1:
 anomalies["very_different"].append({
 "item": item,
 "similarity": similarity
 })
 
 # Check for unusual seed patterns
 if seed:
 # Check for unusual patterns
 if seed.count('a') > 40 or len(set(seed)) < 5:
 anomalies["unusual_seeds"].append(item)
 
 return anomalies

def main():
 """Main function."""
 print("=" * 80)
 print("EXPLORE NEW IDEAS")
 print("=" * 80)
 print()
 
 if not INPUT_FILE.exists():
 print(f"❌ Input file not found: {INPUT_FILE}")
 return
 
 print("1. Loading database...")
 with INPUT_FILE.open() as f:
 database = json.load(f)
 
 mismatches = database.get("mismatches", [])
 print(f" ✅ Loaded {len(mismatches):,} mismatches")
 print()
 
 print("2. Clustering by similarity...")
 clusters = cluster_by_similarity(mismatches)
 print(f" ✅ Found {clusters['total_clusters']} clusters")
 print(f" ✅ Largest cluster: {clusters['largest_clusters'][0][1]} items")
 print()
 
 print("3. Network analysis...")
 network = network_analysis(database)
 print(f" ✅ Network: {network['total_nodes']} nodes, {network['total_edges']} edges")
 print(f" ✅ Largest hub: {network['hubs'][0][1]} connections")
 print()
 
 print("4. Anomaly detection...")
 anomalies = anomaly_detection(mismatches)
 print(f" ✅ Very similar: {len(anomalies['very_similar'])}")
 print(f" ✅ Very different: {len(anomalies['very_different'])}")
 print(f" ✅ Unusual seeds: {len(anomalies['unusual_seeds'])}")
 print()
 
 # Save results
 output_file = OUTPUT_DIR / "new_ideas_exploration.json"
 with output_file.open("w") as f:
 json.dump({
 "clusters": clusters,
 "network": network,
 "anomalies": anomalies
 }, f, indent=2)
 
 print("=" * 80)
 print("EXPLORATION COMPLETE")
 print("=" * 80)
 print(f"✅ Results saved to: {output_file}")

if __name__ == "__main__":
 main()

