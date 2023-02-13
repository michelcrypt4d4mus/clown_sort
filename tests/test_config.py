from os import getcwd
from pathlib import Path

from image_namer.config import Config

TESTS_DIR = Path(getcwd()).joinpath('tests')
FIXTURES_DIR = TESTS_DIR.joinpath('fixtures')
TMP_DIR = TESTS_DIR.joinpath('tmp')
SORTED_DIR = TMP_DIR.joinpath('Sorted')
PROCESSED_DIR = TMP_DIR.joinpath('Processed')


def test_config_folders():
    Config.set_directories(FIXTURES_DIR, TMP_DIR)
    assert SORTED_DIR.is_dir()
    assert PROCESSED_DIR.is_dir()
    SORTED_DIR.rmdir()
    PROCESSED_DIR.rmdir()
