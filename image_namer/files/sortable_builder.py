from pathlib import Path
from typing import List, Union

from image_namer.util.filesystem_helper import is_image, is_movie, is_pdf, is_sortable
from image_namer.files.image_file import ImageFile
from image_namer.files.pdf_file import PdfFile
from image_namer.files.sortable_file import SortableFile


def build_sortable_file(file_path: Union[str, Path]) -> SortableFile:
    if is_image(file_path):
        return ImageFile(file_path)
    elif is_pdf(file_path):
        return PdfFile(file_path)
    else:
        return SortableFile(file_path)
