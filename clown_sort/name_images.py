#!/usr/bin/env python
import shutil
from os import path, remove
from subprocess import run

import PySimpleGUI as sg
from rich.panel import Panel
from rich.text import Text

from social_arsenal.config import DEFAULT_SCREENSHOTS_DIR, Config
from social_arsenal.files.image_file import ImageFile
from social_arsenal.util.dict_helper import get_dict_key_by_value
from social_arsenal.util.logging import console, log

SORTED_DIR = DEFAULT_SCREENSHOTS_DIR.joinpath('Sorted')
PROCESSED_DIR = DEFAULT_SCREENSHOTS_DIR.joinpath('Processed')
RADIO_COLS = 5
DELETE = 'Delete'
OK = 'OK'
OPEN = 'Open'


def subdir_radio_select_columns():
    dirs = Config.get_sort_dirs()

    for i in range(0, len(dirs), RADIO_COLS):
        yield [
            sg.Radio(path.basename(dir), "SORTDIR_RADIO", default=False, key=dir)
            for dir in dirs[i: i + RADIO_COLS]
        ]


def process_file(image: ImageFile) -> None:
    console.print(Panel(Text("Processing: '").append(str(image.file_path), style='cyan reverse').append("'..."), expand=False))
    extracted_text = ' '.join((image.extracted_text() or '').splitlines())
    input = sg.Input() if len(extracted_text) == 0 or len(extracted_text) > 76 else sg.Input(extracted_text)
    log.info(f"OCR Text: {extracted_text} ({len(extracted_text)} chars)")

    layout = [
        [sg.Image(data=image.image_bytes(), key="-IMAGE-")],
        #[sg.Text(image.extracted_text())],
        [sg.Text("Enter file name:")],
        [input]
    ] + list(subdir_radio_select_columns()) + \
        [[sg.Button(OK, bind_return_key=True), sg.Button(DELETE), sg.Button(OPEN)]]

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
        elif event == OK:
            break

    window.close()

    if values[0] is None or len(values[0]) == 0:
        label = ''
    else:
        label = values[0] + ' '

    try:
        new_dir = get_dict_key_by_value(values, True)
    except ValueError:
        if label == '':
            log.info("Not moving file...")
            return

        new_dir = Config.sorted_screenshots_dir

    new_basename = label + image.basename
    new_filename = path.join(new_dir, new_basename)
    log.info(f"Label: '{label}'\nDirectory: '{new_dir}'\nNew file: '{new_filename}'\nEvent: {event}\n")
    log.debug(f"All values: {values}")
    log.info(f"Moving '{image.file_path}' to '{new_filename}'...")
    shutil.move(image.file_path, new_filename)


for image in ImageFile.screenshot_paths():
   process_file(image)
