"""
Wrapper for image files.

OCR:  https://pypi.org/project/pytesseract/
EXIF: https://blog.matthewgove.com/2022/05/13/how-to-bulk-edit-your-photos-exif-data-with-10-lines-of-python/
Tags: https://exiftool.org/TagNames/EXIF.html
"""
import io
import logging
import re
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
from image_namer.util.filesystem_helper import copy_file_creation_time, files_in_dir
from image_namer.util.rich_helper import console

IMAGE_DESCRIPTION = 'ImageDescription'
THUMBNAIL_DIMENSIONS = (400, 400)
TWEET_REGEX = re.compile('(@[a-zA-Z0-9]{3,15}(\\.\\.\\.)?)\\s{1,2}-\\s{1,2}(\\d{1,2}[smhd]|Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)')
TWEET_REPLY_REGEX = re.compile('Replying to (@[a-zA-Z0-9]{3,15})')

EXIF_CODES = {
    IMAGE_DESCRIPTION: 270,
}


class ImageFile:
    def __init__(self, file_path: Union[str, Path]) -> None:
        self.file_path: Path = Path(file_path)
        self.basename: str = path.basename(file_path)
        self.ocr_attempted: bool = False
        self._ocr_text: Optional[str] = None

    @classmethod
    def screenshot_paths(cls) -> List['ImageFile']:
        """Returns a list of ImageFiles for all the screenshots to be sorted."""
        screenshots = [
            ImageFile(f) for f in files_in_dir(Config.screenshots_dir)
            if path.basename(f).startswith('Screen Shot')
        ]

        return sorted(screenshots, key=lambda f: f.basename)

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

    def filename_text(self) -> Optional[str]:
        """Return a descriptive string usable in a filename."""
        if self.ocr_text() is None:
            return None

        self._ocr_text

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
        if destination_subdir is None:
            destination_dir = Config.sorted_screenshots_dir
        else:
            destination_dir = Config.sorted_screenshots_dir.joinpath(destination_subdir)

            if not destination_dir.is_dir():
                logging.warning(f"Creating subdirectory '{destination_dir}'...")
                destination_dir.mkdir()

        new_file = destination_dir.joinpath(self.basename)
        exif_data = self.raw_exif_dict()
        exif_data.update([(EXIF_CODES[IMAGE_DESCRIPTION], self.ocr_text())])
        self._is_tweet()

        if dry_run:
            console.print(Text("Dry run so no copy to '").append(str(new_file), style='color(221)').append("'"), style='dim')
            return new_file

        try:
            img = Image.open(self.file_path)
            img.save(new_file, exif=exif_data)
            copy_file_creation_time(self.file_path, new_file)
        except ValueError as e:
            console.print_exception()
            console.print(f"ERROR while processing '{self.file_path}'", style='bright_red')
            raise e

        txt = Text("  ➤ Copied ").append(self.basename, style='color(221)')
        txt.append(' to ').append(str(new_file), style='cyan')
        console.print(txt)
        return new_file

    def exif_dict(self) -> dict:
        """Return a key/value list of exif tags where keys are strings."""
        raw_exif_tags = Image.open(self.file_path).getexif()
        return {TAGS[k]: v for k,v in raw_exif_tags.items()}

    def raw_exif_dict(self) -> Image.Exif:
        """Return a key/value list of exif tags where keys are integers."""
        return Image.open(self.file_path).getexif()

    def _is_tweet(self) -> bool:
        """Check if it's a screenshot of a tweet."""
        if self.ocr_text() is None:
            return False

        match = TWEET_REGEX.search(self.ocr_text())

        if match is None:
            console.print("NOT a tweet", style='color(158)')
            return False
        else:
            author = match.group(1)
            txt = Text("YES it's a tweet by ", style='color(82)').append(author, style='color(178)')
            reply_to = TWEET_REPLY_REGEX.search(self.ocr_text())

            if reply_to is not None:
                txt.append("\n    -> Replying to ", style='color(23)')
                txt.append(reply_to.group(1), style='color(178)')

            console.print(txt)
            return True

    def __str__(self) -> str:
        return str(self.file_path)

    def __repr__(self) -> str:
        return f"ImageFile('{self.file_path}')"

    def __rich_console__(self, _console: Console, options: ConsoleOptions) -> RenderResult:
        yield Panel(path.basename(self.file_path), expand=False, style='cyan')

        if self.ocr_text() is None:
            yield Text("<None>", style='dim')
        else:
            yield Text(self.ocr_text(), style='dim')
