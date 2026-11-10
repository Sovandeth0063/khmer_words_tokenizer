"""
Module: build_kcc_dataset.py
Purpose: Convert space-segmented Khmer text into KCC-level BIES rows.
Usage: python scripts\\build_kcc_dataset.py --input train.txt --output train.tsv
"""
from __future__ import annotations

import argparse
from pathlib import Path

from khmer_tokenizer.segmenter.kcc import segment_kcc


def word_tags(word: str) -> list[tuple[str, str]]:
    """Convert one lexical word into KCCs and BIES tags."""
    clusters = segment_kcc(word)
    if len(clusters) == 1:
        return [(clusters[0], "S")]
    return list(
        zip(
            clusters,
            ["B"] + ["I"] * (len(clusters) - 2) + ["E"],
        )
    )


def build_dataset(input_path: Path, output_path: Path) -> int:
    """Convert whitespace-separated words into tab-separated KCC rows."""
    rows = 0
    with input_path.open(encoding="utf-8-sig") as source, output_path.open(
        "w", encoding="utf-8", newline="\n"
    ) as target:
        for line in source:
            words = line.split()
            if not words:
                continue
            for word in words:
                for cluster, tag in word_tags(word):
                    target.write(f"{cluster}\t{tag}\n")
                target.write("\n")
                rows += 1
    return rows


def main() -> None:
    """Parse command-line arguments and build the KCC dataset."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    print(f"Wrote {build_dataset(args.input, args.output)} words to {args.output}")


if __name__ == "__main__":
    main()