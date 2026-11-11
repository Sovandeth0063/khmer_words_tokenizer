"""
Module: tokenize_text.py
Purpose: Tokenize one Khmer sentence from the command line.
Usage: py scripts\\tokenize_text.py "ខ្ញុំស្រឡាញ់ប្រទេសកម្ពុជា"
"""
from __future__ import annotations

import argparse
import json
import sys
from typing import Optional

from tokenizer import KhmerTokenizer


def build_parser() -> argparse.ArgumentParser:
    """Create the command-line argument parser."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "text",
        nargs="?",
        help="Khmer text to tokenize. If omitted, enter it when prompted.",
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
    """Read Khmer text, tokenize it, and print a JSON list."""
    args = build_parser().parse_args(argv)
    text = args.text if args.text is not None else input("Enter Khmer text: ")
    tokens = KhmerTokenizer(engine=args.engine).tokenize(
        text, khmer_only=args.khmer_only
    )
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    print(json.dumps(tokens, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
