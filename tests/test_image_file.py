from image_namer.files.image_file import IMAGE_DESCRIPTION, ImageFile

from tests.test_config import *

DO_KWON_TEXT = 'Fed Up Cassa'
DO_KWON_FOLDER = 'DoKwonIsADipshit'


def test_extracted_text_and_move(do_kwon_tweet, test_config):
    image_file = ImageFile(do_kwon_tweet)
    assert(image_file.extracted_text().startswith(DO_KWON_TEXT))
    new_file = image_file.move_file_to_sorted_dir(DO_KWON_FOLDER, dry_run=False)
    new_image_file = ImageFile(new_file)
    assert(new_image_file.exif_dict()[IMAGE_DESCRIPTION].startswith(DO_KWON_TEXT))
    new_file.unlink()
    new_file.parent.rmdir()
