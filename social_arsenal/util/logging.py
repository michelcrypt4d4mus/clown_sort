"""
Logging and printing, for now.
"""
import logging
from pathlib import Path
from sys import exit

from rich.console import Console
from rich.logging import RichHandler
from rich.panel import Panel
from rich.text import Text
from rich.theme import Theme

from social_arsenal.config import Config, PACKAGE_NAME

### Logging ###
LOG_LEVEL = 'INFO'


def set_log_level(log_level) -> None:
    log.setLevel(log_level)

    for handler in log.handlers:
        handler.setLevel(log_level)


log = logging.getLogger(PACKAGE_NAME)
log.addHandler(RichHandler(rich_tracebacks=True))

if Config.debug:
    set_log_level('DEBUG')
else:
    set_log_level('INFO')


### Printing ###
BYTES = 'color(100) dim'
BYTES_NO_DIM = 'color(100)'
BYTES_BRIGHTEST = 'color(220)'
BYTES_BRIGHTER = 'orange1'
BYTES_HIGHLIGHT = 'color(136)'
DARK_GREY = 'color(236)'
GREY = 'color(239)'
GREY_ADDRESS = 'color(238)'
PEACH = 'color(215)'
PURPLE = 'color(20)'

COLOR_THEME_DICT = {
    # colors
    'dark_orange': 'color(58)',
    'grey': GREY,
    'grey.dark': DARK_GREY,
    'grey.dark_italic': f"{DARK_GREY} italic",
    'grey.darker_italic': 'color(8) dim italic',
    'grey.darkest': 'color(235) dim',
    'grey.light': 'color(248)',
    'off_white': 'color(245)',
}

COLOR_THEME = Theme(COLOR_THEME_DICT)
INDENT_SPACES = 4
console = Console(theme=COLOR_THEME, color_system='256')


def print_dim(msg) -> None:
    console.print(msg, style='dim')


def print_headline(headline: str) -> None:
    console.line(2)
    console.print(Panel(headline, style='reverse', width=60))
    console.line()


def print_indented(msg: str, style: str = '', indent_level: int = 1) -> None:
    console.print(f"{indent_whitespace(indent_level)}{msg}", style=style)


def ask_for_confirmation(msg: Text) -> None:
    """Primitive user confirmation"""
    console.print(msg.append("\n('y' to continue, any other key to exit)", style='white dim'))

    if input().lower() != 'y':
        exit()


def indent_whitespace(indent_level: int = 1):
    return ' ' * INDENT_SPACES * indent_level


def copied_file_log_message(basename: str, new_file: Path) -> Text:
    return _file_operation_log_message(basename, new_file, 'Copied')


def move_file_log_message(basename: str, new_file: Path) -> Text:
    return _file_operation_log_message(basename, new_file, 'Moved')


def _file_operation_log_message(basename: str, new_file: Path, log_msg: str) -> Text:
    txt = Text(f"➤ {log_msg} ").append(basename, style='color(221)')
    txt.append(' to ').append(str(new_file), style='cyan')
    return txt
