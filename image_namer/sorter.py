"""
Sort images based on the extracted contents.
"""
import shutil
from pathlib import Path
from typing import List, Optional, Union

from rich.panel import Panel
from rich.text import Text

from image_namer.config import Config
from image_namer.util.filesystem_helper import copy_file_creation_time
from image_namer.util.logging import console, copied_file_log_message, log
from image_namer.util.string_helper import comma_join


def get_sort_folders(search_string: Optional[str]) -> List[str]:
    """Find any folders that could be relevant."""
    if search_string is None:
        return []

    return [sr.folder for sr in Config.sort_rules if sr.regex.search(search_string)]


def sort_file_by_ocr(image_file: 'ImageFile', dry_run: bool = True) -> None:
    """Sort the file to destination_dir subdir."""
    console.print(image_file)
    sort_folders = get_sort_folders(image_file.ocr_text())

    if len(sort_folders) == 0:
        console.print('No sort folders! ', style='magenta dim')
        image_file.set_image_description_exif_as_ocr_text(dry_run=dry_run)
    else:
        console.print(Text('FOLDERS: ', style='magenta') + comma_join(sort_folders))
        possible_old_file = Config.sorted_screenshots_dir.joinpath(image_file.basename)

        if possible_old_file.is_file():
            console.print(Text(f"WARNING: Deleting unsorted file '{possible_old_file}'...", style='red'))
            possible_old_file.unlink()

        for sort_folder in sort_folders:
            image_file.set_image_description_exif_as_ocr_text(sort_folder, dry_run=dry_run)

    _move_to_processed_dir(image_file.file_path, dry_run=dry_run)


def get_sort_destination(basename: str, subdir: Optional[Union[Path, str]] = None) -> Path:
    """Get the destination folder. """
    if subdir is None:
        destination_dir = Config.sorted_screenshots_dir
    else:
        destination_dir = Config.sorted_screenshots_dir.joinpath(subdir)

        if not destination_dir.is_dir():
            log.warning(f"Creating subdirectory '{destination_dir}'...")
            destination_dir.mkdir()

    return destination_dir.joinpath(basename)


def sort_file_by_filename(file_path: Path, dry_run: bool = True) -> None:
    console.line(1)
    console.print(Panel(file_path.name, expand=False, style='cyan'))
    sort_folders = get_sort_folders(str(file_path))

    if len(sort_folders) == 0:
        console.print('No sort folders! Not copying...', style='dim')
        return
    else:
        destination_paths = [get_sort_destination(file_path.name, subdir) for subdir in sort_folders]

    for destination_path in destination_paths:
        if dry_run:
            console.print(f"Dry run, not copying to '{destination_path}'...")
        else:
            shutil.copy(file_path, destination_path)
            copy_file_creation_time(file_path, destination_path)

        console.print(copied_file_log_message(file_path.name, destination_path))

    _move_to_processed_dir(file_path, dry_run=dry_run)


def _move_to_processed_dir(file_path: Path, dry_run: bool = True) -> None:
    processed_file_path = Config.processed_screenshots_dir.joinpath(file_path.name)

    if dry_run:
        console.print(
            f"Not moving file to {Config.sorted_screenshots_dir} because it's a dry run...",
            style='dim'
        )
    elif file_path == processed_file_path:
        console.print("Not moving file because it's the same location...", style='dim')
    else:
        console.print(f"Moving '{file_path}' to '{processed_file_path}'", style='dim')
        shutil.move(file_path, processed_file_path)
