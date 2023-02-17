from os import environ, getcwd, path
from pathlib import Path

from dotenv import load_dotenv

from image_namer.sorter import screenshot_paths, sortable_non_screenshot_paths
from image_namer.util.argument_parser import parse_arguments


# load_dotenv() should be called as soon as possible (before parsing local classes) but not for pytest
if not environ.get('INVOKED_BY_PYTEST', False):
    for dotenv_file in [path.join(dir, '.screenshot_sorter') for dir in [getcwd(), Path.home()]]:
        if path.exists(dotenv_file):
            load_dotenv(dotenv_path=dotenv_file)
            break

parse_arguments()


def sort_screenshots():
    for image in screenshot_paths():
        image.sort_file()


def sort_non_screenshots():
    for file in sortable_non_screenshot_paths():
        file.sort_file()
