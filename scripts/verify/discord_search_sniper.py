#!/usr/bin/env python3
"""
Discord Search Sniper - Direct API Search for CFB Messages

Uses Discord's search API to directly find messages from a specific user.
Much faster than exporting entire channel.
"""

from __future__ import annotations

import json
import os
import time
from pathlib import Path
from typing import List, Optional

import requests

# Configuration
CFB_USER_ID = "395234579805503489"
CHANNEL_ID = "768890598736003092"
GUILD_ID = "768887649540243497"

OUTPUT_DIR = Path("outputs/derived/cfb_discord_messages")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

MESSAGES_FILE = OUTPUT_DIR / f"cfb_messages_channel_{CHANNEL_ID}.json"

# Discord API endpoints
DISCORD_API_BASE = "https://discord.com/api/v10"
SEARCH_ENDPOINT = f"{DISCORD_API_BASE}/guilds/{GUILD_ID}/messages/search"

def search_discord_messages(token: str, author_id: str, channel_id: str, offset: int = 0) -> Optional[dict]:
 """
 Search Discord messages using the search API.
 
 Note: Discord's search API has limitations and may require different approach.
 This is a fallback that uses message history with filtering.
 """
 headers = {
 "Authorization": token,
 "Content-Type": "application/json",
 "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
 }
 
 # Discord search API endpoint (may not work for user search directly)
 # Fallback: Use messages endpoint with filtering
 url = f"{DISCORD_API_BASE}/channels/{channel_id}/messages"
 
 params = {
 "limit": 100, # Max 100 per request
 }
 
 if offset > 0:
 # Use before parameter for pagination
 params["before"] = str(offset)
 
 try:
 response = requests.get(url, headers=headers, params=params, timeout=30)
 
 if response.status_code == 200:
 return response.json()
 elif response.status_code == 429:
 # Rate limited
 retry_after = int(response.headers.get("Retry-After", 5))
 print(f" ⏸️ Rate limited, waiting {retry_after}s...")
 time.sleep(retry_after)
 return None
 else:
 print(f" ⚠️ API Error {response.status_code}: {response.text[:100]}")
 return None
 
 except Exception as e:
 print(f" ❌ Request error: {e}")
 return None

def filter_cfb_messages(messages: List[dict]) -> List[dict]:
 """Filter only CFB messages."""
 return [m for m in messages if m.get("author", {}).get("id") == CFB_USER_ID]

def load_existing() -> tuple[List[dict], Optional[str]]:
 """Load existing messages and last message ID."""
 if MESSAGES_FILE.exists():
 try:
 with MESSAGES_FILE.open(encoding="utf-8") as f:
 messages = json.load(f)
 last_id = messages[-1].get("id") if messages else None
 return messages, last_id
 except Exception:
 pass
 return [], None

def save_messages(messages: List[dict]):
 """Save messages, removing duplicates."""
 seen = set()
 unique = []
 for msg in messages:
 msg_id = msg.get("id")
 if msg_id and msg_id not in seen:
 seen.add(msg_id)
 unique.append(msg)
 
 with MESSAGES_FILE.open("w", encoding="utf-8") as f:
 json.dump(unique, f, indent=2, ensure_ascii=False)
 
 return unique

def main() -> int:
 """Main function."""
 print("=" * 80)
 print("🎯 DISCORD SEARCH SNIPER - Direct CFB Message Search")
 print("=" * 80)
 print()
 
 token = os.getenv("DISCORD_TOKEN")
 if not token:
 print("❌ DISCORD_TOKEN not set!")
 return 1
 
 print(f"✅ Token: {token[:20]}...")
 print(f"📁 Channel: {CHANNEL_ID}")
 print(f"👤 CFB ID: {CFB_USER_ID}")
 print()
 
 # Load existing
 all_cfb, last_id = load_existing()
 if all_cfb:
 print(f"📥 Resuming: {len(all_cfb)} CFB messages already saved")
 if last_id:
 print(f"📌 Last message ID: {last_id}")
 else:
 print("📥 Starting new search...")
 
 print()
 print("Starting search (Ctrl+C to stop, progress saved immediately)...")
 print()
 
 batch_num = 0
 consecutive_empty = 0
 max_empty = 10
 
 try:
 while consecutive_empty < max_empty:
 batch_num += 1
 offset = int(last_id) if last_id else 0
 
 print(f"Batch {batch_num:3d} | ", end="", flush=True)
 
 # Search messages
 start_time = time.time()
 messages = search_discord_messages(token, CFB_USER_ID, CHANNEL_ID, offset=offset)
 elapsed = time.time() - start_time
 
 if not messages:
 print(f"❌ No messages ({elapsed:.1f}s)")
 consecutive_empty += 1
 if consecutive_empty >= 3:
 break
 time.sleep(1)
 continue
 
 if not isinstance(messages, list):
 messages = []
 
 if not messages:
 print(f"0 messages | Stopping")
 break
 
 # Filter CFB
 batch_cfb = filter_cfb_messages(messages)
 batch_size = len(batch_cfb)
 
 if batch_size == 0:
 consecutive_empty += 1
 print(f"0 CFB | Total: {len(all_cfb)} | {elapsed:.1f}s")
 else:
 consecutive_empty = 0
 all_cfb.extend(batch_cfb)
 
 # Update last message ID (oldest in batch for pagination)
 if batch_cfb:
 last_id = batch_cfb[-1].get("id")
 
 print(f"{batch_size:2d} CFB ✅ | Total: {len(all_cfb)} | {elapsed:.1f}s")
 
 # Save immediately
 unique = save_messages(all_cfb)
 if len(unique) != len(all_cfb):
 print(f" (Removed {len(all_cfb) - len(unique)} duplicates)")
 
 # Small delay
 time.sleep(0.5)
 
 except KeyboardInterrupt:
 print("\n\n⚠️ Interrupted")
 unique = save_messages(all_cfb)
 print(f"✅ Saved: {len(unique)} unique CFB messages from {batch_num} batches")
 return 0
 
 except Exception as e:
 print(f"\n❌ Error: {e}")
 import traceback
 traceback.print_exc()
 save_messages(all_cfb)
 return 1
 
 unique = save_messages(all_cfb)
 
 print()
 print("=" * 80)
 print("✅ SEARCH COMPLETE")
 print("=" * 80)
 print(f"Batches: {batch_num}")
 print(f"CFB Messages: {len(unique)}")
 print(f"File: {MESSAGES_FILE}")
 
 return 0

if __name__ == "__main__":
 raise SystemExit(main())

