import re
import sys
from argparse import ArgumentError, ArgumentParser
from importlib.metadata import version
from pathlib import Path

from rich_argparse_plus import RichHelpFormatterPlus

from social_arsenal.config import (Config, CRYPTO_RULES_CSV_PATH, DEFAULT_SCREENSHOTS_DIR,
    MAC_SCREENSHOT_REGEX, PACKAGE_NAME)

DESCRIPTION = "Sort, rename, and tag screenshots (and the occasional PDF) according to rules."
EPILOG = "Defaults are focused on crypto related screenshots."
CRYPTO = 'crypto_rules'


RichHelpFormatterPlus.choose_theme('prince')

parser = ArgumentParser(
    formatter_class=RichHelpFormatterPlus,
    description=DESCRIPTION,
    epilog=EPILOG)

parser.add_argument('-e', '--execute', action='store_true',
                    help='execute the file renames/moves (without this flag no actual changes will be made, you will just be shown the changes it plans to make)')

parser.add_argument('-a', '--all', action='store_true',
                    help="sort all image, movie, and PDF files (without this flag only files of the pattern 'Screen Shot 2023-02-18 at 3.06.44 AM.png' will be examined)")

parser.add_argument('-s', '--screenshots-dir',
                    metavar='SCREENSHOTS_DIR',
                    help='folder containing files you wish to sort',
                    default=str(DEFAULT_SCREENSHOTS_DIR))
                    #default=str(DEFAULT_SCREENSHOTS_DIR).replace(str(Path.home()), '~'))

parser.add_argument('-d', '--destination-dir',
                    metavar='DESTINATION_DIR',
                    help='destination folder to place sorted files (defaults to SCREENSHOTS_DIR/Sorted)')

parser.add_argument('-r', '--rules-csv',
                    metavar='RULES_FILE.CSV',
                    help='use a custom set of sorting rules',
                    default=CRYPTO)

parser.add_argument('-l', '--leave-in-place', action='store_true',
                    help='leave original file in place rather than moving to the SCREENSHOTS_DIR/Processed folder')

parser.add_argument('-f', '--filename-regex',
                    help='filename regular expression',
                    default=MAC_SCREENSHOT_REGEX.pattern)


def parse_arguments():
    """Parse command line args."""
    if '--version' in sys.argv:
        print(f"{PACKAGE_NAME} {version(PACKAGE_NAME)}")
        sys.exit()

    args = parser.parse_args()

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

    return args
