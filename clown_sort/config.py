"""
Global configuration.
"""
import re
import sys
from argparse import ArgumentParser, Namespace
from importlib.metadata import version
from os import environ
from pathlib import Path
from typing import List, Optional, Union

from rich import box
from rich.console import Console
from rich.table import Table
from rich.text import Text

from clown_sort.sort_rule import SortRule, SortRuleParseError
from clown_sort.util import rich_helper
from clown_sort.util.argument_parser import parser
from clown_sort.util.constants import PACKAGE_NAME
from clown_sort.util.filesystem_helper import create_dir_if_it_does_not_exist, subdirs_of_dir
from clown_sort.util.logging import log, set_log_level


class Config:
    # Non-boolean config vars
    filename_regex: re.Pattern
    sort_rules: List[SortRule] = []
    # Boolean config vars
    anonymize_user_dir: bool = False
    delete_originals: bool = False
    debug: bool = False
    dry_run: bool = True
    hide_dirs: bool = False
    leave_in_place: bool = False
    manual_sort: bool = False
    manual_fallback: bool = False
    only_if_match: bool = False
    print_as_parsed: bool = False
    rescan_sorted: bool = False
    screenshots_only: bool = True
    yes_overwrite: bool = False

    @classmethod
    def configure(cls, _parser: Optional[ArgumentParser] = None) -> Namespace:
        """Parse arguments and configure."""
        if '--version' in sys.argv:
            print(f"{PACKAGE_NAME} {version(PACKAGE_NAME)}")
            sys.exit()

        args: Namespace = (_parser or parser).parse_args()

        if args.debug:
            cls.enable_debug_mode()

        Config.filename_regex = re.compile(args.filename_regex)
        Config.anonymize_user_dir = True if args.anonymize_user_dir else False
        Config.delete_originals = True if args.delete_originals else False
        Config.hide_dirs = True if args.hide_dirs else False
        Config.leave_in_place = True if args.leave_in_place else False
        Config.only_if_match = True if args.only_if_match else False
        Config.rescan_sorted = True if args.rescan_sorted else False
        Config.yes_overwrite = True if args.yes_overwrite else False

        screenshots_dir = Path(args.screenshots_dir).expanduser()
        destination_dir = Path(args.destination_dir or args.screenshots_dir).expanduser()
        rules_csvs = SortRule.sort_rules_csvs(args.rules_csv)
        log.debug(f"Rules CSVs: {rules_csvs}")
        Config.set_directories(screenshots_dir, destination_dir, rules_csvs)

        if Config.leave_in_place and Config.delete_originals:
            Console().print("--leave-in-place and --delete-originals are mutually exclusive.", style='red')
            sys.exit(-1)

        if args.show_rules:
            Console().print(cls._rules_table())
            sys.exit()

        if args.execute:
            Config.dry_run = False
            rich_helper.is_dry_run = False
        else:
            print("Dry run...")

        if args.all:
            print("Processing all files in directory, not just 'Screenshot' files....")
            Config.screenshots_only = False

        if args.manual_sort or args.manual_fallback:
            _check_for_pysimplegui()

            if args.manual_sort:
                Config.manual_sort = True
            if args.manual_fallback:
                if Config.only_if_match:
                    Console().print('Only one of --manual-fallback and --only-if-match can be specified.', style='red')
                    sys.exit(-1)

                Config.manual_fallback = True

        return args

    @classmethod
    def set_directories(
            cls,
            screenshots_dir: Path,
            destination_dir: Path,
            rules_csv_paths: List[Path]
    ) -> None:
        """Set the directories to find screenshots in and sort screenshots to."""
        screenshots_dir = Path(screenshots_dir)
        destination_dir = Path(destination_dir or screenshots_dir)
        rules_csv_paths = [Path(r) for r in rules_csv_paths]

        for csv_path in rules_csv_paths:
            if not csv_path.is_file():
                print(f"ERROR: '{csv_path}' is not a file.")
                sys.exit(-1)

            try:
                cls.sort_rules += SortRule.load_rules_csv(csv_path)
            except SortRuleParseError:
                sys.exit(-1)

        cls.screenshots_dir: Path = Path(screenshots_dir)
        cls.destination_dir: Path = Path(destination_dir or screenshots_dir)
        cls.sorted_screenshots_dir = cls.destination_dir.joinpath('Sorted')
        cls.processed_screenshots_dir = cls.destination_dir.joinpath('Processed')
        cls.pdf_errors_dir = cls.destination_dir.joinpath('PDF Errors')

        for dir in [cls.destination_dir, cls.sorted_screenshots_dir, cls.processed_screenshots_dir]:
            create_dir_if_it_does_not_exist(dir)

        cls._log_configured_paths()

    @classmethod
    def get_sort_dirs(cls) -> List[str]:
        """Returns a list of the subdirectories already created for sorted images."""
        return sorted(subdirs_of_dir(cls.sorted_screenshots_dir), key=lambda d: d.lower())

    @classmethod
    def enable_debug_mode(cls) -> None:
        Config.debug = True
        set_log_level('DEBUG')

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
            collapse_padding=True
        )

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
        log.debug(f"pdf_errors_dir: {cls.pdf_errors_dir}")


def _check_for_pysimplegui():
    try:
        import PySimpleGUI as sg
    except ModuleNotFoundError:
        msg = Text('ERROR', style='bright_red')

        msg.append(
            ': PySimpleGUI package must be installed before you can use the manual selector. Try running:',
            style='bright_white'
        )

        log_optional_module_warning('gui', msg)
        console = Console(color_system='256')
        #console.line()
        console.print(f"You make also need to install 'python-tk'. In macOS this can be installed with 'brew install python-tk'.")
        sys.exit()


def check_for_pymupdf() -> bool:
    try:
        import fitz
        return True
    except ModuleNotFoundError:
        log_optional_module_warning('pdf')
        return False


# TODO: it sucks that this is here but it's dependency hell otherwise
def log_optional_module_warning(module_name: str, msg: Optional[Text] = None) -> None:
    """msg is optional argument for a custom message, otherwise it's a warning"""
    if msg is None:
        msg = Text('WARNING', style='bright_red').append(
            f": Optional package '{module_name}' not installed. Try running:",
            style='bright_white'
        )

    console = Console(color_system='256')
    console.line()
    console.print(msg)
    console.line()
    console.print(f"     pipx install clown_sort\\[{module_name}] --force", style='bright_cyan')
    console.line()
    console.print(f"'pip install' works if you're not using pipx. Use 'poetry install --all-extras' if you're in a development environment.")
