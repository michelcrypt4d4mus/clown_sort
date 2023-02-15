"""
Decide on a filename string based on some OCR text.
"""
import re
from typing import Optional

from rich.text import Text

from image_namer.util.logging import console, log

MAX_FILENAME_LENGTH = 255
TWEET_REPLY_REGEX = re.compile('Replying to (@[a-zA-Z0-9]{3,15}).*?\\n(?P<body>.*)', re.DOTALL | re.MULTILINE)

TWEET_REGEX = re.compile(
    '(@[a-zA-Z0-9]{3,15}(\\.\\.\\.)?)(\\s{1,2}-\\s{1,2}(\\d{1,2}[smhd]|Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec).*?)?\\n(?P<body>.*)',
    re.DOTALL | re.MULTILINE)


class FilenameExtractor:
    def __init__(self, image_file: 'ImageFile') -> None:
        self.image_file = image_file
        self.text: Optional[str] = image_file.ocr_text()
        self.basename_length: int = len(image_file.basename)
        self.available_char_count: int = MAX_FILENAME_LENGTH - self.basename_length - 1

    def filename(self) -> str:
        filename: str

        if self.text is None:
            filename = self.image_file.basename
        if self._is_tweet():
            filename = f"{self.image_file.basename_without_ext} {self._filename_str_for_tweet()}"
            filename = filename[0:self.available_char_count] + self.image_file.extension
        else:
            filename = self.image_file.basename

        return filename

    def _is_tweet(self) -> bool:
        """Return true if the text looks like a tweet."""
        return TWEET_REGEX.search(self.text) is not None

    def _filename_str_for_tweet(self) -> str:
        tweet_match = TWEET_REGEX.search(self.text)
        author = tweet_match.group(1)
        #import pdb;pdb.set_trace()
        body = tweet_match.group('body')

        filename_text = f"Tweet by {author}"
        log_txt = Text("YES it's a tweet by ", style='color(82)').append(author, style='color(178)')
        reply_to = TWEET_REPLY_REGEX.search(self.text)

        if reply_to is not None:
            filename_text += f" replying to {reply_to.group(1)}"
            body = reply_to.group('body')
            log_txt.append("\n    -> Replying to ", style='color(23)')
            log_txt.append(reply_to.group(1), style='color(178)')

        console.print(log_txt)
        log.debug(f"\nBody:\n{body}\n")
        body = ' '.join(body.splitlines()).replace('\\s+', ' ')
        log.debug(f"\nBody flattened:\n{body}\n")
        body = re.sub('’', "'", body)
        body = re.sub('[^0-9a-zA-Z@.?_$\'" ]+', '_', body).rstrip()
        return filename_text + ' ' + body
