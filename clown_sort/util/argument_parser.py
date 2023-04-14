from argparse import ArgumentParser
from os import environ
from pathlib import Path

from rich_argparse_plus import RichHelpFormatterPlus

from clown_sort.util.constants import (DEFAULT_SCREENSHOTS_DIR, DEFAULT_DESTINATION_DIR,
     DEFAULT_FILENAME_REGEX)

CRYPTO = 'crypto'
DESCRIPTION = "Sort, rename, and tag screenshots (and the occasional PDF) according to rules."
EPILOG = "Defaults are focused on crypto related screenshots."


RichHelpFormatterPlus.choose_theme('prince')

parser = ArgumentParser(
    formatter_class=RichHelpFormatterPlus,
    description=DESCRIPTION,
    epilog=EPILOG
)

parser.add_argument('-e', '--execute', action='store_true',
                    help='without this flag no actual changes will be made (you will see the logs of the changes it plans to make)')

parser.add_argument('-a', '--all', action='store_true',
                    help="sort all image, movie, and PDF files in SCREENSHOTS_DIR (without this flag only files matching the --filename-regex argument will be examined)")

parser.add_argument('-o', '--only-if-match', action='store_true',
                    help="only move a file if it matches at least one rule (default is to move to DESTINATION_DIR)")

parser.add_argument('-l', '--leave-in-place', action='store_true',
                    help='leave original file in place rather than moving to the SCREENSHOTS_DIR/Processed folder')

parser.add_argument('-s', '--screenshots-dir',
                    metavar='SCREENSHOTS_DIR',
                    help='folder containing files you wish to sort',
                    default=str(DEFAULT_SCREENSHOTS_DIR).replace(str(Path.home()), '~'))

parser.add_argument('-d', '--destination-dir',
                    metavar='DESTINATION_DIR',
                    help='destination folder to place the Sorted/ and Processed/ dirs (default: SCREENSHOTS_DIR)',
                    default=str(DEFAULT_DESTINATION_DIR).replace(str(Path.home()), '~'))

parser.add_argument('-m', '--manual-sort', action='store_true',
                    help='causes a popup to be presented for each file where it can be manually named and a sorting destination selected (experimental)')

parser.add_argument('-r', '--rules-csv',
                    action='append',
                    metavar='RULES_FILE.CSV',
                    help=f"sorting rules can be supplied more than once (use string '{CRYPTO}' to use the defaults)")

parser.add_argument('-f', '--filename-regex',
                    help='filename regular expression',
                    default=DEFAULT_FILENAME_REGEX.pattern)

parser.add_argument('-y', '--yes-overwrite', action='store_true',
                    help='skip confirmation prompt and always overwrite if a file with the same name already exists')

parser.add_argument('--rescan-sorted', action='store_true',
                    help="rescan already sorted files (useful if you updated your sorting rules)")

parser.add_argument('--delete-originals', action='store_true',
                    help="don't preserve the original screenshots in the Processed/ folder")

parser.add_argument('--show-rules', action='store_true',
                    help='display the sorting rules and exit')

parser.add_argument('--debug', action='store_true',
                    help='turn on debug level logging')
