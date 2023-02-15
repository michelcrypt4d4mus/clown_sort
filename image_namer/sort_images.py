#!/usr/bin/env python

import shutil

from rich.text import Text

from image_namer.config import DEFAULT_SCREENSHOTS_DIR, Config
from image_namer.image_file import ImageFile
from image_namer.sorter import get_sort_folders
from image_namer.util.rich_helper import console
from image_namer.util.string_helper import comma_join
from image_namer.sorter import sort_file

SORTED_DIR = DEFAULT_SCREENSHOTS_DIR.joinpath('Sorted')
PROCESSED_DIR = DEFAULT_SCREENSHOTS_DIR.joinpath('Processed')


for image in ImageFile.screenshot_paths():
    sort_file(image)
