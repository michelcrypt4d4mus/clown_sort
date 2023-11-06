"""
Base class for sortable files of any type.
"""
import re
from dataclasses import dataclass
from typing import List, Optional

from clown_sort.config import Config


@dataclass
class RuleMatch:
    folder: str
    match: re.Match

    @classmethod
    def get_rule_matches(cls, search_text: Optional[str]) -> List['RuleMatch']:
        """Find any folders that could be relevant by matching against search_string both with and w/out underscores."""
        if search_text is None:
            return []

        if '_' not in search_text:
            return cls._get_raw_matches(search_text)

        # \b word boundary doesn't match underscores so we replace with spaces and search again
        matched_rules = cls._get_raw_matches(search_text) + cls._get_raw_matches(search_text.replace('_', ' '))
        # Abuse dict comprehension to uniquify the matches and remove dupes.
        return [rm for rm in {rule.folder: rule for rule in matched_rules}.values()]

    @classmethod
    def _get_raw_matches(cls, search_text: Optional[str]) -> List['RuleMatch']:
        """Find any folders that could be relevant."""
        if search_text is None:
            return []

        return [
            cls(sr.folder, sr.regex.search(search_text))
            for sr in Config.sort_rules if sr.regex.search(search_text)
        ]
