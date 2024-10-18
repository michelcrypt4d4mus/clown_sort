"""
Functions and constants having to do with the filesystem.
importlib explanation: https://fossies.org/linux/Python/Lib/importlib/resources.py
"""
import os
import re
import stat
import time
from datetime import datetime
from getpass import getuser
from os import path
from pathlib import Path
from typing import List, Optional, Union

from filedate.Utils import Copy
from filedate import File
from rich.console import Console
from rich.text import Text

from clown_sort.util.constants import MAC_SCREENSHOT_REGEX, SCREENSHOT_REGEX
from clown_sort.util.logging import log
from clown_sort.util.string_helper import spaces_to_underscores

PDF_EXTENSION = '.pdf'
MOVIE_FILE_EXTENSIONS = ['.mov', '.flv', '.avi']
IMAGE_FILE_EXTENSIONS = [f".{ext}" for ext in 'tiff jpg jpeg png heic'.split()]
SORTABLE_FILE_EXTENSIONS = IMAGE_FILE_EXTENSIONS + [PDF_EXTENSION, '.mov']
MAC_SCREENSHOT_TIMESTAMP_FORMAT = '%Y-%m-%d at %I.%M.%S %p'

ANONYMIZED_USERNAME = 'uzor'
CURRENT_USERNAME = getuser()


def files_in_dir(dir: Union[os.PathLike, str], with_extname: Optional[str] = None) -> List[str]:
    """Paths for non-hidden, non-directory files, optionally ending in 'with_extname'."""
    files = [file for file in _non_hidden_files_in_dir(dir) if not path.isdir(file)]

    if with_extname:
        files = [f for f in files if f.endswith(f".{with_extname}")]

    return files


def subdirs_of_dir(dir: Union[os.PathLike, str]) -> List[str]:
    """Find non-hidden subdirs in 'dir'."""
    return [file for file in _non_hidden_files_in_dir(dir) if path.isdir(file)]


def timestamp_for_filename() -> str:
    """Returns a string showing current time in a file name friendly format."""
    return datetime.now().strftime("%Y-%m-%dT%H.%M.%S")


def strip_bad_chars(text: str) -> str:
    """Remove chars that don't work well in filenames."""
    text = ' '.join(text.splitlines()).replace('\\s+', ' ')
    text = re.sub('’', "'", text).replace('|', 'I').replace(',', ',')
    return re.sub('[^-0-9a-zA-Z@.,?_:=#\'\\$" ()]+', '_', text).replace('  ', ' ')


def strip_mac_screenshot(text: str) -> str:
    """Strip default macOS screenshot format from filename."""
    return re.sub(SCREENSHOT_REGEX, '', text).strip()


def is_image(file_path: Union[str, Path]) -> bool:
    return Path(file_path).suffix in IMAGE_FILE_EXTENSIONS


def is_movie(file_path: Union[str, Path]) -> bool:
    return Path(file_path).suffix in MOVIE_FILE_EXTENSIONS


def is_pdf(file_path: Union[str, Path]) -> bool:
    return Path(file_path).suffix == PDF_EXTENSION


def is_sortable(file_path: Union[str, Path]) -> bool:
    """Return True if it's a file clown_sort knows how to process."""
    return Path(file_path).suffix in SORTABLE_FILE_EXTENSIONS


def insert_suffix_before_extension(file_path: Path, suffix: str, separator: str = '__') -> Path:
    """Inserting 'page 1' suffix in 'path/to/file.jpg' -> '/path/to/file__page_1.jpg'."""
    suffix = spaces_to_underscores(strip_bad_chars(suffix))
    file_path_without_extension = file_path.with_suffix('')
    return Path(f"{file_path_without_extension}{separator}{suffix}{file_path.suffix}")


def create_dir_if_it_does_not_exist(dir: Path) -> None:
    """Like it says on the tin."""
    if dir.exists():
        return

    log.warning(f"Need to create '{dir}'")
    dir.mkdir(parents=True, exist_ok=True)


def copy_file_creation_time(source_file: Path, destination_file: Path) -> None:
    """Copy the file creation timestamp from source_file to destination_file."""
    try:
        Copy(str(source_file), str(destination_file)).all()
    except FileNotFoundError:
        msg = Text("WARNING! couldn't copy file creation timestamp because file does not exist for ")
        msg.append(f"'{destination_file}'!")
        Console().print(msg, style='bright_yellow')
        return

    _set_permissions(destination_file)


def set_timestamp_based_on_screenshot_filename(file_path: Path) -> None:
    """Infer a timestamp based on the filename and then change the 'Last Modified' property to match."""
    file_timestamp = extract_timestamp_from_filename(str(file_path))
    print(f"Parsed {file_timestamp} from '{file_path.name}'")
    print("    last modified: %s" % time.ctime(os.path.getmtime(file_path)))
    print("    created: %s" % time.ctime(os.path.getctime(file_path)))
    file_date = File(file_path)
    file_date.set(created = file_timestamp, modified = file_timestamp)
    _set_permissions(file_path)


def extract_timestamp_from_filename(filename: str) -> datetime:
    """Infer a timestamp based on the filename. Assumes there is an iso8601 section in filename."""
    filename = os.path.basename(filename)
    match = MAC_SCREENSHOT_REGEX.match(filename)

    if not match:
        raise ValueError(f"'{filename}' is not a timestamped screenshot file")

    return datetime.strptime(match.group(1), MAC_SCREENSHOT_TIMESTAMP_FORMAT)


def loggable_filename(file_path: Path, config: 'Config') -> str:
    """Return a loggable version of the filename."""
    if config.hide_dirs:
        return Path(file_path).name

    filename = str(file_path)

    if config.anonymize_user_dir:
        username_str = f"{path.sep}{CURRENT_USERNAME}{path.sep}"
        anonuser_str = f"{path.sep}{ANONYMIZED_USERNAME}{path.sep}"
        return filename.replace(username_str, anonuser_str)
    else:
        return filename


def _non_hidden_files_in_dir(dir: Union[os.PathLike, str]) -> List[str]:
    return [path.join(dir, file) for file in os.listdir(dir) if not file.startswith('.')]


def _set_permissions(file_path: Path) -> None:
    """The filedate library has a bad habit of changing all the permissions so we change them back."""
    os.chmod(file_path, stat.S_IRUSR | stat.S_IWUSR | stat.S_IRGRP | stat.S_IROTH)
