from typing import List

from rich.text import Text


def comma_join(strs: List[str]) -> Text:
    return Text(", ").join([Text(s, 'bright_green') for s in strs])
