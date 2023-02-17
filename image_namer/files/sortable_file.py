"""
Wrapper for sortable files of any type.
"""
import shutil
from os import path
from pathlib import Path
from typing import List, Optional, Union

import pytesseract
from exiftool import ExifToolHelper
from rich.console import Console, ConsoleOptions, RenderResult
from rich.panel import Panel
from rich.text import Text

from image_namer.config import Config
from image_namer.util.logging import console, log, move_file_log_message

MAX_EXTRACTION_LENGTH = 4096


class SortableFile:
    def __init__(self, file_path: Union[str, Path]) -> None:
        self.file_path: Path = Path(file_path)
        self.basename: str = path.basename(file_path)
        self.basename_without_ext: str = str(Path(self.basename).with_suffix(''))
        self.extname: str = self.file_path.suffix
        self.text_extraction_attempted: bool = False
        self._extracted_text: Optional[str] = None
        self._new_basename: Optional[str] = None

    def extracted_text(self) -> Optional[str]:
        return self.basename

    def new_basename(self) -> str:
        """Return the original basename."""
        return self.basename

    def exif_dict(self) -> dict:
        """Return the EXIF data as a dict"""
        try:
            with ExifToolHelper() as exiftool:
                return exiftool.get_metadata(self.file_path)[0]
        except:
            log.warning("ExifTool not found; EXIF data ignored. 'brew install exiftool' may solve this.")
            return {}

    def move_file_to_sorted_dir(
            self,
            destination_subdir: Optional[Union[Path, str]] = None,
            dry_run: bool = True
        ) -> Path:
        destination_path = self.sort_destination_path(destination_subdir)
        destination_dir = destination_path.parent

        if not destination_dir.is_dir():
            log.warning(f"Creating subdirectory '{destination_dir}'...")
            destination_dir.mkdir()

        if dry_run:
            console.print(f"Dry run so not moving...", style='dim')
        else:
            shutil.move(self.file_path, destination_path)

        console.print(move_file_log_message(self.basename, destination_path))
        return destination_path

    def sort_destination_path(self, subdir: Optional[Union[Path, str]] = None) -> Path:
        """Get the destination folder. """
        destination_path = Config.sorted_screenshots_dir

        if subdir is not None:
            destination_path = destination_path.joinpath(subdir)

        return destination_path.joinpath(self.new_basename())

    def __str__(self) -> str:
        return str(self.file_path)

    def __repr__(self) -> str:
        return f"SortableFile('{self.file_path}')"

    def __rich_console__(self, console: Console, options: ConsoleOptions) -> RenderResult:
        yield(Text("\n\n\n"))
        yield Panel(path.basename(self.file_path), expand=False, style='cyan')

        if self.extracted_text() is None:
            yield Text("<No extracted text>", style='dim')
        else:
            yield Text(self.extracted_text()[0:MAX_EXTRACTION_LENGTH], style='dim')

        yield Text("DESTINATION BASENAME: ").append(self.new_basename(), style='cyan dim')
        log.debug(f"EXIF: {self.exif_dict()}")
