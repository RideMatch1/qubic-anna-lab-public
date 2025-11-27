#!/usr/bin/env python3
"""
Deep Dive in Top 50 CFB Messages - Detaillierte Analyse for spezifische Hinweise.

Fokussiert auf:
- Identity-Rollen
- Master Identity
- Layer-Struktur
- Helix Gate Details
- Matrix-Hinweise
"""

import json
import re
from pathlib import Path
from typing import List, Dict
from collections import defaultdict
from datetime import datetime

OUTPUT_DIR = Path("outputs/derived")
REPORTS_DIR = Path("outputs/reports")

# Spezifische Such-Patterns
SPECIFIC_PATTERNS = {
 "identity_role": [
 r"identity.*role",
 r"identity.*function",
 r"identity.*purpose",
 r"what.*identity.*for",
 ],
 "master_identity": [
 r"master.*identity",
 r"main.*identity",
 r"anna.*identity",
 r"control.*identity",
 ],
 "layer_structure": [
 r"layer.*3",
 r"layer.*structure",
 r"hierarchical",
 r"layer.*progression",
 ],
 "helix_details": [
 r"helix.*gate",
 r"A\+B\+C",
 r"rotation",
 r"helix.*operation",
 ],
 "matrix_hints": [
 r"matrix.*hint",
 r"matrix.*clue",
 r"128.*128",
 r"anna.*matrix",
 r"intelligent.*tissue",
 ],
 "evolution": [
 r"evolution",
 r"selection",
 r"fitness",
 r"fittest",
 ],
 "oracle_machine": [
 r"oracle.*machine",
 r"oracle.*identity",
 r"OM.*identity",
 ],
}

def load_cfb_messages() -> List[Dict]:
 """Load alle CFB Messages."""
 
 messages = []
 cfb_dir = OUTPUT_DIR / "cfb_discord_messages"
 
 if not cfb_dir.exists():
 print(f"⚠️ CFB messages directory not found: {cfb_dir}")
 return messages
 
 for json_file in cfb_dir.glob("*.json"):
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

def score_message_relevance(message: Dict) -> int:
 """Bewerte Message-Relevanz basierend auf Patterns."""
 
 content = message.get("content", "").lower()
 score = 0
 
 for category, patterns in SPECIFIC_PATTERNS.items():
 for pattern in patterns:
 if re.search(pattern, content, re.IGNORECASE):
 score += 2 # Specific patterns worth more
 
 # Bonus for lange Messages (mehr context)
 if len(content) > 500:
 score += 1
 
 # Bonus for Aigarth/Anna/Helix mentions
 if any(term in content for term in ["aigarth", "anna", "helix", "evolution"]):
 score += 1
 
 return score

def extract_specific_hints(message: Dict) -> Dict:
 """Extrahiere spezifische Hinweise aus einer Message."""
 
 content = message.get("content", "")
 hints = defaultdict(list)
 
 for category, patterns in SPECIFIC_PATTERNS.items():
 for pattern in patterns:
 matches = re.finditer(pattern, content, re.IGNORECASE)
 for match in matches:
 # Extrahiere Context
 start = max(0, match.start() - 150)
 end = min(len(content), match.end() + 150)
 context = content[start:end].replace('\n', ' ').strip()
 
 hints[category].append({
 "pattern": pattern,
 "context": context,
 "position": match.start(),
 })
 
 return dict(hints)

def analyze_top_messages(messages: List[Dict], top_n: int = 50) -> List[Dict]:
 """Analyze Top N Messages im Detail."""
 
 # Bewerte alle Messages
 scored_messages = []
 for msg in messages:
 score = score_message_relevance(msg)
 if score > 0:
 scored_messages.append((score, msg))
 
 # Sortiere nach Score
 scored_messages.sort(key=lambda x: x[0], reverse=True)
 
 # Analyze Top N
 top_messages = []
 for score, msg in scored_messages[:top_n]:
 hints = extract_specific_hints(msg)
 
 analysis = {
 "score": score,
 "id": msg.get("id", ""),
 "timestamp": msg.get("timestamp", ""),
 "content": msg.get("content", ""),
 "hints": hints,
 "hint_count": sum(len(h) for h in hints.values()),
 }
 
 top_messages.append(analysis)
 
 return top_messages

def main():
 """Hauptfunktion."""
 
 print("=" * 80)
 print("CFB MESSAGES DEEP DIVE - TOP 50 ANALYSIS")
 print("=" * 80)
 print()
 
 print("Loading CFB messages...")
 messages = load_cfb_messages()
 print(f"✅ Loaded {len(messages):,} messages")
 print()
 
 if not messages:
 print("⚠️ No messages found. Check if CFB messages are exported.")
 return
 
 print("Analyzing top 50 most relevant messages...")
 top_messages = analyze_top_messages(messages, top_n=50)
 print(f"✅ Analyzed {len(top_messages)} top messages")
 print()
 
 # Statistik
 print("=" * 80)
 print("HINT CATEGORY STATISTICS")
 print("=" * 80)
 print()
 
 category_counts = defaultdict(int)
 for msg in top_messages:
 for category in msg["hints"].keys():
 category_counts[category] += len(msg["hints"][category])
 
 for category, count in sorted(category_counts.items(), key=lambda x: x[1], reverse=True):
 print(f"{category.upper()}: {count} hints")
 print()
 
 # Zeige Top 10 Messages
 print("=" * 80)
 print("TOP 10 MESSAGES WITH HINTS")
 print("=" * 80)
 print()
 
 for i, msg in enumerate(top_messages[:10], 1):
 print(f"{i}. Message ID: {msg['id']}")
 print(f" Score: {msg['score']} | Hints: {msg['hint_count']}")
 print(f" Timestamp: {msg['timestamp']}")
 print(f" Categories: {', '.join(msg['hints'].keys())}")
 print(f" Preview: {msg['content'][:200]}...")
 print()
 
 # Speichere Ergebnisse
 OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
 json_file = OUTPUT_DIR / "cfb_deep_dive_top50.json"
 with json_file.open("w") as f:
 json.dump({
 "total_messages_analyzed": len(messages),
 "top_messages": top_messages,
 "category_statistics": dict(category_counts),
 "timestamp": datetime.now().isoformat(),
 }, f, indent=2)
 
 print(f"💾 Results saved to: {json_file}")
 
 # Erstelle detaillierten Report
 REPORTS_DIR.mkdir(parents=True, exist_ok=True)
 report_file = REPORTS_DIR / "cfb_deep_dive_top50_report.md"
 
 with report_file.open("w") as f:
 f.write("# CFB Messages Deep Dive - Top 50 Analysis\n\n")
 f.write(f"**Generated**: {datetime.now().isoformat()}\n\n")
 f.write("## Overview\n\n")
 f.write(f"- **Total messages analyzed**: {len(messages):,}\n")
 f.write(f"- **Top messages analyzed**: {len(top_messages)}\n")
 f.write(f"- **Total hints found**: {sum(msg['hint_count'] for msg in top_messages)}\n\n")
 
 f.write("## Hint Category Statistics\n\n")
 for category, count in sorted(category_counts.items(), key=lambda x: x[1], reverse=True):
 f.write(f"- **{category}**: {count} hints\n")
 f.write("\n")
 
 f.write("## Top 50 Messages with Detailed Analysis\n\n")
 for i, msg in enumerate(top_messages, 1):
 f.write(f"### Message {i}\n\n")
 f.write(f"- **ID**: {msg['id']}\n")
 f.write(f"- **Score**: {msg['score']}\n")
 f.write(f"- **Timestamp**: {msg['timestamp']}\n")
 f.write(f"- **Total Hints**: {msg['hint_count']}\n")
 f.write(f"- **Categories**: {', '.join(msg['hints'].keys())}\n\n")
 
 f.write("**Content**:\n\n")
 f.write(f"```\n{msg['content']}\n```\n\n")
 
 if msg['hints']:
 f.write("**Extracted Hints**:\n\n")
 for category, hints in msg['hints'].items():
 f.write(f"#### {category.upper()}\n\n")
 for hint in hints[:3]: # Top 3 per category
 f.write(f"- **Pattern**: `{hint['pattern']}`\n")
 f.write(f" **Context**: {hint['context']}\n\n")
 f.write("\n---\n\n")
 
 print(f"📄 Report saved to: {report_file}")
 print()
 print("=" * 80)
 print("✅ CFB DEEP DIVE COMPLETE")
 print("=" * 80)

if __name__ == "__main__":
 main()

