"""Tests that Khmer sentence marks never appear as output tokens."""

from tokenizer import KhmerTokenizer, tokenize
from tokenizer.assembler import drop_sentence_marks
from tokenizer.bimm import BiMMTokenizer


def test_crf_drops_sentence_mark() -> None:
    """Verify CRF tokenization omits the Khmer full stop."""
    assert tokenize("ខ្ញុំស្រឡាញ់ប្រទេសកម្ពុជា។") == [
        "ខ្ញុំ",
        "ស្រឡាញ់",
        "ប្រទេស",
        "កម្ពុជា",
    ]


def test_bimm_drops_sentence_mark() -> None:
    """Verify BiMM tokenization omits the Khmer full stop."""
    tokenizer = KhmerTokenizer(engine="bimm")
    assert tokenizer.tokenize("ខ្ញុំស្រឡាញ់ប្រទេសកម្ពុជា។") == [
        "ខ្ញុំ",
        "ស្រឡាញ់",
        "ប្រទេសកម្ពុជា",
    ]


def test_bimm_engine_drops_sentence_mark_directly() -> None:
    """Verify the BiMM engine itself never emits a sentence mark."""
    assert BiMMTokenizer().tokenize("ខ្ញុំ។") == ["ខ្ញុំ"]


def test_bariyoosan_is_dropped() -> None:
    """Verify the Khmer bariyoosan sign is not emitted."""
    assert tokenize("លោកថា៕") == ["លោកថា"]


def test_mark_only_input_yields_no_tokens() -> None:
    """Verify a lone sentence mark produces an empty token list."""
    assert tokenize("។") == []


def test_mark_inside_text_is_dropped() -> None:
    """Verify a sentence mark between words is removed from output."""
    assert tokenize("សូមមើល។ មើល") == ["សូម", "មើល", "មើល"]


def test_keep_whitespace_still_drops_mark() -> None:
    """Verify keep_whitespace does not resurrect sentence marks."""
    assert tokenize("ខ្ញុំ។", keep_whitespace=True) == ["ខ្ញុំ"]
    assert KhmerTokenizer(engine="bimm").tokenize(
        "ខ្ញុំ។", keep_whitespace=True
    ) == ["ខ្ញុំ"]


def test_non_khmer_punctuation_is_preserved() -> None:
    """Verify non-Khmer punctuation still appears as its own token."""
    assert tokenize("ខ្ញុំ!") == ["ខ្ញុំ", "!"]


def test_khmer_colon_is_preserved() -> None:
    """Verify the Khmer colon keeps its documented behavior."""
    assert tokenize("លោកថា៖ ខ្ញុំទៅ។") == [
        "លោកថា",
        "៖",
        "ខ្ញុំ",
        "ទៅ",
    ]


def test_embedded_mark_is_not_removed() -> None:
    """Verify the filter only drops tokens equal to a sentence mark."""
    assert drop_sentence_marks(["ក។", "។", "ខ"]) == ["ក។", "ខ"]
