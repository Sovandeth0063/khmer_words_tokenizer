"""Tests for mixed input, controls, malformed clusters, and empty text."""

from khmer_tokenizer import KhmerTokenizer, tokenize


def test_mixed_text_and_non_khmer_spans_are_preserved() -> None:
    """Verify links, email, numbers, and punctuation remain atomic."""
    result = tokenize("សូមមើល https://example.com test@example.com 12.5 😊")
    assert result == [
        "សូម",
        "មើល",
        "https://example.com",
        "test@example.com",
        "12.5",
        "😊",
    ]


def test_zero_width_controls_are_removed() -> None:
    """Verify hidden controls do not appear in output tokens."""
    assert "\u200b" not in "".join(tokenize("ក\u200bខ"))


def test_empty_and_whitespace_input_are_safe() -> None:
    """Verify empty and whitespace-only input produce controlled results."""
    assert tokenize("") == []
    assert tokenize("   ") == []
    assert tokenize("   ", keep_whitespace=True) == ["   "]


def test_whitespace_can_be_preserved_for_exact_reconstruction() -> None:
    """Verify callers can request whitespace tokens explicitly."""
    assert tokenize("ក ខ", keep_whitespace=True) == ["ក", " ", "ខ"]


def test_malformed_coeng_input_does_not_crash() -> None:
    """Verify incomplete Khmer clusters remain observable."""
    assert KhmerTokenizer().tokenize("\u17d2\u17d2") == ["\u17d2", "\u17d2"]