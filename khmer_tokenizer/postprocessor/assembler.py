"""
Module: assembler.py
Purpose: Reconstruct lexical words from KCCs and BIES tags.
Usage: assemble_tokens(kccs, tags)
"""
from __future__ import annotations


def assemble_tokens(kccs: list[str], tags: list[str]) -> list[str]:
    """Join KCCs according to BIES tags without dropping invalid input."""
    if len(kccs) != len(tags):
        raise ValueError("KCC and BIES sequences must have equal length")
    tokens: list[str] = []
    current: list[str] = []
    for kcc, tag in zip(kccs, tags):
        if tag == "S":
            if current:
                tokens.append("".join(current))
                current = []
            tokens.append(kcc)
        elif tag == "B":
            if current:
                tokens.append("".join(current))
            current = [kcc]
        elif tag == "I":
            if current:
                current.append(kcc)
            else:
                tokens.append(kcc)
        elif tag == "E":
            if current:
                current.append(kcc)
                tokens.append("".join(current))
                current = []
            else:
                tokens.append(kcc)
        else:
            raise ValueError(f"Unknown BIES tag: {tag}")
    if current:
        tokens.append("".join(current))
    return tokens