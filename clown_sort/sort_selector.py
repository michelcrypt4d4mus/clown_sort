"""
Open a GUI window to allow manual name / select.
TODO: rename to something more appropriate
"""
import sys
from os import path, remove
from typing import Union

from clown_sort.config import Config
from clown_sort.filename_extractor import FilenameExtractor
from clown_sort.util.logging import log
from clown_sort.util.rich_helper import bullet_text, console, indented_bullet
from clown_sort.util.string_helper import is_empty

RADIO_COLS = 11
SELECT_SIZE = 45
DELETE = 'Delete'
OK = 'Move'
OPEN = 'Preview File'
SKIP = 'Skip'
EXIT = 'Exit'


def process_file_with_popup(image: Union['ImageFile', 'PdfFile']) -> None:
    # Do the import here so as to allow usage without installing PySimpleGUI
    import PySimpleGUI as psg
    psg.theme('SystemDefault1')
    suggested_filename = FilenameExtractor(image).filename()
    sort_dirs = [path.basename(dir) for dir in Config.get_sort_dirs()]
    max_dirname_length = max([len(dir) for dir in sort_dirs])
    thumbnail_bytes = image.thumbnail_bytes()

    if thumbnail_bytes is None:
        log.warn(f"Failed to get a thumbnail; skipping...")
        return

    layout = [
        [psg.Column([[psg.Image(data=thumbnail_bytes, key="-IMAGE-")]], justification='center')],
        [psg.HSep()],
        [psg.Text("Choose Filename:")],
        [psg.Input(suggested_filename, size=(len(suggested_filename), 1))],# font=("Courier New", 12))],
        [
            psg.Text(f"Choose Directory:"),
            psg.Combo(sort_dirs, size=(max_dirname_length, SELECT_SIZE)),
            psg.Text(f"(Enter custom text to create new directory. If no directory is chosen file will be copied to '{Config.sorted_screenshots_dir}'.)")
        ],
        [
            psg.Button(OK, bind_return_key=True),
            psg.Button(DELETE),
            psg.Button(OPEN),
            psg.Button(SKIP),
            psg.Button(EXIT)
        ]
    ]

    window = psg.Window(image.basename, layout)

    # Event Loop
    while True:
        event, values = window.Read()

        if event == OPEN:
            image.preview()
            continue

        window.close()

        if event == DELETE:
            log.warning(f"Deleting '{image.file_path}'")
            remove(image.file_path)
            return
        elif event == SKIP or event == psg.WIN_CLOSED:
            return
        elif event == EXIT:
            sys.exit()
        elif event == OK:
            break

    log.debug(f"All values: {values}")
    chosen_filename = values[1]
    new_subdir = values[2]
    destination_dir = Config.sorted_screenshots_dir.joinpath(new_subdir)

    if is_empty(chosen_filename):
        raise ValueError("Filename can't be blank!")

    if not destination_dir.exists():
        result = psg.popup_yes_no(f"Subdir '{new_subdir}' doesn't exist. Create?",  title="Unknown Subdirectory")

        if result == 'Yes' and not Config.dry_run:
            log.info(f"Creating directory '{new_subdir}'...")
            destination_dir.mkdir()
        else:
            console.print(bullet_text(f"Directory not found. Skipping '{image.file_path}'..."))
            return

    new_filename = destination_dir.joinpath(chosen_filename)
    log.info(f"Chosen Filename: '{chosen_filename}'\nSubdir: '{new_subdir}'\nNew file: '{new_filename}'\nEvent: {event}\n")
    console.print(bullet_text(f"Moving '{image.file_path}' to '{new_filename}'..."))
    image.copy_file_to_sorted_dir(new_filename)
    image.move_to_processed_dir()
