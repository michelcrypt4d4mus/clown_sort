from pathlib import Path
from sys import stderr
from typing import List, Optional, Union

from rich.console import Console
from rich.padding import Padding
from rich.panel import Panel
from rich.text import Text
from rich.theme import Theme

ARROW_BULLET = '➤ '
INDENTED_BULLET = f"  {ARROW_BULLET}"
NOT = Text('').append('(Not) ', style='dim')
WARNING = Text('').append('WARNING', style='bright_yellow').append(': ')

### Printing ###
BYTES = 'color(100) dim'
BYTES_NO_DIM = 'color(100)'
BYTES_BRIGHTEST = 'color(220)'
BYTES_BRIGHTER = 'orange1'
BYTES_HIGHLIGHT = 'color(136)'
DARK_GREY = 'color(236)'
FILE_STYLE = 'underline color(81)'
GREY = 'color(239)'
GREY_ADDRESS = 'color(238)'
PEACH = 'color(215)'
PURPLE = 'color(20)'
YELLOW_ON_RED = 'color(190) on red'

COLOR_THEME_DICT = {
    'dark_orange': 'color(58)',
    'file': FILE_STYLE,
    'grey': GREY,
    'grey.dark': DARK_GREY,
    'grey.dark_italic': f"{DARK_GREY} italic",
    'grey.darker_italic': 'color(8) dim italic',
    'grey.darkest': 'color(235) dim',
    'grey.light': 'color(248)',
    'mild_warning': 'color(228) dim',
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
stderr_console = Console(theme=COLOR_THEME, color_system='256', file=stderr)
is_dry_run = True  # TODO: this being set in Config sucks


def indented_bullet(msg: Union[str, Text], style: Optional[str] = None) -> Text:
    return Text('  ') + bullet_text(msg, style)


def bullet_text(msg: Union[str, Text], style: Optional[str] = None) -> Text:
    if isinstance(msg, str):
        msg = Text(msg, style=style)

    return Text(ARROW_BULLET).append(msg)


def print_dim_bullet(msg: Union[str, Text]) -> None:
    console.print(indented_bullet(msg), style='dim')


def print_headline(headline: str) -> None:
    console.line(2)
    console.print(Panel(headline, style='reverse', width=60))
    console.line()


def print_indented(msg: str, style: str = '', indent_level: int = 1) -> None:
    console.print(f"{indent_whitespace(indent_level)}{msg}", style=style)


def indent_whitespace(indent_level: int = 1):
    return ' ' * INDENT_SPACES * indent_level


def copying_file_log_message(basename: str, new_file: Path) -> Text:
    return _file_operation_log_message(basename, new_file, 'Copying')


def moving_file_log_message(basename: str, new_file: Path) -> Text:
    return _file_operation_log_message(basename, new_file, 'Moving processed file')


def mild_warning(msg: str) -> None:
    console.print(indented_bullet(Text(msg, style='mild_warning')))


def warning_text(text: Union[str, Text]) -> Text:
    msg = Text('').append(f"WARNING", style='bright_yellow').append(": ")

    if isinstance(text, Text):
        return msg + text
    else:
        return msg.append(text)


def error_text(text: Union[str, Text]) -> Text:
    msg = Text('').append(f"ERROR", style='bright_red').append(": ")

    if isinstance(text, Text):
        return msg + text
    else:
        return msg.append(text)


def print_error(text: Union[str, Text]) -> Text:
    console.print(error_text(text))


def comma_join(strs: List[str], style: str) -> Text:
    return Text(", ").join([Text(s, style) for s in strs])


def attention_getting_panel(text: Text, title: str, style: str = 'white on red') -> Padding:
    p = Panel(text, padding=(2), title=title, style=style)
    return Padding(p, pad=(1, 10, 2, 10))


def _file_operation_log_message(basename: str, new_file: Path, log_msg: str) -> Text:
    log_msg += ' '
    log_msg = Text(log_msg)

    # TODO: pass the Config in here somehow to check for dry_run?
    # if Config.dry_run:
    #     log_msg = NOT + log_msg

    txt = Text(f"➤ ") + log_msg + Text(basename, style='color(221)')
    txt.append(' to ').append(str(new_file), style='cyan')
    return txt
