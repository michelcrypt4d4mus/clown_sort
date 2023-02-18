"""
Global configuration.
"""
import csv
import importlib.resources
import logging
import re
import sys
from collections import namedtuple
from os import environ
from pathlib import Path
from typing import List, Optional, Union

#from social_arsenal.util.logging import log
from social_arsenal.util.filesystem_helper import subdirs_of_dir

OptionalPath = Optional[Union[str, Path]]
SortRule = namedtuple('SortRule', ['folder', 'regex'])

PACKAGE_NAME = 'social_arsenal'
DEFAULT_SCREENSHOTS_DIR = Path.home().joinpath('Pictures', 'Screenshots')
SORTING_RULES_DIR = importlib.resources.files(PACKAGE_NAME).joinpath('sorting_rules')
CRYPTO_RULES_CSV_PATH = str(SORTING_RULES_DIR.joinpath('crypto.csv'))
MAC_SCREENSHOT_REGEX = re.compile('^Screen Shot \\d{4}-\\d{2}-\\d{2} at \\d{1,2}\\.\\d{2}\\.\\d{2} [AP]M.(png|jpe?g)')

if 'RULES_CSV_PATH' in environ:
    DEFAULT_RULES_CSV_PATH = str(environ.get('RULES_CSV_PATH'))
else:
    DEFAULT_RULES_CSV_PATH = CRYPTO_RULES_CSV_PATH


class Config:
    debug: bool = False
    dry_run: bool = True
    leave_in_place: bool = False
    screenshots_only: bool = True
    filename_regex: re.Pattern = MAC_SCREENSHOT_REGEX

    @classmethod
    def set_directories(
            cls,
            screenshots_dir: OptionalPath = None,
            destination_dir: OptionalPath = None,
            rules_csv_path: OptionalPath = None
    ) -> None:
        """Set the directories to find screenshots in and sort screenshots to."""
        screenshots_dir = Path(screenshots_dir or DEFAULT_SCREENSHOTS_DIR)
        destination_dir = Path(destination_dir or screenshots_dir)
        rules_csv_path = Path(rules_csv_path or DEFAULT_RULES_CSV_PATH)

        if not rules_csv_path.is_file():
            print(f"'{rules_csv_path}' is not a file.")
            sys.exit()

        cls.sort_rules = cls._load_rules_csv(rules_csv_path)
        cls.screenshots_dir: Path = Path(screenshots_dir)
        cls.destination_dir: Path = Path(destination_dir or screenshots_dir)
        cls.sorted_screenshots_dir = cls.destination_dir.joinpath('Sorted')
        cls.processed_screenshots_dir = cls.destination_dir.joinpath('Processed')

        for dir in [cls.destination_dir, cls.sorted_screenshots_dir, cls.processed_screenshots_dir]:
            if not dir.is_dir():
                logging.warning(f"Need to create '{dir}'")
                dir.mkdir(parents=True, exist_ok=True)

    @classmethod
    def get_sort_dirs(cls) -> List[str]:
        """Returns a list of the subdirectories already created for sorted images."""
        return sorted(subdirs_of_dir(cls.sorted_screenshots_dir), key=lambda d: d.lower())

    @classmethod
    def _load_rules_csv(cls, file_path: Union[Path, str]) -> List[SortRule]:
        with open(Path(file_path), mode='r') as csvfile:
            return [
                SortRule(row['folder'], re.compile(row['regex'], re.IGNORECASE | re.MULTILINE))
                for row in csv.DictReader(csvfile, delimiter=',')
            ]
