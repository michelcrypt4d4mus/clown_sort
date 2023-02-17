"""
Wrapper for sortable files of any type.
"""
import io
import logging
from abc import abstractmethod
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


class SortableFile:
    def __init__(self, file_path: Union[str, Path]) -> None:
        self.file_path: Path = Path(file_path)
        self.basename: str = path.basename(file_path)
        self.basename_without_ext: str = str(Path(self.basename).with_suffix(''))
        self.extname: str = self.file_path.suffix
        self.text_extraction_attempted: bool = False
        self._extracted_text: Optional[str] = None
        self.__new_basename: Optional[str] = None

    @abstractmethod
    def extracted_text() -> str:
        pass

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

        if self.extracted_text() is None:
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

        if self.extracted_text() is None:
            yield Text("<None>", style='dim')
        else:
            yield Text(self.extracted_text(), style='dim')

        yield Text("DESTINATION BASENAME: ").append(self._new_basename(), style='cyan dim')
        log.debug(f"RAW EXIF: {self.raw_exif_dict()}")
        log.debug(f"EXIF: {self.exif_dict()}")
