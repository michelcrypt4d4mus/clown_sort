from os import environ, path, pardir, remove
import importlib.resources
from pathlib import Path
#environ['INVOKED_BY_PYTEST'] = 'True'

import pytest

PROJECT_DIR = path.join(str(importlib.resources.files('image_namer')), pardir)
TESTS_DIR = Path(PROJECT_DIR).joinpath('tests')
FIXTURES_DIR = TESTS_DIR.joinpath('fixtures')
TMP_DIR = TESTS_DIR.joinpath('tmp')
SORTED_DIR = TMP_DIR.joinpath('Sorted')
PROCESSED_DIR = TMP_DIR.joinpath('Processed')


@pytest.fixture(scope='session')
def do_kwon_tweet():
    return FIXTURES_DIR.joinpath('do_kwon_debate_the_poor.jpeg')
