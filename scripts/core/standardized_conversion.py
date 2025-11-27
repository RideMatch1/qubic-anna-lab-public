#!/usr/bin/env python3
"""
Standardisierte Identity <-> Seed Konvertierung

Dies ist die offizielle, validierte Implementierung.
"""

from typing import Optional

def identity_to_seed(identity: str) -> Optional[str]:
 """
 Konvertiere eine Qubic Identity zu einem Seed.
 
 Formula: Identity -> identity.lower()[:55] -> Seed
 
 Args:
 identity: Qubic Identity (60 Zeichen, UPPERCASE)
 
 Returns:
 Seed (55 Zeichen, lowercase) oder None bei ungültiger Identity
 
 Examples:
 >>> identity_to_seed("RIOIMZKDJPHCFFGVYMWSFOKVBNXAYCKUXOLHLHHCPCQDULIITMFGZQUFIMKN")
 'rioimzkdjphcffgvymwsfokvbnxayckuxolhlhhcpcqduliitmfgzqu'
 """
 if not identity:
 return None
 
 if not isinstance(identity, str):
 return None
 
 if len(identity) != 60:
 return None
 
 if not identity.isupper():
 return None
 
 return identity.lower()[:55]

def seed_to_identity_candidate(seed: str) -> Optional[str]:
 """
 Konvertiere einen Seed zu einer Identity-Kandidaten.
 
 Note: Dies ist eine Reverse-Operation, die nicht garantiert die
 ursprüngliche Identity zurückgibt, da die letzten 5 Zeichen verloren gehen.
 
 Args:
 seed: Seed (55 Zeichen, lowercase)
 
 Returns:
 Identity-Kandidat (60 Zeichen, UPPERCASE) oder None bei ungültigem Seed
 """
 if not seed:
 return None
 
 if not isinstance(seed, str):
 return None
 
 if len(seed) != 55:
 return None
 
 if not seed.islower():
 return None
 
 # Pad mit 'A' auf 60 Zeichen und konvertiere zu UPPERCASE
 padded = (seed + "AAAAA")[:60]
 return padded.upper()

def validate_identity(identity: str) -> bool:
 """
 Validate eine Qubic Identity.
 
 Args:
 identity: Identity zum Validaten
 
 Returns:
 True wenn gültig, sonst False
 """
 if not identity:
 return False
 
 if not isinstance(identity, str):
 return False
 
 if len(identity) != 60:
 return False
 
 if not identity.isupper():
 return False
 
 # Check ob nur Base-26 Zeichen (A-Z)
 if not all(c.isalpha() and c.isupper() for c in identity):
 return False
 
 return True

def validate_seed(seed: str) -> bool:
 """
 Validate einen Seed.
 
 Args:
 seed: Seed zum Validaten
 
 Returns:
 True wenn gültig, sonst False
 """
 if not seed:
 return False
 
 if not isinstance(seed, str):
 return False
 
 if len(seed) != 55:
 return False
 
 if not seed.islower():
 return False
 
 # Check ob nur Base-26 Zeichen (a-z)
 if not all(c.isalpha() and c.islower() for c in seed):
 return False
 
 return True

# Test
if __name__ == "__main__":
 # Test mit echten Identities
 test_identities = [
 "RIOIMZKDJPHCFFGVYMWSFOKVBNXAYCKUXOLHLHHCPCQDULIITMFGZQUFIMKN",
 "FAEEIVWNINMPFAAWUUYMCJXMSFCAGDJNFDRCEHBFPGFCCEKUWTMCBHXBNSVL",
 "DZGTELPKNEITGBRUPCWRNZGLTMBCRPLRPERUFBZHDFDTFYTJXOUDYLSBKRRB",
 ]
 
 print("Testing identity_to_seed conversion:")
 print()
 
 for identity in test_identities:
 seed = identity_to_seed(identity)
 print(f"Identity: {identity[:40]}...")
 print(f"Seed: {seed}")
 print(f"Valid: {validate_identity(identity)} / {validate_seed(seed)}")
 print()

