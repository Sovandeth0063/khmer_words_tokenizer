"""
Module: constants.py
Purpose: Define shared Khmer Unicode ranges, controls, and tokenizer tags.
Usage: from tokenizer.constants import BIES_TAGS
"""
from __future__ import annotations

from typing import Final

# Unicode range containing Khmer letters, marks, punctuation, and signs.
KHMER_BLOCK_START: Final[int] = 0x1780
KHMER_BLOCK_END: Final[int] = 0x17FF
# Unicode range containing Khmer Symbols such as calendar and numeric signs.
KHMER_SYMBOLS_START: Final[int] = 0x19E0
KHMER_SYMBOLS_END: Final[int] = 0x19FF

# Coeng joins a Khmer consonant to a following subscript consonant.
COENG: Final[str] = "\u17d2"
# ZWSP can indicate a user-provided word boundary before normalization.
ZWSP: Final[str] = "\u200b"
# Invisible characters removed during cleanup.
ZERO_WIDTH_CHARACTERS: Final[frozenset[str]] = frozenset(
    {"\u200b", "\u200c", "\u200d", "\ufeff"}
)

# Khmer sentence terminators kept as boundaries but removed from token output.
KHMER_SENTENCE_MARKS: Final[frozenset[str]] = frozenset({"\u17d4", "\u17d5"})

# BIES labels used later by the word-boundary prediction model.
BIES_TAGS: Final[tuple[str, ...]] = ("B", "I", "E", "S")
# Subranges used to identify Khmer cluster components.
KHMER_BASE_RANGE: Final[range] = range(0x1780, 0x17B4)
DEPENDENT_VOWEL_RANGE: Final[range] = range(0x17B6, 0x17C6)
DIACRITIC_RANGE: Final[range] = range(0x17C6, 0x17D2)