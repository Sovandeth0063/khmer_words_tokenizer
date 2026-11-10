"""
Module: crf_engine.py
Purpose: Predict BIES tags using a lightweight validated CRF contract.
Usage: CRFEngine().predict_tags(kccs, features)
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Optional, Union

from khmer_tokenizer.exceptions import MalformedModelError
from khmer_tokenizer.models.crf.features import extract_features
from khmer_tokenizer.models.trie import Trie


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
            if choices[index] is None:
                continue
            matches = self.trie.match_lengths(kccs, index)
            for length in matches or [1]:
                end = index + length
                score = choices[index][0]
                if not matches:
                    score -= 0.5
                elif length == 1:
                    score += 0.1
                else:
                    score += 1.0 + 0.5 * min(length - 1, 2)
                    score -= 0.1 * max(0, length - 3)
                candidate = (score, length, length)
                if choices[end] is None or candidate > choices[end]:
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