"""
Module: segmenter/__init__.py
Purpose: Expose lexical span and KCC segmentation helpers.
Usage: from khmer_tokenizer.segmenter import lex, segment_kcc
"""

from khmer_tokenizer.segmenter.kcc import segment_kcc
from khmer_tokenizer.segmenter.lexer import LexSpan, lex

__all__ = ["LexSpan", "lex", "segment_kcc"]