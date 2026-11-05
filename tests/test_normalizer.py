"""
Module: test_normalizer.py
Purpose: Test Day 1 Khmer Unicode normalization behavior.
Usage: python -m pytest tests\\test_normalizer.py -v
"""
from pathlib import Path
import unicodedata

import pytest

from khmer_tokenizer.exceptions import InvalidConfigurationError
from khmer_tokenizer.normalizer import KhmerNormalizer, normalize
from khmer_tokenizer.normalizer.reorder import reorder_khmer_clusters


def test_nfc_equivalent_input_has_same_result() -> None:
    """Verify equivalent Unicode input produces equal normalized output."""
    decomposed = "e\u0301"
    composed = unicodedata.normalize("NFC", decomposed)
    assert normalize(decomposed).text == normalize(composed).text


@pytest.mark.parametrize(
    ("source", "expected"),
    [
        ("\u17c1\u17b6", "\u17c4"),
        ("\u17c1\u17b8", "\u17be"),
    ],
)
def test_split_composite_vowels_are_merged(source: str, expected: str) -> None:
    """Verify configured split composite vowels are merged."""
    assert normalize(source).text == expected


def test_deprecated_characters_are_replaced_or_removed() -> None:
    """Verify deprecated Khmer characters follow configured replacements."""
    assert normalize("\u17b4\u17b5\u17a3\u17a4").text == "\u17a2\u17a2\u17b6"


def test_zwsp_is_removed_and_position_is_recorded() -> None:
    """Verify ZWSP is removed and its position is retained."""
    result = normalize("ក\u200bខ")
    assert result.text == "កខ"
    assert result.zwsp_positions == (1,)


def test_shifter_collision_uses_configured_base_series() -> None:
    """Verify shifter selection follows configured consonant series."""
    assert normalize("\u1780\u17bb\u17b8").text == "\u1780\u17c9\u17b8"
    assert normalize("\u1781\u17bb\u17b8").text == "\u1781\u17ca\u17b8"


def test_reordering_keeps_coeng_attached_to_its_base() -> None:
    """Verify reordering keeps Coeng and its subscript attached."""
    result = reorder_khmer_clusters("\u17b6\u1780\u17d2\u179a")
    assert result == "\u1780\u17d2\u179a\u17b6"
    assert "\u17d2" not in result[0:1]


@pytest.mark.parametrize("value", ["\u17d2", "\u17d2\u17d2", "\u1780\u17d2"])
def test_malformed_marks_do_not_raise(value: str) -> None:
    """Verify malformed or incomplete marks do not raise exceptions."""
    normalize(value)


def test_invalid_rules_raise_explicit_error(tmp_path: Path) -> None:
    """Verify malformed rule files raise a configuration error."""
    rules_path = tmp_path / "rules.json"
    rules_path.write_text("[]", encoding="utf-8")
    with pytest.raises(InvalidConfigurationError):
        KhmerNormalizer(rules_path)