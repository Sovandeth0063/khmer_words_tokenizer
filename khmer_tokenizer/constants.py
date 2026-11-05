"""
Module: constants.py
Purpose: Define shared Khmer Unicode ranges, controls, and tokenizer tags.
Usage: from khmer_tokenizer.constants import BIES_TAGS
"""
from __future__ import annotations

from typing import Final

KHMER_BLOCK_START: Final[int] = 0x1780
KHMER_BLOCK_END: Final[int] = 0x17FF
KHMER_SYMBOLS_START: Final[int] = 0x19E0
KHMER_SYMBOLS_END: Final[int] = 0x19FF

COENG: Final[str] = "\u17d2"
ZWSP: Final[str] = "\u200b"
ZERO_WIDTH_CHARACTERS: Final[frozenset[str]] = frozenset(
    {"\u200b", "\u200c", "\u200d", "\ufeff"}
)

BIES_TAGS: Final[tuple[str, ...]] = ("B", "I", "E", "S")
KHMER_BASE_RANGE: Final[range] = range(0x1780, 0x17B4)
DEPENDENT_VOWEL_RANGE: Final[range] = range(0x17B6, 0x17C6)
DIACRITIC_RANGE: Final[range] = range(0x17C6, 0x17D2)