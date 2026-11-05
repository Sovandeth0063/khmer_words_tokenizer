"""
Module: prepare_dictionary.py
Purpose: Convert a Khmer word/POS CSV into a clean Trie word list.
Usage: python scripts\\prepare_dictionary.py --input data\\raw\\khmer_dictionary.csv
"""
from __future__ import annotations

import argparse
import csv
from pathlib import Path


def prepare_dictionary(input_path: Path, output_path: Path) -> int:
    """Write unique non-empty words from a word/POS CSV to a text file."""
    words: set[str] = set()
    with input_path.open(encoding="utf-8-sig", newline="") as source:
        reader = csv.DictReader(source)
        if "word" not in (reader.fieldnames or []):
            raise ValueError("Input CSV must contain a 'word' column")
        for row in reader:
            word = (row.get("word") or "").strip()
            if word:
                words.add(word)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8", newline="\n") as target:
        target.write("\n".join(sorted(words)))
        if words:
            target.write("\n")
    return len(words)


def main() -> None:
    """Parse command-line arguments and prepare the dictionary."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    count = prepare_dictionary(args.input, args.output)
    print(f"Wrote {count} unique words to {args.output}")


if __name__ == "__main__":
    main()
