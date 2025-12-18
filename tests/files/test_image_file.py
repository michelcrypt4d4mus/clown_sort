from shutil import rmtree

from clown_sort.config import Config
from clown_sort.files.image_file import IMAGE_DESCRIPTION, ImageFile

from tests.test_config import *

DO_KWON_TEXT = 'Fed Up Cassa'
SORTED_FILENAME = 'Tweet by @stablekwon replying to @rtalbot55 - "others I don\'t debate the poor on Twitter, and sorry I don\'t have any change on me for her at the moment. 2:51 AM - 7_1_21 - Twitter for iPhone 7 Retwe" do_kwon_debate_the_poor.jpeg'


def test_extracted_text_and_move(do_kwon_tweet, turn_off_dry_run):
    image_file = ImageFile(do_kwon_tweet)
    assert(image_file.extracted_text().startswith(DO_KWON_TEXT))
    image_file.sort_file()
    new_file = ImageFile(Config.sorted_screenshots_dir.joinpath('TerraLuna', SORTED_FILENAME))
    assert(new_file.exif_dict()[IMAGE_DESCRIPTION].startswith(DO_KWON_TEXT))
    assert(new_file.new_basename() == SORTED_FILENAME)  # Check that it doesn't try to re-rename the file
    new_file.file_path.unlink()
    rmtree(new_file.file_path.parent)
