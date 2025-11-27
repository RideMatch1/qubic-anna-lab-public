#!/usr/bin/env python3
"""
Export CFB Messages from Multiple Channels

Exports only CFB's messages (User ID: 395234579805503489) from multiple channels.
"""

from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path
from typing import List

# Configuration
CFB_USER_ID = "395234579805503489"

# Channels to export
CHANNELS = [
 {
 "name": "aigarth",
 "channel_id": "768890598736003092",
 "guild_id": "768887649540243497",
 "url": "https://discord.com/channels/768887649540243497/768890598736003092",
 },
 # Add more channels here as needed
 # {
 # "name": "channel_name",
 # "channel_id": "CHANNEL_ID",
 # "guild_id": "GUILD_ID",
 # "url": "https://discord.com/channels/GUILD_ID/CHANNEL_ID",
 # },
]

EXPORTER_PATH = Path("${DISCORD_EXPORTER_DIR}/DiscordChatExporter.Cli")
OUTPUT_DIR = Path("outputs/derived/cfb_discord_messages")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

def get_discord_token() -> str:
 """Get Discord token from environment or config."""
 token = os.getenv("DISCORD_TOKEN")
 
 if not token:
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
 
 if not token:
 raise ValueError("Discord token not found! Set DISCORD_TOKEN or create ~/.discord_token")
 
 return token

def export_channel_json(token: str, channel_id: str, output_file: Path) -> bool:
 """Export channel to JSON."""
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
 
 try:
 subprocess.run(cmd, capture_output=True, text=True, check=True, timeout=300)
 return True
 except Exception as e:
 print(f"❌ Export error: {e}")
 return False

def filter_cfb_messages(json_file: Path) -> List[dict]:
 """Filter messages from CFB's user ID."""
 try:
 with json_file.open(encoding="utf-8") as f:
 data = json.load(f)
 
 cfb_messages = []
 if "messages" in data:
 for msg in data["messages"]:
 author = msg.get("author", {})
 if author.get("id") == CFB_USER_ID:
 cfb_messages.append(msg)
 
 return cfb_messages
 except Exception as e:
 print(f"❌ Error filtering: {e}")
 return []

def main():
 """Export CFB messages from all configured channels."""
 
 print("=" * 80)
 print("🚀 CFB DISCORD MESSAGE EXPORTER - ALL CHANNELS")
 print("=" * 80)
 print()
 
 token = get_discord_token()
 print(f"✅ Token found (length: {len(token)})")
 print()
 
 all_messages = []
 
 for channel in CHANNELS:
 print(f"📥 Exporting: {channel['name']} ({channel['channel_id']})")
 
 temp_file = OUTPUT_DIR / f"temp_{channel['name']}.json"
 
 if export_channel_json(token, channel['channel_id'], temp_file):
 cfb_messages = filter_cfb_messages(temp_file)
 print(f" ✅ Found {len(cfb_messages)} CFB messages")
 all_messages.extend(cfb_messages)
 temp_file.unlink(missing_ok=True)
 else:
 print(f" ❌ Export failed")
 
 print()
 print(f"✅ Total CFB messages: {len(all_messages)}")
 
 # Save all messages
 output_file = OUTPUT_DIR / "cfb_all_messages.json"
 with output_file.open("w", encoding="utf-8") as f:
 json.dump(all_messages, f, indent=2, ensure_ascii=False)
 
 print(f"💾 Saved to: {output_file}")
 
 return 0

if __name__ == "__main__":
 raise SystemExit(main())

