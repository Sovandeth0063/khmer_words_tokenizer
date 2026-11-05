"""
Module: exceptions.py
Purpose: Define explicit tokenizer configuration and setup exceptions.
Usage: from khmer_tokenizer.exceptions import InvalidConfigurationError
"""
class TokenizerError(Exception):
    """Base exception for tokenizer configuration and processing failures."""


class InvalidConfigurationError(TokenizerError):
    """Raised when a tokenizer configuration is missing or invalid."""


class MalformedModelError(TokenizerError):
    """Raised when a model or lexicon artifact cannot be loaded."""


class TokenizerSetupError(TokenizerError):
    """Raised when tokenizer initialization cannot be completed."""