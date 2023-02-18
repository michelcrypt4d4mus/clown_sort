import sys
from argparse import ArgumentError, ArgumentParser
from importlib.metadata import version

from rich_argparse_plus import RichHelpFormatterPlus

from social_arsenal.config import Config, CRYPTO_RULES_CSV_PATH, DEFAULT_SCREENSHOTS_DIR, PACKAGE_NAME

DESCRIPTION = "Sort, rename, and tag screenshots (and the occasional PDF) according to rules."
EPILOG = "Defaults are focused on crypto related screenshots."


RichHelpFormatterPlus.choose_theme('prince')

parser = ArgumentParser(
    formatter_class=RichHelpFormatterPlus,
    description=DESCRIPTION,
    epilog=EPILOG)

parser.add_argument('-e', '--execute', action='store_true',
                    help='execute the moves (default is dry run)')

parser.add_argument('-s', '--screenshots-dir',
                    metavar='SCREENSHOTS_DIR',
                    help='folder containing files you wish to sort',
                    default=DEFAULT_SCREENSHOTS_DIR)

parser.add_argument('-d', '--destination-dir',
                    metavar='DESTINATION_DIR',
                    help='destination folder to place sorted files (defaults to SCREENSHOTS_DIR/Sorted)')

parser.add_argument('-r', '--rules-csv',
                    metavar='RULES_FILE.CSV',
                    help='use a custom set of sorting rules',
                    default=CRYPTO_RULES_CSV_PATH)


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
        Config.dry_run = True

    Config.set_directories(
        screenshots_dir=args.screenshots_dir,
        destination_dir=args.destination_dir,
        rules_csv_path=args.rules_csv
    )

    return args
