"""
Module: trie.py
Purpose: Store Khmer words as KCC sequences for fast dictionary matching.
Usage: Trie.from_file("data/dictionaries/chuon_nath_dict.txt")
"""
from __future__ import annotations

import csv
from collections.abc import Iterable
from pathlib import Path
from typing import Union

from khmer_tokenizer.segmenter.kcc import segment_kcc


class _TrieNode:
    """A single prefix-tree node."""

    def __init__(self) -> None:
        self.children: dict[str, _TrieNode] = {}
        self.terminal = False


class Trie:
    """Prefix Trie supporting dictionary and custom-word matching."""

    def __init__(self, words: Iterable[str] = ()) -> None:
        self._root = _TrieNode()
        self._custom_words: set[str] = set()
        for word in words:
            self.add_word(word)

    def add_word(self, word: str, *, custom: bool = True) -> None:
        """Add a non-empty Khmer word to the Trie."""
        clusters = segment_kcc(word.strip())
        if not word.strip() or not clusters:
            return
        node = self._root
        for cluster in clusters:
            node = node.children.setdefault(cluster, _TrieNode())
        node.terminal = True
        if custom:
            self._custom_words.add(word.strip())

    def remove_word(self, word: str) -> None:
        """Remove a word from the Trie without affecting other entries."""
        clusters = segment_kcc(word.strip())
        path: list[tuple[_TrieNode, str, _TrieNode]] = []
        node = self._root
        for cluster in clusters:
            child = node.children.get(cluster)
            if child is None:
                return
            path.append((node, cluster, child))
            node = child
        if not node.terminal:
            return
        node.terminal = False
        self._custom_words.discard(word.strip())
        for parent, cluster, child in reversed(path):
            if child.terminal or child.children:
                break
            del parent.children[cluster]

    def longest_match(self, clusters: list[str], start: int = 0) -> int:
        """Return the KCC length of the longest word at a sequence position."""
        node = self._root
        longest = 0
        for index in range(start, len(clusters)):
            node = node.children.get(clusters[index])
            if node is None:
                break
            if node.terminal:
                longest = index - start + 1
        return longest

    @classmethod
    def from_file(cls, path: Union[str, Path]) -> "Trie":
        """Load words from a newline list or a CSV containing a word column."""
        file_path = Path(path)
        trie = cls()
        if file_path.suffix.lower() == ".csv":
            with file_path.open(encoding="utf-8-sig", newline="") as file:
                for row in csv.DictReader(file):
                    word = (row.get("word") or "").strip()
                    if word:
                        trie.add_word(word, custom=False)
            return trie
        with file_path.open(encoding="utf-8-sig") as file:
            for line in file:
                word = line.strip()
                if word:
                    trie.add_word(word, custom=False)
        return trie

    def load_custom_dict(self, path: Union[str, Path]) -> None:
        """Add custom words from a newline-separated dictionary file."""
        for line in Path(path).read_text(encoding="utf-8-sig").splitlines():
            if line.strip():
                self.add_word(line.strip())

    def contains(self, word: str) -> bool:
        """Return whether the exact word is present in the Trie."""
        clusters = segment_kcc(word.strip())
        return bool(clusters) and self.longest_match(clusters) == len(clusters)