"""
Module: test_crf_tokenizer.py
Purpose: Test BIES prediction, assembly, overrides, and public tokenization.
Usage: python -m pytest tests\test_crf_tokenizer.py -v
"""

import json
from pathlib import Path

import pytest

from khmer_tokenizer import KhmerTokenizer, tokenize
from khmer_tokenizer.exceptions import MalformedModelError
from khmer_tokenizer.models.crf.crf_engine import CRFEngine
from khmer_tokenizer.models.crf.features import extract_features
from khmer_tokenizer.models.trie import Trie
from khmer_tokenizer.postprocessor.assembler import assemble_tokens


def test_assemble_bies_tags() -> None:
    """Verify valid BIES tags reconstruct lexical words."""
    assert assemble_tokens(
        ["ស្រ", "ឡា", "ញ់", "ប្រ", "ទេ", "ស"],
        ["B", "I", "E", "B", "I", "E"],
    ) == ["ស្រឡាញ់", "ប្រទេស"]


def test_assemble_invalid_tags_do_not_drop_clusters() -> None:
    """Verify malformed BIES sequences preserve every cluster."""
    assert assemble_tokens(["ក", "ខ", "គ"], ["I", "E", "B"]) == ["ក", "ខ", "គ"]


def test_default_tokenizer_segments_canonical_example() -> None:
    """Verify the public default API returns the canonical token sequence."""
    expected = ["ខ្ញុំ", "ស្រឡាញ់", "ប្រទេស", "កម្ពុជា"]
    assert tokenize("ខ្ញុំស្រឡាញ់ប្រទេសកម្ពុជា") == expected


def test_custom_word_override_applies_to_default_engine() -> None:
    """Verify custom dictionary words lock a span as one token."""
    tokenizer = KhmerTokenizer()
    tokenizer.add_word("ប្រទេសកម្ពុជា")
    assert tokenizer.tokenize("ប្រទេសកម្ពុជា") == ["ប្រទេសកម្ពុជា"]


def test_bimm_engine_is_selectable() -> None:
    """Verify the public API supports the explicit BiMM engine."""
    tokenizer = KhmerTokenizer(engine="bimm")
    assert tokenizer.tokenize("ក") == ["ក"]


def test_features_include_base_series_and_zwsp() -> None:
    """Verify required orthographic and boundary features are emitted."""
    features = extract_features(
        ["ក", "ខ"], Trie(["ក", "ខ"]), zwsp_positions=(1,)
    )
    assert features[0]["base_series"] in {"first", "second"}
    assert extract_features(["គ"], Trie(["គ"]))[0]["base_series"] == "second"
    assert extract_features(["ណ"], Trie(["ណ"]))[0]["base_series"] == "second"
    assert features[1]["zwsp_before"] == "True"


def test_zwsp_after_a_multi_codepoint_kcc_maps_to_next_kcc() -> None:
    """Verify character offsets are converted to KCC boundary indices."""
    tokenizer = KhmerTokenizer()
    result = tokenizer.tokenize("កា\u200bខ")
    assert result == ["កា", "ខ"]


def test_missing_or_corrupt_model_is_explicit(tmp_path: Path) -> None:
    """Verify invalid explicit CRF model files raise a clear error."""
    missing = tmp_path / "missing.crfsuite"
    with pytest.raises(MalformedModelError):
        CRFEngine(model_path=missing)

    corrupt = tmp_path / "corrupt.crfsuite"
    corrupt.write_text("not-json", encoding="utf-8")
    with pytest.raises(MalformedModelError):
        CRFEngine(model_path=corrupt)


def test_json_model_can_be_loaded(tmp_path: Path) -> None:
    """Verify the lightweight model format can be loaded."""
    model = tmp_path / "model.crfsuite"
    model.write_text(json.dumps({"version": 1}), encoding="utf-8")
    assert CRFEngine(model_path=model)