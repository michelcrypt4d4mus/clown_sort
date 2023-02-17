"""
Sort images based on the extracted contents.
"""
from os import path
from typing import List

from image_namer.config import Config
from image_namer.files.sortable_builder import build_sortable_file
from image_namer.util.filesystem_helper import files_in_dir, is_sortable


def screenshot_paths() -> List['SortableFile']:
    """Returns a list of ImageFiles for all the screenshots to be sorted."""
    screenshots = [
        build_sortable_file(f) for f in files_in_dir(Config.screenshots_dir)
        if path.basename(f).startswith('Screen Shot')
    ]

    return sorted(screenshots, key=lambda f: f.basename)


def sortable_non_screenshot_paths() -> List['SortableFile']:
    """Returns a list of ImageFiles for all the screenshots to be sorted."""
    files = [
        build_sortable_file(f) for f in files_in_dir(Config.screenshots_dir)
        if is_sortable(f) and not path.basename(f).startswith('Screen Shot')
    ]

    return sorted(files, key=lambda f: str(f))
