"""
Module: normalizer.py
Purpose: Load normalization rules and expose the Khmer normalization pipeline.
Usage: from tokenizer.normalizer import normalize
"""
from __future__ import annotations

import json
import unicodedata
from dataclasses import dataclass
from pathlib import Path
from typing import Mapping, Optional, Union

from tokenizer.constants import (
    COENG,
    DEPENDENT_VOWEL_RANGE,
    DIACRITIC_RANGE,
    KHMER_BASE_RANGE,
    ZERO_WIDTH_CHARACTERS,
    ZWSP,
)
from tokenizer.exceptions import InvalidConfigurationError

# ---------------------------------------------------------------------------
# cleaner
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class CleanText:
    """Normalized text with boundary positions captured before cleanup."""

    text: str
    zwsp_positions: tuple[int, ...]


def extract_boundary_cues(
    text: str, zero_width_characters: frozenset[str] = ZERO_WIDTH_CHARACTERS
) -> CleanText:
    """Remove invisible controls and record ZWSP positions in cleaned text."""
    cleaned: list[str] = []
    positions: list[int] = []
    for character in text:
        if character == ZWSP:
            positions.append(len(cleaned))
        elif character not in zero_width_characters:
            cleaned.append(character)
    return CleanText("".join(cleaned), tuple(positions))


# ---------------------------------------------------------------------------
# vowels
# ---------------------------------------------------------------------------


def apply_character_replacements(
    text: str, replacements: Mapping[str, str]
) -> str:
    """Apply configured literal character replacements."""
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
    """Resolve a mistyped shifter using base and vowel context."""
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


# ---------------------------------------------------------------------------
# reorder
# ---------------------------------------------------------------------------


def _is_base(character: str) -> bool:
    """Check whether a character is a Khmer base character."""
    return ord(character) in KHMER_BASE_RANGE


def _mark_order(character: str) -> int:
    """Return the canonical ordering group for a cluster character."""
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


# ---------------------------------------------------------------------------
# KhmerNormalizer + normalize()
# ---------------------------------------------------------------------------


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
            else Path(__file__).parent / "resources" / "normalizer_rules.json"
        )
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


__all__ = ["KhmerNormalizer", "NormalizedText", "normalize", "reorder_khmer_clusters"]
