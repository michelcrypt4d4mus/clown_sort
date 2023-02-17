import sys
from argparse import ArgumentError, ArgumentParser
from importlib.metadata import version

from rich_argparse_plus import RichHelpFormatterPlus

from image_namer.config import Config, PACKAGE_NAME

DESCRIPTION = "Sort screenshots according to rules."
EPILOG = "Currently focused on crypto related screenshots."

RichHelpFormatterPlus.choose_theme('prince')

parser = ArgumentParser(
    formatter_class=RichHelpFormatterPlus,
    description=DESCRIPTION,
    epilog=EPILOG)

parser.add_argument('-e', '--execute', action='store_true',
                    help='execute the moves (default is dry run)')


# The Parsening Begins
def parse_arguments():
    Config.set_directories()

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

    return args
