"""
Methods to help with string operations.
"""
import re


def is_empty(text: str) -> bool:
    return text is None or len(text) == 0


def spaces_to_underscores(text: str) -> str:
    return text.replace(' ', '_')


def exception_str(e: Exception) -> str:
    """A string with the type and message."""
    return f"{type(e).__name__}: {e}"
