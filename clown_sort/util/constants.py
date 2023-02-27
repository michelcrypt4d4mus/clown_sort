"""
Constants in use across the application pulled from the environment as appropriate.
"""
import importlib.resources
import re
from os import environ
from pathlib import Path

PACKAGE_NAME = 'clown_sort'

# Sorting and destination paths
_DEFAULT_SCREENSHOTS_DIR = Path.home().joinpath('Pictures', 'Screenshots')
DEFAULT_SCREENSHOTS_DIR = Path(environ.get('CLOWN_SORT_SCREENSHOTS_DIR', _DEFAULT_SCREENSHOTS_DIR))
DEFAULT_DESTINATION_DIR = Path(environ.get('CLOWN_SORT_DESTINATION_DIR', _DEFAULT_SCREENSHOTS_DIR))

# Sorting rules stuff
SORTING_RULES_DIR = importlib.resources.files(PACKAGE_NAME).joinpath('sorting_rules')
CRYPTO_RULES_CSV_PATH = str(SORTING_RULES_DIR.joinpath('crypto.csv'))

# Filename regex stuff
MAC_SCREENSHOT_REGEX = re.compile('Screen Shot (\\d{4}-\\d{2}-\\d{2} at \\d{1,2}\\.\\d{2}\\.\\d{2} [AP]M).(png|jpe?g)')
ENV_FILENAME_REGEX = environ.get('CLOWN_SORT_FILENAME_REGEX')

if ENV_FILENAME_REGEX is None:
    DEFAULT_FILENAME_REGEX = MAC_SCREENSHOT_REGEX
else:
    DEFAULT_FILENAME_REGEX = re.compile(ENV_FILENAME_REGEX)
