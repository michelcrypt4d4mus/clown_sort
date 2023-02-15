from image_namer.filename_extractor import FilenameExtractor
from image_namer.image_file import ImageFile

TEXT = 'foo'


def test_filename(do_kwon_tweet):
    filename = FilenameExtractor(ImageFile(do_kwon_tweet()))
