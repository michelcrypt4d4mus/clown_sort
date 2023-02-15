#!/usr/bin/env python

from image_namer.config import DEFAULT_SCREENSHOTS_DIR
from image_namer.image_file import ImageFile
from image_namer.sorter import sort_file

SORTED_DIR = DEFAULT_SCREENSHOTS_DIR.joinpath('Sorted')
PROCESSED_DIR = DEFAULT_SCREENSHOTS_DIR.joinpath('Processed')


for image in ImageFile.screenshot_paths():
    sort_file(image)
