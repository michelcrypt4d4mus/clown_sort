"""
Global configuration.
"""
import csv
import logging
import re
import sys
from argparse import Namespace
from collections import namedtuple
from importlib.metadata import version
from os import environ
from pathlib import Path
from typing import List, Optional, Union

from rich import box
from rich.console import Console
from rich.table import Table
from rich.text import Text

from clown_sort.util.constants import CRYPTO_RULES_CSV_PATH, PACKAGE_NAME
from clown_sort.util.argument_parser import CRYPTO, parser
from clown_sort.util.filesystem_helper import MAC_SCREENSHOT_REGEX, subdirs_of_dir

StringOrPath = Union[str, Path]
SortRule = namedtuple('SortRule', ['folder', 'regex'])

RULES_CSV_PATH = 'RULES_CSV_PATH'

if RULES_CSV_PATH in environ:
    DEFAULT_RULES_CSV_PATH = str(environ.get(RULES_CSV_PATH))
else:
    DEFAULT_RULES_CSV_PATH = CRYPTO_RULES_CSV_PATH


class Config:
    debug: bool = False
    dry_run: bool = True
    leave_in_place: bool = False
    screenshots_only: bool = True
    filename_regex: re.Pattern = MAC_SCREENSHOT_REGEX
    sort_rules: List[SortRule] = []

    @classmethod
    def configure(cls):
        """Parse arguments and configure."""
        if '--version' in sys.argv:
            print(f"{PACKAGE_NAME} {version(PACKAGE_NAME)}")
            sys.exit()

        args: Namespace = parser.parse_args()

        if args.debug:
            Config.debug = True

        if args.rules_csv is None:
            rules_csvs = [CRYPTO_RULES_CSV_PATH]
        else:
            rules_csvs = [CRYPTO_RULES_CSV_PATH if arg == CRYPTO else arg for arg in args.rules_csv]

        destination_dir = args.destination_dir or args.screenshots_dir
        Config.set_directories(args.screenshots_dir, destination_dir, rules_csvs)
        Config.filename_regex = re.compile(args.filename_regex)
        Config.leave_in_place = True if args.leave_in_place else False

        if args.show_rules:
            Console().print(cls._rules_table())
            sys.exit()

        if args.execute:
            Config.dry_run = False
        else:
            print("Dry run...")

        if args.all:
            print("Processing all files in directory, not just 'Screenshot' files....")
            Config.screenshots_only = False

        if Config.debug:
            print(f"Rules CSV: {rules_csvs}")

    @classmethod
    def set_directories(
            cls,
            screenshots_dir: StringOrPath,
            destination_dir: StringOrPath,
            rules_csv_paths: List[StringOrPath]
    ) -> None:
        """Set the directories to find screenshots in and sort screenshots to."""
        screenshots_dir = Path(screenshots_dir or DEFAULT_SCREENSHOTS_DIR)
        destination_dir = Path(destination_dir or screenshots_dir)
        rules_csv_paths = [Path(r) for r in rules_csv_paths]

        for csv_path in rules_csv_paths:
            if not csv_path.is_file():
                print(f"'{csv_path}' is not a file.")
                sys.exit()
            else:
                cls.sort_rules += cls._load_rules_csv(csv_path)

        cls.screenshots_dir: Path = Path(screenshots_dir)
        cls.destination_dir: Path = Path(destination_dir or screenshots_dir)
        cls.sorted_screenshots_dir = cls.destination_dir.joinpath('Sorted')
        cls.processed_screenshots_dir = cls.destination_dir.joinpath('Processed')

        for dir in [cls.destination_dir, cls.sorted_screenshots_dir, cls.processed_screenshots_dir]:
            if not dir.is_dir():
                logging.warning(f"Need to create '{dir}'")
                dir.mkdir(parents=True, exist_ok=True)

        # TODO: this sucks
        if cls.debug:
            log = logging.getLogger(PACKAGE_NAME)
            log.setLevel('DEBUG')
            log.info(f"screenshots_dir: {cls.screenshots_dir}")
            log.info(f"destination_dir: {cls.destination_dir}")
            log.info(f"sorted_screenshots_dir: {cls.sorted_screenshots_dir}")
            log.info(f"processed_screenshots_dir: {cls.processed_screenshots_dir}")

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

    @classmethod
    def _rules_table(cls) -> Table:
        """Generate a table of the sort rules in effect."""
        table = Table(
            'Folder', 'Regex',
            title='Sorting Rules',
            title_style='color(153) italic dim',
            header_style='off_white',
            box=box.SIMPLE,
            show_edge=False,
            collapse_padding=True)

        for sort_rule in Config.sort_rules:
            table.add_row(sort_rule.folder, sort_rule.regex.pattern)

        table.columns[0].style = 'bright_red'
        table.columns[1].style = 'color(65)'
        return table
