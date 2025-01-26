"""
Parse arguments for both the main sort_screenshots() as well as extract_text_from_files().
"""
import re
import sys
from argparse import ArgumentParser, Namespace
from os import environ
from pathlib import Path

from rich_argparse_plus import RichHelpFormatterPlus

from clown_sort.lib.page_range import PageRange, PageRangeArgumentValidator
from clown_sort.util.constants import (CRYPTO, DEFAULT_SCREENSHOTS_DIR, DEFAULT_DESTINATION_DIR,
     DEFAULT_FILENAME_REGEX)
from clown_sort.util.filesystem_helper import files_in_dir, is_pdf
from clown_sort.util.logging import log

DESCRIPTION = "Sort, rename, and tag screenshots (and the occasional PDF) according to rules."
EPILOG = "Defaults are focused on crypto related screenshots."
page_range_validator = PageRangeArgumentValidator()
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

parser.add_argument('-s', '--screenshots-dir',
                    metavar='SCREENSHOTS_DIR',
                    help='folder containing files you wish to sort',
                    default=str(DEFAULT_SCREENSHOTS_DIR).replace(str(Path.home()), '~'))

parser.add_argument('-d', '--destination-dir',
                    metavar='DESTINATION_DIR',
                    help='destination folder to place the Sorted/ and Processed/ dirs (default: SCREENSHOTS_DIR)',
                    default=str(DEFAULT_DESTINATION_DIR).replace(str(Path.home()), '~'))

parser.add_argument('-r', '--rules-csv',
                    action='append',
                    metavar='RULES_FILE.CSV',
                    help=f"sorting rules can be supplied more than once (use string '{CRYPTO}' to use the defaults)")

parser.add_argument('-f', '--filename-regex',
                    help='filename regular expression',
                    default=DEFAULT_FILENAME_REGEX.pattern)

parser.add_argument('-l', '--leave-in-place', action='store_true',
                    help='leave original file in place rather than moving to the SCREENSHOTS_DIR/Processed folder')

parser.add_argument('-m', '--manual-sort', action='store_true',
                    help='causes a popup to be presented for each file where it can be manually named and a sorting destination selected (experimental)')

parser.add_argument('-mf', '--manual-fallback', action='store_true',
                    help='causes a popup to be presented for each file only as a fallback when no sort rules are matched (experimental)')

parser.add_argument('-y', '--yes-overwrite', action='store_true',
                    help='skip confirmation prompt and always overwrite if a file with the same name already exists')

parser.add_argument('--hide-dirs', action='store_true',
                    help='hide directories in log output (only show basenames)')

parser.add_argument('--anonymize-user-dir', action='store_true',
                    help='anonymize the user directory in log output')

parser.add_argument('--rescan-sorted', action='store_true',
                    help="rescan already sorted files (useful if you updated your sorting rules)")

parser.add_argument('--delete-originals', action='store_true',
                    help="don't preserve the original screenshots in the Processed/ folder")

parser.add_argument('--show-rules', action='store_true',
                    help='display the sorting rules and exit')

parser.add_argument('--debug', action='store_true',
                    help='turn on debug level logging')


############################################
# Parse args for extract_text_from_files() #
############################################
extract_text_parser = ArgumentParser(
    formatter_class=RichHelpFormatterPlus,
    description="Extract the text from one or more files or directories.",
    epilog="If any of the FILE_OR_DIRs is a directory all files in that directory will be extracted."
)

extract_text_parser.add_argument('file_or_dir', nargs='+', metavar='FILE_OR_DIR')
extract_text_parser.add_argument('--debug', action='store_true', help='turn on debug level logging')

extract_text_parser.add_argument('--page-range', '-r',
                                 type=page_range_validator,
                                 help=f"[PDFs only] {page_range_validator.HELP_MSG}")

extract_text_parser.add_argument('--print-as-parsed', '-p',
                                 action='store_true',
                                 help='print pages as they are parsed instead of waiting until document is fully parsed')


def parse_text_extraction_args() -> Namespace:
    args = extract_text_parser.parse_args()
    args.files_to_process = []

    for file_or_dir in args.file_or_dir:
        file_path = Path(file_or_dir)

        if not file_path.exists():
            log.error(f"File '{file_path}' doesn't exist!")
            sys.exit(-1)
        elif file_path.is_dir():
            args.files_to_process.extend(files_in_dir(file_path))
        else:
            args.files_to_process.append(file_path)

    if args.page_range and (len(args.files_to_process) > 1 or not is_pdf(args.files_to_process[0])):
        log.error(f"--page-range can only be specified for a single PDF")
        sys.exit(-1)

    return args


###########################################
# Parse args for extract_pages_from_pdf() #
###########################################
extract_pdf_parser = ArgumentParser(
    formatter_class=RichHelpFormatterPlus,
    description="Extract pages from one PDF into a new PDF.",
)

extract_pdf_parser.add_argument('pdf_file', metavar='PDF_FILE', help='PDF to extract pages from')

extract_pdf_parser.add_argument('--page-range', '-r',
                                type=page_range_validator,
                                help=page_range_validator.HELP_MSG,
                                required=True)

extract_pdf_parser.add_argument('--destination-dir', '-d',
                                help="directory to write the new PDF to",
                                default=Path.cwd())

extract_pdf_parser.add_argument('--debug', action='store_true', help='turn on debug level logging')


def parse_pdf_page_extraction_args() -> Namespace:
    args = extract_pdf_parser.parse_args()

    if not is_pdf(args.pdf_file):
        log.error(f"'{args.pdf_file}' is not a PDF.")
        sys.exit(-1)
    elif not Path(args.destination_dir).exists():
        log.error(f"Destination dir '{args.destination_dir}' does not exist.")
        sys.exit(1)

    return args


##############################################
# Parse args for purge_non_images_from_dir() #
##############################################
purge_arg_parser = ArgumentParser(
    add_help=False,
    description="Check if a file exists in the sorted directory structure.",
    parents=[parser],
)

purge_arg_parser.add_argument(
    'subdirs_to_purge',
    help='Sorted subdirectories to purge non-image files from',
    metavar='DIR',
    nargs='+')
