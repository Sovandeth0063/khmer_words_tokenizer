"""
Module: lexer.py
Purpose: Identify Khmer and passthrough spans before word segmentation.
Usage: lex("ប្រទេស 12.5 https://example.com")
"""
from __future__ import annotations

import re
from dataclasses import dataclass

from khmer_tokenizer.constants import KHMER_BLOCK_END, KHMER_BLOCK_START

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