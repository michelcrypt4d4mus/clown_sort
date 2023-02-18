"""
Base class for sortable files of any type.
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

from social_arsenal.config import Config
from social_arsenal.util.logging import console, log, move_file_log_message
from social_arsenal.util.string_helper import comma_join

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

    def sort_file(self) -> None:
        """Sort the file to destination_dir subdir."""
        console.print(self)
        sort_folders = type(self).get_sort_folders(self.extracted_text())

        if len(sort_folders) == 0:
            console.print(Text('➤ ').append('No sort folders!', style='magenta dim'))
            sort_folders = [None]
        else:
            console.print(Text('➤ ').append('FOLDERS: ', style='magenta') + comma_join(sort_folders))

        for folder in sort_folders:
            if folder is not None:
                destination_dir = Config.sorted_screenshots_dir.joinpath(folder)

                if not destination_dir.is_dir() and not Config.dry_run:
                    log.warning(f"Creating subdirectory '{destination_dir}'...")
                    destination_dir.mkdir()

            self.move_file_to_sorted_dir(folder)

    def extracted_text(self) -> Optional[str]:
        """Only PdfFiles and ImageFiles have extracted text; other files are sorted on filename."""
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

    def move_file_to_sorted_dir(self, destination_subdir: Optional[Union[Path, str]] = None) -> Path:
        if destination_subdir is None:
            destination_dir = Config.sorted_screenshots_dir
        else:
            destination_dir = Config.sorted_screenshots_dir.joinpath(destination_subdir)

        destination_path = destination_dir.joinpath(self.new_basename())

        if Config.dry_run:
            console.print(Text('➤ ').append(f"Dry run so not moving...", style='dim'))
        elif Config.leave_in_place:
            shutil.copy2(self.file_path, destination_path)
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

    @classmethod
    def get_sort_folders(cls, search_text: Optional[str]) -> List[str]:
        """Find any folders that could be relevant."""
        if search_text is None:
            return []

        return [sr.folder for sr in Config.sort_rules if sr.regex.search(search_text)]

    def __str__(self) -> str:
        return str(self.file_path)

    def __repr__(self) -> str:
        return f"SortableFile('{self.file_path}')"

    def __rich_console__(self, console: Console, options: ConsoleOptions) -> RenderResult:
        yield(Text("\n\n"))
        yield Panel(path.basename(self.file_path), expand=False, style='cyan')

        if self.extracted_text() is None:
            txt = "<No extracted text>"
        else:
            txt = self.extracted_text()[0:MAX_EXTRACTION_LENGTH]

        yield Panel(txt, expand=True, style='dim')
        yield Text('➤ DESTINATION BASENAME: ').append(self.new_basename(), style='cyan dim')
        log.debug(f"EXIF: {self.exif_dict()}")
