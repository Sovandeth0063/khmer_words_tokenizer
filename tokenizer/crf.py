"""
Module: crf.py
Purpose: Extract KCC features and predict BIES tags using a lightweight CRF.
Usage: from tokenizer.crf import CRFEngine, extract_features
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Optional, Union

from tokenizer.constants import COENG, DEPENDENT_VOWEL_RANGE
from tokenizer.exceptions import MalformedModelError
from tokenizer.trie import Trie

# ---------------------------------------------------------------------------
# features
# ---------------------------------------------------------------------------

_FIRST_SERIES = frozenset("កខចឆដឋទធបផស អអំ")


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


# ---------------------------------------------------------------------------
# CRFEngine
# ---------------------------------------------------------------------------


class CRFEngine:
    """Thread-safe deterministic BIES prediction engine."""

    def __init__(
        self,
        trie: Optional[Trie] = None,
        model_path: Optional[Union[str, Path]] = None,
    ) -> None:
        """Load an optional JSON model artifact and retain the supplied Trie."""
        self.trie = trie or Trie()
        self._model: dict[str, Any] = {}
        if model_path is not None:
            path = Path(model_path)
            try:
                with path.open(encoding="utf-8") as file:
                    model = json.load(file)
            except (OSError, json.JSONDecodeError) as error:
                raise MalformedModelError(
                    f"Unable to load CRF model from {path}"
                ) from error
            if not isinstance(model, dict) or model.get("version") != 1:
                raise MalformedModelError(
                    f"Unsupported CRF model format: {path}"
                )
            self._model = model

    def predict_tags(
        self,
        kccs: list[str],
        features: Optional[list[dict[str, str]]] = None,
    ) -> list[str]:
        """Predict a valid BIES sequence for a KCC sequence."""
        if not kccs:
            return []
        features = features or extract_features(kccs, self.trie)
        boundaries = [False] * (len(kccs) + 1)
        choices: list[Optional[tuple[float, int, int]]] = [None] * (
            len(kccs) + 1
        )
        choices[0] = (0.0, 0, 0)
        for index in range(len(kccs)):
            choice = choices[index]
            if choice is None:
                continue
            matches = self.trie.match_lengths(kccs, index)
            for length in matches or [1]:
                end = index + length
                score = choice[0]
                if not matches:
                    score -= 0.5
                elif length == 1:
                    score += 0.1
                else:
                    score += 1.0 + 0.5 * min(length - 1, 2)
                    score -= 0.1 * max(0, length - 3)
                if self.trie.is_forced_split(kccs, index, length):
                    score -= 2.0
                candidate = (score, length, length)
                current = choices[end]
                if current is None or candidate > current:
                    choices[end] = candidate
        index = len(kccs)
        boundaries[index] = True
        while index:
            choice = choices[index]
            if choice is None:
                index -= 1
                boundaries[index] = True
                continue
            length = choice[2]
            boundaries[index - length] = True
            index -= length

        tags: list[str] = []
        for index in range(len(kccs)):
            starts = boundaries[index]
            ends = boundaries[index + 1]
            if starts and ends:
                tags.append("S")
            elif starts:
                tags.append("B")
            elif ends:
                tags.append("E")
            else:
                tags.append("I")
        return tags


__all__ = ["CRFEngine", "extract_features"]
