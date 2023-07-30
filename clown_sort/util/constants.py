"""
Constants in use across the application pulled from the environment as appropriate.
"""
import re
from os import environ
from pathlib import Path

PACKAGE_NAME = 'clown_sort'
MAC_DEFAULT_SCREENSHOTS_DIR = Path.home().joinpath('Pictures', 'Screenshots')

# Miscellaneous strings
CRYPTO = 'crypto'
PDF_ERRORS = 'PDF Errors'


### Environment variables
# build_env_var_string('XYZ') => 'CLOWN_SORT_XYZ'
build_env_var_string = lambda label: f"{PACKAGE_NAME.upper()}_{label}"

# build_env_var_dir_string('XYZ') => 'CLOWN_SORT_XYZ_DIR'
build_env_var_dir_string = lambda label: build_env_var_string(f"{label}_DIR")

# Check in env for a value for CLOWN_SORT_SCREENSHOTS_DIR etc, default to MAC_DEFAULT_SCREENSHOTS_DIR
get_dir_from_env_var = lambda label: Path(environ.get(build_env_var_dir_string(label), MAC_DEFAULT_SCREENSHOTS_DIR))

# Source and destination dirs
DEFAULT_SCREENSHOTS_DIR = get_dir_from_env_var('SCREENSHOTS')
DEFAULT_DESTINATION_DIR = get_dir_from_env_var('DESTINATION')


# Filename regex stuff
SCREENSHOT_REGEX = re.compile('Screen Shot (\\d{4}-\\d{2}-\\d{2} at \\d{1,2}\\.\\d{2}\\.\\d{2} [AP]M)')
MAC_SCREENSHOT_REGEX = re.compile('Screen Shot (\\d{4}-\\d{2}-\\d{2} at \\d{1,2}\\.\\d{2}\\.\\d{2} [AP]M).(png|jpe?g)')
ENV_FILENAME_REGEX = environ.get('CLOWN_SORT_FILENAME_REGEX')

if ENV_FILENAME_REGEX is None:
    DEFAULT_FILENAME_REGEX = MAC_SCREENSHOT_REGEX
else:
    DEFAULT_FILENAME_REGEX = re.compile(ENV_FILENAME_REGEX)


# PDF related
# TODO: make this an argument
MIN_PDF_SIZE_TO_LOG_PROGRESS_TO_STDERR = 1024 * 1024 * 20
