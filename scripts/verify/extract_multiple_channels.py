#!/usr/bin/env python3
"""
Extract CFB messages from multiple Discord channels.

Prioritized extraction:
1. Smart Contracts (highest priority)
2. Core Technology (high priority)
3. Dev (medium priority)
4. Price Discussion (low-medium, but CFB very active)
"""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

# Channel priorities
CHANNELS = {
 "smart_contracts": {
 "id": "1023173129071251467",
 "name": "Smart Contracts",
 "priority": 5,
 "description": "Directly relevant to puzzle contract",
 },
 "core_technology": {
 "id": "1301317725444116490",
 "name": "Core Technology",
 "priority": 4,
 "description": "Technical deep-dives, encoding methods",
 },
 "dev": {
 "id": "1087017597133922474",
 "name": "Dev",
 "priority": 3,
 "description": "Developer discussions",
 },
 "price_discussion": {
 "id": "1131698704240365759",
 "name": "Price Discussion",
 "priority": 2,
 "description": "CFB very active, might have hidden clues",
 },
}

SCRIPT_PATH = Path(__file__).parent / "discord_api_direct.py"
OUTPUT_DIR = Path("outputs/derived/cfb_discord_messages")

def extract_channel(channel_key: str, channel_info: dict) -> bool:
 """Extract CFB messages from a single channel."""
 channel_id = channel_info["id"]
 channel_name = channel_info["name"]
 
 print()
 print("=" * 80)
 print(f"📥 EXTRACTING: {channel_name}")
 print(f" Channel ID: {channel_id}")
 print(f" Description: {channel_info['description']}")
 print("=" * 80)
 print()
 
 # Set environment variables
 env = os.environ.copy()
 env["DISCORD_TOKEN"] = os.getenv("DISCORD_TOKEN", "")
 env["DISCORD_CHANNEL_ID"] = channel_id
 
 if not env["DISCORD_TOKEN"]:
 print("❌ DISCORD_TOKEN not set!")
 return False
 
 # Run extraction
 try:
 result = subprocess.run(
 [sys.executable, str(SCRIPT_PATH)],
 env=env,
 capture_output=True,
 text=True,
 timeout=3600, # 1 hour max per channel
 )
 
 if result.returncode == 0:
 print(f"✅ {channel_name} extraction complete")
 return True
 else:
 print(f"❌ {channel_name} extraction failed")
 print(result.stderr)
 return False
 
 except subprocess.TimeoutExpired:
 print(f"⏱️ {channel_name} extraction timed out")
 return False
 except Exception as e:
 print(f"❌ {channel_name} extraction error: {e}")
 return False

def main() -> int:
 """Main function."""
 print("=" * 80)
 print("🚀 MULTI-CHANNEL CFB MESSAGE EXTRACTION")
 print("=" * 80)
 print()
 
 # Check token
 token = os.getenv("DISCORD_TOKEN")
 if not token:
 print("❌ DISCORD_TOKEN not set!")
 print(" Set it with: export DISCORD_TOKEN='your_token'")
 return 1
 
 print(f"✅ Token: {token[:20]}...")
 print()
 
 # Sort channels by priority (highest first)
 sorted_channels = sorted(
 CHANNELS.items(),
 key=lambda x: x[1]["priority"],
 reverse=True
 )
 
 print("Extraction order:")
 for i, (key, info) in enumerate(sorted_channels, 1):
 print(f" {i}. {info['name']} (Priority: {info['priority']})")
 print()
 
 # Extract each channel
 results = {}
 for channel_key, channel_info in sorted_channels:
 success = extract_channel(channel_key, channel_info)
 results[channel_key] = {
 "success": success,
 "channel_id": channel_info["id"],
 "channel_name": channel_info["name"],
 }
 
 # Check results after each extraction
 if success:
 messages_file = OUTPUT_DIR / f"cfb_messages_channel_{channel_info['id']}.json"
 if messages_file.exists():
 import json
 with messages_file.open() as f:
 msgs = json.load(f)
 print(f" 📊 Found {len(msgs)} CFB messages")
 
 print()
 
 # Summary
 print("=" * 80)
 print("✅ EXTRACTION COMPLETE")
 print("=" * 80)
 print()
 print("Results:")
 for channel_key, result in results.items():
 status = "✅" if result["success"] else "❌"
 print(f" {status} {result['channel_name']}: {result['channel_id']}")
 
 return 0

if __name__ == "__main__":
 raise SystemExit(main())

