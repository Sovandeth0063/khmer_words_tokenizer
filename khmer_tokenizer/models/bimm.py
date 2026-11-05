"""
Module: bimm.py
Purpose: Segment Khmer spans using Bi-Directional Maximal Matching.
Usage: BiMMTokenizer(trie).tokenize("ប្រទេសកម្ពុជា")
"""
from __future__ import annotations

from pathlib import Path
from typing import Optional, Union

from khmer_tokenizer.models.trie import Trie
from khmer_tokenizer.normalizer import normalize
from khmer_tokenizer.segmenter import lex, segment_kcc


class BiMMTokenizer:
    """Dictionary tokenizer combining forward and backward maximal matching."""

    def __init__(
        self,
        trie: Optional[Trie] = None,
        custom_dict_path: Optional[Union[str, Path]] = None,
    ) -> None:
        """Create a BiMM tokenizer with optional custom dictionary entries."""
        self.trie = trie or Trie()
        if custom_dict_path is not None:
            self.trie.load_custom_dict(custom_dict_path)

    def add_word(self, word: str) -> None:
        """Add a custom word that takes precedence during matching."""
        self.trie.add_word(word)

    def remove_word(self, word: str) -> None:
        """Remove a custom word from the matching Trie."""
        self.trie.remove_word(word)

    def _forward(self, clusters: list[str]) -> list[str]:
        """Segment clusters with forward maximal matching."""
        result: list[str] = []
        index = 0
        while index < len(clusters):
            length = self.trie.longest_match(clusters, index) or 1
            result.append("".join(clusters[index : index + length]))
            index += length
        return result

    def _backward(self, clusters: list[str]) -> list[str]:
        """Segment clusters with backward maximal matching."""
        result: list[str] = []
        end = len(clusters)
        while end:
            best_start = end - 1
            for start in range(end - 1, -1, -1):
                if self.trie.longest_match(clusters, start) == end - start:
                    best_start = start
                    break
            result.append("".join(clusters[best_start:end]))
            end = best_start
        result.reverse()
        return result

    def _score(self, tokens: list[str]) -> tuple[int, int]:
        """Score a segmentation by token count and unknown singleton count."""
        unknown_singletons = sum(
            len(segment_kcc(token)) == 1 and not self.trie.contains(token)
            for token in tokens
        )
        return len(tokens), unknown_singletons

    def segment(self, text: str) -> list[str]:
        """Segment one normalized Khmer span into dictionary words."""
        clusters = segment_kcc(text)
        forward = self._forward(clusters)
        backward = self._backward(clusters)
        return min(
            (forward, backward),
            key=self._score,
        )

    def tokenize(self, text: str) -> list[str]:
        """Normalize and tokenize Khmer and passthrough spans."""
        normalized = normalize(text)
        output: list[str] = []
        for span in lex(normalized.text):
            if span.kind == "khmer":
                output.extend(self.segment(span.text))
            else:
                output.append(span.text)
        return output