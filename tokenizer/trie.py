"""
Module: trie.py
Purpose: Store Khmer words as KCC sequences for fast dictionary matching.
Usage: Trie.from_file("tokenizer/resources/khmer_dictionary.txt")
"""
from __future__ import annotations

import csv
from collections.abc import Iterable
from pathlib import Path
from typing import Union

from tokenizer.segmenter import segment_kcc


class _TrieNode:
    """A single prefix-tree node."""

    def __init__(self) -> None:
        self.children: dict[str, _TrieNode] = {}
        self.terminal = False


class Trie:
    """Prefix Trie supporting dictionary and custom-word matching."""

    def __init__(self, words: Iterable[str] = ()) -> None:
        self._root = _TrieNode()
        self._base_words: set[str] = set()
        self._custom_words: set[str] = set()
        self._custom_cluster_words: set[tuple[str, ...]] = set()
        self._forced_splits: set[tuple[str, ...]] = set()
        for word in words:
            self.add_word(word, custom=False)

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
            self._custom_cluster_words.add(tuple(clusters))
        else:
            self._base_words.add(word.strip())

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
        normalized_word = word.strip()
        if normalized_word not in self._custom_words:
            return
        self._custom_words.remove(normalized_word)
        self._custom_cluster_words.discard(tuple(clusters))
        if normalized_word in self._base_words:
            return
        node.terminal = False
        for parent, cluster, child in reversed(path):
            if child.terminal or child.children:
                break
            del parent.children[cluster]

    def longest_match(self, clusters: list[str], start: int = 0) -> int:
        """Return the KCC length of the longest word at a sequence position."""
        node = self._root
        longest = 0
        for index in range(start, len(clusters)):
            child = node.children.get(clusters[index])
            if child is None:
                break
            node = child
            if node.terminal:
                longest = index - start + 1
        return longest

    def match_lengths(self, clusters: list[str], start: int = 0) -> list[int]:
        """Return all terminal word lengths at a sequence position."""
        node = self._root
        lengths: list[int] = []
        for index in range(start, len(clusters)):
            child = node.children.get(clusters[index])
            if child is None:
                break
            node = child
            if node.terminal:
                lengths.append(index - start + 1)
        return lengths

    def is_forced_split(
        self, clusters: list[str], start: int, length: int
    ) -> bool:
        """Return whether a lexical-boundary rule splits this exact span."""
        span = tuple(clusters[start : start + length])
        return span in self._forced_splits and span not in self._custom_cluster_words

    def load_split_rules(self, path: Union[str, Path]) -> None:
        """Load tab-separated phrases that must be split at lexical boundaries."""
        for line_number, line in enumerate(
            Path(path).read_text(encoding="utf-8-sig").splitlines(), 1
        ):
            fields = line.split("\t")
            if len(fields) < 2 or not fields[0].strip():
                raise ValueError(f"Invalid split rule at line {line_number}")
            phrase = tuple(segment_kcc(fields[0].strip()))
            parts = tuple(part.strip() for part in fields[1:] if part.strip())
            if len(parts) < 2 or tuple(
                cluster
                for part in parts
                for cluster in segment_kcc(part)
            ) != phrase:
                raise ValueError(f"Invalid split rule at line {line_number}")
            self._forced_splits.add(phrase)

    def preferred_match_lengths(
        self, clusters: list[str], start: int = 0
    ) -> list[int]:
        """Return matches after preferring valid lexical decompositions."""
        lengths = self.match_lengths(clusters, start)
        decomposable = {
            length
            for length in lengths
            if self.is_forced_split(clusters, start, length)
        }
        alternatives = [length for length in lengths if length not in decomposable]
        return alternatives or lengths

    @property
    def custom_words(self) -> frozenset[str]:
        """Return custom dictionary words without exposing mutable state."""
        return frozenset(self._custom_words)

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

    def lookup(self, word: str) -> tuple[bool, bool]:
        """Return (is_prefix, is_word) for a Khmer string in one Trie walk."""
        clusters = segment_kcc(word.strip())
        if not clusters:
            return False, False
        node = self._root
        for cluster in clusters:
            child = node.children.get(cluster)
            if child is None:
                return False, False
            node = child
        return True, node.terminal

    def contains(self, word: str) -> bool:
        """Return whether the exact word is present in the Trie."""
        return self.lookup(word)[1]
