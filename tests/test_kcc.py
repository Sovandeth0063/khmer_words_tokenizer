"""
Module: test_kcc.py
Purpose: Test Khmer Character Cluster segmentation and integrity.
Usage: python -m pytest tests\test_kcc.py -v
"""

from tokenizer.segmenter import segment_kcc


def test_segment_kcc_preserves_subscripts_and_vowels() -> None:
    """Verify Khmer words are split into indivisible character clusters."""
    assert segment_kcc("ប្រទេស") == ["ប្រ", "ទេ", "ស"]


def test_segment_kcc_does_not_leave_dangling_coeng() -> None:
    """Verify no cluster contains an unpaired Coeng mark."""
    clusters = segment_kcc("ខ្ញុំប្រទេស")
    assert all("\u17d2" not in cluster or len(cluster) > 1 for cluster in clusters)
    assert all(not cluster.endswith("\u17d2") for cluster in clusters)


def test_segment_kcc_handles_malformed_marks_without_crashing() -> None:
    """Verify incomplete and repeated Coeng marks remain observable safely."""
    assert segment_kcc("\u17d2\u17d2") == ["\u17d2", "\u17d2"]
