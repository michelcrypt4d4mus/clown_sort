import importlib.resources
from os import environ
from pathlib import Path

_DEFAULT_SCREENSHOTS_DIR = Path.home().joinpath('Pictures', 'Screenshots')

PACKAGE_NAME = 'clown_sort'
DEFAULT_SCREENSHOTS_DIR = Path(environ.get('CLOWN_SORT_SCREENSHOTS_DIR', _DEFAULT_SCREENSHOTS_DIR))
DEFAULT_DESTINATION_DIR = Path(environ.get('CLOWN_SORT_DESTINATION_DIR', _DEFAULT_SCREENSHOTS_DIR))
SORTING_RULES_DIR = importlib.resources.files(PACKAGE_NAME).joinpath('sorting_rules')
CRYPTO_RULES_CSV_PATH = str(SORTING_RULES_DIR.joinpath('crypto.csv'))
