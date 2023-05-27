"""
Methods to help with string operations.
"""
import re

from clown_sort.util.constants import SCREENSHOT_REGEX


def strip_bad_chars(text: str) -> str:
    """Remove chars that don't work well in filenames"""
    text = ' '.join(text.splitlines()).replace('\\s+', ' ')
    text = re.sub('’', "'", text).replace('|', 'I').replace(',', ',')
    return re.sub('[^-0-9a-zA-Z@.,?_:=#\'\\$" ()]+', '_', text).replace('  ', ' ')


def strip_mac_screenshot(text: str) -> str:
    return re.sub(SCREENSHOT_REGEX, '', text).strip()
