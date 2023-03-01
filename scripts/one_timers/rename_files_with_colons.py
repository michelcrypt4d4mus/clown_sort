import shutil
from glob import glob
from os import path

from clown_sort.util.constants import *
from clown_sort.config import Config


Config.configure()
Config.set_directories(DEFAULT_SCREENSHOTS_DIR, DEFAULT_DESTINATION_DIR, [CRYPTO_RULES_CSV_PATH])
file_paths = []

for pattern in ['*', '**/*']:
    glob_pattern = Config.sorted_screenshots_dir.joinpath(f"{pattern}")
    file_paths.extend(glob(str(glob_pattern)))

for file in file_paths:
    if ':' in path.basename(file):
        print(f"Has a colon: '{path.basename(file)}'")
        new_file = file.replace(':', '')
        print(f"No colon:    '{path.basename(new_file)}'")
        print('\n\n')
        shutil.move(file, new_file)
