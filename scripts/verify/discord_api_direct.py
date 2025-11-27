#!/usr/bin/env python3
"""
Discord API Direct - Fast CFB Message Extraction

Uses Discord REST API directly to fetch messages in batches of 100,
filters CFB messages immediately, saves incrementally.

Much faster than DiscordChatExporter for our use case.
"""

from __future__ import annotations

import json
import os
import time
from pathlib import Path
from typing import List, Optional

try:
 import requests
 REQUESTS_AVAILABLE = True
except ImportError:
 REQUESTS_AVAILABLE = False
 print("⚠️ requests library not installed: pip install requests")

# Configuration
CFB_USER_ID = "395234579805503489"
# Channel ID will be set via environment variable or default to Aigarth
CHANNEL_ID = os.getenv("DISCORD_CHANNEL_ID", "768890598736003092")

OUTPUT_DIR = Path("outputs/derived/cfb_discord_messages")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

MESSAGES_FILE = OUTPUT_DIR / f"cfb_messages_channel_{CHANNEL_ID}.json"

# Discord API
DISCORD_API_BASE = "https://discord.com/api/v10"

def fetch_messages_batch(token: str, channel_id: str, before: Optional[str] = None, limit: int = 100) -> tuple[bool, List[dict], Optional[str]]:
 """
 Fetch a batch of messages from Discord API.
 Returns: (success, messages, last_message_id)
 """
 if not REQUESTS_AVAILABLE:
 return False, [], None
 
 url = f"{DISCORD_API_BASE}/channels/{channel_id}/messages"
 
 headers = {
 "Authorization": token,
 "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
 }
 
 params = {
 "limit": min(limit, 100), # Discord max is 100
 }
 
 if before:
 params["before"] = before
 
 try:
 response = requests.get(url, headers=headers, params=params, timeout=30)
 
 if response.status_code == 200:
 messages = response.json()
 last_id = messages[-1].get("id") if messages else None
 return True, messages, last_id
 
 elif response.status_code == 429:
 # Rate limited
 retry_after = float(response.headers.get("Retry-After", 5))
 print(f" ⏸️ Rate limited, waiting {retry_after:.1f}s...")
 time.sleep(retry_after)
 return False, [], None
 
 elif response.status_code == 401:
 print(f" ❌ Authentication failed - check token")
 return False, [], None
 
 else:
 error_text = response.text[:200] if response.text else "Unknown error"
 print(f" ⚠️ API Error {response.status_code}: {error_text}")
 return False, [], None
 
 except requests.exceptions.Timeout:
 print(f" ⏱️ Timeout")
 return False, [], None
 except Exception as e:
 print(f" ❌ Error: {e}")
 return False, [], None

def filter_cfb(messages: List[dict]) -> List[dict]:
 """Filter only CFB messages."""
 return [m for m in messages if m.get("author", {}).get("id") == CFB_USER_ID]

def load_existing() -> tuple[List[dict], Optional[str]]:
 """Load existing messages."""
 if MESSAGES_FILE.exists():
 try:
 with MESSAGES_FILE.open(encoding="utf-8") as f:
 messages = json.load(f)
 last_id = messages[-1].get("id") if messages else None
 return messages, last_id
 except Exception:
 pass
 return [], None

def save_messages(messages: List[dict]) -> List[dict]:
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
 print("🎯 DISCORD API DIRECT - Fast CFB Message Extraction")
 print("=" * 80)
 print()
 
 if not REQUESTS_AVAILABLE:
 print("❌ requests library not installed!")
 print(" Install: pip install requests")
 return 1
 
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
 print("📥 Starting from newest messages...")
 
 print()
 print("Starting fast extraction (Ctrl+C to stop, progress saved immediately)...")
 print()
 
 batch_num = 0
 consecutive_empty = 0
 max_empty = 100 # Continue even with many empty batches (CFB might not post for long periods)
 total_messages_scanned = 0
 max_batches = 500 # Safety limit: max 50,000 messages (should cover ~1450 CFB messages)
 
 try:
 while consecutive_empty < max_empty and batch_num < max_batches:
 batch_num += 1
 
 print(f"Batch {batch_num:3d} | ", end="", flush=True)
 
 # Fetch batch
 start_time = time.time()
 success, messages, new_last_id = fetch_messages_batch(
 token, CHANNEL_ID, before=last_id, limit=100
 )
 elapsed = time.time() - start_time
 
 if not success:
 print(f"❌ Failed ({elapsed:.1f}s)")
 consecutive_empty += 1
 if consecutive_empty >= 5:
 print(" ⚠️ Too many failures, stopping")
 break
 time.sleep(2)
 continue
 
 if not messages:
 print(f"0 messages | Channel exhausted ({elapsed:.1f}s)")
 break
 
 total_messages_scanned += len(messages)
 
 # Filter CFB
 batch_cfb = filter_cfb(messages)
 batch_size = len(batch_cfb)
 
 if batch_size == 0:
 consecutive_empty += 1
 print(f"0 CFB | Scanned: {total_messages_scanned} | Total CFB: {len(all_cfb)} | {elapsed:.1f}s")
 # Don't stop - CFB might not have posted for a while, but there are more messages
 # Only stop if we've scanned a LOT and found nothing
 else:
 consecutive_empty = 0 # Reset counter when we find CFB
 all_cfb.extend(batch_cfb)
 
 print(f"{batch_size:2d} CFB ✅ | Scanned: {total_messages_scanned} | Total CFB: {len(all_cfb)} | {elapsed:.1f}s")
 
 # Update last message ID (oldest in batch for pagination) - always update
 if messages:
 last_id = messages[-1].get("id")
 
 # Save immediately
 unique = save_messages(all_cfb)
 if len(unique) != len(all_cfb):
 print(f" (Removed {len(all_cfb) - len(unique)} duplicates)")
 
 # Progress update every 10 batches
 if batch_num % 10 == 0:
 progress_pct = (len(unique) / 1450 * 100) if len(unique) > 0 else 0
 print(f" 📊 Progress: {batch_num} batches, {total_messages_scanned} messages scanned, {len(unique)} CFB found ({progress_pct:.1f}% of ~1450)")
 
 # Only stop if we've scanned a huge amount and found nothing new for a very long time
 # Or if we've reached our target
 if len(unique) >= 1400: # Close to target
 print(f"\n 🎯 Close to target ({len(unique)}/1450), continuing...")
 elif consecutive_empty >= max_empty and total_messages_scanned > 10000:
 print(f"\n ⏸️ Scanned {total_messages_scanned} messages, {consecutive_empty} empty batches, stopping")
 break
 
 # Small delay to avoid rate limits
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
 print("✅ EXTRACTION COMPLETE")
 print("=" * 80)
 print(f"Batches: {batch_num}")
 print(f"CFB Messages: {len(unique)}")
 print(f"File: {MESSAGES_FILE}")
 print()
 
 if unique:
 print("Sample messages:")
 for i, msg in enumerate(unique[:3], 1):
 timestamp = msg.get("timestamp", "N/A")
 content = msg.get("content", "")[:80]
 print(f" {i}. [{timestamp}] {content}...")
 
 return 0

if __name__ == "__main__":
 raise SystemExit(main())

