from typing import Optional, Union

from rich.text import Text

ARROW_BULLET = '➤ '
INDENTED_BULLET = f"  {ARROW_BULLET}"


def indented_bullet(msg: Union[str, Text], style: Optional[str] = None) -> Text:
    return Text('  ') + bullet_text(msg, style)


def bullet_text(msg: Union[str, Text], style: Optional[str] = None) -> Text:
    if isinstance(msg, str):
        msg = Text(msg, style=style)

    return Text(ARROW_BULLET).append(msg)
