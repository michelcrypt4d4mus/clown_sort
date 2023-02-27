from os import environ, getcwd, path
from pathlib import Path
from typing import List, Union

from dotenv import load_dotenv

# load_dotenv() should be called as soon as possible (before parsing local classes) but not for pytest
if not environ.get('INVOKED_BY_PYTEST', False):
    for dotenv_file in [path.join(dir, '.clown_sort') for dir in [getcwd(), Path.home()]]:
        if path.exists(dotenv_file):
            load_dotenv(dotenv_path=dotenv_file)
            break

from clown_sort.config import Config
from clown_sort.files.image_file import ImageFile
from clown_sort.files.pdf_file import PdfFile
from clown_sort.files.sortable_file import SortableFile
from clown_sort.sort_selector import process_file
from clown_sort.util.filesystem_helper import (files_in_dir, is_image, is_pdf,
     set_timestamp_based_on_screenshot_filename)


def sort_screenshots():
    Config.configure()

    for image in screenshot_paths(Config.screenshots_dir):
        if Config.manual_sort:
            if not isinstance(image, ImageFile):
                print(f"'{image.file_path}' is not suitable for manual sort, skipping...")
                continue

            process_file(image)
        else:
            image.sort_file()


def set_screenshot_timestamps():
    Config.configure()

    for image in screenshot_paths(Config.screenshots_dir):
        set_timestamp_based_on_screenshot_filename(image.file_path)


def screenshot_paths(dir: Path) -> List[SortableFile]:
    """Returns a list of ImageFiles for all the screenshots to be sorted."""
    screenshots = [
        _build_sortable_file(f) for f in files_in_dir(Config.screenshots_dir)
        if not Config.screenshots_only or Config.filename_regex.match(path.basename(f))
    ]

    return sorted(screenshots, key=lambda f: f.basename)


def _build_sortable_file(file_path: Union[str, Path]) -> SortableFile:
    if is_image(file_path):
        return ImageFile(file_path)
    elif is_pdf(file_path):
        return PdfFile(file_path)
    else:
        return SortableFile(file_path)
