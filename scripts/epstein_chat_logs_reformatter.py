#!/usr/bin/env python
"""
Reformat Epstein text message file form for readability. Requires python.
For use with iMessage log files from https://drive.google.com/drive/folders/1hTNH5woIRio578onLGElkTWofUSWRoH_
Can handle being called on multiple filenames and/or wildcards.

Install: 'pip install rich'
    Run: 'python epstein_chat_logs_reformatter.py [TEXT_MESSAGE_FILENAMES]'
"""
import csv
import json
import re
from io import StringIO
from os import environ
from pathlib import Path

from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.theme import Theme
from sys import argv

#  of who is the counterparty in each file
AI_COUNTERPARTY_DETERMINATION_TSV = StringIO("""
filename	counterparty	source
HOUSE_OVERSIGHT_025363.txt	Steve Bannon	Trump and New York Times coverage
HOUSE_OVERSIGHT_025368.txt	Steve Bannon	Trump and New York Times coverage
HOUSE_OVERSIGHT_025400.txt	Steve Bannon (likely)	Trump NYT article criticism; Hannity media strategy
HOUSE_OVERSIGHT_025403.txt	Personal contact	Personal/social plans
HOUSE_OVERSIGHT_025408.txt	Steve Bannon	Trump and New York Times coverage
HOUSE_OVERSIGHT_025423.txt	unclear	unclear
HOUSE_OVERSIGHT_025426.txt	unclear	unclear
HOUSE_OVERSIGHT_025429.txt	Stacey Plaskett	Michael Cohen congressional testimony coordination
HOUSE_OVERSIGHT_025452.txt	Steve Bannon	Trump and New York Times coverage
HOUSE_OVERSIGHT_025479.txt	Steve Bannon	China strategy and geopolitics; Trump discussions
HOUSE_OVERSIGHT_025707.txt	Steve Bannon	Trump and New York Times coverage
HOUSE_OVERSIGHT_025734.txt	Steve Bannon	China strategy and geopolitics; Trump discussions
HOUSE_OVERSIGHT_025735.txt	Unidentified	unclear
HOUSE_OVERSIGHT_027128.txt	Personal contact	Personal/social plans
HOUSE_OVERSIGHT_027133.txt	Steve Bannon	Political strategy and international affairs
HOUSE_OVERSIGHT_027141.txt	unclear	unclear
HOUSE_OVERSIGHT_027148.txt	Steve Bannon	Middle East politics and business deals; Trump discussions
HOUSE_OVERSIGHT_027165.txt	Michael Wolff	Trump book/journalism project
HOUSE_OVERSIGHT_027184.txt	Steve Bannon	Trump and New York Times coverage
HOUSE_OVERSIGHT_027214.txt	unclear	unclear
HOUSE_OVERSIGHT_027217.txt	Business associate	Business discussions
HOUSE_OVERSIGHT_027225.txt	Personal contact	Personal/social plans
HOUSE_OVERSIGHT_027232.txt	Personal contact	Personal/social plans
HOUSE_OVERSIGHT_027248.txt	unclear	unclear
HOUSE_OVERSIGHT_027250.txt	Personal contact	Personal/social plans
HOUSE_OVERSIGHT_027255.txt	Business associate	Business discussions
HOUSE_OVERSIGHT_027257.txt	unclear	unclear
HOUSE_OVERSIGHT_027260.txt	Steve Bannon	Trump and New York Times coverage
HOUSE_OVERSIGHT_027275.txt	unclear	unclear
HOUSE_OVERSIGHT_027278.txt	Personal contact	Personal/social plans
HOUSE_OVERSIGHT_027281.txt	Steve Bannon	Trump and New York Times coverage
HOUSE_OVERSIGHT_027307.txt	Steve Bannon	Trump and New York Times coverage
HOUSE_OVERSIGHT_027330.txt	unclear	unclear
HOUSE_OVERSIGHT_027333.txt	Personal contact	Personal/social plans
HOUSE_OVERSIGHT_027346.txt	Steve Bannon	Trump and New York Times coverage
HOUSE_OVERSIGHT_027365.txt	Steve Bannon	Trump and New York Times coverage
HOUSE_OVERSIGHT_027374.txt	Steve Bannon	China strategy and geopolitics
HOUSE_OVERSIGHT_027396.txt	Personal contact	Personal/social plans
HOUSE_OVERSIGHT_027401.txt	unclear	unclear
HOUSE_OVERSIGHT_027406.txt	Steve Bannon	Trump and New York Times coverage
HOUSE_OVERSIGHT_027428.txt	unclear	unclear
HOUSE_OVERSIGHT_027434.txt	Business associate	Business discussions
HOUSE_OVERSIGHT_027440.txt	Michael Wolff	Trump book/journalism project
HOUSE_OVERSIGHT_027445.txt	Steve Bannon	China strategy and geopolitics; Trump discussions
HOUSE_OVERSIGHT_027452.txt	unclear	unclear
HOUSE_OVERSIGHT_027455.txt	Steve Bannon (likely)	China strategy and geopolitics; Trump discussions
HOUSE_OVERSIGHT_027460.txt	Steve Bannon	Trump and New York Times coverage
HOUSE_OVERSIGHT_027515.txt	Personal contact	Personal/social plans
HOUSE_OVERSIGHT_027536.txt	Steve Bannon	China strategy and geopolitics; Trump discussions
HOUSE_OVERSIGHT_027568.txt	Personal contact	Personal/social plans
HOUSE_OVERSIGHT_027576.txt	Michael Wolff	Trump book/journalism project
HOUSE_OVERSIGHT_027585.txt	Business associate	Business discussions
HOUSE_OVERSIGHT_027655.txt	Steve Bannon	Trump and New York Times coverage
HOUSE_OVERSIGHT_027695.txt	Personal contact	Personal/social plans
HOUSE_OVERSIGHT_027707.txt	Steve Bannon	Italian politics; Trump discussions
HOUSE_OVERSIGHT_027722.txt	Steve Bannon	Trump and New York Times coverage
HOUSE_OVERSIGHT_027735.txt	Steve Bannon	Trump and New York Times coverage
HOUSE_OVERSIGHT_027764.txt	Michael Wolff	Trump book/journalism project
HOUSE_OVERSIGHT_027794.txt	Steve Bannon	Trump and New York Times coverage
HOUSE_OVERSIGHT_029744.txt	Steve Bannon (likely)	Trump and New York Times coverage
HOUSE_OVERSIGHT_031042.txt	Personal contact	Personal/social plans
HOUSE_OVERSIGHT_031045.txt	Steve Bannon (likely)	Trump and New York Times coverage
HOUSE_OVERSIGHT_031054.txt	Personal contact	Personal/social plans
HOUSE_OVERSIGHT_031173.txt	unclear	unclear
""".strip())

MSG_REGEX = re.compile(r'Sender:(.*?)\nTime:(.*? (AM|PM)).*?Message:(.*?)\n(?=(Sender))', re.DOTALL)
FILE_ID_REGEX = re.compile(r'.*HOUSE_OVERSIGHT_(\d+)\.txt')
PHONE_NUMBER_REGEX = re.compile(r'^[\d+]+.*')
PHONE_NUMBER = 'phone_number'
BANNON = 'Bannon'
DEFAULT = 'default'
EPSTEIN = 'Epstein'
PLASKETT = 'Stacey Plaskett'
SUMMERS = 'Larry Summers'
UNKNOWN = '(unknown)'

# Color different counterparties differently
COUNTERPARTY_COLORS = {
    BANNON: 'color(58)',
    DEFAULT: 'yellow1',
    EPSTEIN: 'blue',  # Epstein
    "Michael Wolff": 'grey54',
    PHONE_NUMBER: 'bright_green',
    PLASKETT: 'medium_orchid3',
    SUMMERS: 'bright_red',
    UNKNOWN: 'cyan',
}

KNOWN_COUNTERPARTY_FILE_IDS = {
    '025707': BANNON,
    '025734': BANNON,
    '025452': BANNON,
    '025408': BANNON,
    '025429': PLASKETT,
    '027777': SUMMERS,
}

GUESSED_COUNTERPARTY_FILE_IDS = {
    '025363': BANNON,
    '025368': BANNON,
}

for counterparty in COUNTERPARTY_COLORS:
    COUNTERPARTY_COLORS[counterparty] = f"{COUNTERPARTY_COLORS[counterparty]} bold"


def extract_file_id(filename) -> str:
    file_match = FILE_ID_REGEX.match(str(filename))

    if file_match:
        return file_match.group(1)
    else:
        raise RuntimeError(f"Failed to extract file ID from {filename}")


for row in csv.DictReader(AI_COUNTERPARTY_DETERMINATION_TSV, delimiter='\t'):
    file_id = extract_file_id(row['filename'].strip())
    counterparty = row['counterparty'].strip()
    counterparty = BANNON if counterparty.startswith('Steve Bannon') else counterparty

    if counterparty in ['unclear', 'Unidentified', 'Personal contact', 'Business associate']:
        continue
    else:
        GUESSED_COUNTERPARTY_FILE_IDS[file_id] = counterparty.replace(' (likely)', '').strip()


is_debug = len(environ.get('DEBUG') or '') > 0
is_build = len(environ.get('BUILD') or '') > 0
console = Console(color_system='256', theme=Theme(COUNTERPARTY_COLORS))
console.record = True
files_processed = 0
msgs_processed = 0

if is_debug:
    console.print('KNOWN_COUNTERPARTY_FILE_IDS\n--------------')
    console.print(json.dumps(KNOWN_COUNTERPARTY_FILE_IDS))
    console.print('\n\n\nGUESSED_COUNTERPARTY_FILE_IDS\n--------------')
    console.print_json(json.dumps(GUESSED_COUNTERPARTY_FILE_IDS))
    console.line(2)


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
                    console.print(f"'{file_arg}' looks like JSON, moving to '{json_subdir_path}'\n", style='yellow1 bold')
                    file_arg.rename(json_subdir_path)
                else:
                    console.print(f"'iMessage' string not found in '{file_basename}', top lines:")
                    console.print('\n'.join(file_lines[0:4]) + '\n', style='dim')

            continue

        files_processed += 1
        console.print(Panel(file_basename, style='reverse', expand=False))
        file_id = extract_file_id(file_basename)
        counterparty = UNKNOWN
        counterparty_guess = None

        if file_id:
            counterparty = KNOWN_COUNTERPARTY_FILE_IDS.get(file_id, UNKNOWN)

            if counterparty != UNKNOWN:
                hint_txt = Text(f"Found known counterparty ", style='dim')
                hint_txt.append(counterparty, style=COUNTERPARTY_COLORS.get(counterparty, DEFAULT))
                console.print(hint_txt.append(" for file ID {file_id}...\n"))
            elif file_id in GUESSED_COUNTERPARTY_FILE_IDS:
                counterparty_guess = GUESSED_COUNTERPARTY_FILE_IDS[file_id]
                txt = Text("(This might be a conversation with ", style='grey')
                txt.append(counterparty_guess, style=f"{COUNTERPARTY_COLORS.get(counterparty_guess, DEFAULT)}")
                console.print(txt.append(')\n'))

        for i, match in enumerate(MSG_REGEX.finditer(file_text)):
            msgs_processed += 1
            sender = sender_str = match.group(1).strip()
            sender_style = None
            timestamp = Text(f"[{match.group(2).strip()}] ", style='dim')
            msg = match.group(4).strip()
            msg_lines = msg.split('\n')

            if len(sender) > 0:
                if sender == 'e:jeeitunes@gmail.com':
                    sender = sender_str = EPSTEIN
                elif PHONE_NUMBER_REGEX.match(sender):
                    sender_style = PHONE_NUMBER
            else:
                sender = counterparty_guess or UNKNOWN
                sender_str = f"{sender} (??)" if sender != UNKNOWN else sender

            sender_txt = Text(sender_str, style=sender_style or COUNTERPARTY_COLORS.get(sender, DEFAULT))

            # Fix multiline links
            if msg.startswith('http'):
                if len(msg_lines) > 1 and not msg_lines[0].endswith('html'):
                    if len(msg_lines) > 2 and msg_lines[1].endswith('-'):
                        msg = msg.replace('\n', '', 2)
                    else:
                        msg = msg.replace('\n', '', 1)

                msg_lines = msg.split('\n')
                link_text = msg_lines.pop()
                msg = Text('').append(link_text, style='deep_sky_blue4 underline')

                if len(msg_lines) > 0:
                    msg = msg.append('\n' + ' '.join(msg_lines))
            else:
                msg = msg.replace('\n', ' ')  # remove newlines

            console.print(Text('').append(timestamp).append(sender_txt).append(': ').append(msg))

    console.line(2)


console.print(f"\nProcessed {files_processed} iMessage log files with {msgs_processed} text messages.")
output_basename = "epstein_text_messaged_colorized"
output_html = f"{output_basename}.html"
colored_text_filename = f"{output_basename}.ascii.txt"

if is_build:
    console.save_html(output_html, inline_styles=True, clear=False)
    console.save_text(colored_text_filename, styles=True)
    console.print(f"Wrote HTML to '{output_html}' (is_build={is_build})")
    console.print(f"Wrote colored ASCII to '{colored_text_filename}'")
else:
    console.print(f"\nNot writing HTML because BUILD=true evn var is not set.")
