from datetime import datetime

from clown_sort.util.filesystem_helper import extract_timestamp_from_filename

TEST_FILE = '/Users/hrollins/Screen Shot 2023-02-10 at 4.00.32 PM.png'


def test_extract_timestamp_from_filename():
    assert extract_timestamp_from_filename(TEST_FILE) == datetime(2023, 2, 10, 16, 0, 32)
