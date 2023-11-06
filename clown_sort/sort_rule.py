"""
Class to contain a text sorting rule.
SortRule = namedtuple('SortRule', ['folder', 'regex'])
"""
import csv
import importlib.resources
import re
import sys
from dataclasses import dataclass
from os import environ
from pathlib import Path
from typing import List, Optional, Union

from rich.console import Console
from rich.text import Text

from clown_sort.util.constants import CRYPTO, PACKAGE_NAME
from clown_sort.util.rich_helper import print_error

RULES_CSV_PATHS = 'RULES_CSV_PATHS'
SORTING_RULES_DIR = importlib.resources.files(PACKAGE_NAME).joinpath('sorting_rules')
CRYPTO_RULES_CSV_PATH = Path(str(SORTING_RULES_DIR.joinpath('crypto.csv')))


class SortRuleParseError(RuntimeError):
    pass


@dataclass
class SortRule:
    folder: str
    regex: Union[str, re.Pattern]

    def __post_init__(self):
        try:
            self.regex = re.compile(self.regex, re.IGNORECASE | re.MULTILINE)
        except re.error as e:
            msg = f"{str(e)} while processing '{self.folder}' sort rule '{self.regex}'"
            raise SortRuleParseError(msg) from e

    @classmethod
    def load_rules_csv(cls, file_path: Path) -> List['SortRule']:
        """Turn a CSV of sort rules into a list of SortRule objects."""
        sort_rules = []

        with open(Path(file_path), mode='r') as csvfile:
            for row in csv.DictReader( filter(SortRule.is_valid_row, csvfile), delimiter=','):
                try:
                    sort_rules.append(cls(row['folder'], row['regex']))
                except SortRuleParseError as e:
                    print_error(f"{str(e)} in file '{file_path}'!")
                    raise e

        return sort_rules

    @staticmethod
    def is_valid_row(row: str) -> bool:
        """Returns false for whitespace rows and those that start with '#'."""
        stripped_row = row.strip()
        return len(stripped_row) > 0 and stripped_row[0] != '#'

    @staticmethod
    def sort_rules_csvs(csv_paths: Optional[str]) -> List[Path]:
        """Expects str of paths separated by ':'. Replace the string 'crypto' with the default CSV."""
        if isinstance(csv_paths, Path):
            return [csv_paths]
        elif csv_paths is None:
            return SortRule.default_rules_csv_paths()

        return [
            CRYPTO_RULES_CSV_PATH if csv_path == CRYPTO else Path(csv_path)
            for csv_path in csv_paths.split(':')
        ]

    @staticmethod
    def default_rules_csv_paths() -> List[Path]:
        """Check for RULES_CSV_PATHS in env vars otherwise return default crypto rules."""
        return SortRule.sort_rules_csvs(environ.get(RULES_CSV_PATHS, CRYPTO_RULES_CSV_PATH))

    def __eq__(self, other: 'SortRule') -> bool:
        return self.folder == other.folder and self.regex == other.regex
