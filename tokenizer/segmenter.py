"""
Module: segmenter.py
Purpose: Segment Khmer text into KCCs and identify typed lexical spans.
Usage: from tokenizer.segmenter import lex, segment_kcc
"""
from __future__ import annotations

import re
from dataclasses import dataclass

from tokenizer.constants import (
    COENG,
    DEPENDENT_VOWEL_RANGE,
    DIACRITIC_RANGE,
    KHMER_BASE_RANGE,
    KHMER_BLOCK_END,
    KHMER_BLOCK_START,
)

# ---------------------------------------------------------------------------
# kcc
# ---------------------------------------------------------------------------

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


# ---------------------------------------------------------------------------
# lexer
# ---------------------------------------------------------------------------

_TOKEN_PATTERN = re.compile(
    r"https?://[^\s]+|"
    r"(?:[A-Za-z0-9._%+-]+)@(?:[A-Za-z0-9.-]+\.[A-Za-z]{2,})|"
    r"\d+(?:\.\d+)?|"
    r"[០-៩]+(?:[.០-៩]+)*|"
    r"[A-Za-z]+(?:['-][A-Za-z]+)*"
)


@dataclass(frozen=True)
class LexSpan:
    """A typed text span produced by the pre-lexer."""

    text: str
    kind: str


def _is_khmer(character: str) -> bool:
    """Check whether a character belongs to the Khmer Unicode block."""
    codepoint = ord(character)
    return KHMER_BLOCK_START <= codepoint <= KHMER_BLOCK_END


def lex(text: str) -> list[LexSpan]:
    """Split text into Khmer, passthrough, whitespace, and punctuation spans."""
    spans: list[LexSpan] = []
    index = 0
    while index < len(text):
        match = _TOKEN_PATTERN.match(text, index)
        if match is not None:
            spans.append(LexSpan(match.group(), "passthrough"))
            index = match.end()
            continue
        if _is_khmer(text[index]):
            end = index + 1
            while end < len(text) and _is_khmer(text[end]):
                end += 1
            spans.append(LexSpan(text[index:end], "khmer"))
            index = end
            continue
        if text[index].isspace():
            end = index + 1
            while end < len(text) and text[end].isspace():
                end += 1
            spans.append(LexSpan(text[index:end], "whitespace"))
            index = end
            continue
        spans.append(LexSpan(text[index], "punctuation"))
        index += 1
    return spans


__all__ = ["LexSpan", "lex", "segment_kcc"]
