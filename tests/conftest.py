import importlib.resources
from os import environ, path, pardir, remove
from pathlib import Path
#environ['INVOKED_BY_PYTEST'] = 'True'

import pytest

from image_namer.config import Config
from image_namer.util.argument_parser import PACKAGE_NAME

PROJECT_DIR = path.join(str(importlib.resources.files(PACKAGE_NAME)), pardir)
TESTS_DIR = Path(PROJECT_DIR).joinpath('tests')
FIXTURES_DIR = TESTS_DIR.joinpath('fixtures')
TMP_DIR = TESTS_DIR.joinpath('tmp')
SORTED_DIR = TMP_DIR.joinpath('Sorted')
PROCESSED_DIR = TMP_DIR.joinpath('Processed')


@pytest.fixture(scope='session', autouse=True)
def test_config():
    yield Config.set_directories(FIXTURES_DIR, TMP_DIR)
    SORTED_DIR.rmdir()
    PROCESSED_DIR.rmdir()


@pytest.fixture(scope='session')
def do_kwon_tweet():
    return FIXTURES_DIR.joinpath('do_kwon_debate_the_poor.jpeg')
