#!/usr/bin/env python3
"""
Export CFB Discord Messages from Aigarth Channel

This script uses DiscordChatExporter.Cli to export all messages from CFB's profile
in the aigarth channel (~1500 messages).

Requirements:
- DiscordChatExporter.Cli (set DISCORD_EXPORTER_DIR environment variable)
- Discord Token (user token)
- Channel ID for aigarth channel
- Guild ID for Qubic server

Usage:
 python scripts/verify/export_cfb_discord_messages.py
"""

from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path
from typing import Optional

EXPORTER_PATH = Path("${DISCORD_EXPORTER_DIR}/DiscordChatExporter.Cli")
OUTPUT_DIR = Path("outputs/derived/cfb_discord_messages")
OUTPUT_JSON = OUTPUT_DIR / "cfb_messages.json"
OUTPUT_MD = OUTPUT_DIR / "cfb_messages.md"

def get_discord_credentials() -> dict:
 """Get Discord credentials from environment or user input."""
 credentials = {
 "token": os.getenv("DISCORD_TOKEN"),
 "channel_id": os.getenv("DISCORD_CHANNEL_ID"),
 "guild_id": os.getenv("DISCORD_GUILD_ID"),
 }
 
 # Try to find in common locations
 config_files = [
 Path.home() / ".discord_token",
 Path("${DISCORD_EXPORTER_DIR}/.discord_token"),
 Path("${DISCORD_EXPORTER_DIR}/.discord_config.json"),
 ]
 
 for config_file in config_files:
 if config_file.exists():
 try:
 if config_file.suffix == ".json":
 with config_file.open() as f:
 config = json.load(f)
 credentials.update(config)
 else:
 # Plain text file, assume token on first line
 with config_file.open() as f:
 credentials["token"] = f.readline().strip()
 break
 except Exception:
 continue
 
 return credentials

def export_discord_channel(
 token: str,
 channel_id: str,
 output_path: Path,
 format: str = "Json",
) -> bool:
 """
 Export Discord channel using DiscordChatExporter.Cli.
 
 Args:
 token: Discord authentication token
 channel_id: Channel ID to export
 output_path: Output file path
 format: Export format (Json, PlainText, HtmlDark, etc.)
 
 Returns:
 True if successful, False otherwise
 """
 if not EXPORTER_PATH.exists():
 print(f"❌ DiscordChatExporter.Cli not found at: {EXPORTER_PATH}")
 return False
 
 output_path.parent.mkdir(parents=True, exist_ok=True)
 
 cmd = [
 str(EXPORTER_PATH),
 "export",
 "--channel", channel_id,
 "--token", token,
 "--output", str(output_path),
 "--format", format,
 "--markdown", "True",
 ]
 
 print(f"Exporting Discord channel {channel_id}...")
 print(f"Output: {output_path}")
 print()
 
 try:
 result = subprocess.run(
 cmd,
 capture_output=True,
 text=True,
 check=True,
 )
 print(result.stdout)
 return True
 except subprocess.CalledProcessError as e:
 print(f"❌ Error exporting channel:")
 print(f" {e.stderr}")
 return False

def filter_cfb_messages(json_file: Path) -> list:
 """Filter messages from CFB's profile."""
 try:
 with json_file.open(encoding="utf-8") as f:
 data = json.load(f)
 
 # Find CFB's user ID (look for "Come-from-Beyond" or "VFB" in author names)
 cfb_user_id = None
 cfb_messages = []
 
 if "messages" in data:
 for message in data["messages"]:
 author = message.get("author", {})
 author_name = author.get("name", "").lower()
 author_id = author.get("id", "")
 
 # Check if this is CFB
 if any(keyword in author_name for keyword in ["come-from-beyond", "cfb", "vfb", "sergey"]):
 if cfb_user_id is None:
 cfb_user_id = author_id
 print(f"✅ Found CFB's profile: {author.get('name')} (ID: {author_id})")
 
 # Collect CFB's messages
 if author_id == cfb_user_id or (cfb_user_id is None and any(keyword in author_name for keyword in ["come-from-beyond", "cfb", "vfb"])):
 cfb_messages.append(message)
 
 return cfb_messages
 
 except Exception as e:
 print(f"❌ Error filtering messages: {e}")
 return []

def analyze_cfb_messages(messages: list) -> dict:
 """Analyze CFB messages for relevant keywords."""
 analysis = {
 "total_messages": len(messages),
 "keywords_found": {
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
 },
 "relevant_messages": [],
 }
 
 keywords = {
 "matrix": ["matrix", "anna", "anna-matrix"],
 "puzzle": ["puzzle", "riddle", "challenge"],
 "reward": ["reward", "prize", "treasure"],
 "contract": ["contract", "POCCZYCKTRQGHFIPWGSBLJTEQFDDVVBMNUHNCKMRACBGQOPBLURNRCBAFOBD"],
 "genesis": ["genesis", "asset", "token"],
 "26": ["26", "twenty-six"],
 "676": ["676", "six hundred seventy-six"],
 "128": ["128", "one hundred twenty-eight"],
 "block": ["block", "block-id"],
 "layer": ["layer", "seed", "identity"],
 }
 
 for msg in messages:
 content = msg.get("content", "").lower()
 timestamp = msg.get("timestamp", "")
 message_id = msg.get("id", "")
 
 relevant = False
 
 for category, terms in keywords.items():
 for term in terms:
 if term.lower() in content:
 analysis["keywords_found"][category].append({
 "message_id": message_id,
 "timestamp": timestamp,
 "preview": content[:200],
 })
 relevant = True
 
 if relevant:
 analysis["relevant_messages"].append({
 "id": message_id,
 "timestamp": timestamp,
 "content": msg.get("content", ""),
 })
 
 return analysis

def main() -> int:
 OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
 
 print("=" * 80)
 print("🔍 EXPORT CFB DISCORD MESSAGES")
 print("=" * 80)
 print()
 
 # Get credentials
 credentials = get_discord_credentials()
 
 if not credentials.get("token"):
 print("⚠️ Discord token not found in environment or config files")
 print()
 print("Please provide:")
 print(" 1. Discord Token (user token)")
 print(" 2. Channel ID for aigarth channel")
 print()
 print("You can set them as environment variables:")
 print(" export DISCORD_TOKEN='your_token_here'")
 print(" export DISCORD_CHANNEL_ID='channel_id_here'")
 print()
 print("Or create a config file at:")
 print(" ~/.discord_token (plain text, token on first line)")
 print(" or")
 print(" ~/.discord_config.json (JSON with 'token' and 'channel_id')")
 print()
 
 # Try interactive input
 token = input("Discord Token (or press Enter to skip): ").strip()
 if not token:
 return 1
 credentials["token"] = token
 
 channel_id = input("Aigarth Channel ID (or press Enter to skip): ").strip()
 if not channel_id:
 return 1
 credentials["channel_id"] = channel_id
 
 # Export channel
 temp_json = OUTPUT_DIR / "raw_export.json"
 
 if not export_discord_channel(
 token=credentials["token"],
 channel_id=credentials["channel_id"],
 output_path=temp_json,
 format="Json",
 ):
 return 1
 
 print()
 print("=" * 80)
 print("FILTERING CFB MESSAGES")
 print("=" * 80)
 print()
 
 # Filter CFB messages
 cfb_messages = filter_cfb_messages(temp_json)
 
 print(f"Found {len(cfb_messages)} messages from CFB")
 print()
 
 if not cfb_messages:
 print("⚠️ No CFB messages found. Check the export file manually.")
 return 1
 
 # Save filtered messages
 with OUTPUT_JSON.open("w", encoding="utf-8") as f:
 json.dump(cfb_messages, f, indent=2, ensure_ascii=False)
 
 print(f"✅ Saved {len(cfb_messages)} CFB messages to: {OUTPUT_JSON}")
 print()
 
 # Analyze messages
 print("=" * 80)
 print("ANALYZING MESSAGES")
 print("=" * 80)
 print()
 
 analysis = analyze_cfb_messages(cfb_messages)
 
 print(f"Total CFB messages: {analysis['total_messages']}")
 print()
 print("Keywords found:")
 for category, matches in analysis["keywords_found"].items():
 if matches:
 print(f" {category}: {len(matches)} matches")
 print()
 
 # Save analysis
 analysis_file = OUTPUT_DIR / "cfb_messages_analysis.json"
 with analysis_file.open("w", encoding="utf-8") as f:
 json.dump(analysis, f, indent=2, ensure_ascii=False)
 
 # Create markdown report
 with OUTPUT_MD.open("w", encoding="utf-8") as f:
 f.write("# CFB Discord Messages Analysis\n\n")
 f.write(f"**Total Messages:** {analysis['total_messages']}\n\n")
 
 f.write("## Keywords Found\n\n")
 for category, matches in analysis["keywords_found"].items():
 if matches:
 f.write(f"### {category.upper()} ({len(matches)} matches)\n\n")
 for match in matches[:10]: # First 10
 f.write(f"- **{match['timestamp']}**: {match['preview']}...\n")
 f.write("\n")
 
 f.write("## Relevant Messages\n\n")
 for msg in analysis["relevant_messages"][:20]: # First 20
 f.write(f"### {msg['timestamp']}\n\n")
 f.write(f"{msg['content']}\n\n")
 f.write("---\n\n")
 
 print(f"✅ Analysis saved to: {analysis_file}")
 print(f"✅ Markdown report: {OUTPUT_MD}")
 print()
 print("=" * 80)
 print("✅ EXPORT COMPLETE")
 print("=" * 80)
 
 return 0

if __name__ == "__main__":
 raise SystemExit(main())

