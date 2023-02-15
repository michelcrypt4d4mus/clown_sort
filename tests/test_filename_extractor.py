from image_namer.filename_extractor import FilenameExtractor
from image_namer.image_file import ImageFile

WUBLOCKCHAIN_TWEET_TEXT = """wu

BLOCKC}*AIN

Wu Blockchain @ @WuBlockchain - 21m see
a16z voted 15 million UNI against the final proposal to deploy Uniswap V3
on BNB Chain proposed by OxPlasma Labs. The proposal uses Wormhole
as a cross-chain bridge. a16z opposes the use of Wormhole and supports
the use of LayerZero. tally.xyz/gov/uniswap/pr...

O 8 tl 7 Q 35 it 6,634 4,"""


def test_filename(do_kwon_tweet):
    image_file = ImageFile(do_kwon_tweet)
    image_file._ocr_text = WUBLOCKCHAIN_TWEET_TEXT
    image_file.ocr_attempted = True
    assert FilenameExtractor(image_file).filename() == 'do_kwon_debate_the_poor Tweet by @WuBlockchain.jpeg'
