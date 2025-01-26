"""
Base class for sortable files of any type.
"""
import re
import platform
import shutil
from collections import namedtuple
from glob import glob
from os import path, remove
from pathlib import Path
from subprocess import run
from typing import List, Optional, Union

from exiftool import ExifToolHelper
from rich.console import Console, ConsoleOptions, RenderResult
from rich.panel import Panel
from rich.prompt import Confirm
from rich.text import Text
from unidecode import unidecode

from clown_sort.config import Config
from clown_sort.filename_extractor import FilenameExtractor
from clown_sort.lib.rule_match import RuleMatch
from clown_sort.sort_selector import process_file_with_popup
from clown_sort.util.filesystem_helper import copy_file_creation_time, loggable_filename
from clown_sort.util.logging import log
from clown_sort.util.rich_helper import (bullet_text, comma_join, console,
     copying_file_log_message, indented_bullet, mild_warning, moving_file_log_message,
     print_dim_bullet, stderr_console)

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

    def sort_file(self) -> None:
        """Sort the file to destination_dir subdir based on the filename and any extracted text."""
        console.print(self)
        search_text = unidecode(self.basename_without_ext + ' ' + (self.extracted_text() or ''))
        rule_matches = RuleMatch.get_rule_matches(search_text)
        sort_folders = [rm.folder for rm in rule_matches]

        # Handle the case where there are no matches to any configured folders.
        if len(rule_matches) == 0:
            if Config.manual_fallback:
                console.print(Panel('Extracted Text', expand=False))
                console.print(self._extracted_text_panel())

                if self._can_be_presented_in_popup():
                    process_file_with_popup(self)
                    return

                print_dim_bullet(f"'{self.file_path}' cannot be displayed in a popup window yet.")
            elif Config.only_if_match:
                print_dim_bullet('No folder match and --only-if-match option selected. Skipping...')
                return
            elif Config.sorted_screenshots_dir in self.file_path.parents:
                print_dim_bullet("Not moving because no folder match and file already in a sorted folder...")
                return

            console.print(NO_SORT_FOLDERS_MSG)
            sort_folders = [None]
            rule_matches = [None]
        else:
            console.print(bullet_text(Text('Sort folders: ') + comma_join(sort_folders, 'sort_folder')))

        # Copy the renamed file to all the folders whose sorting rules were matched.
        for rule_match in rule_matches:
            # Create the subdir if it doesn't exist.
            folder = None
            match = None

            if rule_match is not None:
                folder = rule_match.folder
                match = rule_match.match
                destination_dir = Config.sorted_screenshots_dir.joinpath(folder)

                if not destination_dir.is_dir() and not Config.dry_run:
                    log.info(f"Creating subdirectory '{destination_dir}'...")
                    destination_dir.mkdir()

            destination_path = self.sort_destination_path(folder)

            if destination_path == self.file_path:
                mild_warning("Source and destination file are the same! Skipping...")
                continue
            elif destination_path.exists():
                if Config.rescan_sorted:
                    mild_warning(f"'{destination_path.name}' already exists in {folder}, skipping...")
                    continue

                if not SortableFile.confirm_file_overwrite(destination_path):
                    continue

            self._paths_of_sorted_copies.append(destination_path)
            self.copy_file_to_sorted_dir(destination_path, match)

        self.move_to_processed_dir()

    def move_to_processed_dir(self) -> None:
        """Finalize the file handling, either leaving, deleting, or moving to processed files dir."""
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

    def new_basename(self) -> str:
        """Basename to rename this file to. Overridden in ImageFile for images with OCR text."""
        return self.basename

    def extracted_text(self) -> Optional[str]:
        """Only PdfFiles and ImageFiles have extracted text; other files are sorted on filename."""
        return self.basename

    def exif_dict(self) -> dict:
        """Return the EXIF data as a dict."""
        try:
            with ExifToolHelper() as exiftool:
                return exiftool.get_metadata(self.file_path)[0]
        except:
            log.warning("ExifTool not found; EXIF data ignored. 'brew install exiftool' may solve this.")
            return {}

    def copy_file_to_sorted_dir(self, destination_path: Path, match: Optional[re.Match] = None):
        """Move or copy the file to destination_subdir."""
        if self.file_path == destination_path:
            console.print(indented_bullet("Source and destination are the same..."))
            return

        self._log_copy_file(destination_path, match)

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

    def preview(self) -> None:
        """Attempt to open a separate application to view the image (Preview on macOS)."""
        log.info(f"Opening '{self.file_path}'")

        if platform.system() == 'Windows':
            log.debug("Windows platform detected; attempting to run the file itself...")
            run([self.file_path])
        else:
            run(['open', self.file_path])

    def print_extracted_text(self) -> None:
        """Pretty print the filename and extracted text."""
        console.print(self._filename_panel())
        console.print(self._extracted_str())

    def file_size(self) -> int:
        """Returns file size in bytes."""
        return self.file_path.stat().st_size

    def _extracted_str(self, max_chars: Optional[int] = None) -> str:
        """Raw string version of extracted text but truncated to max_chars if provided."""
        txt = self.extracted_text()

        if txt is None:
            txt = "<No extracted text>"
        else:
            if max_chars is not None:
                txt = txt[0:MAX_EXTRACTION_LENGTH]

        return txt

    def _extracted_text_panel(self) -> Panel:
        """Panelized version of the extracted text for display."""
        return Panel(self._extracted_str(MAX_EXTRACTION_LENGTH), expand=True, style='dim')

    def _filename_panel(self) -> Panel:
        """Panelized version of the filename for display."""
        filename = loggable_filename(self.file_path, Config)
        return Panel(filename, expand=False, style='bright_white reverse')

    def _log_copy_file(self, destination_path: Path, match: Optional[re.Match] = None) -> None:
        """Log info about a file copy."""
        if Config.debug:
            console.print(copying_file_log_message(self.basename, destination_path))
            return

        log_msg = Text('').append('Copying to ', style='dim')

        if destination_path.parent == Config.destination_dir:
            console.print(indented_bullet(log_msg.append('root sorted dir...')))
            return

        dirname = loggable_filename(destination_path.parent, Config)
        log_msg.append(str(dirname), style='sort_destination')

        if match is not None:
            log_msg.append(f" (matched '", style='dim')
            log_msg.append(match.group(0).strip(), style='magenta dim')
            log_msg.append("')", style='dim')

        console.print(indented_bullet(log_msg))

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

    def _can_be_presented_in_popup(self) -> bool:
        return False

    def __str__(self) -> str:
        return str(self.file_path)

    def __repr__(self) -> str:
        return f"SortableFile('{self.file_path}')"

    def __rich_console__(self, console: Console, options: ConsoleOptions) -> RenderResult:
        """Rich text method."""
        yield Text("\n\n")
        yield self._filename_panel()

        if Config.debug:
            yield self._extracted_text_panel()

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

    @classmethod
    def all_sorted_files(cls) -> List[Path]:
        """Return all the files in the sorted directory."""
        file_paths = []

        for pattern in ['*', '**/*']:
            glob_pattern = Config.sorted_screenshots_dir.joinpath(pattern)
            file_paths.extend(glob(str(glob_pattern)))

        return [Path(f) for f in file_paths]

    @staticmethod
    def confirm_file_overwrite(file_path: Path) -> bool:
        """Check if a path exists when about to write to it and ask for confirmation if it does."""
        if not file_path.exists() or Config.yes_overwrite:
            return True

        msg = Text('').append(f"\nWARNING", style='bright_yellow').append(f": File ")
        msg.append(file_path.name, style='cyan').append(" already exists in ")
        msg.append(str(file_path.parent), style='sort_folder')
        stderr_console.print(msg)

        if Config.rescan_sorted:
            stderr_console.print(f"--rescan-sorted flag is on; skipping...", style='dim')
            return False
        elif Confirm.ask(f"Overwrite?", console=stderr_console):
            return True
        else:
            stderr_console.print("Skipping...", style='dim')
            return False
