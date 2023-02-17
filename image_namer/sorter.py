"""
Sort images based on the extracted contents.
"""
import shutil
from os import path
from pathlib import Path
from typing import List, Optional, Union

from rich.panel import Panel
from rich.text import Text

from image_namer.config import Config
from image_namer.files.sortable_builder import build_sortable_file
from image_namer.util.filesystem_helper import files_in_dir, is_sortable


def screenshot_paths() -> List['SortableFile']:
    """Returns a list of ImageFiles for all the screenshots to be sorted."""
    screenshots = [
        build_sortable_file(f) for f in files_in_dir(Config.screenshots_dir)
        if path.basename(f).startswith('Screen Shot')
    ]

    return sorted(screenshots, key=lambda f: f.basename)


def sortable_non_screenshot_paths() -> List['SortableFile']:
    """Returns a list of ImageFiles for all the screenshots to be sorted."""
    files = [
        build_sortable_file(f) for f in files_in_dir(Config.screenshots_dir)
        if is_sortable(f) and not path.basename(f).startswith('Screen Shot')
    ]

    return sorted(files, key=lambda f: str(f))


# def sort_file_by_ocr(image_file: 'ImageFile', dry_run: bool = True) -> None:
#     """Sort the file to destination_dir subdir."""
#     console.print(image_file)
#     sort_folders = get_sort_folders(image_file.extracted_text())

#     if len(sort_folders) == 0:
#         console.print('No sort folders! ', style='magenta dim')
#         image_file.move_file_to_sorted_dir(dry_run=dry_run)
#     else:
#         console.print(Text('FOLDERS: ', style='magenta') + comma_join(sort_folders))
#         possible_old_file = Config.sorted_screenshots_dir.joinpath(image_file.basename)

#         if possible_old_file.is_file():
#             console.print(Text(f"WARNING: Deleting unsorted file '{possible_old_file}'...", style='red'))
#             possible_old_file.unlink()

#         for sort_folder in sort_folders:
#             image_file.move_file_to_sorted_dir(sort_folder, dry_run=dry_run)

#     _move_to_processed_dir(image_file.file_path, dry_run=dry_run)


# def sort_file_by_filename(file_path: Path, dry_run: bool = True) -> None:
#     console.line(1)
#     console.print(Panel(file_path.name, expand=False, style='cyan'))
#     sort_folders = get_sort_folders(str(file_path))

#     if len(sort_folders) == 0:
#         console.print('No sort folders! Not copying...', style='dim')
#         return
#     else:
#         destination_paths = [sort_destination_path(file_path.name, subdir) for subdir in sort_folders]

#     for destination_path in destination_paths:
#         if dry_run:
#             console.print(f"Dry run, not copying to '{destination_path}'...")
#         else:
#             shutil.copy(file_path, destination_path)
#             copy_file_creation_time(file_path, destination_path)

#         console.print(copied_file_log_message(file_path.name, destination_path))

#     _move_to_processed_dir(file_path, dry_run=dry_run)


# def _move_to_processed_dir(file_path: Path, dry_run: bool = True) -> None:
#     processed_file_path = Config.processed_screenshots_dir.joinpath(file_path.name)

#     if dry_run:
#         console.print(
#             f"Not moving file to {Config.sorted_screenshots_dir} because it's a dry run...",
#             style='dim'
#         )
#     elif file_path == processed_file_path:
#         console.print("Not moving file because it's the same location...", style='dim')
#     else:
#         console.print(f"Moving '{file_path}' to '{processed_file_path}'", style='dim')
#         shutil.move(file_path, processed_file_path)
