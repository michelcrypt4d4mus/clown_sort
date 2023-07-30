"""
Decide on a filename string based on some OCR text.
"""
import re
from difflib import SequenceMatcher
from typing import Optional

from clown_sort.util.logging import log
from clown_sort.util.filesystem_helper import strip_bad_chars, strip_mac_screenshot

TWEET_REPLY_REGEX = re.compile(
    'Replying to (@\\w{3,15}).*?\\n(?P<body>.*)',
    re.DOTALL | re.MULTILINE
)

TWEET_REGEX = re.compile(
    '(@\\w{3,15}(\\.\\.\\.)?)(\\s{1,2}-\\s{1,2}([\\dti]{1,2}[smhd]|Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec).*?)?\\n(?P<body>.*)',
    re.DOTALL | re.MULTILINE
)

REDDIT_POST_REGEX = re.compile(
    '(r/(?P<sub>\\w{3,30}) - )?Posted by u/(?P<author>\\w{3,30}) \\d+.*?\\n(?P<body>.*)',
    re.DOTALL | re.MULTILINE
)

REDDIT_REPLY_REGEX = re.compile(
    '(?P<author>\\w{3,30})( OP -)?\\s+(.*?)-\\s+\\d+\\s+(seconds|min(\\.|utes)|hours|hr\\.|days|months|years)\\s+ago\\s*(.*?)\\n(?P<body>.*?)(Reply\\s+)?Give\\s?Award\\s+Share\\s+Report',
    re.DOTALL | re.MULTILINE | re.IGNORECASE
)

REVEDDIT_REGEX = re.compile('Reveddit Real.?Time')
SUBREDDIT_REGEX = re.compile('/r/(?P<subreddit>\\w+)|\\sse(lf|ir)\\.(?P<subreddit2>\\w+)')
DUNE_ANALYTICS_REGEX = re.compile('Query results (.*) @\\w+')
RETWEETED_REGEX = re.compile('(.*) Retweeted')

MAX_FILENAME_LENGTH = 225
MIN_LENGTH_FOR_DUPE_CHECK = 9
DEFAULT_LENGTH_FOR_LONG_FILENAMES = 190
MIN_SIMILARITY_RATIO_TO_BE_SAME = 0.80


class FilenameExtractor:
    def __init__(self, image_file: 'ImageFile') -> None:
        self.image_file = image_file
        self.text: Optional[str] = image_file.extracted_text()
        self.basename_length: int = len(image_file.basename)
        self.available_char_count: int = MAX_FILENAME_LENGTH - self.basename_length - 1
        self.author: Optional[str] = None
        self.reply_to_account: Optional[str] = None

    def filename(self) -> str:
        """Examine self.text and decide on an appropriate filename."""
        if self.text is None:
            return self.image_file.basename

        if DUNE_ANALYTICS_REGEX.search(self.text):
            dune_match = DUNE_ANALYTICS_REGEX.search(self.text)
            query_title = strip_bad_chars(dune_match.group(1))
            filename_str = 'Dune Analytics "' + query_title + '" '
            new_filename = filename_str + self.image_file.basename
        elif self._is_tweet() or self._is_reddit():
            if self._is_tweet():
                filename_str = self._filename_str_for_tweet()
            else:
                filename_str = self._filename_str_for_reddit()

            filename_str = filename_str[0:-1] if filename_str.endswith('.') else filename_str
            filename = f"{filename_str} {self.image_file.basename_without_ext}"
            new_filename = filename + self.image_file.extname
        elif self._is_reveddit():
            filename_str = 'Reveddit '
            subreddit_match = SUBREDDIT_REGEX.search(self.text)

            if subreddit_match is not None:
                filename_str += 'r_' + (subreddit_match.group('subreddit') or subreddit_match.group('subreddit2'))

            new_filename = filename_str[0:self.available_char_count]  + ' ' + self.image_file.basename
        else:
            filename_str = self.text[0:max(100, self.available_char_count)]
            new_filename = self._build_filename(self.image_file.basename_without_ext, self.text)
            new_filename = new_filename[0:MAX_FILENAME_LENGTH] + self.image_file.extname

        if self._is_text_already_in_filename(filename_str):
            return self.image_file.basename

        if len(new_filename) > 255:
            raise ValueError(f"'{new_filename}' is {len(new_filename)} chars")

        return new_filename

    def _is_tweet(self) -> bool:
        """Return true if the text looks like a tweet."""
        # TODO: the check for @crypto_oracle is a hack
        return TWEET_REGEX.search(self.text) is not None and '@crypto_oracle' not in self.text

    def _is_retweet(self) -> bool:
        """Return true if the text looks like a retweet."""
        return self._is_tweet() and RETWEETED_REGEX.search(self._first_line()) is not None

    def _retweeter(self) -> Optional[str]:
        """Return the name of the retweeter (or None if there isn't one)"""
        if self._is_retweet():
            retweet_match = RETWEETED_REGEX.search(self._first_line())
            retweeter = retweet_match.group(1)
            # Remove the leading 'tl' (or whatever Tesseract interprets the loop arrow icon to be)
            return ','.join(retweeter.split()[1:])
        else:
            return None

    def _is_reddit(self) -> bool:
        """Return true if it's a reddit post or reddit comment."""
        return self._is_reddit_post() or self._is_reddit_comment()

    def _is_reddit_post(self) -> bool:
        """Return true if it's a reddit post."""
        return REDDIT_POST_REGEX.search(self.text) is not None

    def _is_reddit_comment(self) -> bool:
        """Return true if it's a reddit comment."""
        return REDDIT_REPLY_REGEX.search(self.text) is not None

    def _is_reveddit(self) -> bool:
        """Return true if text is from reveddit.com (site for deleted reddit posts and comments)."""
        return REVEDDIT_REGEX.search(self.text) is not None

    def _filename_str_for_tweet(self) -> str:
        """Build a filename for tweets."""
        tweet_match = TWEET_REGEX.search(self.text)
        self.author = tweet_match.group(1)
        body = tweet_match.group('body')
        filename_text = f"Tweet by {self.author}"
        retweeter = self._retweeter()
        reply_to = TWEET_REPLY_REGEX.search(self.text)

        if retweeter is not None:
            filename_text = f'Retweeted by {retweeter} - {filename_text}'

        if reply_to is not None:
            self.reply_to_account = reply_to.group(1)

            if self.reply_to_account != self.author:
                filename_text += f" replying to {self.reply_to_account}"

            body = reply_to.group('body')

        return self._build_filename(filename_text, body)

    def _filename_str_for_reddit(self) -> str:
        """Build a filename for Reddit posts and comments."""
        if self._is_reddit_post():
            reddit_match = REDDIT_POST_REGEX.search(self.text)
            self.author = reddit_match.group('author')
            subreddit: str = reddit_match.group('sub')
            body: str = reddit_match.group('body')
            filename_text: str = f"Reddit post by {self.author}"

            if subreddit:
                filename_text += f" in {subreddit}"
        else:
            reddit_match = REDDIT_REPLY_REGEX.search(self.text)
            self.author = reddit_match.group('author')
            body: str = reddit_match.group('body')
            filename_text: str = f"Reddit post by {self.author}"

        return self._build_filename(filename_text, body)

    def _build_filename(self, filename_text: str, body: str) -> str:
        """Construct a workable filename."""
        body = strip_bad_chars(body)
        end_position = self.available_char_count - len(filename_text) - 2

        if end_position < 0:
            end_position = DEFAULT_LENGTH_FOR_LONG_FILENAMES

        body = body[0:end_position].strip()

        if len(body) == 0:
            return filename_text

        return f'{filename_text} - "{body}"'.replace('  ', ' ')

    def _is_text_already_in_filename(self, filename_str: str) -> bool:
        """Check if the extracted text is already in the filename"""

        # Subtract 25 to account for the 'Screenshot at 2020-05-05' etc part of filename
        chars_to_compare = min(len(filename_str), len(self.image_file.basename) - 25)
        # In case it's < 0 or v. small
        chars_to_compare = max(chars_to_compare, MIN_LENGTH_FOR_DUPE_CHECK)

        # Cleanup strings before comparing
        clean_filename_str = strip_mac_screenshot(strip_bad_chars(filename_str))[0:chars_to_compare]
        clean_basename = strip_mac_screenshot(self.image_file.basename)[0:len(clean_filename_str)]
        matcher = SequenceMatcher(None, clean_filename_str, clean_basename)
        similarity = matcher.ratio()

        is_duplicate_text = (matcher.ratio() > MIN_SIMILARITY_RATIO_TO_BE_SAME) \
                         or (clean_filename_str in self.image_file.basename)

        msg = f"Similarity of '{clean_filename_str}'\n  and '{clean_basename}'\n" \
              f"  is {similarity} (is_duplicate_text: {is_duplicate_text})"
        log.debug(msg)

        if is_duplicate_text and len(filename_str) > MIN_LENGTH_FOR_DUPE_CHECK:
            log.debug(f"'{clean_filename_str}' already appears in filename, not renaming.")
            log.debug(f"Extracted text: '{self.text}'")
            return True
        else:
            log.debug(f"\n'{clean_filename_str}'\nis not in\n'{self.image_file.basename}'\n")
            return False

    def _first_line(self) -> str:
        return self.text.split('\n')[0]
