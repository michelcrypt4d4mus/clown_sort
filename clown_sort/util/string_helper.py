"""
Methods to help with string operations.
"""
import re


def is_empty(text: str) -> bool:
    return text is None or len(text) == 0


def spaces_to_underscores(text: str) -> str:
    return text.replace(' ', '_')
