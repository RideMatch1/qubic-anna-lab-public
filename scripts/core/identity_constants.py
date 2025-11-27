"""Shared identity constants for consistency across the codebase.

This module provides a single source of truth for all identity definitions.
Import from here instead of defining identities in multiple places.
"""
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(project_root))

from analysis.utils.identity_tools import IDENTITY_BODY_LENGTH, IDENTITY_LENGTH

# Seed length (55 chars) - derived from identity body length
SEED_LENGTH = 55

# Diagonal identities (with valid checksums)
DIAGONAL_IDENTITIES = [
 "AQIOSQQMACYBPQXQSJNIUAYLMXXIWQOXQMEQYXBBTBONSJJRCWPXXDDRDWOR",
 "GWUXOMMMMFMTBWFZSNGMUKWBILTXQDKNMMMNYPEFTAMRONJMABLHTRRROHXZ",
 "ACGJGQQYILBPXDRBORFGWFZBBBNLQNGHDDELVLXXXLBNNNFBLLPBNNNLJIFV",
 "GIUVFGAWCBBFFKVBMFJESLHBBFBFWZWNNXCBQBBJRVFBNVJLTJBBBHTHKLDC",
]

# Vortex identities (with valid checksums)
VORTEX_IDENTITIES = [
 "UUFEEMUUBIYXYXDUXZCFBIHABAYSACQSWSGABOBKNXBZCICLYOKOBMLKMUAF",
 "HJBRFBHTBZJLVRBXTDRFORBWNACAHAQMSBUNBONHTRHNJKXKKNKHWCBNAXLD",
 "JKLMNOIPDQORWSICTWWUIYVMOFIQCQSYKMKACMOKQYCCMCOGOCQCSCWCDQFL",
 "XYZQAUBQUUQBQBYQAYEIYAQYMMEMQQQMMQSQEQAZSMOGWOXKIRMJXMCLFAVK",
]

# All identities combined
ALL_IDENTITIES = DIAGONAL_IDENTITIES + VORTEX_IDENTITIES

__all__ = [
 "DIAGONAL_IDENTITIES",
 "VORTEX_IDENTITIES",
 "ALL_IDENTITIES",
 "IDENTITY_BODY_LENGTH",
 "IDENTITY_LENGTH",
 "SEED_LENGTH",
]
