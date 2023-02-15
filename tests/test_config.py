from os import getcwd
from pathlib import Path

from image_namer.config import Config

TESTS_DIR = Path(getcwd()).joinpath('tests')



def test_config_folders():
    Config.set_directories(FIXTURES_DIR, TMP_DIR)
    assert SORTED_DIR.is_dir()
    assert PROCESSED_DIR.is_dir()
    SORTED_DIR.rmdir()
    PROCESSED_DIR.rmdir()
