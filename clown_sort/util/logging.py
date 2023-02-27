"""
Logging and printing, for now.
"""
import logging

from rich.logging import RichHandler

from clown_sort.util.constants import PACKAGE_NAME


log = logging.getLogger(PACKAGE_NAME)
log.addHandler(RichHandler(rich_tracebacks=True))


def set_log_level(log_level) -> None:
    log.setLevel(log_level)

    for handler in log.handlers:
        handler.setLevel(log_level)
