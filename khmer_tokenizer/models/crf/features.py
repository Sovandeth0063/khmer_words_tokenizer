"""
Module: features.py
Purpose: Extract KCC context and lexicon features for BIES prediction.
Usage: extract_features(kccs, trie)
"""
from __future__ import annotations

from typing import Optional

from khmer_tokenizer.constants import COENG, DEPENDENT_VOWEL_RANGE
from khmer_tokenizer.models.trie import Trie

_FIRST_SERIES = frozenset("កខចឆដឋតថបផសហឡអ")


def _has_dependent_vowel(kcc: str) -> bool:
    """Check whether a KCC contains a dependent vowel."""
    return any(ord(character) in DEPENDENT_VOWEL_RANGE for character in kcc)


def _base_series(kcc: str) -> str:
    """Return the configured consonant-series label for a KCC."""
    if not kcc or not (0x1780 <= ord(kcc[0]) <= 0x17B3):
        return "none"
    return "first" if kcc[0] in _FIRST_SERIES else "second"


def extract_features(
    kccs: list[str],
    trie: Optional[Trie] = None,
    zwsp_positions: tuple[int, ...] = (),
) -> list[dict[str, str]]:
    """Extract context, orthographic, Trie, and ZWSP features for each KCC."""
    features: list[dict[str, str]] = []
    for index, kcc in enumerate(kccs):
        current: dict[str, str] = {
            "kcc": kcc,
            "kcc.lower": kcc.lower(),
            "has_coeng": str(COENG in kcc),
            "has_vowel": str(_has_dependent_vowel(kcc)),
            "base_series": _base_series(kcc),
            "has_closing_sign": str(any(
                character in {"\u17cb", "\u17cd"} for character in kcc
            )),
            "zwsp_before": str(index in zwsp_positions),
        }
        for offset in range(-3, 4):
            position = index + offset
            current[f"kcc[{offset}]"] = (
                kccs[position] if 0 <= position < len(kccs) else "__BOS__"
            )
        current["bigram.prev"] = (
            f"{kccs[index - 1]}|{kcc}" if index else "__BOS__"
        )
        current["trigram"] = (
            f"{kccs[index - 1]}|{kcc}|{kccs[index + 1]}"
            if 0 < index < len(kccs) - 1
            else "__EDGE__"
        )
        if trie is not None:
            current["match.forward"] = str(trie.longest_match(kccs, index))
            current["match.backward"] = str(
                max(
                    (
                        index - start + 1
                        for start in range(index + 1)
                        if trie.longest_match(kccs, start) >= index - start + 1
                    ),
                    default=0,
                )
            )
        else:
            current["match.forward"] = "0"
            current["match.backward"] = "0"
        features.append(current)
    return features