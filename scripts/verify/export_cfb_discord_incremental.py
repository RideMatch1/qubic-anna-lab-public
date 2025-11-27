#!/usr/bin/env python3
"""
Incremental CFB Discord Message Exporter

Exports only CFB's messages with incremental saving.
Can be interrupted and resumed without losing progress.

CFB User ID: 395234579805503489
Channel: 768890598736003092 (aigarth)
"""

from __future__ import annotations

import json
import os
import subprocess
import time
from pathlib import Path
from typing import Optional

# Configuration
CFB_USER_ID = "395234579805503489"
CHANNEL_ID = "768890598736003092"
GUILD_ID = "768887649540243497"

# Paths
EXPORTER_PATH = Path(os.getenv("DISCORD_EXPORTER_PATH", "DiscordChatExporter.Cli"))
OUTPUT_DIR = Path("outputs/derived/cfb_discord_messages")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# State files
STATE_FILE = OUTPUT_DIR / "export_state.json"
MESSAGES_FILE = OUTPUT_DIR / f"cfb_messages_channel_{CHANNEL_ID}.json"
PROGRESS_FILE = OUTPUT_DIR / "export_progress.txt"

def load_state() -> dict:
 """Load export state (resume support)."""
 if STATE_FILE.exists():
 try:
 with STATE_FILE.open() as f:
 return json.load(f)
 except Exception:
 pass
 return {
 "last_message_id": None,
 "total_messages": 0,
 "batches_completed": 0,
 "start_time": time.time(),
 }

def save_state(state: dict):
 """Save export state."""
 state["last_update"] = time.time()
 with STATE_FILE.open("w") as f:
 json.dump(state, f, indent=2)

def load_existing_messages() -> list:
 """Load already exported messages."""
 if MESSAGES_FILE.exists():
 try:
 with MESSAGES_FILE.open(encoding="utf-8") as f:
 return json.load(f)
 except Exception:
 pass
 return []

def save_messages(messages: list):
 """Save messages incrementally."""
 with MESSAGES_FILE.open("w", encoding="utf-8") as f:
 json.dump(messages, f, indent=2, ensure_ascii=False)

def update_progress(state: dict, batch_size: int):
 """Update progress file."""
 elapsed = time.time() - state["start_time"]
 rate = state["total_messages"] / elapsed if elapsed > 0 else 0
 
 with PROGRESS_FILE.open("w") as f:
 f.write(f"CFB Discord Export Progress\n")
 f.write(f"{'=' * 60}\n\n")
 f.write(f"Batches completed: {state['batches_completed']}\n")
 f.write(f"Total CFB messages: {state['total_messages']}\n")
 f.write(f"Last message ID: {state.get('last_message_id', 'N/A')}\n")
 f.write(f"Elapsed time: {elapsed:.1f}s\n")
 f.write(f"Rate: {rate:.1f} messages/sec\n")
 f.write(f"Last batch size: {batch_size}\n")

def export_channel_json(
 token: str,
 channel_id: str,
 output_file: Path,
 after: Optional[str] = None,
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
 
 try:
 result = subprocess.run(
 cmd,
 capture_output=True,
 text=True,
 check=True,
 timeout=120, # 2 minutes per batch
 )
 return True
 except subprocess.TimeoutExpired:
 print(f"⏱️ Timeout")
 return False
 except subprocess.CalledProcessError as e:
 if "429" in e.stderr or "rate limit" in e.stderr.lower():
 print(f"⏸️ Rate limited, waiting...")
 time.sleep(5)
 return False
 print(f"❌ Error: {e.stderr[:100]}")
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
 if author.get("id") == CFB_USER_ID:
 cfb_messages.append(msg)
 
 return cfb_messages
 except Exception as e:
 print(f"❌ Error filtering: {e}")
 return []

def main() -> int:
 """Main export function with incremental saving."""
 
 print("=" * 80)
 print("🚀 INCREMENTAL CFB DISCORD MESSAGE EXPORTER")
 print("=" * 80)
 print()
 
 # Get token
 token = os.getenv("DISCORD_TOKEN")
 if not token:
 print("❌ DISCORD_TOKEN environment variable not set!")
 return 1
 
 print(f"✅ Token found (length: {len(token)})")
 print(f"📁 Channel: {CHANNEL_ID}")
 print(f"👤 CFB User ID: {CFB_USER_ID}")
 print()
 
 # Load state and existing messages
 state = load_state()
 all_messages = load_existing_messages()
 
 if state["batches_completed"] > 0:
 print(f"📥 Resuming export...")
 print(f" Already have {len(all_messages)} messages from {state['batches_completed']} batches")
 print(f" Last message ID: {state.get('last_message_id', 'N/A')}")
 print()
 else:
 print(f"📥 Starting new export...")
 print()
 
 batch_num = state["batches_completed"]
 consecutive_empty = 0
 max_consecutive_empty = 3 # Stop after 3 empty batches
 
 print("Starting export (press Ctrl+C to stop, progress will be saved)...")
 print()
 
 try:
 while True:
 batch_num += 1
 temp_file = OUTPUT_DIR / f"batch_{batch_num}_temp.json"
 
 print(f"Batch {batch_num:4d} | ", end="", flush=True)
 
 # Export batch
 success = export_channel_json(
 token=token,
 channel_id=CHANNEL_ID,
 output_file=temp_file,
 after=state.get("last_message_id"),
 )
 
 if not success:
 print("❌ Export failed, retrying...")
 time.sleep(2)
 continue
 
 # Filter CFB messages
 batch_cfb = filter_cfb_messages(temp_file)
 batch_size = len(batch_cfb)
 
 if batch_size == 0:
 consecutive_empty += 1
 print(f"✅ (0 CFB) | Total: {len(all_messages)}")
 
 # Check if channel is exhausted
 try:
 with temp_file.open(encoding="utf-8") as f:
 data = json.load(f)
 if not data.get("messages"):
 print()
 print("✅ No more messages in channel")
 break
 except Exception:
 pass
 
 if consecutive_empty >= max_consecutive_empty:
 print()
 print(f"✅ No CFB messages in last {max_consecutive_empty} batches, stopping")
 break
 else:
 consecutive_empty = 0
 all_messages.extend(batch_cfb)
 state["total_messages"] = len(all_messages)
 
 # Update last message ID
 if batch_cfb:
 state["last_message_id"] = batch_cfb[-1].get("id")
 
 print(f"✅ ({batch_size:3d} CFB) | Total: {len(all_messages)}")
 
 # Save incrementally
 save_messages(all_messages)
 state["batches_completed"] = batch_num
 save_state(state)
 update_progress(state, batch_size)
 
 # Cleanup temp file
 temp_file.unlink(missing_ok=True)
 
 # Small delay to avoid rate limits
 time.sleep(0.5)
 
 except KeyboardInterrupt:
 print()
 print()
 print("⚠️ Interrupted by user")
 print(f"✅ Progress saved: {len(all_messages)} messages from {batch_num} batches")
 save_messages(all_messages)
 save_state(state)
 return 0
 
 except Exception as e:
 print()
 print(f"❌ Error: {e}")
 save_messages(all_messages)
 save_state(state)
 return 1
 
 # Final save
 save_messages(all_messages)
 state["batches_completed"] = batch_num
 save_state(state)
 
 print()
 print("=" * 80)
 print("✅ EXPORT COMPLETE")
 print("=" * 80)
 print()
 print(f"Total batches: {batch_num}")
 print(f"Total CFB messages: {len(all_messages)}")
 print(f"Saved to: {MESSAGES_FILE}")
 print()
 
 # Create summary
 if all_messages:
 timestamps = [msg.get("timestamp", "") for msg in all_messages if msg.get("timestamp")]
 if timestamps:
 print(f"Date range: {min(timestamps)} to {max(timestamps)}")
 
 return 0

if __name__ == "__main__":
 raise SystemExit(main())

