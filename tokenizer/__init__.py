"""
Module: __init__.py
Purpose: Expose normalization and public Khmer tokenizer APIs.
Usage: from tokenizer import tokenize
"""
from __future__ import annotations

from bisect import bisect_left
from pathlib import Path
from typing import Optional, Union

from tokenizer.assembler import apply_maximum, assemble_tokens, drop_sentence_marks
from tokenizer.bimm import BiMMTokenizer
from tokenizer.crf import CRFEngine, extract_features
from tokenizer.normalizer import KhmerNormalizer, NormalizedText, normalize
from tokenizer.segmenter import lex, segment_kcc
from tokenizer.trie import Trie


class KhmerTokenizer:
    """Public tokenizer supporting CRF and BiMM segmentation engines."""

    def __init__(
        self,
        engine: str = "crf",
        custom_dict_path: Optional[Union[str, Path]] = None,
        model_path: Optional[Union[str, Path]] = None,
    ) -> None:
        """Create a tokenizer using the bundled dictionary and selected engine."""
        dictionary = Path(__file__).parent / "resources" / "khmer_dictionary.txt"
        self.trie = Trie.from_file(dictionary) if dictionary.exists() else Trie()
        split_rules = Path(__file__).parent / "resources" / "lexical_splits.txt"
        if split_rules.exists():
            self.trie.load_split_rules(split_rules)
        if custom_dict_path is not None:
            self.trie.load_custom_dict(custom_dict_path)
        if engine not in {"crf", "bimm"}:
            raise ValueError("engine must be 'crf' or 'bimm'")
        self.engine = engine
        self._bimm = BiMMTokenizer(self.trie)
        self._crf: Optional[CRFEngine]
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

    def _predict_span_tokens(
        self,
        text: str,
        zwsp_positions: tuple[int, ...],
        use_maximum: bool,
    ) -> list[str]:
        """Predict, assemble, and optionally merge one Khmer text slice."""
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
        features = extract_features(kccs, self.trie, kcc_zwsp_positions)
        tags = self._crf.predict_tags(kccs, features)
        tokens = assemble_tokens(kccs, tags)
        return apply_maximum(tokens, self.trie) if use_maximum else tokens

    def _segment_crf(
        self,
        text: str,
        zwsp_positions: tuple[int, ...] = (),
        use_maximum: bool = True,
    ) -> list[str]:
        """Segment a normalized Khmer span with CRF BIES prediction."""
        custom_words = sorted(self.trie.custom_words, key=len, reverse=True)
        if not custom_words:
            return self._predict_span_tokens(text, zwsp_positions, use_maximum)

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
                prefix_positions = tuple(
                    position
                    for position in zwsp_positions
                    if position < len(prefix)
                )
                output.extend(
                    self._predict_span_tokens(
                        prefix, prefix_positions, use_maximum
                    )
                )
            remainder = remainder[next_index:]
        return output

    def tokenize(
        self,
        text: str,
        keep_whitespace: bool = False,
        khmer_only: bool = False,
        apply_maximum: bool = True,
    ) -> list[str]:
        """Normalize and tokenize text with optional filtering."""
        if self.engine == "bimm":
            return drop_sentence_marks(
                self._bimm.tokenize(
                    text,
                    keep_whitespace=keep_whitespace,
                    khmer_only=khmer_only,
                )
            )
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
                output.extend(
                    self._segment_crf(
                        span.text, span_positions, use_maximum=apply_maximum
                    )
                )
            elif not khmer_only and (
                span.kind != "whitespace" or keep_whitespace
            ):
                output.append(span.text)
            cursor += len(span.text)
        return drop_sentence_marks(output)


_default_tokenizer = KhmerTokenizer()


def tokenize(
    text: str,
    keep_whitespace: bool = False,
    khmer_only: bool = False,
    apply_maximum: bool = True,
) -> list[str]:
    """Tokenize text with optional whitespace and Khmer-only filtering."""
    return _default_tokenizer.tokenize(
        text,
        keep_whitespace=keep_whitespace,
        khmer_only=khmer_only,
        apply_maximum=apply_maximum,
    )


__all__ = [
    "KhmerNormalizer",
    "KhmerTokenizer",
    "NormalizedText",
    "apply_maximum",
    "normalize",
    "tokenize",
]