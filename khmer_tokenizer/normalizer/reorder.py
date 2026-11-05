"""
Module: reorder.py
Purpose: Reorder Khmer cluster marks without detaching Coeng or vowels.
Usage: reorder_khmer_clusters(text)
"""
from __future__ import annotations

from khmer_tokenizer.constants import (
    COENG,
    DEPENDENT_VOWEL_RANGE,
    DIACRITIC_RANGE,
    KHMER_BASE_RANGE,
)


def _is_base(character: str) -> bool:
    return ord(character) in KHMER_BASE_RANGE


def _mark_order(character: str) -> int:
    codepoint = ord(character)
    if character in {"\u17cc", "\u17c9", "\u17ca"}:
        return 0
    if character == COENG or _is_base(character):
        return 1
    if codepoint in DEPENDENT_VOWEL_RANGE:
        return 2
    if codepoint in DIACRITIC_RANGE or character in {"\u17d3", "\u17dd"}:
        return 3
    return 4


def reorder_khmer_clusters(text: str) -> str:
    """Place Khmer cluster marks in the documented stable canonical order."""
    output: list[str] = []
    pending_marks: list[str] = []
    index = 0
    while index < len(text):
        if not _is_base(text[index]):
            if _mark_order(text[index]) < 4:
                pending_marks.append(text[index])
            else:
                output.extend(pending_marks)
                pending_marks.clear()
                output.append(text[index])
            index += 1
            continue

        base = text[index]
        marks = pending_marks
        pending_marks = []
        index += 1
        while index < len(text):
            if _is_base(text[index]):
                if not marks or marks[-1] != COENG:
                    break
                marks.append(text[index])
                index += 1
                continue
            if _mark_order(text[index]) < 4:
                marks.append(text[index])
            else:
                break
            index += 1
        output.append(base)
        output.extend(
            character
            for _, character in sorted(
                enumerate(marks),
                key=lambda item: (_mark_order(item[1]), item[0]),
            )
        )
    output.extend(pending_marks)
    return "".join(output)