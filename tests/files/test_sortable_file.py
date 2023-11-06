from typing import List

from clown_sort.config import Config
from clown_sort.files.image_file import ImageFile
from clown_sort.files.sortable_file import SortableFile

from tests.test_config import *

SIGNATURE = """Signature

Bank"""


def test_sort_file(three_of_swords_file, turn_off_dry_run):
    sortable_file = SortableFile(three_of_swords_file)
    assert sortable_file.extracted_text() == three_of_swords_file.name
    sortable_file.sort_file()
    new_file = ImageFile(Config.sorted_screenshots_dir.joinpath('Art', three_of_swords_file.name))
    new_file.file_path.unlink()
    new_file.file_path.parent.rmdir()
