"""
Module: cli.py
Purpose: Stream Khmer text through the tokenizer from the command line.
Usage: python -m tokenizer.cli --input data.txt --output tokens.txt
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Optional, TextIO

from tokenizer import KhmerTokenizer


def _open_input(path: Optional[Path]) -> TextIO:
    """Open the input file or return standard input."""
    return path.open("r", encoding="utf-8-sig") if path else sys.stdin


def _open_output(path: Optional[Path]) -> TextIO:
    """Open the output file or return standard output."""
    return path.open("w", encoding="utf-8", newline="\n") if path else sys.stdout


def process_stream(
    source: TextIO,
    target: TextIO,
    tokenizer: KhmerTokenizer,
    delimiter: str,
    khmer_only: bool = False,
) -> None:
    """Tokenize one input line at a time without loading the complete file."""
    for line in source:
        newline = "\n" if line.endswith(("\n", "\r")) else ""
        text = line.rstrip("\r\n")
        target.write(
            delimiter.join(tokenizer.tokenize(text, khmer_only=khmer_only))
        )
        target.write(newline)


def build_parser() -> argparse.ArgumentParser:
    """Create the command-line argument parser."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, help="Input text file; default is stdin.")
    parser.add_argument("--output", type=Path, help="Output text file; default is stdout.")
    parser.add_argument(
        "--delimiter",
        default=" ",
        help="String used between output tokens (default: a space).",
    )
    parser.add_argument(
        "--engine",
        choices=("crf", "bimm"),
        default="crf",
        help="Tokenizer engine to use (default: crf).",
    )
    parser.add_argument(
        "--khmer-only",
        action="store_true",
        help="Exclude non-Khmer tokens from output.",
    )
    return parser


def main(argv: Optional[list[str]] = None) -> int:
    """Run the streaming command-line tokenizer."""
    args = build_parser().parse_args(argv)
    if "\n" in args.delimiter or "\r" in args.delimiter:
        raise SystemExit("--delimiter cannot contain a newline")
    tokenizer = KhmerTokenizer(engine=args.engine)
    source = _open_input(args.input)
    target = _open_output(args.output)
    try:
        process_stream(
            source,
            target,
            tokenizer,
            args.delimiter,
            khmer_only=args.khmer_only,
        )
    finally:
        if args.input:
            source.close()
        if args.output:
            target.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())