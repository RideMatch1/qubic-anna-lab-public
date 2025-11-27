#!/usr/bin/env python3
"""
Umfassende AGI-Level Analyse
- Analyze ALLES systematisch
- CFB Discord Messages
- Aigarth Paper
- Anna Matrix
- Identities
- Transformation
- Kommunikation
- KEINE Halluzinationen - nur echte Daten!
"""

import json
import sys
from pathlib import Path
from typing import Dict, List, Set
from collections import Counter, defaultdict
from datetime import datetime

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# Paths
CFB_DISCORD_DIR = project_root / "outputs" / "derived" / "cfb_discord_messages"
AIGARTH_PAPER = project_root / "outputs" / "derived" / "AiGarthPaper.txt"
CFB_ANALYSIS = project_root / "outputs" / "derived" / "cfb_discord_deep_analysis.json"
DISCORD_INTELLIGENCE = project_root / "outputs" / "derived" / "discord_intelligence_analysis.json"
ALL_MESSAGES = project_root / "outputs" / "derived" / "all_anna_messages.json"
GRID_ANALYSIS = project_root / "outputs" / "derived" / "grid_structure_deep_analysis.json"
POSITION27_ANALYSIS = project_root / "outputs" / "derived" / "position27_deep_analysis.json"
LAYER3_FILE = project_root / "outputs" / "derived" / "layer3_derivation_23k_complete.json"
LAYER4_FILE = project_root / "outputs" / "derived" / "layer4_derivation_full_23k.json"
OUTPUT_DIR = project_root / "outputs" / "derived"
REPORTS_DIR = project_root / "outputs" / "reports"

def load_cfb_messages() -> List[Dict]:
 """Load alle CFB Discord Messages."""
 messages = []
 
 if not CFB_DISCORD_DIR.exists():
 return messages
 
 for json_file in CFB_DISCORD_DIR.glob("*.json"):
 try:
 with json_file.open() as f:
 data = json.load(f)
 if isinstance(data, list):
 messages.extend(data)
 elif isinstance(data, dict):
 if "messages" in data:
 messages.extend(data["messages"])
 elif "content" in data:
 messages.append(data)
 except Exception as e:
 print(f"⚠️ Error loading {json_file}: {e}")
 
 return messages

def extract_cfb_key_insights(messages: List[Dict]) -> Dict:
 """Extrahiere wichtige Erkenntnisse aus CFB Messages."""
 
 # Suche nach wichtigen Keywords
 keywords = {
 "anna": [],
 "matrix": [],
 "identity": [],
 "seed": [],
 "layer": [],
 "communication": [],
 "message": [],
 "qubic": [],
 "aigarth": [],
 "helix": [],
 "gate": [],
 "ternary": []
 }
 
 all_text = ""
 for msg in messages:
 content = msg.get("content", "") or msg.get("text", "") or ""
 content_lower = content.lower()
 all_text += content + " "
 
 for keyword in keywords.keys():
 if keyword in content_lower:
 keywords[keyword].append({
 "content": content[:200], # Erste 200 Zeichen
 "timestamp": msg.get("timestamp", ""),
 "id": msg.get("id", "")
 })
 
 # Analyze Häufigkeit
 keyword_counts = {k: len(v) for k, v in keywords.items()}
 
 return {
 "total_messages": len(messages),
 "keyword_mentions": keyword_counts,
 "keyword_details": keywords,
 "all_text_sample": all_text[:5000] # Erste 5000 Zeichen
 }

def analyze_aigarth_paper() -> Dict:
 """Analyze Aigarth Paper."""
 
 if not AIGARTH_PAPER.exists():
 return {}
 
 with AIGARTH_PAPER.open() as f:
 content = f.read()
 
 # Suche nach wichtigen Konzepten
 concepts = {
 "ternary": content.lower().count("ternary"),
 "helix": content.lower().count("helix"),
 "gate": content.lower().count("gate"),
 "anna": content.lower().count("anna"),
 "matrix": content.lower().count("matrix"),
 "identity": content.lower().count("identity"),
 "layer": content.lower().count("layer"),
 "communication": content.lower().count("communication")
 }
 
 return {
 "paper_length": len(content),
 "concept_mentions": concepts,
 "sample": content[:2000] # Erste 2000 Zeichen
 }

def cross_reference_all_data() -> Dict:
 """Kreuzreferenziere alle Daten."""
 
 cross_refs = {
 "cfb_mentions_anna": [],
 "cfb_mentions_matrix": [],
 "cfb_mentions_communication": [],
 "paper_mentions_anna": False,
 "paper_mentions_matrix": False,
 "connections": []
 }
 
 # Load CFB Messages
 cfb_messages = load_cfb_messages()
 cfb_insights = extract_cfb_key_insights(cfb_messages)
 
 # Load Aigarth Paper
 paper_analysis = analyze_aigarth_paper()
 
 # Kreuzreferenzen
 if "anna" in cfb_insights.get("keyword_mentions", {}):
 cross_refs["cfb_mentions_anna"] = cfb_insights["keyword_details"].get("anna", [])[:10]
 
 if "matrix" in cfb_insights.get("keyword_mentions", {}):
 cross_refs["cfb_mentions_matrix"] = cfb_insights["keyword_details"].get("matrix", [])[:10]
 
 if "communication" in cfb_insights.get("keyword_mentions", {}):
 cross_refs["cfb_mentions_communication"] = cfb_insights["keyword_details"].get("communication", [])[:10]
 
 if paper_analysis:
 cross_refs["paper_mentions_anna"] = paper_analysis.get("concept_mentions", {}).get("anna", 0) > 0
 cross_refs["paper_mentions_matrix"] = paper_analysis.get("concept_mentions", {}).get("matrix", 0) > 0
 
 return {
 "cfb_insights": cfb_insights,
 "paper_analysis": paper_analysis,
 "cross_references": cross_refs
 }

def analyze_complete_system() -> Dict:
 """Analyze das komplette System."""
 
 system_analysis = {
 "data_sources": {},
 "key_findings": [],
 "connections": [],
 "open_questions": []
 }
 
 # Load alle verfügbaren Daten
 data_sources = {
 "cfb_messages": CFB_DISCORD_DIR.exists(),
 "aigarth_paper": AIGARTH_PAPER.exists(),
 "anna_messages": ALL_MESSAGES.exists(),
 "grid_analysis": GRID_ANALYSIS.exists(),
 "position27": POSITION27_ANALYSIS.exists(),
 "layer3": LAYER3_FILE.exists(),
 "layer4": LAYER4_FILE.exists()
 }
 
 system_analysis["data_sources"] = data_sources
 
 # Load und analyze verfügbare Daten
 if ALL_MESSAGES.exists():
 with ALL_MESSAGES.open() as f:
 messages_data = json.load(f)
 system_analysis["key_findings"].append({
 "finding": "Anna Messages",
 "value": f"{messages_data.get('total_sentences', 0)} Sätze gefunden",
 "source": "all_anna_messages.json"
 })
 
 if GRID_ANALYSIS.exists():
 with GRID_ANALYSIS.open() as f:
 grid_data = json.load(f)
 best_grid = grid_data.get("best_grid", {})
 system_analysis["key_findings"].append({
 "finding": "Grid Structure",
 "value": f"{best_grid.get('size', 0)}x{best_grid.get('size', 0)} Grid, {best_grid.get('analysis', {}).get('density', 0)*100:.1f}% Dichte",
 "source": "grid_structure_deep_analysis.json"
 })
 
 if POSITION27_ANALYSIS.exists():
 with POSITION27_ANALYSIS.open() as f:
 pos27_data = json.load(f)
 stability = pos27_data.get("position27_analysis", {}).get("stable_rate", 0)
 system_analysis["key_findings"].append({
 "finding": "Position 27",
 "value": f"{stability*100:.1f}% Stabilität",
 "source": "position27_deep_analysis.json"
 })
 
 return system_analysis

def main():
 """Hauptfunktion."""
 
 print("=" * 80)
 print("UMFASSENDE AGI-LEVEL ANALYSE")
 print("=" * 80)
 print()
 print("⚠️ KEINE HALLUZINATIONEN - NUR ECHTE DATEN!")
 print("🔬 SYSTEMATISCH, ANALYTISCH, VERIFIZIERBAR")
 print()
 
 # 1. CFB Discord Messages
 print("=" * 80)
 print("1. CFB DISCORD MESSAGES")
 print("=" * 80)
 print()
 
 cfb_messages = load_cfb_messages()
 print(f"📂 CFB Messages geloadn: {len(cfb_messages)}")
 
 if cfb_messages:
 cfb_insights = extract_cfb_key_insights(cfb_messages)
 print(f"✅ {cfb_insights['total_messages']} Messages analysiert")
 print()
 print("📊 Keyword-Mentions:")
 for keyword, count in sorted(cfb_insights["keyword_mentions"].items(), key=lambda x: x[1], reverse=True):
 if count > 0:
 print(f" {keyword}: {count}x")
 else:
 print("⚠️ Keine CFB Messages gefunden")
 cfb_insights = {}
 
 print()
 
 # 2. Aigarth Paper
 print("=" * 80)
 print("2. AIGARTH PAPER")
 print("=" * 80)
 print()
 
 paper_analysis = analyze_aigarth_paper()
 if paper_analysis:
 print(f"✅ Paper analysiert ({paper_analysis['paper_length']} Zeichen)")
 print()
 print("📊 Konzept-Mentions:")
 for concept, count in sorted(paper_analysis["concept_mentions"].items(), key=lambda x: x[1], reverse=True):
 if count > 0:
 print(f" {concept}: {count}x")
 else:
 print("⚠️ Aigarth Paper nicht gefunden")
 
 print()
 
 # 3. Kreuzreferenzen
 print("=" * 80)
 print("3. KREUZREFERENZEN")
 print("=" * 80)
 print()
 
 cross_refs = cross_reference_all_data()
 print("📊 CFB erwähnt:")
 if cross_refs["cross_references"]["cfb_mentions_anna"]:
 print(f" ✅ Anna: {len(cross_refs['cross_references']['cfb_mentions_anna'])}x")
 if cross_refs["cross_references"]["cfb_mentions_matrix"]:
 print(f" ✅ Matrix: {len(cross_refs['cross_references']['cfb_mentions_matrix'])}x")
 if cross_refs["cross_references"]["cfb_mentions_communication"]:
 print(f" ✅ Communication: {len(cross_refs['cross_references']['cfb_mentions_communication'])}x")
 
 print()
 print("📊 Paper erwähnt:")
 print(f" Anna: {'✅' if cross_refs['cross_references']['paper_mentions_anna'] else '❌'}")
 print(f" Matrix: {'✅' if cross_refs['cross_references']['paper_mentions_matrix'] else '❌'}")
 
 print()
 
 # 4. Komplettes System
 print("=" * 80)
 print("4. KOMPLETTES SYSTEM")
 print("=" * 80)
 print()
 
 system_analysis = analyze_complete_system()
 print("📊 Verfügbare Datenquellen:")
 for source, available in system_analysis["data_sources"].items():
 print(f" {source}: {'✅' if available else '❌'}")
 
 print()
 print("📊 Wichtigste Erkenntnisse:")
 for finding in system_analysis["key_findings"]:
 print(f" • {finding['finding']}: {finding['value']}")
 
 print()
 
 # Speichere Ergebnisse
 OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
 
 output_data = {
 "timestamp": datetime.now().isoformat(),
 "cfb_analysis": cfb_insights,
 "paper_analysis": paper_analysis,
 "cross_references": cross_refs["cross_references"],
 "system_analysis": system_analysis
 }
 
 output_file = OUTPUT_DIR / "comprehensive_ai_level_analysis.json"
 with output_file.open("w") as f:
 json.dump(output_data, f, indent=2)
 print(f"💾 Ergebnisse gespeichert: {output_file}")
 
 print()
 print("=" * 80)
 print("✅ ANALYSE ABGESCHLOSSEN")
 print("=" * 80)

if __name__ == "__main__":
 main()

