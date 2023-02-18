"""
Decide on a filename string based on some OCR text.
"""
import re
from typing import Optional

from rich.text import Text

from social_arsenal.util.logging import console, log

MAX_FILENAME_LENGTH = 225

TWEET_REPLY_REGEX = re.compile(
    'Replying to (@[a-zA-Z0-9]{3,15}).*?\\n(?P<body>.*)',
    re.DOTALL | re.MULTILINE
)

TWEET_REGEX = re.compile(
    '(@[a-zA-Z0-9]{3,15}(\\.\\.\\.)?)(\\s{1,2}-\\s{1,2}([\\dti]{1,2}[smhd]|Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec).*?)?\\n(?P<body>.*)',
    re.DOTALL | re.MULTILINE
)

REDDIT_POST_REGEX = re.compile(
    'r/(?P<sub>\\w{3,30}) - Posted by u/(?P<author>\\w{3,30}) \\d+.*?\\n(?P<body>.*)',
    re.DOTALL | re.MULTILINE
)

REDDIT_REPLY_REGEX = re.compile(
    '(?P<author>\\w{3,30})\\s+(.*?)-\\s+\\d+\\s+(seconds|minutes|hours|hr\\.|days|months|years)\\s+ago\\s*(.*?)\\n(?P<body>.*?)(Reply\\s+)?Give\\s?Award\\s+Share\\s+Report',
    re.DOTALL | re.MULTILINE | re.IGNORECASE
)


class FilenameExtractor:
    def __init__(self, image_file: 'ImageFile') -> None:
        self.image_file = image_file
        self.text: Optional[str] = image_file.extracted_text()
        self.basename_length: int = len(image_file.basename)
        self.available_char_count: int = MAX_FILENAME_LENGTH - self.basename_length - 1

    def filename(self) -> str:
        filename: str

        if self.text is None:
            filename = self.image_file.basename
        elif self._is_tweet() or self._is_reddit():
            if self._is_tweet():
                filename_str = self._filename_str_for_tweet()
            else:
                filename_str = self._filename_str_for_reddit()

            filename = f"{filename_str} {self.image_file.basename_without_ext}"
            filename = filename[0:-1] if filename.endswith('.') else filename
            filename = filename + self.image_file.extname
        else:
            filename = self.image_file.basename

        return filename

    def _is_tweet(self) -> bool:
        """Return true if the text looks like a tweet."""
        return TWEET_REGEX.search(self.text) is not None

    def _is_reddit(self) -> bool:
        return self._is_reddit_post() or self._is_reddit_reply()

    def _is_reddit_post(self) -> bool:
        return REDDIT_POST_REGEX.search(self.text) is not None

    def _is_reddit_reply(self) -> bool:
        return REDDIT_REPLY_REGEX.search(self.text) is not None

    def _filename_str_for_tweet(self) -> str:
        """Build a filename for tweets."""
        tweet_match = TWEET_REGEX.search(self.text)
        author = tweet_match.group(1)
        body = tweet_match.group('body')

        filename_text = f"Tweet by {author}"
        log_txt = Text("It's a tweet by ", style='color(82)').append(author, style='color(178)')
        reply_to = TWEET_REPLY_REGEX.search(self.text)

        if reply_to is not None:
            reply_to_account = reply_to.group(1)

            if reply_to_account != author:
                filename_text += f" replying to {reply_to_account}"

            body = reply_to.group('body')
            log_txt.append("\n    -> Replying to ", style='color(23)')
            log_txt.append(reply_to.group(1), style='color(178)')

        console.print(log_txt)
        return self._build_filename(filename_text, body)

    def _filename_str_for_reddit(self) -> str:
        """Build a filename for Reddit posts and comments."""
        if self._is_reddit_post():
            reddit_match = REDDIT_POST_REGEX.search(self.text)
            author: str = reddit_match.group('author')
            subreddit: str = reddit_match.group('sub')
            body: str = reddit_match.group('body')
            filename_text: str = f"Reddit post by {author} in {subreddit}"
        else:
            reddit_match = REDDIT_REPLY_REGEX.search(self.text)
            author: str = reddit_match.group('author')
            body: str = reddit_match.group('body')
            filename_text: str = f"Reddit post by {author}"

        return self._build_filename(filename_text, body)

    def _build_filename(self, filename_text: str, body: str) -> str:
        body = ' '.join(body.splitlines()).replace('\\s+', ' ')
        log.debug(f"\nBody flattened:\n{body}\n")
        body = re.sub('’', "'", body).replace('|', 'I').replace(',', ',')
        body = re.sub('[^0-9a-zA-Z@.?_:\'" ]+', '_', body)
        body = body[0:self.available_char_count - len(filename_text) - 2].strip()
        return f'{filename_text}: "{body}"'.replace('  ', ' ')
