"""
Sort images based on the extracted contents.
"""
from os import path
from pathlib import Path
from typing import List, Union

from social_arsenal.config import Config
from social_arsenal.files.image_file import ImageFile
from social_arsenal.files.pdf_file import PdfFile
from social_arsenal.files.sortable_file import SortableFile
from social_arsenal.util.filesystem_helper import files_in_dir, is_image, is_pdf


def screenshot_paths() -> List[SortableFile]:
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
