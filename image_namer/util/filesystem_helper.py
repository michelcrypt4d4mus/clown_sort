"""
Functions and constants having to do with the filesystem.
importlib explanation: https://fossies.org/linux/Python/Lib/importlib/resources.py
"""
import gzip
import logging
import os
import stat
from datetime import datetime
from os import path
from pathlib import Path
from typing import List, Optional, Union

from filedate.Utils import Copy

GZIP_EXTENSION = '.gz'


def files_in_dir(dir: Union[os.PathLike, str], with_extname: Optional[str] = None) -> List[str]:
    """paths for non-hidden files, optionally ending in 'with_extname'"""
    files = [file for file in _non_hidden_files_in_dir(dir) if not path.isdir(file)]

    if with_extname:
        files = [f for f in files if f.endswith(f".{with_extname}")]

    return files


def subdirs_of_dir(dir: Union[os.PathLike, str]) -> List[str]:
    """Find non-hidden subdirs in 'dir'."""
    return [file for file in _non_hidden_files_in_dir(dir) if path.isdir(file)]


def get_lines(file_path: str, comment_char: Optional[str] = '#') -> List[str]:
    """Get lines from text or gzip file optionally skipping lines starting with comment_char."""
    if file_path.endswith(GZIP_EXTENSION):
        with gzip.open(file_path, 'rb') as file:
            lines = [line.decode() for line in file]
    else:
        with open(file_path, 'r') as file:
            lines = file.readlines()

    if comment_char:
        lines = [line.strip() for line in lines if not line.startswith(comment_char)]

    return lines


def timestamp_for_filename() -> str:
    """Returns a string showing current time in a file name friendly format."""
    return datetime.now().strftime("%Y-%m-%dT%H.%M.%S")


def copy_file_creation_time(source_file: Path, destination_file: Path) -> None:
    Copy(str(source_file), str(destination_file)).modified()
    # The filedate library has a bad habit of changing all the permissions so we change them back.
    os.chmod(destination_file, stat.S_IRUSR | stat.S_IWUSR | stat.S_IRGRP | stat.S_IROTH)


def _non_hidden_files_in_dir(dir: Union[os.PathLike, str]) -> List[str]:
    return [path.join(dir, file) for file in os.listdir(dir) if not file.startswith('.')]
