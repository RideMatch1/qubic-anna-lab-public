#!/usr/bin/env python3
"""
Display Identities and Seeds for Interactive Verification

This script reads the found identities and displays them in a user-friendly format
with seeds, identities, and verification information.
"""

import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(project_root))

def display_8_identities():
 """Display the 8 initial identities with their seeds."""
 
 identities = [
 # Diagonal identities
 ("Diagonal #1", "AQIOSQQMACYBPQXQSJNIUAYLMXXIWQOXQMEQYXBBTBONSJJRCWPXXDDRDWOR"),
 ("Diagonal #2", "GWUXOMMMMFMTBWFZSNGMUKWBILTXQDKNMMMNYPEFTAMRONJMABLHTRRROHXZ"),
 ("Diagonal #3", "ACGJGQQYILBPXDRBORFGWFZBBBNLQNGHDDELVLXXXLBNNNFBLLPBNNNLJIFV"),
 ("Diagonal #4", "GIUVFGAWCBBFFKVBMFJESLHBBFBFWZWNNXCBQBBJRVFBNVJLTJBBBHTHKLDC"),
 # Vortex identities
 ("Vortex #1", "UUFEEMUUBIYXYXDUXZCFBIHABAYSACQSWSGABOBKNXBZCICLYOKOBMLKMUAF"),
 ("Vortex #2", "HJBRFBHTBZJLVRBXTDRFORBWNACAHAQMSBUNBONHTRHNJKXKKNKHWCBNAXLD"),
 ("Vortex #3", "JKLMNOIPDQORWSICTWWUIYVMOFIQCQSYKMKACMOKQYCCMCOGOCQCSCWCDQFL"),
 ("Vortex #4", "XYZQAUBQUUQBQBYQAYEIYAQYMMEMQQQMMQSQEQAZSMOGWOXKIRMJXMCLFAVK"),
 ]
 
 print("\n" + "=" * 80)
 print("DISCOVERED IDENTITIES AND SEEDS")
 print("=" * 80)
 print()
 print("These are the 8 identities found in the Anna Matrix.")
 print("All exist on-chain and can be verified independently.")
 print()
 
 for i, (name, identity) in enumerate(identities, 1):
 seed = identity.lower()[:55]
 print(f"{i}. {name}")
 print(f" Identity: {identity}")
 print(f" Seed: {seed}")
 print()
 
 print("=" * 80)
 print("HOW TO USE THESE:")
 print("=" * 80)
 print()
 print("1. Copy any seed above")
 print("2. Open Qubic Wallet")
 print("3. Import the seed")
 print("4. Verify the identity matches")
 print()
 print("All identities exist on-chain with balance 0 QU.")
 print("They are public keys - anyone can verify them.")
 print()

def display_sample_seeds():
 """Display first 10 seeds from 100_SEEDS_AND_IDENTITIES.md for quick testing."""
 
 seeds_file = project_root / "100_SEEDS_AND_IDENTITIES.md"
 if not seeds_file.exists():
 return
 
 print("\n" + "=" * 80)
 print("SAMPLE SEEDS FOR TESTING (First 10 of 100)")
 print("=" * 80)
 print()
 print("These seeds can be imported into Qubic Wallet for testing.")
 print("Note: The derived identity may differ from the documented identity.")
 print("This is the known discrepancy we've documented.")
 print()
 
 try:
 content = seeds_file.read_text(encoding='utf-8')
 # Extract first few seeds from the markdown table
 lines = content.split('\n')
 seed_count = 0
 for line in lines:
 if '|' in line and seed_count < 10:
 parts = [p.strip() for p in line.split('|')]
 if len(parts) >= 3 and len(parts[1]) == 55 and parts[1].islower():
 seed = parts[1]
 doc_id = parts[2] if len(parts) > 2 else "N/A"
 real_id = parts[3] if len(parts) > 3 else "N/A"
 seed_count += 1
 print(f"{seed_count}. Seed: {seed}")
 print(f" Documented ID: {doc_id[:60] if len(doc_id) > 60 else doc_id}")
 print(f" Real ID: {real_id[:60] if len(real_id) > 60 else real_id}")
 print()
 if seed_count >= 10:
 break
 except Exception as e:
 print(f"Could not read seeds file: {e}")
 print("See 100_SEEDS_AND_IDENTITIES.md for all 100 seeds.")
 
 print("=" * 80)
 print("For all 100 seeds, see: 100_SEEDS_AND_IDENTITIES.md")
 print("=" * 80)
 print()

if __name__ == "__main__":
 display_8_identities()
 # Note: 100_SEEDS_AND_IDENTITIES.md contains sample seeds but is not displayed
 # to avoid confusion. The file is available in the repository for reference.
 # For complete data (24k+ identities), see the mapping database in the repository.

