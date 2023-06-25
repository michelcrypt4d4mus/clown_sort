import sys
from argparse import Namespace
from glob import glob
from os import environ, getcwd, path
from pathlib import Path
from typing import List, Union

from dotenv import load_dotenv

# load_dotenv() should be called as soon as possible (before parsing local classes) but not for pytest
if not environ.get('INVOKED_BY_PYTEST', False):
    for dotenv_file in [path.join(dir, '.clown_sort') for dir in [getcwd(), Path.home()]]:
        if path.exists(dotenv_file):
            load_dotenv(dotenv_path=dotenv_file)
            break

from clown_sort.util.argument_parser import extraction_parser
from clown_sort.config import Config
from clown_sort.files.image_file import ImageFile
from clown_sort.files.pdf_file import PdfFile
from clown_sort.files.sortable_file import SortableFile
from clown_sort.sort_selector import process_file_with_popup
from clown_sort.util.filesystem_helper import (IMAGE_FILE_EXTENSIONS, files_in_dir, is_image,
      is_pdf, set_timestamp_based_on_screenshot_filename)
from clown_sort.util.logging import log
from clown_sort.util.rich_helper import console


def sort_screenshots():
    Config.configure()

    if Config.rescan_sorted:
        _rescan_sorted_screenshots()
        return

    for file_to_sort in screenshot_paths(Config.screenshots_dir):
        if Config.manual_sort:
            if file_to_sort._can_be_presented_in_popup():
                process_file_with_popup(file_to_sort)
            else:
                print(f"'{file_to_sort.file_path}' is not suitable for manual sort, skipping...")
        else:
            file_to_sort.sort_file()


def extract_text_from_files() -> None:
    """
    Extract text from a single file or from all files in a given directory. Can accept
    multiple paths as arguments on the command line.
    """
    args: Namespace = extraction_parser.parse_args()
    console.line()
    files_to_process = []

    if args.debug:
        Config.enable_debug_mode()

    for file_or_dir in args.file_or_dir:
        file_path = Path(file_or_dir)

        if not file_path.exists():
            console.print(f"File '{file_path}' doesn't exist!")
            sys.exit()
        elif file_path.is_dir():
            files_to_process.extend(files_in_dir(file_path))
        else:
            files_to_process.append(file_path)

    for file_path in files_to_process:
        build_sortable_file(file_path).print_extracted_text()
        console.line(2)


def set_screenshot_timestamps_from_filenames():
    """Parse the filenames to reset the file creation timestamps."""
    Config.configure()

    for image in screenshot_paths(Config.screenshots_dir):
        set_timestamp_based_on_screenshot_filename(image.file_path)


def _rescan_sorted_screenshots():
    """Rescan sorted folders."""
    console.print(f"Rescanning '{Config.sorted_screenshots_dir}'...")
    sortable_files: List[SortableFile] = []
    file_paths: List[str] = []

    for extname in IMAGE_FILE_EXTENSIONS:
        for pattern in ['*', '**/*']:
            glob_pattern = Config.sorted_screenshots_dir.joinpath(f"{pattern}{extname}")
            log.debug(f"Adding '{glob_pattern}' to glob patterns...")
            file_paths.extend(glob(str(glob_pattern)))

    for file_path in file_paths:
        if Config.screenshots_only and not Config.filename_regex.match(path.basename(file_path)):
            log.debug(f"Skipping '{file_path}' because it doesn't match the filename_regex...")
            continue

        sortable_files.append(build_sortable_file(file_path))

    console.print(
        f"Re-processing {len(sortable_files)} files in '{Config.sorted_screenshots_dir}'...",
        style='bright_green'
    )

    for file_path in sortable_files:
        file_path.sort_file()


def screenshot_paths(dir: Path) -> List[SortableFile]:
    """Returns a list of ImageFiles for all the screenshots to be sorted."""
    screenshots = [
        build_sortable_file(f) for f in files_in_dir(Config.screenshots_dir)
        if not Config.screenshots_only or Config.filename_regex.match(path.basename(f))
    ]

    return sorted(screenshots, key=lambda f: f.basename)


def build_sortable_file(file_path: Union[str, Path]) -> SortableFile:
    """Decide if it's a PDF, image, or other type of file."""
    if is_image(file_path):
        return ImageFile(file_path)
    elif is_pdf(file_path):
        return PdfFile(file_path)
    else:
        return SortableFile(file_path)
