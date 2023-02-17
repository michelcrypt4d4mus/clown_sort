"""
Functions and constants having to do with the filesystem.
importlib explanation: https://fossies.org/linux/Python/Lib/importlib/resources.py
"""
import os
import stat
from datetime import datetime
from os import path
from pathlib import Path
from typing import List, Optional, Union

from filedate.Utils import Copy

PDF_EXTENSION = '.pdf'
IMAGE_FILE_EXTENSIONS = [f".{ext}" for ext in 'tiff jpg jpeg png heic'.split()]
MOVIE_FILE_EXTENSIONS = ['.mov', '.flv', '.avi']
SORTABLE_FILE_EXTENSIONS = IMAGE_FILE_EXTENSIONS + [PDF_EXTENSION, '.mov']


def files_in_dir(dir: Union[os.PathLike, str], with_extname: Optional[str] = None) -> List[str]:
    """Paths for non-hidden files, optionally ending in 'with_extname'"""
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


def copy_file_creation_time(source_file: Path, destination_file: Path) -> None:
    """Copy the file creation timestamp from source_file to destination_file."""
    Copy(str(source_file), str(destination_file)).modified()
    # The filedate library has a bad habit of changing all the permissions so we change them back.
    os.chmod(destination_file, stat.S_IRUSR | stat.S_IWUSR | stat.S_IRGRP | stat.S_IROTH)


def is_image(file_path: Union[str, Path]) -> bool:
    return Path(file_path).suffix in IMAGE_FILE_EXTENSIONS


def is_movie(file_path: Union[str, Path]) -> bool:
    return Path(file_path).suffix in MOVIE_FILE_EXTENSIONS


def is_pdf(file_path: Union[str, Path]) -> bool:
    return Path(file_path).suffix == PDF_EXTENSION


def is_sortable(file_path: Union[str, Path]) -> bool:
    return Path(file_path).suffix in SORTABLE_FILE_EXTENSIONS


def _non_hidden_files_in_dir(dir: Union[os.PathLike, str]) -> List[str]:
    return [path.join(dir, file) for file in os.listdir(dir) if not file.startswith('.')]
