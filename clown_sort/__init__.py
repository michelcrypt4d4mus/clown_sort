from os import environ, getcwd, path
from pathlib import Path

from dotenv import load_dotenv

from clown_sort.config import Config
from clown_sort.sorter import screenshot_paths
from clown_sort.util.argument_parser import parse_arguments
from clown_sort.util.filesystem_helper import set_timestamp_based_on_screenshot_filename

# load_dotenv() should be called as soon as possible (before parsing local classes) but not for pytest
if not environ.get('INVOKED_BY_PYTEST', False):
    for dotenv_file in [path.join(dir, '.clown_sort') for dir in [getcwd(), Path.home()]]:
        if path.exists(dotenv_file):
            load_dotenv(dotenv_path=dotenv_file)
            break


def sort_screenshots():
    parse_arguments()

    for image in screenshot_paths(Config.screenshots_dir):
        image.sort_file()


def set_screenshot_timestamps():
    parse_arguments()

    for image in screenshot_paths(Config.screenshots_dir):
        set_timestamp_based_on_screenshot_filename(image.file_path)
