from datetime import datetime
from pathlib import Path

from clown_sort.util.filesystem_helper import *

TEST_FILE = '/Users/hrollins/Screen Shot 2023-02-10 at 4.00.32 PM.png'
TEST_PATH = Path(TEST_FILE)


def test_extract_timestamp_from_filename():
    assert extract_timestamp_from_filename(TEST_FILE) == datetime(2023, 2, 10, 16, 0, 32)


def test_strip_bad_chars():
    assert strip_bad_chars('$food = truth!') == '$food = truth_'
    assert strip_bad_chars('who - knew') == 'who - knew'


def test_insert_suffix_before_extension():
    assert insert_suffix_before_extension(TEST_PATH, 'pages 1-10') == Path('/Users/hrollins/Screen Shot 2023-02-10 at 4.00.32 PM__pages_1-10.png')
    assert insert_suffix_before_extension(TEST_PATH, 'wacko!!! $/(Sx::)') == Path('/Users/hrollins/Screen Shot 2023-02-10 at 4.00.32 PM__wacko__$_(Sx::).png')
