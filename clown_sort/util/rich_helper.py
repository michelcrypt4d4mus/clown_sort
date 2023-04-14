from pathlib import Path
from typing import List, Optional, Union

from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.theme import Theme

from clown_sort.config import Config

ARROW_BULLET = '➤ '
INDENTED_BULLET = f"  {ARROW_BULLET}"
NOT = Text('').append('(Not) ', style='dim')

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
    'social_media': 'color(82)',
    'author': 'color(178)',
    'sort_destination': 'magenta',
    'sort_folder': 'color(62)'
}

COLOR_THEME = Theme(COLOR_THEME_DICT)
INDENT_SPACES = 4

# Main rich text output object.
console = Console(theme=COLOR_THEME, color_system='256')


def indented_bullet(msg: Union[str, Text], style: Optional[str] = None) -> Text:
    return Text('  ') + bullet_text(msg, style)


def bullet_text(msg: Union[str, Text], style: Optional[str] = None) -> Text:
    if isinstance(msg, str):
        msg = Text(msg, style=style)

    return Text(ARROW_BULLET).append(msg)


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


def copying_file_log_message(basename: str, new_file: Path) -> Text:
    return _file_operation_log_message(basename, new_file, 'Copying')


def moving_file_log_message(basename: str, new_file: Path) -> Text:
    return _file_operation_log_message(basename, new_file, 'Moving processed file')


def comma_join(strs: List[str], style: str) -> Text:
    return Text(", ").join([Text(s, style) for s in strs])


def _file_operation_log_message(basename: str, new_file: Path, log_msg: str) -> Text:
    log_msg += ' '
    log_msg = Text(log_msg)

    if Config.dry_run:
        log_msg = NOT + log_msg

    txt = Text(f"➤ ") + log_msg + Text(basename, style='color(221)')
    txt.append(' to ').append(str(new_file), style='cyan')
    return txt
