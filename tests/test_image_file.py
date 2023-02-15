import filedate

from image_namer.image_file import IMAGE_DESCRIPTION, ImageFile

from tests.test_config import *

DO_KWON_TEXT = 'Fed Up Cassa'
DO_KWON_FOLDER = 'DoKwonIsADipshit'


def test_ocr_text_and_move(do_kwon_tweet):
    Config.set_directories(FIXTURES_DIR, TMP_DIR)
    image_file = ImageFile(do_kwon_tweet())
    assert(image_file.ocr_text().startswith(DO_KWON_TEXT))
    new_file = image_file.set_image_description_exif_as_ocr_text(DO_KWON_FOLDER)
    new_image_file = ImageFile(new_file)
    assert(new_image_file.exif_dict()[IMAGE_DESCRIPTION].startswith(DO_KWON_TEXT))
    new_file.unlink()
    new_file.parent.rmdir()
