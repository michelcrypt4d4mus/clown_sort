"""
A range of page numbers.
"""
import re
from argparse import ArgumentTypeError
from dataclasses import dataclass
from typing import Tuple

PAGE_RANGE_REGEX = re.compile('\\d(-\\d)?')


@dataclass
class PageRange:
    page_range: str

    def __post_init__(self):
        if not PAGE_RANGE_REGEX.match(self.page_range):
            raise ValueError(f"Invalid page range '{self.page_range}'")

        if '-' in self.page_range:
            (self.first_page, self.last_page) = (int(p) for p in self.page_range.split('-'))
        else:
            self.first_page = int(self.page_range)
            self.last_page = self.first_page + 1

        if self.last_page <= self.first_page:
            raise ValueError(f"Invalid page range {self.__repr__()}")

    def in_range(self, page_number) -> bool:
        """Returns True if page_number is in this range."""
        return page_number >= self.first_page and page_number < self.last_page

    def file_suffix(self) -> str:
        """String that can be used as file suffix."""
        if self.first_page + 1 == self.last_page:
            return f"page_{self.first_page}"
        else:
            return f"pages_{self.first_page}-{self.last_page}"

    def to_tuple(self) -> Tuple[int, int]:
        return (self.first_page, self.last_page)

    def __repr__(self) -> str:
        return f"PageRange({self.first_page}, {self.last_page})"


class PageRangeArgumentValidator(object):
    HELP_MSG = "a single digit ('11') or a range ('11-15') (WILL NOT extract the last page)"

    def __call__(self, value):
        if not PAGE_RANGE_REGEX.match(value):
            raise ArgumentTypeError("Argument has to match '{}'".format(PAGE_RANGE_REGEX.pattern))

        return PageRange(value)
