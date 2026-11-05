"""
Module: kcc.py
Purpose: Segment Khmer text into indivisible Khmer Character Clusters.
Usage: segment_kcc("ប្រទេស")
"""
from __future__ import annotations

from khmer_tokenizer.constants import (
    COENG,
    DEPENDENT_VOWEL_RANGE,
    DIACRITIC_RANGE,
    KHMER_BASE_RANGE,
)

_SHIFTERS = frozenset({"\u17cc", "\u17c9", "\u17ca"})


def _is_base(character: str) -> bool:
    """Check whether a character can begin a Khmer character cluster."""
    return ord(character) in KHMER_BASE_RANGE


def _is_cluster_mark(character: str) -> bool:
    """Check whether a character belongs to a cluster mark range."""
    codepoint = ord(character)
    return (
        character in _SHIFTERS
        or codepoint in DEPENDENT_VOWEL_RANGE
        or codepoint in DIACRITIC_RANGE
        or character == COENG
    )


def segment_kcc(text: str) -> list[str]:
    """Split Khmer text into clusters without breaking valid subscript units."""
    clusters: list[str] = []
    index = 0
    while index < len(text):
        if not _is_base(text[index]):
            clusters.append(text[index])
            index += 1
            continue

        cluster = [text[index]]
        index += 1
        while index < len(text):
            character = text[index]
            if _is_base(character):
                if cluster[-1] != COENG:
                    break
                cluster.append(character)
                index += 1
                continue
            if not _is_cluster_mark(character):
                break
            cluster.append(character)
            index += 1
        clusters.append("".join(cluster))
    return clusters