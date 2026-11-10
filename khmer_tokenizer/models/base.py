"""
Module: base.py
Purpose: Define the common tokenizer engine interface.
Usage: class CustomTokenizer(BaseTokenizer)
"""
from __future__ import annotations

from abc import ABC, abstractmethod


class BaseTokenizer(ABC):
    """Abstract interface shared by tokenizer engines."""

    @abstractmethod
    def tokenize(self, text: str) -> list[str]:
        """Tokenize one input string."""