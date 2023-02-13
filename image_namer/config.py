import logging
import os
from pathlib import Path
from typing import List, Optional, Union

from image_namer.util.filesystem_helper import subdirs_of_dir

DEFAULT_SCREENSHOTS_DIR = Path.home().joinpath('Pictures', 'Screenshots')


class Config:
    debug = False

    @classmethod
    def set_directories(
            cls,
            screenshots_dir: Union[str, Path] = DEFAULT_SCREENSHOTS_DIR,
            destination_dir: Optional[Union[str, Path]] = None
    ) -> None:
        """Set the directories to find screenshots in and sort screenshots to."""
        cls.screenshots_dir: Path = Path(screenshots_dir)
        cls.destination_dir: Path = Path(destination_dir or screenshots_dir)
        cls.sorted_screenshots_dir = cls.destination_dir.joinpath('Sorted')
        cls.processed_screenshots_dir = cls.destination_dir.joinpath('Processed')

        for dir in [cls.destination_dir, cls.sorted_screenshots_dir, cls.processed_screenshots_dir]:
            if not dir.is_dir():
                logging.warning(f"Need to create '{dir}'")
                dir.mkdir(parents=True, exist_ok=True)

    @classmethod
    def get_sort_dirs(cls) -> List[str]:
        return sorted(subdirs_of_dir(cls.sorted_screenshots_dir), key=lambda d: d.lower())
