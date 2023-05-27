"""
Open a GUI window to allow manual name / select.
TODO: rename to something more appropriate
"""
import shutil
import sys
from os import path, remove
from subprocess import run

from rich.panel import Panel
from rich.text import Text

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

    layout = [
        [sg.Image(data=image.image_bytes(), key="-IMAGE-")],
        [sg.Text("Enter file name:")],
        [sg.Input(suggested_filename, size=(len(suggested_filename), 1))]
    ]

    sort_dirs = [path.basename(dir) for dir in Config.get_sort_dirs()]
    layout += [[sg.Combo(sort_dirs, size=(max([len(dir) for dir in sort_dirs]), SELECT_SIZE))]]

    layout += [[
        sg.Button(OK, bind_return_key=True),
        sg.Button(DELETE),
        sg.Button(OPEN),
        sg.Button(SKIP),
        sg.Button(EXIT)
    ]]

    window = sg.Window(image.basename, layout)

    # Event Loop
    while True:
        event, values = window.Read()
        window.close()

        if event == DELETE:
            log.warning(f"Deleting '{image.file_path}'")
            remove(image.file_path)
            return
        elif event == OPEN:
            log.info(f"Opening '{image.file_path}'")
            run(['open', image.file_path])
        elif event == SKIP:
            return
        elif event == EXIT:
            sys.exit()
        elif event == OK:
            break

    chosen_filename = values[0]
    new_dir = values[1]

    if is_empty(chosen_filename):
        raise ValueError("Filename can't be blank!")

    new_dir = Config.sorted_screenshots_dir.joinpath(new_dir)
    new_filename = new_dir.joinpath(chosen_filename)
    log.info(f"Chosen Filename: '{chosen_filename}'\nDirectory: '{new_dir}'\nNew file: '{new_filename}'\nEvent: {event}\n")
    log.debug(f"All values: {values}")
    console.print(bullet_text(f"Moving '{image.file_path}' to '{new_filename}'..."))

    if Config.dry_run:
        console.print(indented_bullet("Dry run so not moving..."), style='dim')
    else:
        shutil.move(image.file_path, new_filename)


def _subdir_radio_select_columns(sg):
    dirs = Config.get_sort_dirs()

    for i in range(0, len(dirs), RADIO_COLS):
        yield [
            sg.Radio(path.basename(dir), "SORTDIR_RADIO", default=False, key=dir)
            for dir in dirs[i: i + RADIO_COLS]
        ]


def _subdir_combobox_items():
    return [path.basename(dir) for dir in Config.get_sort_dirs()]
