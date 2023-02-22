import importlib.resources
from pathlib import Path

PACKAGE_NAME = 'clown_sort'
DEFAULT_SCREENSHOTS_DIR = Path.home().joinpath('Pictures', 'Screenshots')
SORTING_RULES_DIR = importlib.resources.files(PACKAGE_NAME).joinpath('sorting_rules')
CRYPTO_RULES_CSV_PATH = str(SORTING_RULES_DIR.joinpath('crypto.csv'))
