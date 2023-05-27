"""
Open a GUI window to allow manual name / select.
TODO: rename to something more appropriate
"""
import shutil
import sys
from os import path, remove
from subprocess import run

from clown_sort.config import Config
from clown_sort.filename_extractor import FilenameExtractor
from clown_sort.util.logging import log
from clown_sort.util.rich_helper import bullet_text, console, indented_bullet
from clown_sort.util.string_helper import is_empty

RADIO_COLS = 11
SELECT_SIZE = 45
DELETE = 'Delete'
OK = 'Move'
OPEN = 'Preview Image'
SKIP = 'Skip'
EXIT = 'Exit'


def process_file_with_popup(image: 'ImageFile') -> None:
    # Do the import here so as to allow usage without installing PySimpleGUI
    import PySimpleGUI as sg
    suggested_filename = FilenameExtractor(image).filename()
    sort_dirs = [path.basename(dir) for dir in Config.get_sort_dirs()]

    layout = [
        [sg.Image(data=image.image_bytes(), key="-IMAGE-")],
        [sg.Text("Enter file name:")],
        [sg.Input(suggested_filename, size=(len(suggested_filename), 1))],
        [sg.Combo(sort_dirs, size=(max([len(dir) for dir in sort_dirs]), SELECT_SIZE))],
        [
            sg.Button(OK, bind_return_key=True),
            sg.Button(DELETE),
            sg.Button(OPEN),
            sg.Button(SKIP),
            sg.Button(EXIT)
        ]
    ]

    window = sg.Window(image.basename, layout)

    # Event Loop
    while True:
        event, values = window.Read()

        if event == OPEN:
            log.info(f"Opening '{image.file_path}'")
            run(['open', image.file_path])
            continue

        window.close()

        if event == DELETE:
            log.warning(f"Deleting '{image.file_path}'")
            remove(image.file_path)
            return
        elif event == SKIP:
            return
        elif event == EXIT:
            sys.exit()
        elif event == OK:
            break

    log.debug(f"All values: {values}")
    chosen_filename = values[0]
    new_dir = values[1]

    if is_empty(chosen_filename):
        raise ValueError("Filename can't be blank!")

    new_dir = Config.sorted_screenshots_dir.joinpath(new_dir)
    new_filename = new_dir.joinpath(chosen_filename)
    log.info(f"Chosen Filename: '{chosen_filename}'\nDirectory: '{new_dir}'\nNew file: '{new_filename}'\nEvent: {event}\n")
    console.print(bullet_text(f"Moving '{image.file_path}' to '{new_filename}'..."))
    image.copy_file_to_sorted_dir(new_filename)


def _subdir_combobox_items():
    return [path.basename(dir) for dir in Config.get_sort_dirs()]
