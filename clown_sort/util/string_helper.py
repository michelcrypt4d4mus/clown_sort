"""
Methods to help with string operations.
"""
import re


def strip_bad_chars(text: str) -> str:
    """Remove chars that don't work well in filenames"""
    text = ' '.join(text.splitlines()).replace('\\s+', ' ')
    text = re.sub('’', "'", text).replace('|', 'I').replace(',', ',')
    return re.sub('[^0-9a-zA-Z@.?_:\'" ()]+', '_', text)
