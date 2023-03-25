"""
Wrapper for image files.

OCR:  https://pypi.org/project/pytesseract/
EXIF: https://blog.matthewgove.com/2022/05/13/how-to-bulk-edit-your-photos-exif-data-with-10-lines-of-python/
Tags: https://exiftool.org/TagNames/EXIF.html
"""
import io
from pathlib import Path
from typing import Optional

import pytesseract
from PIL import Image
from PIL.ExifTags import TAGS

from clown_sort.config import Config
from clown_sort.filename_extractor import FilenameExtractor
from clown_sort.files.sortable_file import SortableFile
from clown_sort.util.filesystem_helper import copy_file_creation_time
from clown_sort.util.logging import log
from clown_sort.util.rich_helper import console

THUMBNAIL_DIMENSIONS = (400, 400)
IMAGE_DESCRIPTION = 'ImageDescription'

EXIF_CODES = {
    IMAGE_DESCRIPTION: 270,
}


class ImageFile(SortableFile):
    def copy_file_to_sorted_dir(self, destination_path: Path) -> Path:
        """
        Copies to a new file and injects the ImageDescription exif tag.
        If :destination_subdir is given new file will be in :destination_subdir off
        of the configured :destination_dir. Returns new file path.
        """
        exif_data = self.raw_exif_dict()
        exif_data.update([(EXIF_CODES[IMAGE_DESCRIPTION], self.extracted_text())])
        self._log_copy_file(destination_path)

        if Config.dry_run:
            return destination_path

        try:
            self.pillow_image_obj().save(destination_path, exif=exif_data)
            copy_file_creation_time(self.file_path, destination_path)
        except ValueError as e:
            console.print_exception()
            console.print(f"ERROR while processing '{self.file_path}'", style='bright_red')
            raise e

        return destination_path

    def new_basename(self) -> str:
        """Return a descriptive string usable in a filename."""
        if self._new_basename is not None:
            return self._new_basename

        if self.extracted_text() is None:
            self._new_basename = self.basename
        else:
            self._filename_extractor = FilenameExtractor(self)
            self._new_basename = self._filename_extractor.filename()

        self._new_basename = self._new_basename.replace('""', '"')
        return self._new_basename

    def image_bytes(self) -> bytes:
        """Return bytes for a thumbnail."""
        image = self.pillow_image_obj()
        image.thumbnail(THUMBNAIL_DIMENSIONS)
        _image_bytes = io.BytesIO()
        image.save(_image_bytes, format="PNG")
        return _image_bytes.getvalue()

    def extracted_text(self) -> Optional[str]:
        """Use Tesseract to OCR the text in the image, which is returned as a string."""
        if self.text_extraction_attempted:
            return self._extracted_text

        try:
            self._extracted_text = pytesseract.image_to_string(self.pillow_image_obj())
        except Exception as e:
            console.print_exception()
            console.print(f"Error while extracting '{self.file_path}'!", style='bright_red')
            raise e

        if self._extracted_text is not None:
            self._extracted_text = self._extracted_text.strip()

        self.text_extraction_attempted = True
        return self._extracted_text

    def exif_dict(self) -> dict:
        """Return a key/value list of exif tags where keys are strings."""
        raw_exif_tags = self.pillow_image_obj().getexif()
        return {TAGS[k]: v for k,v in raw_exif_tags.items()}

    def raw_exif_dict(self) -> Image.Exif:
        """Return a key/value list of exif tags where keys are integers."""
        return self.pillow_image_obj().getexif()

    def pillow_image_obj(self) -> Image.Image:
        """Return the file as Pillow Image object."""
        return Image.open(self.file_path)

    def __repr__(self) -> str:
        return f"ImageFile('{self.file_path}')"

    # def __rich_console__(self, console: Console, options: ConsoleOptions) -> RenderResult:
    #     super().__rich_console__(console, options)
    #     log.debug(f"RAW EXIF: {self.raw_exif_dict()}")
