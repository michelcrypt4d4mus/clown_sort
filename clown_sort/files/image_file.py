"""
Wrapper for image files.

OCR:  https://pypi.org/project/pytesseract/
EXIF: https://blog.matthewgove.com/2022/05/13/how-to-bulk-edit-your-photos-exif-data-with-10-lines-of-python/
Tags: https://exiftool.org/TagNames/EXIF.html
"""
import io
import re
from pathlib import Path
from typing import Optional, Union

import pytesseract
from PIL import Image
from PIL.ExifTags import TAGS

from clown_sort.config import Config
from clown_sort.filename_extractor import FilenameExtractor
from clown_sort.files.sortable_file import RuleMatch, SortableFile
from clown_sort.util.filesystem_helper import copy_file_creation_time
from clown_sort.util.logging import log
from clown_sort.util.rich_helper import console, warning_text

THUMBNAIL_DIMENSIONS = (512, 512)
IMAGE_DESCRIPTION = 'ImageDescription'
FILENAME_LENGTH_TO_CONSIDER_SORTED = 80

EXIF_CODES = {
    IMAGE_DESCRIPTION: 270,
}


class ImageFile(SortableFile):
    def copy_file_to_sorted_dir(self, destination_path: Path, match: Optional[re.Match] = None) -> None:
        """
        Copies to a new file and injects the ImageDescription exif tag.
        If :destination_subdir is given new file will be in :destination_subdir off
        of the configured :destination_dir. Returns new file path.
        """
        exif_data = self.raw_exif_dict()
        exif_data.update([(EXIF_CODES[IMAGE_DESCRIPTION], self.extracted_text())])
        self._log_copy_file(destination_path, match)

        if Config.dry_run:
            return

        try:
            self.pillow_image_obj().save(destination_path, exif=exif_data)
            copy_file_creation_time(self.file_path, destination_path)
        except ValueError as e:
            console.print_exception()
            console.print(f"ERROR while processing '{self.file_path}'", style='bright_red')
            raise e

    def new_basename(self) -> str:
        """Return a descriptive string usable in a filename."""
        if self._new_basename is not None:
            return self._new_basename

        if self.extracted_text() is None \
                or len(self.extracted_text()) == 0 \
                or len(self.basename) > FILENAME_LENGTH_TO_CONSIDER_SORTED:
            self._new_basename = self.basename
        else:
            self._filename_extractor = FilenameExtractor(self)
            self._new_basename = self._filename_extractor.filename()

        self._new_basename = self._new_basename.replace('""', '"')
        return self._new_basename

    def thumbnail_bytes(self) -> bytes:
        """Return bytes for a thumbnail."""
        image = self.pillow_image_obj()
        image.thumbnail(THUMBNAIL_DIMENSIONS)
        _thumbnail_bytes = io.BytesIO()
        image.save(_thumbnail_bytes, format="PNG")
        return _thumbnail_bytes.getvalue()

    def extracted_text(self) -> Optional[str]:
        """Use Tesseract to OCR the text in the image, which is returned as a string."""
        if self.text_extraction_attempted:
            return self._extracted_text

        self._extracted_text = ImageFile.extract_text(self.pillow_image_obj(), str(self.file_path))
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

    def _can_be_presented_in_popup(self) -> bool:
        return True

    def __repr__(self) -> str:
        return f"ImageFile('{self.file_path}')"

    # def __rich_console__(self, console: Console, options: ConsoleOptions) -> RenderResult:
    #     super().__rich_console__(console, options)
    #     log.debug(f"RAW EXIF: {self.raw_exif_dict()}")

    @staticmethod
    def extract_text(image: Image.Image, image_name: str) -> Optional[str]:
        text = None

        try:
            text = pytesseract.image_to_string(image)
        except OSError as e:
            if 'truncated' in str(e):
                console.print(warning_text(f"Truncated image file! '{image_name}'!"))
            else:
                console.print_exception()
                console.print(f"Error while extracting '{image_name}'!", style='bright_red')
                raise e
        except Exception as e:
            console.print_exception()
            console.print(f"Error while extracting '{image_name}'!", style='bright_red')
            raise e

        return None if text is None else text.strip()
