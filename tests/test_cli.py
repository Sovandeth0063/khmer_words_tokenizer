"""Tests for the streaming command-line interface."""

from io import StringIO

import pytest

from tokenizer import KhmerTokenizer
from tokenizer.cli import main, process_stream


def test_process_stream_tokenizes_each_line() -> None:
    """Verify streaming output preserves line boundaries."""
    source = StringIO("ខ្ញុំស្រឡាញ់ប្រទេសកម្ពុជា\nក")
    target = StringIO()
    process_stream(source, target, KhmerTokenizer(), " ")
    assert target.getvalue() == "ខ្ញុំ ស្រឡាញ់ ប្រទេស កម្ពុជា\nក"


def test_cli_supports_file_input_and_output(tmp_path) -> None:
    """Verify the CLI reads and writes files."""
    input_path = tmp_path / "input.txt"
    output_path = tmp_path / "output.txt"
    input_path.write_text("ក", encoding="utf-8")
    assert main(
        ["--input", str(input_path), "--output", str(output_path), "--engine", "bimm"]
    ) == 0
    assert output_path.read_text(encoding="utf-8") == "ក"


def test_cli_rejects_newline_delimiter() -> None:
    """Verify invalid delimiters fail explicitly."""
    with pytest.raises(SystemExit, match="cannot contain"):
        main(["--delimiter", "\n"])


def test_cli_khmer_only_drops_non_khmer_tokens(tmp_path) -> None:
    """Verify --khmer-only omits non-Khmer spans from CLI output."""
    input_path = tmp_path / "input.txt"
    output_path = tmp_path / "output.txt"
    input_path.write_text("ខ្ញុំស្រឡាញ់ប្រទេសកម្ពុជា ! 2026", encoding="utf-8")
    assert main(
        [
            "--input",
            str(input_path),
            "--output",
            str(output_path),
            "--khmer-only",
        ]
    ) == 0
    assert (
        output_path.read_text(encoding="utf-8")
        == "ខ្ញុំ ស្រឡាញ់ ប្រទេស កម្ពុជា"
    )
