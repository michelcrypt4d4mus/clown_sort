"""
Global configuration.
"""
import csv
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

from clown_sort.util.argument_parser import CRYPTO, parser
from clown_sort.util.constants import CRYPTO_RULES_CSV_PATH, PACKAGE_NAME
from clown_sort.util.filesystem_helper import subdirs_of_dir
from clown_sort.util.logging import log, set_log_level

StringOrPath = Union[str, Path]
SortRule = namedtuple('SortRule', ['folder', 'regex'])

RULES_CSV_PATHS = 'RULES_CSV_PATHS'

if RULES_CSV_PATHS in environ:
    DEFAULT_RULES_CSV_PATHS = str(environ.get(RULES_CSV_PATHS)).split(':')
else:
    DEFAULT_RULES_CSV_PATHS = [CRYPTO_RULES_CSV_PATH]


class Config:
    debug: bool = False
    dry_run: bool = True
    manual_sort: bool = False
    only_if_match: bool = False
    leave_in_place: bool = False
    screenshots_only: bool = True
    delete_originals: bool = False
    rescan_sorted: bool = False
    yes_overwrite: bool = False
    sort_rules: List[SortRule] = []
    filename_regex: re.Pattern

    @classmethod
    def configure(cls):
        """Parse arguments and configure."""
        if '--version' in sys.argv:
            print(f"{PACKAGE_NAME} {version(PACKAGE_NAME)}")
            sys.exit()

        args: Namespace = parser.parse_args()

        if args.debug:
            Config.debug = True
            set_log_level('DEBUG')

        rules_csvs = args.rules_csv or DEFAULT_RULES_CSV_PATHS
        rules_csvs = [CRYPTO_RULES_CSV_PATH if arg == CRYPTO else arg for arg in rules_csvs]
        log.debug(f"Rules CSVs: {rules_csvs}")

        screenshots_dir = Path(args.screenshots_dir).expanduser()
        destination_dir = Path(args.destination_dir or args.screenshots_dir).expanduser()
        Config.set_directories(screenshots_dir, destination_dir, rules_csvs)
        Config.filename_regex = re.compile(args.filename_regex)
        Config.leave_in_place = True if args.leave_in_place else False
        Config.only_if_match = True if args.only_if_match else False
        Config.delete_originals = True if args.delete_originals else False
        Config.rescan_sorted = True if args.rescan_sorted else False
        Config.yes_overwrite = True if args.yes_overwrite else False

        if Config.leave_in_place and Config.delete_originals:
            Console().print("--leave-in-place and --delete-originals are mutually exclusive.", style='red')
            sys.exit()

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

        if args.manual_sort:
            _check_for_pysimplegui()
            Config.manual_sort = True

    @classmethod
    def set_directories(
            cls,
            screenshots_dir: StringOrPath,
            destination_dir: StringOrPath,
            rules_csv_paths: List[StringOrPath]
    ) -> None:
        """Set the directories to find screenshots in and sort screenshots to."""
        screenshots_dir = Path(screenshots_dir)
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
                log.warning(f"Need to create '{dir}'")
                dir.mkdir(parents=True, exist_ok=True)

        cls._log_configured_paths()

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
            header_style='color(245)',
            box=box.SIMPLE,
            show_edge=False,
            collapse_padding=True)

        for sort_rule in Config.sort_rules:
            table.add_row(sort_rule.folder, sort_rule.regex.pattern)

        table.columns[0].style = 'bright_red'
        table.columns[1].style = 'color(65)'
        return table

    @classmethod
    def _log_configured_paths(cls) -> None:
        log.debug(f"screenshots_dir: {cls.screenshots_dir}")
        log.debug(f"destination_dir: {cls.destination_dir}")
        log.debug(f"sorted_screenshots_dir: {cls.sorted_screenshots_dir}")
        log.debug(f"processed_screenshots_dir: {cls.processed_screenshots_dir}")


def _check_for_pysimplegui():
    try:
        import PySimpleGUI as sg
    except ModuleNotFoundError:
        msg = Text('ERROR: ', style='bright_red')

        msg.append(
            'PySimpleGUI package must be installed before you can use the manual selector. Try running:',
            style='bright_white'
        )
        log_optional_module_warning('PySimpleGUI', msg)
        sys.exit()


# TODO: it sucks that this is here but it's dependency hell otherwise
def log_optional_module_warning(module_name: str, msg: Optional[Text] = None) -> None:
    """msg is optional argument for a custom message, otherwise it's a warning"""
    if msg is None:
        msg = Text('WARNING: ', style='bright_red').append(
            f"Optional package '{module_name}' not installed. . Try running:",
            style='bright_white'
        )

    console = Console()
    console.line(2)
    console.print(msg)
    console.line(2)
    console.print(f"     pipx install clown_sort[{module_name}]", style='bright_cyan')
    console.line(2)

