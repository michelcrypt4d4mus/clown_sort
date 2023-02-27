"""
Open a GUI window to allow manual name / select.
"""
import shutil
import sys
from os import path, remove
from subprocess import run

from rich.panel import Panel
from rich.text import Text

from clown_sort.config import Config
from clown_sort.filename_extractor import FilenameExtractor
from clown_sort.files.image_file import ImageFile
from clown_sort.util.dict_helper import get_dict_key_by_value
from clown_sort.util.logging import log
from clown_sort.util.rich_helper import bullet_text, console, indented_bullet

RADIO_COLS = 10
DELETE = 'Delete'
OK = 'Move'
OPEN = 'Preview Image'
SKIP = 'Skip'
EXIT = 'Exit'


def process_file(image: ImageFile) -> None:
    import PySimpleGUI as sg
    console.print(Panel(Text("Processing: '").append(str(image.file_path), style='cyan reverse').append("'..."), expand=False))
    extracted_text = ' '.join((image.extracted_text() or '').splitlines())
    log.info(f"OCR Text: {extracted_text} ({len(extracted_text)} chars)")
    suggested_filename = FilenameExtractor(image).filename()
    input = sg.Input(suggested_filename, size=(len(suggested_filename), 1))

    layout = [
        [sg.Image(data=image.image_bytes(), key="-IMAGE-")],
        #[sg.Text(image.extracted_text())],
        [sg.Text("Enter file name:")],
        [input]
    ] + list(_subdir_radio_select_columns(sg)) + \
        [[sg.Button(OK, bind_return_key=True), sg.Button(DELETE), sg.Button(OPEN), sg.Button(SKIP), sg.Button(EXIT)]]

    window = sg.Window(image.basename, layout)

    # Event Loop
    while True:
        event, values = window.Read()

        if event == DELETE:
            log.warning(f"Deleting '{image.file_path}'")
            remove(image.file_path)
            window.close()
            return
        elif event == OPEN:
            log.info(f"Opening '{image.file_path}'")
            run(['open', image.file_path])
        elif event == SKIP:
            window.close()
            return
        elif event == EXIT:
            window.close()
            sys.exit()
        elif event == OK:
            break

    window.close()
    chosen_filename = values[0]

    if chosen_filename is None or len(chosen_filename) == 0:
        raise ValueError("Filename can't be blank!")

    try:
        new_dir = get_dict_key_by_value(values, True)
    except ValueError:
        new_dir = Config.sorted_screenshots_dir

    new_filename = path.join(new_dir, chosen_filename)
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
