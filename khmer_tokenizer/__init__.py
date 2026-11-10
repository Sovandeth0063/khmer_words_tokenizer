"""
Module: __init__.py
Purpose: Expose normalization and public Khmer tokenizer APIs.
Usage: from khmer_tokenizer import tokenize
"""
from __future__ import annotations

from bisect import bisect_left
from pathlib import Path
from typing import Optional, Union

from khmer_tokenizer.models.bimm import BiMMTokenizer
from khmer_tokenizer.models.crf import CRFEngine
from khmer_tokenizer.models.crf.features import extract_features
from khmer_tokenizer.models.trie import Trie
from khmer_tokenizer.normalizer import KhmerNormalizer, NormalizedText, normalize
from khmer_tokenizer.postprocessor import assemble_tokens
from khmer_tokenizer.segmenter import lex, segment_kcc


class KhmerTokenizer:
    """Public tokenizer supporting CRF and BiMM segmentation engines."""

    def __init__(
        self,
        engine: str = "crf",
        custom_dict_path: Optional[Union[str, Path]] = None,
        model_path: Optional[Union[str, Path]] = None,
    ) -> None:
        """Create a tokenizer using the bundled dictionary and selected engine."""
        dictionary = (
            Path(__file__).parent / "resources" / "chuon_nath_dict.txt"
        )
        if not dictionary.exists():
            dictionary = (
                Path(__file__).parents[1]
                / "data"
                / "dictionaries"
                / "chuon_nath_dict.txt"
            )
        self.trie = Trie.from_file(dictionary) if dictionary.exists() else Trie()
        if custom_dict_path is not None:
            self.trie.load_custom_dict(custom_dict_path)
        if engine not in {"crf", "bimm"}:
            raise ValueError("engine must be 'crf' or 'bimm'")
        self.engine = engine
        self._bimm = BiMMTokenizer(self.trie)
        default_model = (
            Path(__file__).parent / "resources" / "crf_khmer_base.crfsuite"
        )
        if engine == "crf":
            self._crf = CRFEngine(
                self.trie,
                model_path=model_path or default_model,
            )
        else:
            self._crf = None

    def add_word(self, word: str) -> None:
        """Add a custom word for both tokenizer engines."""
        self.trie.add_word(word)

    def remove_word(self, word: str) -> None:
        """Remove a custom word from both tokenizer engines."""
        self.trie.remove_word(word)

    def _segment_crf(
        self, text: str, zwsp_positions: tuple[int, ...] = ()
    ) -> list[str]:
        """Segment a normalized Khmer span with CRF BIES prediction."""
        if self._crf is None:
            raise RuntimeError("CRF engine is not initialized")
        kccs = segment_kcc(text)
        kcc_starts: list[int] = []
        character_offset = 0
        for kcc in kccs:
            kcc_starts.append(character_offset)
            character_offset += len(kcc)
        kcc_zwsp_positions = tuple(
            bisect_left(kcc_starts, position) for position in zwsp_positions
        )
        custom_words = sorted(self.trie.custom_words, key=len, reverse=True)
        if not custom_words:
            features = extract_features(kccs, self.trie, kcc_zwsp_positions)
            tags = self._crf.predict_tags(kccs, features)
            return assemble_tokens(kccs, tags)

        output: list[str] = []
        remainder = text
        while remainder:
            match = next(
                (word for word in custom_words if remainder.startswith(word)),
                None,
            )
            if match is not None:
                output.append(match)
                remainder = remainder[len(match) :]
                continue
            next_index = min(
                (
                    remainder.find(word)
                    for word in custom_words
                    if remainder.find(word) >= 0
                ),
                default=len(remainder),
            )
            prefix = remainder[:next_index]
            if prefix:
                prefix_kccs = segment_kcc(prefix)
                prefix_starts: list[int] = []
                prefix_offset = 0
                for kcc in prefix_kccs:
                    prefix_starts.append(prefix_offset)
                    prefix_offset += len(kcc)
                prefix_positions = tuple(
                    bisect_left(prefix_starts, position)
                    for position in zwsp_positions
                    if position < len(prefix)
                )
                features = extract_features(
                    prefix_kccs, self.trie, prefix_positions
                )
                tags = self._crf.predict_tags(prefix_kccs, features)
                output.extend(assemble_tokens(prefix_kccs, tags))
            remainder = remainder[next_index:]
        return output

    def tokenize(self, text: str, keep_whitespace: bool = False) -> list[str]:
        """Normalize and tokenize text with optional whitespace tokens."""
        if self.engine == "bimm":
            return self._bimm.tokenize(text, keep_whitespace=keep_whitespace)
        normalized = normalize(text)
        output: list[str] = []
        cursor = 0
        for span in lex(normalized.text):
            if span.kind == "khmer":
                span_end = cursor + len(span.text)
                span_positions = tuple(
                    position - cursor
                    for position in normalized.zwsp_positions
                    if cursor <= position < span_end
                )
                output.extend(self._segment_crf(span.text, span_positions))
            elif span.kind != "whitespace" or keep_whitespace:
                output.append(span.text)
            cursor += len(span.text)
        return output


_default_tokenizer = KhmerTokenizer()


def tokenize(text: str, keep_whitespace: bool = False) -> list[str]:
    """Tokenize text with optional whitespace tokens."""
    return _default_tokenizer.tokenize(text, keep_whitespace=keep_whitespace)


__all__ = [
    "KhmerNormalizer",
    "KhmerTokenizer",
    "NormalizedText",
    "normalize",
    "tokenize",
]