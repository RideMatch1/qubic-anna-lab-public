#!/usr/bin/env python3
"""
Fast CFB Discord Message Exporter

Exports only CFB's messages (User ID: 395234579805503489) from specified channels.
Uses DiscordChatExporter.Cli for fast batch exports.

Channel: https://discord.com/channels/768887649540243497/768890598736003092
CFB User ID: 395234579805503489
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Optional

# Configuration
CFB_USER_ID = "395234579805503489"
CHANNEL_ID = "768890598736003092" # Aigarth channel
GUILD_ID = "768887649540243497"

# Paths
EXPORTER_PATH = Path("${DISCORD_EXPORTER_DIR}/DiscordChatExporter.Cli")
OUTPUT_DIR = Path("outputs/derived/cfb_discord_messages")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

def get_discord_token() -> Optional[str]:
 """Get Discord token from environment or config."""
 token = os.getenv("DISCORD_TOKEN")
 
 if not token:
 # Try config files
 config_files = [
 Path.home() / ".discord_token",
 Path("${DISCORD_EXPORTER_DIR}/.discord_token"),
 ]
 
 for config_file in config_files:
 if config_file.exists():
 try:
 with config_file.open() as f:
 token = f.readline().strip()
 if token:
 break
 except Exception:
 continue
 
 return token

def export_channel_json(
 token: str,
 channel_id: str,
 output_file: Path,
 after: Optional[str] = None,
 before: Optional[str] = None,
) -> bool:
 """Export channel to JSON using DiscordChatExporter.Cli."""
 
 if not EXPORTER_PATH.exists():
 print(f"❌ DiscordChatExporter.Cli not found at: {EXPORTER_PATH}")
 return False
 
 cmd = [
 str(EXPORTER_PATH),
 "export",
 "--channel", channel_id,
 "--token", token,
 "--output", str(output_file),
 "--format", "Json",
 "--markdown", "True",
 ]
 
 if after:
 cmd.extend(["--after", after])
 if before:
 cmd.extend(["--before", before])
 
 try:
 result = subprocess.run(
 cmd,
 capture_output=True,
 text=True,
 check=True,
 timeout=300, # 5 minutes max
 )
 return True
 except subprocess.TimeoutExpired:
 print(f"⏱️ Export timeout for channel {channel_id}")
 return False
 except subprocess.CalledProcessError as e:
 print(f"❌ Export error: {e.stderr[:200]}")
 return False
 except Exception as e:
 print(f"❌ Error: {e}")
 return False

def filter_cfb_messages(json_file: Path) -> list:
 """Filter messages from CFB's user ID."""
 try:
 with json_file.open(encoding="utf-8") as f:
 data = json.load(f)
 
 cfb_messages = []
 
 if "messages" in data:
 for msg in data["messages"]:
 author = msg.get("author", {})
 author_id = author.get("id", "")
 
 if author_id == CFB_USER_ID:
 cfb_messages.append(msg)
 
 return cfb_messages
 
 except Exception as e:
 print(f"❌ Error filtering messages: {e}")
 return []

def export_cfb_messages_batch(
 token: str,
 channel_id: str,
 batch_size: int = 100,
) -> list:
 """
 Export CFB messages in batches.
 Returns all CFB messages found.
 """
 all_cfb_messages = []
 last_message_id = None
 batch_num = 0
 
 print(f"📥 Exporting CFB messages from channel {channel_id}...")
 print(f" CFB User ID: {CFB_USER_ID}")
 print()
 
 while True:
 batch_num += 1
 temp_file = OUTPUT_DIR / f"batch_{batch_num}_temp.json"
 
 print(f" Batch {batch_num}...", end=" ", flush=True)
 
 # Export batch (after last message ID)
 success = export_channel_json(
 token=token,
 channel_id=channel_id,
 output_file=temp_file,
 after=last_message_id,
 )
 
 if not success:
 print("❌")
 break
 
 # Filter CFB messages
 batch_cfb = filter_cfb_messages(temp_file)
 
 if not batch_cfb:
 print(f"✅ (0 CFB messages)")
 # No more CFB messages, but check if there are any messages at all
 try:
 with temp_file.open(encoding="utf-8") as f:
 data = json.load(f)
 if not data.get("messages"):
 print(" No more messages in channel")
 temp_file.unlink(missing_ok=True)
 break
 except Exception:
 pass
 temp_file.unlink(missing_ok=True)
 break
 
 print(f"✅ ({len(batch_cfb)} CFB messages)")
 all_cfb_messages.extend(batch_cfb)
 
 # Update last message ID for next batch
 if batch_cfb:
 last_message_id = batch_cfb[-1].get("id")
 
 # Cleanup temp file
 temp_file.unlink(missing_ok=True)
 
 # Stop if we got fewer than batch_size (reached the end)
 if len(batch_cfb) < batch_size:
 break
 
 return all_cfb_messages

def analyze_cfb_messages(messages: list) -> dict:
 """Analyze CFB messages for relevant keywords."""
 analysis = {
 "total_messages": len(messages),
 "date_range": {
 "earliest": None,
 "latest": None,
 },
 "keywords": {
 "matrix": [],
 "puzzle": [],
 "reward": [],
 "contract": [],
 "genesis": [],
 "26": [],
 "676": [],
 "128": [],
 "block": [],
 "layer": [],
 "seed": [],
 "identity": [],
 },
 "relevant_messages": [],
 }
 
 keywords_map = {
 "matrix": ["matrix", "anna", "anna-matrix"],
 "puzzle": ["puzzle", "riddle", "challenge"],
 "reward": ["reward", "prize", "treasure"],
 "contract": ["contract", "POCCZYCKTRQGHFIPWGSBLJTEQFDDVVBMNUHNCKMRACBGQOPBLURNRCBAFOBD"],
 "genesis": ["genesis", "asset", "token"],
 "26": ["26", "twenty-six"],
 "676": ["676", "six hundred seventy-six"],
 "128": ["128", "one hundred twenty-eight"],
 "block": ["block", "block-id"],
 "layer": ["layer"],
 "seed": ["seed"],
 "identity": ["identity", "public key", "publickey"],
 }
 
 timestamps = []
 
 for msg in messages:
 content = msg.get("content", "").lower()
 timestamp = msg.get("timestamp", "")
 message_id = msg.get("id", "")
 
 if timestamp:
 timestamps.append(timestamp)
 
 relevant = False
 
 for category, terms in keywords_map.items():
 for term in terms:
 if term.lower() in content:
 analysis["keywords"][category].append({
 "id": message_id,
 "timestamp": timestamp,
 "preview": content[:150],
 })
 relevant = True
 
 if relevant:
 analysis["relevant_messages"].append({
 "id": message_id,
 "timestamp": timestamp,
 "content": msg.get("content", ""),
 })
 
 if timestamps:
 analysis["date_range"]["earliest"] = min(timestamps)
 analysis["date_range"]["latest"] = max(timestamps)
 
 return analysis

def main() -> int:
 """Main export function."""
 
 print("=" * 80)
 print("🚀 FAST CFB DISCORD MESSAGE EXPORTER")
 print("=" * 80)
 print()
 
 # Get token
 token = get_discord_token()
 
 if not token:
 print("❌ Discord token not found!")
 print()
 print("Set it as environment variable:")
 print(" export DISCORD_TOKEN='your_token'")
 print()
 print("Or create ~/.discord_token with token on first line")
 return 1
 
 print(f"✅ Token found (length: {len(token)})")
 print()
 
 # Export CFB messages
 cfb_messages = export_cfb_messages_batch(
 token=token,
 channel_id=CHANNEL_ID,
 batch_size=100,
 )
 
 print()
 print(f"✅ Total CFB messages found: {len(cfb_messages)}")
 print()
 
 if not cfb_messages:
 print("⚠️ No CFB messages found in this channel")
 return 0
 
 # Save all CFB messages
 output_json = OUTPUT_DIR / f"cfb_messages_channel_{CHANNEL_ID}.json"
 with output_json.open("w", encoding="utf-8") as f:
 json.dump(cfb_messages, f, indent=2, ensure_ascii=False)
 
 print(f"💾 Saved to: {output_json}")
 print()
 
 # Analyze messages
 print("=" * 80)
 print("📊 ANALYZING MESSAGES")
 print("=" * 80)
 print()
 
 analysis = analyze_cfb_messages(cfb_messages)
 
 print(f"Total messages: {analysis['total_messages']}")
 if analysis["date_range"]["earliest"]:
 print(f"Date range: {analysis['date_range']['earliest']} to {analysis['date_range']['latest']}")
 print()
 
 print("Keywords found:")
 for category, matches in analysis["keywords"].items():
 if matches:
 print(f" {category}: {len(matches)} matches")
 print()
 
 # Save analysis
 analysis_file = OUTPUT_DIR / f"cfb_analysis_channel_{CHANNEL_ID}.json"
 with analysis_file.open("w", encoding="utf-8") as f:
 json.dump(analysis, f, indent=2, ensure_ascii=False)
 
 # Create markdown report
 report_file = OUTPUT_DIR / f"cfb_report_channel_{CHANNEL_ID}.md"
 with report_file.open("w", encoding="utf-8") as f:
 f.write(f"# CFB Discord Messages - Channel {CHANNEL_ID}\n\n")
 f.write(f"**Total Messages:** {analysis['total_messages']}\n\n")
 
 if analysis["date_range"]["earliest"]:
 f.write(f"**Date Range:** {analysis['date_range']['earliest']} to {analysis['date_range']['latest']}\n\n")
 
 f.write("## Keywords Found\n\n")
 for category, matches in analysis["keywords"].items():
 if matches:
 f.write(f"### {category.upper()} ({len(matches)} matches)\n\n")
 for match in matches[:10]:
 f.write(f"- **{match['timestamp']}**: {match['preview']}...\n")
 f.write("\n")
 
 f.write("## Relevant Messages\n\n")
 for msg in analysis["relevant_messages"][:50]:
 f.write(f"### {msg['timestamp']}\n\n")
 f.write(f"{msg['content']}\n\n")
 f.write("---\n\n")
 
 print(f"💾 Analysis saved to: {analysis_file}")
 print(f"📄 Report saved to: {report_file}")
 print()
 print("=" * 80)
 print("✅ EXPORT COMPLETE")
 print("=" * 80)
 
 return 0

if __name__ == "__main__":
 raise SystemExit(main())

