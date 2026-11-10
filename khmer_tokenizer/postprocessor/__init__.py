"""
Module: postprocessor/__init__.py
Purpose: Expose BIES token assembly helpers.
Usage: from khmer_tokenizer.postprocessor import assemble_tokens
"""

from khmer_tokenizer.postprocessor.assembler import assemble_tokens

__all__ = ["assemble_tokens"]