"""
Entry point for all of the clown_sort scripts.
"""
import shutil
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

from clown_sort.util.argument_parser import (parse_text_extraction_args, parse_pdf_page_extraction_args,
     purge_arg_parser)
from clown_sort.config import Config
from clown_sort.files.image_file import ImageFile
from clown_sort.files.pdf_file import PdfFile
from clown_sort.files.sortable_file import SortableFile
from clown_sort.sort_selector import process_file_with_popup
from clown_sort.util.filesystem_helper import (IMAGE_FILE_EXTENSIONS, files_in_dir, is_image,
      is_pdf, set_timestamp_based_on_screenshot_filename)
from clown_sort.util.logging import log, set_log_level
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
    args: Namespace = parse_text_extraction_args()
    console.line()

    if args.debug:
        Config.enable_debug_mode()
    if args.print_as_parsed:
        Config.print_as_parsed = True

    for file_path in args.files_to_process:
        sortable_file = build_sortable_file(file_path)

        if isinstance(sortable_file, PdfFile):
            sortable_file.print_extracted_text(page_range=args.page_range)
        else:
            sortable_file.print_extracted_text()

        console.line(2)


def extract_pages_from_pdf() -> None:
    args = parse_pdf_page_extraction_args()
    PdfFile(args.pdf_file).extract_page_range(args.page_range, destination_dir=args.destination_dir)


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


def purge_non_images_from_dir() -> None:
    """Find all non images in a dir and purge them if they appear elsewhere in the sorted hierarchy."""
    args = Config.configure(purge_arg_parser)
    sorted_files = SortableFile.all_sorted_files()
    set_log_level('INFO')

    for subdir in args.subdirs_to_purge:
        console.print(f"Purging '{subdir}' of non-images...")

        for file_path in files_in_dir(Config.sorted_screenshots_dir.joinpath(subdir)):
            if not is_pdf(file_path):
                log.debug(f"Skipping image '{file_path}'...")
                continue

            basename = path.basename(file_path)
            console.print(f"Checking for '{basename}' in sorted files...")
            matching_files = [f for f in sorted_files if f.name == basename]

            if len(matching_files) <= 1:
                console.print(f" -> Only {len(matching_files)} copies of '{basename}'...", style="dim")
                continue

            processed_file_path = Config.processed_screenshots_dir.joinpath(basename)
            shutil.move(file_path, processed_file_path)
            console.print(f"    Found {len(matching_files)} copies of '{basename}'...")
            console.print(f"    Moved '{file_path}' to '{processed_file_path}'...", style="red")
            console.line()
