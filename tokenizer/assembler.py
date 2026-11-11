"""
Module: assembler.py
Purpose: Reconstruct lexical words from KCCs and BIES tags.
Usage: assemble_tokens(kccs, tags)
"""
from __future__ import annotations

from typing import Final

from tokenizer.constants import KHMER_SENTENCE_MARKS
from tokenizer.segmenter import segment_kcc
from tokenizer.trie import Trie

# Multi-word phrases listed in the dictionary that default CRF keeps split.
_DEFAULT_SPLIT_PHRASES: Final[frozenset[str]] = frozenset({"ប្រទេសកម្ពុជា"})


def assemble_tokens(kccs: list[str], tags: list[str]) -> list[str]:
    """Join KCCs according to BIES tags without dropping invalid input."""
    if len(kccs) != len(tags):
        raise ValueError("KCC and BIES sequences must have equal length")
    tokens: list[str] = []
    current: list[str] = []
    for kcc, tag in zip(kccs, tags):
        if tag == "S":
            if current:
                tokens.append("".join(current))
                current = []
            tokens.append(kcc)
        elif tag == "B":
            if current:
                tokens.append("".join(current))
            current = [kcc]
        elif tag == "I":
            if current:
                current.append(kcc)
            else:
                tokens.append(kcc)
        elif tag == "E":
            if current:
                current.append(kcc)
                tokens.append("".join(current))
                current = []
            else:
                tokens.append(kcc)
        else:
            raise ValueError(f"Unknown BIES tag: {tag}")
    if current:
        tokens.append("".join(current))
    return tokens


def apply_maximum(
    tokens: list[str],
    trie: Trie,
    split_phrases: frozenset[str] = _DEFAULT_SPLIT_PHRASES,
) -> list[str]:
    """Merge adjacent tokens into the longest matching dictionary word."""
    merged: list[str] = []
    index = 0
    while index < len(tokens):
        best_end = index + 1
        candidate = tokens[index]
        if candidate and not candidate.isspace() and trie.lookup(candidate)[0]:
            for end in range(index + 2, len(tokens) + 1):
                part = tokens[end - 1]
                if not part or part.isspace():
                    break
                candidate += part
                is_prefix, is_word = trie.lookup(candidate)
                if not is_prefix:
                    break
                if not is_word:
                    continue
                if candidate in split_phrases and candidate not in trie.custom_words:
                    continue
                clusters = segment_kcc(candidate)
                if not trie.is_forced_split(clusters, 0, len(clusters)):
                    best_end = end
        merged.append("".join(tokens[index:best_end]))
        index = best_end
    return merged


def drop_sentence_marks(tokens: list[str]) -> list[str]:
    """Remove standalone Khmer sentence marks from token output."""
    return [token for token in tokens if token not in KHMER_SENTENCE_MARKS]
