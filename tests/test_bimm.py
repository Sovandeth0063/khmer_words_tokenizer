"""
Module: test_bimm.py
Purpose: Test Trie matching and Bi-Directional Maximal Matching.
Usage: python -m pytest tests\test_bimm.py -v
"""

from pathlib import Path

from khmer_tokenizer.models.bimm import BiMMTokenizer
from khmer_tokenizer.models.trie import Trie


def test_trie_matches_longest_word() -> None:
    """Verify the Trie returns the longest matching dictionary word."""
    trie = Trie(["ក", "កក", "កកកុញ"])
    assert trie.longest_match(["ក", "ក", "កុ", "ញ"]) == 4


def test_custom_word_overrides_dictionary_segmentation() -> None:
    """Verify custom words are added and removed independently."""
    trie = Trie(["ប្រទេស"])
    trie.add_word("ប្រទេសកម្ពុជា")
    tokenizer = BiMMTokenizer(trie)
    assert tokenizer.segment("ប្រទេសកម្ពុជា") == ["ប្រទេសកម្ពុជា"]
    trie.remove_word("ប្រទេសកម្ពុជា")
    assert tokenizer.segment("ប្រទេសកម្ពុជា") != ["ប្រទេសកម្ពុជា"]


def test_tokenizer_add_and_remove_word_forward_to_trie() -> None:
    """Verify tokenizer-level custom dictionary methods work."""
    tokenizer = BiMMTokenizer(Trie(["ប្រទេស"]))
    tokenizer.add_word("ប្រទេសកម្ពុជា")
    assert tokenizer.segment("ប្រទេសកម្ពុជា") == ["ប្រទេសកម្ពុជា"]
    tokenizer.remove_word("ប្រទេសកម្ពុជា")
    assert tokenizer.segment("ប្រទេសកម្ពុជា") != ["ប្រទេសកម្ពុជា"]


def test_tokenizer_loads_custom_dictionary_path(tmp_path: Path) -> None:
    """Verify custom dictionary files are loaded during initialization."""
    custom_path = tmp_path / "custom.txt"
    custom_path.write_text("ប្រទេសកម្ពុជា\n", encoding="utf-8")
    tokenizer = BiMMTokenizer(Trie(["ប្រទេស"]), custom_dict_path=custom_path)
    assert tokenizer.segment("ប្រទេសកម្ពុជា") == ["ប្រទេសកម្ពុជា"]


def test_trie_loads_word_pos_csv(tmp_path: Path) -> None:
    """Verify dictionary CSV loading uses only the word column."""
    dictionary = tmp_path / "dictionary.csv"
    dictionary.write_text("word,pos\nក,ន.\nកក,គុ.\n", encoding="utf-8")
    trie = Trie.from_file(dictionary)
    assert trie.longest_match(["ក", "ក"]) == 2


def test_bimm_preserves_non_khmer_spans() -> None:
    """Verify BiMM preserves URLs, numbers, and Latin text."""
    tokenizer = BiMMTokenizer(Trie(["ប្រទេស"]))
    assert tokenizer.tokenize("ប្រទេស 12.5 https://example.com") == [
        "ប្រទេស",
        " ",
        "12.5",
        " ",
        "https://example.com",
    ]