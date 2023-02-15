from os import environ, getcwd, path
from pathlib import Path

from dotenv import load_dotenv

from image_namer.config import Config
from image_namer.image_file import ImageFile
from image_namer.sorter import sort_file


# load_dotenv() should be called as soon as possible (before parsing local classes) but not for pytest
if not environ.get('INVOKED_BY_PYTEST', False):
    for dotenv_file in [path.join(dir, '.screenshot_sorter') for dir in [getcwd(), Path.home()]]:
        if path.exists(dotenv_file):
            load_dotenv(dotenv_path=dotenv_file)
            break

Config.set_directories()


def sort_screenshots():
    for image in ImageFile.screenshot_paths():
        sort_file(image)
