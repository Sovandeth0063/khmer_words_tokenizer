"""
Module: cleaner.py
Purpose: Remove invisible controls while preserving ZWSP boundary cues.
Usage: extract_boundary_cues(text)
"""
from __future__ import annotations

from dataclasses import dataclass

from khmer_tokenizer.constants import ZERO_WIDTH_CHARACTERS, ZWSP


@dataclass(frozen=True)
class CleanText:
    """Normalized text with boundary positions captured before cleanup."""

    text: str
    zwsp_positions: tuple[int, ...]


def extract_boundary_cues(
    text: str, zero_width_characters: frozenset[str] = ZERO_WIDTH_CHARACTERS
) -> CleanText:
    """Remove invisible controls and record ZWSP positions in cleaned text."""
    cleaned: list[str] = []
    positions: list[int] = []
    for character in text:
        if character == ZWSP:
            positions.append(len(cleaned))
        elif character not in zero_width_characters:
            cleaned.append(character)
    return CleanText("".join(cleaned), tuple(positions))