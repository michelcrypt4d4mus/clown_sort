from os import environ, getcwd, path
from pathlib import Path

from dotenv import load_dotenv


# load_dotenv() should be called as soon as possible (before parsing local classes) but not for pytest
if not environ.get('INVOKED_BY_PYTEST', False):
    for dotenv_file in [path.join(dir, '.screenshot_sorter') for dir in [getcwd(), Path.home()]]:
        if path.exists(dotenv_file):
            import pdb; pdb.set_trace()
            load_dotenv(dotenv_path=dotenv_file)
            break
