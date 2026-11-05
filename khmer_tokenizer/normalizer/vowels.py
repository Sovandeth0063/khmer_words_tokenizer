"""
Module: vowels.py
Purpose: Apply Khmer vowel replacements and register-shifter corrections.
Usage: apply_character_replacements(text, replacements)
"""
from __future__ import annotations

from typing import Mapping


def apply_character_replacements(
    text: str, replacements: Mapping[str, str]
) -> str:
    """Apply configured literal replacements in one deterministic pass."""
    for source, target in replacements.items():
        text = text.replace(source, target)
    return text


def resolve_shifter_collision(
    text: str,
    *,
    source: str,
    upper_vowels: set[str],
    muusikatoan_bases: set[str],
    triisap_bases: set[str],
) -> str:
    """Resolve a mistyped shifter using the preceding base and upper vowel."""
    characters = list(text)
    for index, character in enumerate(characters):
        if character != source or index == 0:
            continue
        previous = characters[index - 1]
        following = characters[index + 1] if index + 1 < len(characters) else ""
        if following not in upper_vowels:
            continue
        if previous in triisap_bases:
            characters[index] = "\u17ca"
        elif previous in muusikatoan_bases:
            characters[index] = "\u17c9"
    return "".join(characters)