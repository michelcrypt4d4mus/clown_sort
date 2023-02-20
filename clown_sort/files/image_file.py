"""
Wrapper for image files.

OCR:  https://pypi.org/project/pytesseract/
EXIF: https://blog.matthewgove.com/2022/05/13/how-to-bulk-edit-your-photos-exif-data-with-10-lines-of-python/
Tags: https://exiftool.org/TagNames/EXIF.html
"""
import io
import shutil
from pathlib import Path
from typing import Optional, Union

import pytesseract
from PIL import Image
from PIL.ExifTags import TAGS
from rich.text import Text

from clown_sort.config import Config
from clown_sort.filename_extractor import FilenameExtractor
from clown_sort.files.sortable_file import SortableFile
from clown_sort.util.filesystem_helper import copy_file_creation_time
from clown_sort.util.logging import console, copying_file_log_message
from clown_sort.util.rich_helper import bullet_text, indented_bullet

THUMBNAIL_DIMENSIONS = (400, 400)
IMAGE_DESCRIPTION = 'ImageDescription'

EXIF_CODES = {
    IMAGE_DESCRIPTION: 270,
}


class ImageFile(SortableFile):
    def move_file_to_sorted_dir(self, destination_subdir: Optional[Union[Path, str]] = None) -> Path:
        """
        Copies to a new file and injects the ImageDescription exif tag.
        If :destination_subdir is given new file will be in :destination_subdir off
        of the configured :destination_dir. Returns new file path.
        """
        new_file = self.sort_destination_path(destination_subdir)
        exif_data = self.raw_exif_dict()
        exif_data.update([(EXIF_CODES[IMAGE_DESCRIPTION], self.extracted_text())])

        # TODO: refactor
        if Config.debug:
            console.print(copying_file_log_message(self.basename, new_file))
        else:
            log_msg = Text('Copying to ')

            if Config.dry_run:
                log_msg = Text('').append('(Not) ', style='dim') + log_msg

            if destination_subdir is None:
                console.print(indented_bullet(log_msg + Text('root sorted dir...')))
            else:
                log_msg.append(str(destination_subdir), style='sort_destination')
                console.print(indented_bullet(log_msg.append('...')))

        if Config.dry_run:
            log_msg = Text("  ➤ ").append("Dry run otherwise would copy to '", style='dim')
            log_msg.append(str(new_file), style='color(221)').append("'")

            if Config.debug:
                console.print(log_msg)

            return new_file

        try:
            img = Image.open(self.file_path)
            img.save(new_file, exif=exif_data)
            copy_file_creation_time(self.file_path, new_file)
        except ValueError as e:
            console.print_exception()
            console.print(f"ERROR while processing '{self.file_path}'", style='bright_red')
            raise e

        console.print(copying_file_log_message(self.basename, new_file))
        return new_file

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
        image = Image.open(self.file_path)
        image.thumbnail(THUMBNAIL_DIMENSIONS)
        _image_bytes = io.BytesIO()
        image.save(_image_bytes, format="PNG")
        return _image_bytes.getvalue()

    def extracted_text(self) -> Optional[str]:
        """Use Tesseract to OCR the text in the image, which is returned as a string."""
        if self.text_extraction_attempted:
            return self._extracted_text

        self._extracted_text = pytesseract.image_to_string(Image.open(self.file_path))
        self.text_extraction_attempted = True
        return self._extracted_text

    def exif_dict(self) -> dict:
        """Return a key/value list of exif tags where keys are strings."""
        raw_exif_tags = Image.open(self.file_path).getexif()
        return {TAGS[k]: v for k,v in raw_exif_tags.items()}

    def raw_exif_dict(self) -> Image.Exif:
        """Return a key/value list of exif tags where keys are integers."""
        return Image.open(self.file_path).getexif()

    def __repr__(self) -> str:
        return f"ImageFile('{self.file_path}')"

    # def __rich_console__(self, console: Console, options: ConsoleOptions) -> RenderResult:
    #     super().__rich_console__(console, options)
    #     log.debug(f"RAW EXIF: {self.raw_exif_dict()}")
