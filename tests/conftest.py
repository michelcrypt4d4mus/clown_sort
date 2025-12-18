from os import environ, path, pardir
from pathlib import Path
environ['INVOKED_BY_PYTEST'] = 'True'

import pytest

from clown_sort.config import Config
from clown_sort.sort_rule import CRYPTO_RULES_CSV_PATH

# TODO: importlib doesn't play nice with running tests via GitHub actions
# import importlib.resources
# from clown_sort.util.constants import PACKAGE_NAME
# PROJECT_DIR = path.join(str(importlib.resources.files(PACKAGE_NAME)), pardir)

PYTESTS_DIR = path.dirname(__file__)
PROJECT_DIR = path.join(PYTESTS_DIR, pardir)
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


@pytest.fixture
def turn_off_dry_run():
    Config.dry_run = False
    Config.leave_in_place = True
    yield
    Config.dry_run = True


@pytest.fixture(scope='session')
def do_kwon_tweet():
    return FIXTURES_DIR.joinpath('do_kwon_debate_the_poor.jpeg')


@pytest.fixture(scope='session')
def parrot_retweet():
    return FIXTURES_DIR.joinpath('parrot_retweet.png')


@pytest.fixture(scope='session')
def three_of_swords_file():
    return FIXTURES_DIR.joinpath('3 of swords occult_arbitrum.jpeg')


@pytest.fixture(scope='session')
def unicode_filename():
    return FIXTURES_DIR.joinpath('Déltèç_bank_sücks.png')
