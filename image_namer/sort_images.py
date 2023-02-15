#!/usr/bin/env python

import shutil

from rich.text import Text

from image_namer.config import DEFAULT_SCREENSHOTS_DIR, Config
from image_namer.image_file import ImageFile
from image_namer.sorter import get_sort_folders
from image_namer.util.rich_helper import console
from image_namer.util.string_helper import comma_join

SORTED_DIR = DEFAULT_SCREENSHOTS_DIR.joinpath('Sorted')
PROCESSED_DIR = DEFAULT_SCREENSHOTS_DIR.joinpath('Processed')


for image in ImageFile.screenshot_paths():
    console.print(image)
    console.print(f"RAW EXIF: {image.raw_exif_dict()}", style='color(145)')
    console.print(f"EXIF: {image.exif_dict()}", style='color(147)')
    sort_folders = get_sort_folders(image.ocr_text())
    console.print(Text('FOLDERS: ', style='magenta') + comma_join(sort_folders))

    if len(sort_folders) == 0:
        console.print(" . WARNING: No :sort_folders found!", style='bright_red')
        image.set_image_description_exif_as_ocr_text()
    else:
        possible_old_file = SORTED_DIR.joinpath(image.basename)

        if possible_old_file.is_file():
            console.print(Text(f"WARNING: Deleting unsorted file '{possible_old_file}'...", style='red'))
            possible_old_file.unlink()

        for sort_folder in sort_folders:
            new_file = image.set_image_description_exif_as_ocr_text(sort_folder)

    processed_file_path = Config.processed_screenshots_dir.joinpath(image.basename)

    if image.file_path == processed_file_path:
        console.print("Not moving file because it's the same location...", style='dim')
    else:
        console.print(f"Move '{image.file_path}' to '{processed_file_path}'", style='dim')
        shutil.move(image.file_path, processed_file_path)
