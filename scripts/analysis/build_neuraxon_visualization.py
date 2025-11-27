#!/usr/bin/env python3
"""
Hilfsskript, um Real-ID-Mappings in ein Neuraxon-Netzwerk zu injizieren und
eine visualisierungsfreundliche JSON-Datei mit Metadaten zu erzeugen.

Beispiel:
 python scripts/analysis/build_neuraxon_visualization.py \
 --mapping-file /path/to/complete_24846_seeds_to_real_ids_mapping.json \
 --output data/neuraxon_exports/real_ids_network.json \
 --network-name "Real ID Showcase" \
 --num-input 64 --num-hidden 128 --num-output 32 \
 --max-mapping 64 --seed 42

Ergebnis: Eine JSON-Datei, die neben dem regulären Neuraxon-Export
zusätzliche Metadaten (Real-IDs, Seeds, Hashes) sowie ein
Visualisierungs-Manifest enthält.
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
from pathlib import Path
from typing import Dict, List, Tuple, Any, Optional

import sys

REPO_ROOT = Path(__file__).resolve().parents[2]
NEURAXON_PATH = REPO_ROOT / "repos" / "neuraxon"
if str(NEURAXON_PATH) not in sys.path:
 sys.path.insert(0, str(NEURAXON_PATH))

from neuraxon import NeuraxonNetwork, NetworkParameters

def parse_simple_mapping(path: Path, max_entries: int | None = None) -> List[Dict[str, Any]]:
 """Liest eine einfache Mapping-Datei ein und normalisiert sie zu einer Liste."""
 with path.open("r") as fh:
 raw = json.load(fh)

 entries: List[Dict[str, Any]] = []

 def _normalize(seed: str, real_id: Any) -> Dict[str, Any]:
 return {
 "seed": seed,
 "real_id": real_id,
 }

 if isinstance(raw, dict):
 for idx, (seed, real_id) in enumerate(raw.items()):
 entries.append(_normalize(str(seed), real_id))
 if max_entries and len(entries) >= max_entries:
 break
 elif isinstance(raw, list):
 for item in raw:
 if isinstance(item, dict):
 # Versuche generische Schlüssel
 seed = (
 item.get("seed")
 or item.get("input")
 or item.get("seed_id")
 or item.get("id")
 or item.get("key")
 or f"seed_{len(entries)}"
 )
 real_id = (
 item.get("real_id")
 or item.get("value")
 or item.get("target")
 or item.get("output")
 or item
 )
 entries.append(_normalize(str(seed), real_id))
 else:
 entries.append(_normalize(f"seed_{len(entries)}", item))
 if max_entries and len(entries) >= max_entries:
 break
 else:
 raise ValueError(f"Unbekanntes Mapping-Format: {type(raw)}")

 if not entries:
 raise ValueError("Mapping enthält keine Einträge.")

 return entries

def parse_mapping_database(path: Path, max_entries: Optional[int] = None) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
 """Lädt die vollständige Mapping-Datenbank (~24k Seeds)."""
 if not path.exists():
 raise FileNotFoundError(f"Mapping-Datenbank nicht gefunden: {path}")

 with path.open("r") as fh:
 data = json.load(fh)

 seed_to_real = data.get("seed_to_real_id", {})
 seed_to_doc = data.get("seed_to_doc_id", {})
 stats = data.get("statistics", {})

 if not seed_to_real:
 raise ValueError("Mapping-Datenbank enthält keine 'seed_to_real_id'-Einträge.")

 entries: List[Dict[str, Any]] = []
 for idx, seed in enumerate(sorted(seed_to_real.keys())):
 entry = {
 "seed": seed,
 "real_id": seed_to_real[seed],
 "doc_id": seed_to_doc.get(seed),
 "index": idx,
 }
 entries.append(entry)
 if max_entries and len(entries) >= max_entries:
 break

 return entries, stats

def trinary_from_string(value: str) -> int:
 """Erzeugt einen stabilen Trinarystate (-1,0,1) for eine ID."""
 digest = hashlib.sha256(value.encode("utf-8")).hexdigest()
 mod = int(digest, 16) % 3
 return [-1, 0, 1][mod]

def attach_metadata(payload: Dict[str, Any], annotations: Dict[int, Dict[str, Any]]) -> None:
 payload.setdefault("metadata", {})
 payload["metadata"]["neuron_annotations"] = annotations

def compute_seed_hash(seed: str) -> str:
 return hashlib.sha256(seed.encode("utf-8")).hexdigest()

def chunk_entries(entries: List[Dict[str, Any]], chunk_size: int) -> List[List[Dict[str, Any]]]:
 return [entries[i : i + chunk_size] for i in range(0, len(entries), chunk_size)]

def extract_top_connections(
 network: NeuraxonNetwork, node_ids: List[int], top_n: int
) -> List[Dict[str, Any]]:
 """Return the strongest synapses within the given node set."""
 if top_n <= 0:
 return []

 node_set = set(node_ids)
 connections: List[Dict[str, Any]] = []
 for synapse in network.synapses:
 if synapse.pre_id in node_set and synapse.post_id in node_set:
 weight = abs(
 (synapse.w_fast or 0.0)
 + (synapse.w_slow or 0.0)
 + (synapse.w_meta or 0.0)
 )
 if weight <= 0:
 continue
 connections.append(
 {
 "pre_id": synapse.pre_id,
 "post_id": synapse.post_id,
 "weight": weight,
 "w_fast": synapse.w_fast,
 "w_slow": synapse.w_slow,
 "w_meta": synapse.w_meta,
 "synapse_type": synapse.synapse_type.value,
 }
 )

 connections.sort(key=lambda c: c["weight"], reverse=True)
 return connections[:top_n]

def build_network(
 args: argparse.Namespace, entries: List[Dict[str, Any]]
) -> Tuple[NeuraxonNetwork, List[Dict[str, Any]]]:
 """Erstellt ein Neuraxon-Netzwerk und generiert Frame-Annotationen."""
 chunk_size = min(args.chunk_size, len(entries))
 params = NetworkParameters(
 network_name=args.network_name,
 num_input_neurons=chunk_size,
 num_hidden_neurons=args.num_hidden,
 num_output_neurons=args.num_output,
 connection_probability=args.connection_probability,
 dt=args.dt,
 )
 network = NeuraxonNetwork(params)

 frames: List[Dict[str, Any]] = []
 chunks = chunk_entries(entries, chunk_size)
 for chunk_idx, chunk in enumerate(chunks):
 annotations: Dict[int, Dict[str, Any]] = {}
 states: List[int] = []
 node_ids: List[int] = []
 for neuron_idx in range(chunk_size):
 neuron = network.input_neurons[neuron_idx]
 if neuron_idx < len(chunk):
 entry = chunk[neuron_idx]
 rid = str(entry.get("real_id"))
 seed = entry.get("seed", "")
 state = trinary_from_string(rid)
 node_ids.append(neuron.id)
 annotations[neuron.id] = {
 "seed": seed,
 "seed_hash": compute_seed_hash(seed),
 "real_id": rid,
 "doc_id": entry.get("doc_id"),
 "state_from_hash": state,
 "source_index": entry.get("index", neuron_idx),
 }
 states.append(state)
 else:
 states.append(0)

 frames.append(
 {
 "frame_id": f"chunk_{chunk_idx}",
 "start_index": chunk_idx * chunk_size,
 "end_index": chunk_idx * chunk_size + len(chunk) - 1,
 "annotations": annotations,
 "states": states,
 "node_ids": node_ids,
 "top_connections": extract_top_connections(
 network, node_ids, args.top_connections
 ),
 }
 )

 if frames:
 network.set_input_states(frames[0]["states"])

 return network, frames

def export_payload(
 network: NeuraxonNetwork,
 frames: List[Dict[str, Any]],
 args: argparse.Namespace,
 global_stats: Dict[str, Any],
 total_entries: int,
) -> Dict[str, Any]:
 """Erzeugt das finale Payload inklusive Manifest."""
 payload = network.to_dict()
 initial_annotations = frames[0]["annotations"] if frames else {}
 attach_metadata(payload, initial_annotations)
 cli_args = {
 key: (str(value) if isinstance(value, Path) else value)
 for key, value in vars(args).items()
 }
 payload["metadata"]["source"] = {
 "mapping_file": str(args.mapping_file) if args.mapping_file else None,
 "mapping_database": str(args.mapping_database) if args.mapping_database else None,
 "generated_at": dt.datetime.utcnow().isoformat() + "Z",
 "cli_args": cli_args,
 }
 payload["metadata"]["frames"] = frames
 payload["metadata"]["global_stats"] = {
 "total_entries": total_entries,
 "chunk_size": args.chunk_size,
 "frame_count": len(frames),
 "database_stats": global_stats,
 }
 payload["visualization_manifest"] = {
 "legend": {
 "input": "Farbkodierte Knoten mit Real-ID Labels",
 "hidden": "Graue Knoten, Fokus auf Weiterleitung",
 "output": "Blau/Rot for finale Zustände",
 "edge_weight": "Breite proportional zu |w_fast + w_slow|",
 },
 "recommended_tools": ["Plotly Scatter3d", "HuggingFace Space Fork", "Three.js"],
 }
 return payload

def ensure_output_dir(path: Path) -> None:
 path.parent.mkdir(parents=True, exist_ok=True)

def parse_args() -> argparse.Namespace:
 parser = argparse.ArgumentParser(description="Real-ID ➜ Neuraxon Exporter")
 parser.add_argument("--mapping-file", type=Path, help="Pfad zu einer einfachen Mapping-Datei")
 parser.add_argument(
 "--mapping-database",
 type=Path,
 default=Path("outputs/analysis/complete_mapping_database.json"),
 help="Pfad zur vollständigen Mapping-Datenbank",
 )
 parser.add_argument("--output", type=Path, required=True, help="Zielpfad for den Export (JSON)")
 parser.add_argument("--network-name", type=str, default="Real ID Showcase")
 parser.add_argument("--num-input", type=int, default=64) # will durch chunk-size aboveschrieben
 parser.add_argument("--num-hidden", type=int, default=128)
 parser.add_argument("--num-output", type=int, default=32)
 parser.add_argument("--connection-probability", type=float, default=0.08)
 parser.add_argument("--dt", type=float, default=1.0)
 parser.add_argument("--max-mapping", type=int, default=None, help="Anzahl verwendeter Mapping-Einträge")
 parser.add_argument("--chunk-size", type=int, default=512, help="Seeds pro Visualisierungsframe")
 parser.add_argument("--top-connections", type=int, default=30, help="Anzahl starker Verbindungen pro Frame")
 parser.add_argument("--seed", type=int, default=7, help="RNG-Seed for deterministische Netze")
 return parser.parse_args()

def main() -> None:
 args = parse_args()

 if args.seed is not None:
 import random

 random.seed(args.seed)

 if args.mapping_file:
 entries = parse_simple_mapping(args.mapping_file, args.max_mapping)
 global_stats = {}
 else:
 entries, stats = parse_mapping_database(args.mapping_database, args.max_mapping)
 global_stats = stats

 if args.chunk_size > len(entries):
 args.chunk_size = len(entries)

 network, frames = build_network(args, entries)
 payload = export_payload(network, frames, args, global_stats, total_entries=len(entries))

 ensure_output_dir(args.output)
 with args.output.open("w") as fh:
 json.dump(payload, fh, indent=2)

 print(f"[OK] Export gespeichert unter: {args.output}")
 print(f" Frames: {len(frames)} mit je {args.chunk_size} Seeds (gesamt {len(entries)})")

if __name__ == "__main__":
 main()

