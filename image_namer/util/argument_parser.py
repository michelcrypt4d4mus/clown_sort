import sys
from argparse import ArgumentError, ArgumentParser
from collections import namedtuple
from functools import partial, update_wrapper
from importlib.metadata import version
from os import environ, getcwd, path
from typing import List

from rich_argparse_plus import RichHelpFormatterPlus

DESCRIPTION = "Sort screenshots according to rules."
EPILOG = "Currently focused on crypto related screenshots."
PACKAGE_NAME = 'image_namer'

RichHelpFormatterPlus.choose_theme('prince')

parser = ArgumentParser(
    formatter_class=RichHelpFormatterPlus,
    description=DESCRIPTION,
    epilog=EPILOG)

parser.add_argument('-e', '--execute', action='store_true',
                    help='execute the moves (default is dry run)')


# The Parsening Begins
def parse_arguments():
    """Parse command line args."""
    if '--version' in sys.argv:
        print(f"{PACKAGE_NAME} {version(PACKAGE_NAME)}")
        sys.exit()

    args = parser.parse_args()

    if args.execute:
        print("Executing...")
        args.dry_run = False
    else:
        print("Dry run...")
        args.dry_run = True

    return args
