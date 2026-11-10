"""
Module: normalizer/__init__.py
Purpose: Load normalization rules and expose the Khmer normalization pipeline.
Usage: from khmer_tokenizer.normalizer import normalize
"""
from __future__ import annotations

import json
import unicodedata
from dataclasses import dataclass
from pathlib import Path
from typing import Mapping, Optional, Union

from khmer_tokenizer.exceptions import InvalidConfigurationError
from khmer_tokenizer.normalizer.cleaner import CleanText, extract_boundary_cues
from khmer_tokenizer.normalizer.reorder import reorder_khmer_clusters
from khmer_tokenizer.normalizer.vowels import (
    apply_character_replacements,
    resolve_shifter_collision,
)


@dataclass(frozen=True)
class NormalizedText:
    """Result of normalization with ZWSP boundary metadata."""

    text: str
    zwsp_positions: tuple[int, ...]


def _load_rules(path: Path) -> dict[str, object]:
    """Load and validate the normalization configuration object."""
    try:
        with path.open(encoding="utf-8") as file:
            rules = json.load(file)
    except (OSError, json.JSONDecodeError) as error:
        raise InvalidConfigurationError(
            f"Unable to load normalization rules from {path}"
        ) from error
    if not isinstance(rules, dict):
        raise InvalidConfigurationError("Normalization rules must be a JSON object")
    return rules


def _string_mapping(value: object, field: str) -> Mapping[str, str]:
    """Validate a configuration mapping containing only strings."""
    if not isinstance(value, dict) or not all(
        isinstance(key, str) and isinstance(item, str)
        for key, item in value.items()
    ):
        raise InvalidConfigurationError(f"{field} must be an object of strings")
    return value


def _string_list(value: object, field: str) -> list[str]:
    """Validate a configuration list containing only strings."""
    if not isinstance(value, list) or not all(
        isinstance(item, str) for item in value
    ):
        raise InvalidConfigurationError(f"{field} must be a list of strings")
    return value


class KhmerNormalizer:
    """Apply the project's Khmer Unicode normalization contract."""

    def __init__(self, rules_path: Optional[Union[str, Path]] = None) -> None:
        """Load rules from the supplied or default configuration path."""
        path = (
            Path(rules_path)
            if rules_path is not None
            else Path(__file__).parent.parent
            / "resources"
            / "normalizer_rules.json"
        )
        if rules_path is None and not path.exists():
            path = Path(__file__).parents[2] / "configs" / "normalizer_rules.json"
        rules = _load_rules(path)
        try:
            composite_vowels = _string_mapping(
                rules["composite_vowels"], "composite_vowels"
            )
            deprecated = _string_mapping(
                rules["deprecated_characters"], "deprecated_characters"
            )
            zero_width = _string_list(
                rules["zero_width_characters"], "zero_width_characters"
            )
            collision = rules["shifter_collision"]
            if not isinstance(collision, dict):
                raise InvalidConfigurationError(
                    "shifter_collision must be an object"
                )
            source = collision["source"]
            upper_vowels = _string_list(
                collision["upper_vowels"], "shifter_collision.upper_vowels"
            )
            muusikatoan_bases = _string_list(
                collision["muusikatoan_bases"],
                "shifter_collision.muusikatoan_bases",
            )
            triisap_bases = _string_list(
                collision["triisap_bases"], "shifter_collision.triisap_bases"
            )
            if not isinstance(source, str):
                raise InvalidConfigurationError(
                    "shifter_collision.source must be a string"
                )
        except KeyError as error:
            raise InvalidConfigurationError(
                "Normalization rules are missing required fields"
            ) from error
        self._composite_vowels = composite_vowels
        self._deprecated = deprecated
        self._zero_width_characters = frozenset(zero_width)
        self._source = source
        self._upper_vowels = set(upper_vowels)
        self._muusikatoan_bases = set(muusikatoan_bases)
        self._triisap_bases = set(triisap_bases)

    def normalize(self, text: str) -> NormalizedText:
        """Normalize text and return its cleaned form with ZWSP positions."""
        normalized = unicodedata.normalize("NFC", text)
        normalized = apply_character_replacements(
            normalized, {**self._deprecated, **self._composite_vowels}
        )
        normalized = resolve_shifter_collision(
            normalized,
            source=self._source,
            upper_vowels=self._upper_vowels,
            muusikatoan_bases=self._muusikatoan_bases,
            triisap_bases=self._triisap_bases,
        )
        cleaned: CleanText = extract_boundary_cues(
            normalized, self._zero_width_characters
        )
        return NormalizedText(
            text=reorder_khmer_clusters(cleaned.text),
            zwsp_positions=cleaned.zwsp_positions,
        )


_default_normalizer = KhmerNormalizer()


def normalize(text: str) -> NormalizedText:
    """Normalize text using the default project configuration."""
    return _default_normalizer.normalize(text)


__all__ = ["KhmerNormalizer", "NormalizedText", "normalize"]