import re
import sys
from argparse import ArgumentError, ArgumentParser
from importlib.metadata import version
from pathlib import Path

from rich import box
from rich.table import Table
from rich.text import Text
from rich_argparse_plus import RichHelpFormatterPlus

from clown_sort.config import (Config, CRYPTO_RULES_CSV_PATH, DEFAULT_SCREENSHOTS_DIR,
    MAC_SCREENSHOT_REGEX, PACKAGE_NAME)
from clown_sort.util.logging import console

DESCRIPTION = "Sort, rename, and tag screenshots (and the occasional PDF) according to rules."
EPILOG = "Defaults are focused on crypto related screenshots."
CRYPTO = 'crypto_rules'


RichHelpFormatterPlus.choose_theme('prince')

parser = ArgumentParser(
    formatter_class=RichHelpFormatterPlus,
    description=DESCRIPTION,
    epilog=EPILOG)

parser.add_argument('-e', '--execute', action='store_true',
                    help='without this flag no actual changes will be made (you will see the logs of the changes it plans to make)')

parser.add_argument('-a', '--all', action='store_true',
                    help="sort all image, movie, and PDF files is SCREENSHOTS_DIR (without this flag only files of the pattern 'Screen Shot 2023-02-18 at 3.06.44 AM.png' will be examined)")

parser.add_argument('-l', '--leave-in-place', action='store_true',
                    help='leave original file in place rather than moving to the SCREENSHOTS_DIR/Processed folder')

parser.add_argument('-s', '--screenshots-dir',
                    metavar='SCREENSHOTS_DIR',
                    help='folder containing files you wish to sort',
                    default=str(DEFAULT_SCREENSHOTS_DIR))
                    #default=str(DEFAULT_SCREENSHOTS_DIR).replace(str(Path.home()), '~'))

parser.add_argument('-d', '--destination-dir',
                    metavar='DESTINATION_DIR',
                    help='destination folder to place the Sorted/ and Processed/ dirs (default: SCREENSHOTS_DIR)')

parser.add_argument('-r', '--rules-csv',
                    metavar='RULES_FILE.CSV',
                    help='use a custom set of sorting rules',
                    default=CRYPTO)

parser.add_argument('-f', '--filename-regex',
                    help='filename regular expression',
                    default=MAC_SCREENSHOT_REGEX.pattern)

parser.add_argument('--show-rules', action='store_true',
                    help='display the sorting rules and exit')

parser.add_argument('--debug', action='store_true',
                    help='turn on debug level logging')


def parse_arguments():
    """Parse command line args."""
    if '--version' in sys.argv:
        print(f"{PACKAGE_NAME} {version(PACKAGE_NAME)}")
        sys.exit()

    args = parser.parse_args()

    if args.debug:
        Config.debug = True

    if args.execute:
        print("Executing...")
        Config.dry_run = False
    else:
        print("Dry run...")

    if args.leave_in_place:
        Config.leave_in_place = True

    if args.all:
        print("Processing all files in directory, not just 'Screenshot' files....")
        Config.screenshots_only = False

    if args.filename_regex:
        Config.filename_regex = re.compile(args.filename_regex)

    Config.set_directories(
        screenshots_dir=args.screenshots_dir,
        destination_dir=args.destination_dir,
        rules_csv_path=args.rules_csv if args.rules_csv != CRYPTO else CRYPTO_RULES_CSV_PATH
    )

    if args.show_rules:
        console.print(_rules_table())
        sys.exit()

    return args


def _rules_table() -> Table:
    table = Table(
        'Folder', 'Regex',
        title='Sorting Rules',
        title_style='color(153) italic dim',
        header_style='off_white',
        #style='dim',
        box=box.SIMPLE,
        show_edge=False,

        collapse_padding=True)

    for sort_rule in Config.sort_rules:
        table.add_row(sort_rule.folder, sort_rule.regex.pattern)

    table.columns[0].style = 'bright_red'
    table.columns[1].style = 'color(65)'
    return table
