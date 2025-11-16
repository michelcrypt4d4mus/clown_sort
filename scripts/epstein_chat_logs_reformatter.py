#!/usr/bin/env python
"""
Reformat Epstein text message file form for readability. Requires python.
For use with iMessage log files from https://drive.google.com/drive/folders/1hTNH5woIRio578onLGElkTWofUSWRoH_
Can handle being called on multiple filenames and/or wildcards.

Install: 'pip install rich'
    Run: 'python colorize_epstein_text_messages.py [TEXT_MESSAGE_FILENAMES]'
"""

import re
from os import environ
from pathlib import Path

from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.theme import Theme
from sys import argv

MSG_REGEX = re.compile(r'Sender:(.*?)\nTime:(.*? (AM|PM)).*?Message:(.*?)\n(?=(Sender))', re.DOTALL)
FILE_ID_REGEX = re.compile(r'.*HOUSE_OVERSIGHT_(\d+)\.txt')
PHONE_NUMBER_REGEX = re.compile(r'^[\d+]+.*')
PHONE_NUMBER = 'phone_number'
BANNON = 'Bannon'
DEFAULT = 'default'
EPSTEIN = 'Epstein'
UNKNOWN = '(unknown)'
HTML_WIDTH = 85

# Color different counterparties differently
COUNTERPARTY_COLORS = {
    'Bannon': 'color(58)',
    DEFAULT: 'yellow1',
    EPSTEIN: 'blue',  # Epstein
    PHONE_NUMBER: 'bright_green',
    UNKNOWN: 'cyan',
}

KNOWN_COUNTERPARTY_FILE_IDS = {
    '025707': BANNON,
    '025734': BANNON,
    '025452': BANNON,
}

for counterparty in COUNTERPARTY_COLORS:
    COUNTERPARTY_COLORS[counterparty] = f"{COUNTERPARTY_COLORS[counterparty]} bold"

is_debug = len(environ.get('DEBUG') or '') > 0
is_build = len(environ.get('BUILD') or '') > 0
console = Console(color_system='256', theme=Theme(COUNTERPARTY_COLORS), width=HTML_WIDTH if is_build else 125)
console.record = True


for i, file_arg in enumerate(argv):
    file_arg = Path(file_arg)

    if i == 0 or file_arg.is_dir():
        continue

    with open(file_arg) as f:
        file_basename = file_arg.name
        file_lines = [l.strip() for l in f.read().split('\n') if not l.startswith('HOUSE OVERSIGHT')]

        # Strip 1st char if it's the BOM "\ufeff"
        if file_lines[0][0] == '\ufeff':
            file_lines[0] = file_lines[0][1:]

        file_text = '\n'.join(file_lines)

        if 'iMessage' not in file_text:
            if is_debug:
                if len(file_text) > 0 and file_text[0] == '{':
                    json_subdir_path = file_arg.parent.joinpath('json_files').joinpath(file_basename + '.json')
                    console.print(f"'{file_arg}' looks like JSON, moving to '{json_subdir_path}'", style='yellow1 bold')
                    file_arg.rename(json_subdir_path)
                else:
                    console.print(f"'iMessage' string not found in '{file_basename}', top lines:")
                    console.print('\n'.join(file_lines[0:4]) + '\n', style='dim')

            continue

        console.print('\n\n', Panel(file_basename, style='reverse', expand=False))
        file_match = FILE_ID_REGEX.match(str(file_basename))
        counterparty = UNKNOWN

        if file_match:
            file_id = file_match.group(1)
            counterparty = KNOWN_COUNTERPARTY_FILE_IDS.get(file_id, UNKNOWN)

            if counterparty != UNKNOWN and is_debug:
                console.print(f"Found known counterparty '{counterparty}' for file ID {file_id}...\n", style='dim')

        for i, match in enumerate(MSG_REGEX.finditer(file_text)):
            sender = match.group(1).strip()
            timestamp = Text(f"[{match.group(2).strip()}] ", style='dim')
            msg = match.group(4).strip()
            msg_lines = msg.split('\n')
            sender_style = None

            if len(sender) > 0:
                if sender == 'e:jeeitunes@gmail.com':
                    sender = EPSTEIN
                elif PHONE_NUMBER_REGEX.match(sender):
                    sender_style = PHONE_NUMBER
            else:
                sender = counterparty or UNKNOWN

            if msg.startswith('http'):
                if len(msg_lines) > 1 and not msg_lines[0].endswith('html'):  # Fix multiline links
                    msg = msg.replace('\n', '', 1)

                msg_lines = msg.split('\n')
                link_text = msg_lines.pop()
                msg = Text('').append(link_text, style='deep_sky_blue4 underline')

                if len(msg_lines) > 0:
                    msg = msg.append('\n' + ' '.join(msg_lines))
            else:
                msg = msg.replace('\n', ' ')  # remove newlines

            sender_txt = Text(sender, style=sender_style or COUNTERPARTY_COLORS.get(sender, DEFAULT))
            console.print(Text('').append(timestamp).append(sender_txt).append(': ').append(msg))

    console.line()


output_basename = "epstein_text_messaged_colorized"
output_html = f"{output_basename}.html"
colored_text_filename = f"{output_basename}.ascii.txt"



if is_build:
    console.save_html(output_html, inline_styles=True, clear=False)
    console.save_text(colored_text_filename, styles=True)
    console.line(2)
    console.print(f"Wrote HTML to '{output_html}' (is_build={is_build})")
    # console.print(f"Wrote colored ASCII to '{colored_text_filename}'")
else:
    console.print(f"\nNot writing HTML because BUILD=true evn var is not set.")
