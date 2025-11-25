"""Probe public Qubic nodes and log responses for the hidden CFB identities.

The script talks to the JSON-RPC interface over raw TCP (port 21841) and
records whether nodes are reachable as well as how they respond to the eight
identities extracted from Anna Matrix layers (four diagonal + four 9-vortex).

Outputs:
    - A timestamped Markdown report under `outputs/reports/`.
    - A JSON lines logfile with the raw responses for further analysis.

Usage:
    python -m analysis.72_live_node_check
"""
from __future__ import annotations

import json
import socket
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Tuple

BASE_DIR = Path(__file__).resolve().parents[1]
REPORT_DIR = BASE_DIR / "outputs" / "reports"
LOG_FILE = REPORT_DIR / "live_node_monitor.log"

# Public Qubic RPC nodes (these are publicly accessible endpoints)
# Note: These IPs are public infrastructure, not sensitive data
NODES: List[Dict[str, Any]] = [
    {"label": "nyc-01", "host": "167.99.139.198", "port": 21841},
    {"label": "nyc-02", "host": "167.99.253.63", "port": 21841},
    {"label": "ams-01", "host": "134.122.69.166", "port": 21841},
    {"label": "ams-02", "host": "64.226.122.206", "port": 21841},
    {"label": "sgp-01", "host": "45.152.160.217", "port": 21841},
]

IDENTITIES: List[Dict[str, str]] = [
    {
        "label": "Anna Base26 #1",
        "identity": "AQIOSQQMACYBPQXQSJNIUAYLMXXIWQOXQMEQYXBBTBONSJJRCWPXXDDRMDCK",
        "source": "Diagonal extraction",
    },
    {
        "label": "Anna Base26 #2",
        "identity": "GWUXOMMMMFMTBWFZSNGMUKWBILTXQDKNMMMNYPEFTAMRONJMABLHTRRRDGKC",
        "source": "Diagonal extraction",
    },
    {
        "label": "Anna Base26 #3",
        "identity": "ACGJGQQYILBPXDRBORFGWFZBBBNLQNGHDDELVLXXXLBNNNFBLLPBNNNLDPHO",
        "source": "Diagonal extraction",
    },
    {
        "label": "Anna Base26 #4",
        "identity": "GIUVFGAWCBBFFKVBMFJESLHBBFBFWZWNNXCBQBBJRVFBNVJLTJBBBHTHXMTI",
        "source": "Diagonal extraction",
    },
    {
        "label": "9-Vortex #1",
        "identity": "UUFEEMUUBIYXYXDUXZCFBIHABAYSACQSWSGABOBKNXBZCICLYOKOBMLKMUAF",
        "source": "Rings radius 18",
    },
    {
        "label": "9-Vortex #2",
        "identity": "HJBRFBHTBZJLVRBXTDRFORBWNACAHAQMSBUNBONHTRHNJKXKKNKHWCBNAXLD",
        "source": "Rings radius 44",
    },
    {
        "label": "9-Vortex #3",
        "identity": "JKLMNOIPDQORWSICTWWUIYVMOFIQCQSYKMKACMOKQYCCMCOGOCQCSCWCDQFL",
        "source": "Rings radius 66",
    },
    {
        "label": "9-Vortex #4",
        "identity": "XYZQAUBQUUQBQBYQAYEIYAQYMMEMQQQMMQSQEQAZSMOGWOXKIRMJXMCLFAVK",
        "source": "Rings radius 82",
    },
]

def send_rpc(host: str, port: int, payload: Dict[str, Any], timeout: float = 5.0) -> Dict[str, Any]:
    """Send a JSON-RPC payload over raw TCP and return the decoded response."""

    data = json.dumps(payload).encode("utf-8") + b"\n"
    with socket.create_connection((host, port), timeout=timeout) as sock:
        sock.sendall(data)
        raw = sock.makefile().readline()
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        raise RuntimeError(f"invalid JSON response: {raw!r}")

def check_node(node: Dict[str, Any]) -> Tuple[Dict[str, Any], List[Dict[str, Any]]]:
    """Query a node for tick info and all identities."""

    host, port = node["host"], node["port"]
    node_report: Dict[str, Any] = {"label": node["label"], "host": host, "port": port}
    identity_reports: List[Dict[str, Any]] = []

    try:
        tick_resp = send_rpc(host, port, {"jsonrpc": "2.0", "id": 1, "method": "getCurrentTick"})
        result = tick_resp.get("result", {})
        node_report.update(
            {
                "reachable": True,
                "tick": result.get("tick"),
                "epoch": result.get("epoch"),
                "alignedVotes": result.get("alignedVotes"),
                "misalignedVotes": result.get("misalignedVotes"),
            }
        )
    except Exception as exc:  # pylint: disable=broad-except
        node_report.update({"reachable": False, "error": str(exc)})
        return node_report, identity_reports

    for identity in IDENTITIES:
        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "getIdentity",
            "params": {"identity": identity["identity"]},
        }
        entry = {"label": identity["label"], "identity": identity["identity"], "source": identity["source"]}
        try:
            resp = send_rpc(host, port, payload)
            entry["status"] = "ok" if "result" in resp else "error"
            entry["response"] = resp
        except Exception as exc:  # pylint: disable=broad-except
            entry["status"] = "exception"
            entry["response"] = {"error": str(exc)}
        identity_reports.append(entry)
    return node_report, identity_reports

def write_report(timestamp: str, node_results: Iterable[Dict[str, Any]], identity_results: Dict[str, List[Dict[str, Any]]]) -> Path:
    """Render a Markdown summary with all responses."""

    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    report_path = REPORT_DIR / f"live_node_check_{timestamp.replace(':', '-')}.md"

    lines: List[str] = [
        "# Live Node Monitor",
        "",
        f"- Captured at: `{timestamp}`",
        f"- Nodes tested: {len(NODES)}",
        f"- Identities tested: {len(IDENTITIES)}",
        "",
        "## Node Reachability",
        "| Node | Host | Tick | Epoch | Reachable | Notes |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for node in node_results:
        notes = node.get("error", "")
        lines.append(
            f"| {node['label']} | `{node['host']}` | {node.get('tick','-')} | {node.get('epoch','-')} | "
            f"{'REACHABLE' if node.get('reachable') else 'UNREACHABLE'} | {notes} |"
        )

    lines.append("\n## Identity Responses")
    for node in node_results:
        node_label = node["label"]
        lines.append(f"\n### Node {node_label}")
        lines.append("| Identity | Source | Status | Raw |")
        lines.append("| --- | --- | --- | --- |")
        for entry in identity_results.get(node_label, []):
            status = entry.get("status", "n/a")
            raw = entry.get("response")
            snippet = json.dumps(raw)[:80] + ("…" if raw and len(json.dumps(raw)) > 80 else "")
            lines.append(
                f"| {entry['label']} | {entry['source']} | {status} | `{snippet}` |"
            )

    report_path.write_text("\n".join(lines), encoding="utf-8")
    return report_path

def append_json_log(timestamp: str, node_payloads: Dict[str, Any], identity_payloads: Dict[str, List[Dict[str, Any]]]) -> None:
    """Store a JSON lines log for downstream correlation checks."""

    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    with LOG_FILE.open("a", encoding="utf-8") as handle:
        handle.write(
            json.dumps(
                {
                    "timestamp": timestamp,
                    "nodes": node_payloads,
                    "identities": identity_payloads,
                }
            )
        )
        handle.write("\n")

def run_monitor() -> None:
    """Execute node checks and render outputs."""

    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    node_results: List[Dict[str, Any]] = []
    identity_results: Dict[str, List[Dict[str, Any]]] = {}

    for node in NODES:
        node_report, identity_report = check_node(node)
        node_results.append(node_report)
        identity_results[node["label"]] = identity_report

    report_path = write_report(timestamp, node_results, identity_results)
    append_json_log(timestamp, node_results, identity_results)
    print(f"[live-node-check] ✓ report -> {report_path}")
    print(f"[live-node-check] ✓ log appended -> {LOG_FILE}")

if __name__ == "__main__":
    run_monitor()

