from os import path
from pathlib import Path
from typing import List

from image_namer.config import Config
from image_namer.util.filesystem_helper import files_in_dir, is_sortable
from image_namer.files.sortable_file import SortableFile
from image_namer.files.image_file import ImageFile


def screenshot_paths() -> List['ImageFile']:
    """Returns a list of ImageFiles for all the screenshots to be sorted."""
    screenshots = [
        ImageFile(f) for f in files_in_dir(Config.screenshots_dir)
        if path.basename(f).startswith('Screen Shot')
    ]

    return sorted(screenshots, key=lambda f: f.basename)


def sortable_non_screenshot_paths() -> List[Path]:
    """Returns a list of ImageFiles for all the screenshots to be sorted."""
    files = [
        Path(f) for f in files_in_dir(Config.screenshots_dir)
        if is_sortable(f) and not path.basename(f).startswith('Screen Shot')
    ]

    return sorted(files, key=lambda f: str(f))
