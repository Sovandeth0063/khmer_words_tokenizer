"""Tests for the simple standalone tokenization script."""

import json

from scripts.tokenize_text import main


def test_tokenize_script_prints_json(capsys) -> None:
    """Verify the script prints tokenized Khmer text as JSON."""
    assert main(["ខ្ញុំស្រឡាញ់ប្រទេសកម្ពុជា"]) == 0
    assert json.loads(capsys.readouterr().out) == [
        "ខ្ញុំ",
        "ស្រឡាញ់",
        "ប្រទេស",
        "កម្ពុជា",
    ]


def test_tokenize_script_khmer_only_filters_non_khmer(capsys) -> None:
    """Verify --khmer-only omits non-Khmer tokens from JSON output."""
    assert main(["--khmer-only", "ខ្ញុំស្រឡាញ់ប្រទេសកម្ពុជា !"]) == 0
    assert json.loads(capsys.readouterr().out) == [
        "ខ្ញុំ",
        "ស្រឡាញ់",
        "ប្រទេស",
        "កម្ពុជា",
    ]
