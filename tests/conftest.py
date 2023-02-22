import importlib.resources
from os import path, pardir
from pathlib import Path
#environ['INVOKED_BY_PYTEST'] = 'True'

import pytest

from clown_sort.config import Config
from clown_sort.util.constants import CRYPTO_RULES_CSV_PATH, PACKAGE_NAME

PROJECT_DIR = path.join(str(importlib.resources.files(PACKAGE_NAME)), pardir)
TESTS_DIR = Path(PROJECT_DIR).joinpath('tests')
FIXTURES_DIR = TESTS_DIR.joinpath('fixtures')
TMP_DIR = TESTS_DIR.joinpath('tmp')
SORTED_DIR = TMP_DIR.joinpath('Sorted')
PROCESSED_DIR = TMP_DIR.joinpath('Processed')


@pytest.fixture(scope='session', autouse=True)
def test_config():
    yield Config.set_directories(FIXTURES_DIR, TMP_DIR, [CRYPTO_RULES_CSV_PATH])
    SORTED_DIR.rmdir()
    PROCESSED_DIR.rmdir()


@pytest.fixture(scope='session')
def do_kwon_tweet():
    return FIXTURES_DIR.joinpath('do_kwon_debate_the_poor.jpeg')


@pytest.fixture(scope='session')
def three_of_swords_file():
    return FIXTURES_DIR.joinpath('3 of swords occult.jpeg')
