from os import environ, getcwd, path
from pathlib import Path

from dotenv import load_dotenv

from image_namer.config import Config
from image_namer.files.image_file import ImageFile
from image_namer.sorter import sort_file_by_ocr, sort_file_by_filename
from image_namer.util.argument_parser import parse_arguments


# load_dotenv() should be called as soon as possible (before parsing local classes) but not for pytest
if not environ.get('INVOKED_BY_PYTEST', False):
    for dotenv_file in [path.join(dir, '.screenshot_sorter') for dir in [getcwd(), Path.home()]]:
        if path.exists(dotenv_file):
            load_dotenv(dotenv_path=dotenv_file)
            break



def sort_screenshots():
    args = parse_arguments()

    for image in ImageFile.screenshot_paths():
        sort_file_by_ocr(image, args.dry_run)


def sort_non_screenshots():
    args = parse_arguments()

    for file in ImageFile.sortable_non_screenshot_paths():
        sort_file_by_filename(file, args.dry_run)
