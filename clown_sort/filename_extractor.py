"""
Decide on a filename string based on some OCR text.
"""
import re
from typing import Optional

from rich.text import Text

from clown_sort.util.logging import log
from clown_sort.util.rich_helper import console

MAX_FILENAME_LENGTH = 225

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
MIN_LENGTH_FOR_DUPE_CHECK = 9


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
            query_title = self._strip_bad_chars(dune_match.group(1))
            filename_str = 'Dune Analytics "' + query_title + '" '
            new_filename = filename_str + self.image_file.basename
        elif self._is_tweet() or self._is_reddit():
            if self._is_tweet():
                filename_str = self._filename_str_for_tweet()
            else:
                filename_str = self._filename_str_for_reddit()

            filename = f"{filename_str} {self.image_file.basename_without_ext}"
            filename = filename[0:-1] if filename.endswith('.') else filename
            new_filename = filename + self.image_file.extname
        elif self._is_reveddit():
            filename_str = 'Reveddit '
            subreddit_match = SUBREDDIT_REGEX.search(self.text)

            if subreddit_match is not None:
                filename_str += 'r_' + (subreddit_match.group('subreddit') or subreddit_match.group('subreddit2')) + ' '

            new_filename = filename_str + self.image_file.basename
        else:
            filename_str = self.text[0:self.available_char_count]
            new_filename = self._build_filename(self.image_file.basename_without_ext, filename_str)
            new_filename += self.image_file.extname

        # If we already seem to have scanned the file then just return the filename
        if self._is_text_already_in_filename(filename_str):
            log.warning(f"'{filename_str}' already appears in filename, not renaming.")
            return self.image_file.basename

        return new_filename

    def _is_tweet(self) -> bool:
        """Return true if the text looks like a tweet."""
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
        body = ' '.join(body.splitlines()).replace('\\s+', ' ')
        body = re.sub('’', "'", body).replace('|', 'I').replace(',', ',')
        body = self._strip_bad_chars(body)
        body = body[0:self.available_char_count - len(filename_text) - 2].strip()
        return f'{filename_text} - "{body}"'.replace('  ', ' ')

    def _strip_bad_chars(self, text: str) -> str:
        """Remove chars that don't work well in filenames"""
        return re.sub('[^0-9a-zA-Z@.?_:\'" ()]+', '_', text)

    def _is_text_already_in_filename(self, filename_str: str) -> bool:
        """Check if the extracted text is already in the filename"""
        return filename_str[0:100] in self.image_file.basename and len(filename_str) > MIN_LENGTH_FOR_DUPE_CHECK

    def _first_line(self) -> str:
        return self.text.split('\n')[0]
