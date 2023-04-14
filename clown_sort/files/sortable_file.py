"""
Base class for sortable files of any type.
"""
import shutil
from os import path, remove
from pathlib import Path
from typing import List, Optional, Union

from exiftool import ExifToolHelper
from rich.console import Console, ConsoleOptions, RenderResult
from rich.panel import Panel
from rich.prompt import Confirm
from rich.text import Text

from clown_sort.config import Config
from clown_sort.filename_extractor import FilenameExtractor
from clown_sort.util.filesystem_helper import copy_file_creation_time
from clown_sort.util.logging import log
from clown_sort.util.rich_helper import (bullet_text, comma_join, indented_bullet, console,
     copying_file_log_message, moving_file_log_message)

MAX_EXTRACTION_LENGTH = 4096
NOT_MOVING_FILE = "Not moving file to processed dir because it's"
NO_SORT_FOLDERS_MSG = bullet_text('No sort folders matched so copying to base sorted dir...', style='color(209)')


class SortableFile:
    def __init__(self, file_path: Union[str, Path]) -> None:
        self.file_path: Path = Path(file_path)
        self.basename: str = path.basename(file_path)
        self.basename_without_ext: str = str(Path(self.basename).with_suffix(''))
        self.extname: str = self.file_path.suffix
        self.text_extraction_attempted: bool = False
        self._extracted_text: Optional[str] = None
        self._new_basename: Optional[str] = None
        self._filename_extractor: Optional[FilenameExtractor] = None
        self._paths_of_sorted_copies: List[Path] = []

    @classmethod
    def get_sort_folders(cls, search_text: Optional[str]) -> List[str]:
        """Find any folders that could be relevant."""
        if search_text is None:
            return []

        return [sr.folder for sr in Config.sort_rules if sr.regex.search(search_text)]

    def sort_file(self) -> None:
        """Sort the file to destination_dir subdir."""
        console.print(self)
        search_text = self.basename_without_ext + ' ' + (self.extracted_text() or '')
        sort_folders = type(self).get_sort_folders(search_text)

        # Handle the case where there are no matches to any configured folders.
        if len(sort_folders) == 0:
            if Config.only_if_match:
                console.print('No folder match and --only-if-match option selected. Skipping...')
                return

            console.print(NO_SORT_FOLDERS_MSG)
            sort_folders = [None]
        else:
            console.print(bullet_text(Text('Sort folders: ') + comma_join(sort_folders, 'sort_folder')))

        # Copy the renamed file to all the folders whose sorting rules were matched.
        for folder in sort_folders:
            # Create the subdir if it doesn't exist.
            if folder is not None:
                destination_dir = Config.sorted_screenshots_dir.joinpath(folder)

                if not destination_dir.is_dir() and not Config.dry_run:
                    log.info(f"Creating subdirectory '{destination_dir}'...")
                    destination_dir.mkdir()

            destination_path = self.sort_destination_path(folder)

            if destination_path.exists():
                console.line()
                msg = Text('').append(f"WARNING", style='bright_yellow').append(f": File ")
                msg.append(destination_path.name, style='cyan').append(" already exists in ")
                msg.append(folder, style='sort_folder')
                console.print(msg)

                if not (Config.yes_overwrite or Confirm.ask(f"Overwrite?")):
                    console.print("Skipping...", style='dim')
                    continue

            self._paths_of_sorted_copies.append(destination_path)
            self.copy_file_to_sorted_dir(destination_path)

        if Config.leave_in_place:
            console.print(bullet_text(Text('Leaving in place...', style='dim')))
            return

        # Don't move the file to the processed_dir if it started in a sorted location
        if self.file_path in self._paths_of_sorted_copies:
            console.print(bullet_text(Text('Not moving original file to processed dir...', style='color(127)')))
            return

        if Config.delete_originals:
            self._delete_original()
            return

        self._move_to_processed_dir()

    def extracted_text(self) -> Optional[str]:
        """Only PdfFiles and ImageFiles have extracted text; other files are sorted on filename."""
        return self.basename

    def new_basename(self) -> str:
        """Return the original basename."""
        return self.basename

    def exif_dict(self) -> dict:
        """Return the EXIF data as a dict."""
        try:
            with ExifToolHelper() as exiftool:
                return exiftool.get_metadata(self.file_path)[0]
        except:
            log.warning("ExifTool not found; EXIF data ignored. 'brew install exiftool' may solve this.")
            return {}

    def copy_file_to_sorted_dir(self, destination_path: Path):
        """Move or copy the file to destination_subdir."""
        if self.file_path == destination_path:
            console.print(indented_bullet("Source and destination are the same..."))
            return

        self._log_copy_file(destination_path)

        if Config.dry_run:
            console.print(indented_bullet("Dry run so not actually copying...", style='dim'))
        else:
            shutil.copy2(self.file_path, destination_path)
            copy_file_creation_time(self.file_path, destination_path)

    def sort_destination_path(self, subdir: Optional[Union[Path, str]] = None) -> Path:
        """Get the destination folder."""
        destination_path = Config.sorted_screenshots_dir

        if subdir is not None:
            destination_path = destination_path.joinpath(subdir)

        return destination_path.joinpath(self.new_basename())

    def _log_copy_file(self, destination_path: Path) -> None:
        """Log info about a file copy."""
        if Config.debug:
            console.print(copying_file_log_message(self.basename, destination_path))
            return

        log_msg = Text('').append('Copying to ', style='dim')

        if destination_path.parent == Config.destination_dir:
            console.print(indented_bullet(log_msg.append('root sorted dir...')))
        else:
            log_msg.append(str(destination_path.parent), style='sort_destination')
            console.print(indented_bullet(log_msg.append('...')))

    def _move_to_processed_dir(self) -> None:
        """Relocate the original file to the [SCREENSHOTS_DIR]/Processed/ folder."""
        processed_file_path = Config.processed_screenshots_dir.joinpath(self.file_path.name)

        if Config.debug:
            console.print(moving_file_log_message(str(self.file_path), processed_file_path))
        else:
            console.print(bullet_text("Moving to processed dir..."))

        if self.file_path == processed_file_path:
            console.print(indented_bullet(f"{NOT_MOVING_FILE} the same location...", style='dim'))
            return
        elif Config.dry_run:
            msg = f"{NOT_MOVING_FILE} a dry run or --leave-in-place specified..."
            console.print(indented_bullet(msg, style='dim'))
        else:
            shutil.move(self.file_path, processed_file_path)

    def _delete_original(self) -> None:
        """Delete the original file (unless it's a dry run)."""
        console.print(bullet_text(Text(f"Deleting original file...")))

        if Config.dry_run:
            console.print(indented_bullet(Text('Skipping delete because this is a dry run...', style='dim')))
            return

        remove(self.file_path)

    def __str__(self) -> str:
        return str(self.file_path)

    def __repr__(self) -> str:
        return f"SortableFile('{self.file_path}')"

    def __rich_console__(self, console: Console, options: ConsoleOptions) -> RenderResult:
        """Rich text method."""
        yield Text("\n\n")
        yield Panel(str(self.file_path), expand=False, style='bright_white reverse')

        if Config.debug:
            if self.extracted_text() is None:
                txt = "<No extracted text>"
            else:
                txt = self.extracted_text()[0:MAX_EXTRACTION_LENGTH]

            yield Panel(txt, expand=True, style='dim')

        if self._filename_extractor is not None:
            if self._filename_extractor._is_tweet():
                log_txt = bullet_text("It's a tweet by ", style='social_media')
                log_txt.append(self._filename_extractor.author or 'NO_AUTHOR', style='author')

                if self._filename_extractor.reply_to_account is not None:
                    log_txt.append("\n    -> Replying to ", style='color(23)')
                    log_txt.append(self._filename_extractor.reply_to_account, style='author')

                yield log_txt
            elif self._filename_extractor._is_reddit():
                yield Text("It's a reddit post", style='social_media')

        log_msg = Text('Destination filename: ').append(self.new_basename(), style='cyan')
        yield bullet_text(log_msg)

        if Config.debug:
            yield bullet_text('EXIF: ')
            yield f"   {self.exif_dict()}\n\n"
