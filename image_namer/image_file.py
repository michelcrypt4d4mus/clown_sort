"""
Wrapper for image files.

OCR:  https://pypi.org/project/pytesseract/
EXIF: https://blog.matthewgove.com/2022/05/13/how-to-bulk-edit-your-photos-exif-data-with-10-lines-of-python/
Tags: https://exiftool.org/TagNames/EXIF.html
"""
import io
import logging
from os import path
from pathlib import Path
from typing import List, Optional, Union

import pytesseract
from PIL import Image
from PIL.ExifTags import TAGS
from rich.console import Console, ConsoleOptions, RenderResult
from rich.panel import Panel
from rich.text import Text

from image_namer.config import Config
from image_namer.filename_extractor import FilenameExtractor
from image_namer.sorter import get_sort_destination
from image_namer.util.filesystem_helper import copy_file_creation_time, files_in_dir, is_sortable
from image_namer.util.logging import console, copied_file_log_message, log

THUMBNAIL_DIMENSIONS = (400, 400)
IMAGE_DESCRIPTION = 'ImageDescription'

EXIF_CODES = {
    IMAGE_DESCRIPTION: 270,
}


class ImageFile:
    def __init__(self, file_path: Union[str, Path]) -> None:
        self.file_path: Path = Path(file_path)
        self.basename: str = path.basename(file_path)
        self.basename_without_ext: str = str(Path(self.basename).with_suffix(''))
        self.extname: str = self.file_path.suffix
        self.ocr_attempted: bool = False
        self._ocr_text: Optional[str] = None
        self.__new_basename: Optional[str] = None

    @classmethod
    def screenshot_paths(cls) -> List['ImageFile']:
        """Returns a list of ImageFiles for all the screenshots to be sorted."""
        screenshots = [
            ImageFile(f) for f in files_in_dir(Config.screenshots_dir)
            if path.basename(f).startswith('Screen Shot')
        ]

        return sorted(screenshots, key=lambda f: f.basename)

    @classmethod
    def sortable_non_screenshot_paths(cls) -> List[Path]:
        """Returns a list of ImageFiles for all the screenshots to be sorted."""
        files = [
            Path(f) for f in files_in_dir(Config.screenshots_dir)
            if is_sortable(f) and not path.basename(f).startswith('Screen Shot')
        ]

        return sorted(files, key=lambda f: str(f))

    def image_bytes(self) -> bytes:
        """Return bytes for a thumbnail."""
        image = Image.open(self.file_path)
        image.thumbnail(THUMBNAIL_DIMENSIONS)
        _image_bytes = io.BytesIO()
        image.save(_image_bytes, format="PNG")
        return _image_bytes.getvalue()

    def ocr_text(self) -> Optional[str]:
        """Use Tesseract to OCR the text in the image, which is returned as a string."""
        if self.ocr_attempted:
            return self._ocr_text

        self._ocr_text = pytesseract.image_to_string(Image.open(self.file_path))
        self.ocr_attempted = True
        return self._ocr_text

    def set_image_description_exif_as_ocr_text(
            self,
            destination_subdir: Optional[Union[Path, str]] = None,
            dry_run: bool = True
        ) -> Path:
        """
        Copies to a new file and injects the ImageDescription exif tag.
        If :destination_subdir is given new file will be in :destination_subdir off of configured :destination_dir.
        Returns new file path.
        """
        new_file = get_sort_destination(self._new_basename(), destination_subdir)
        exif_data = self.raw_exif_dict()
        exif_data.update([(EXIF_CODES[IMAGE_DESCRIPTION], self.ocr_text())])

        if dry_run:
            log_msg = Text("Dry run so no copy to '").append(str(new_file), style='color(221)').append("'")
            console.print(log_msg, style='dim')
            return new_file

        try:
            img = Image.open(self.file_path)
            img.save(new_file, exif=exif_data)
            copy_file_creation_time(self.file_path, new_file)
        except ValueError as e:
            console.print_exception()
            console.print(f"ERROR while processing '{self.file_path}'", style='bright_red')
            raise e

        console.print(copied_file_log_message(self.basename, new_file))
        return new_file

    def exif_dict(self) -> dict:
        """Return a key/value list of exif tags where keys are strings."""
        raw_exif_tags = Image.open(self.file_path).getexif()
        return {TAGS[k]: v for k,v in raw_exif_tags.items()}

    def raw_exif_dict(self) -> Image.Exif:
        """Return a key/value list of exif tags where keys are integers."""
        return Image.open(self.file_path).getexif()

    def _new_basename(self) -> str:
        """Return a descriptive string usable in a filename."""
        if self.__new_basename is not None:
            return self.__new_basename

        if self.ocr_text() is None:
            self.__new_basename = self.basename
        else:
            self.__new_basename = FilenameExtractor(self).filename()

        self.__new_basename = self.__new_basename.replace('""', '"')
        return self.__new_basename

    def __str__(self) -> str:
        return str(self.file_path)

    def __repr__(self) -> str:
        return f"ImageFile('{self.file_path}')"

    def __rich_console__(self, console: Console, options: ConsoleOptions) -> RenderResult:
        yield(Text("\n\n\n"))
        yield Panel(path.basename(self.file_path), expand=False, style='cyan')

        if self.ocr_text() is None:
            yield Text("<None>", style='dim')
        else:
            yield Text(self.ocr_text(), style='dim')

        yield Text("DESTINATION BASENAME: ").append(self._new_basename(), style='cyan dim')
        log.debug(f"RAW EXIF: {self.raw_exif_dict()}")
        log.debug(f"EXIF: {self.exif_dict()}")
