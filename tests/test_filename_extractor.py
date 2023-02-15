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

REPLY_TWEET_TEXT = """gedaominas @ = @ @gedaominas - 6h

Replying to @tier10k

The same thing happened with their SEPA transfers a couple of years ago.
Just because Binance isn't licensed for money institution activities, they
have to rely on 3rd parties and such parties in this industry have a
tendency to change. Not a big deal if you asked me.

QO 5 td 2 QO 34 ili 14.5K 4

Bitrashi Nakedfoto @Stevi Wunda- 5h
Replying to @gedaominas and @tier10k
Why isn’t Binance licensed for money institution activities?

You don’t think it’s a big deal that they use straw men as fronts for their
business?

I think it reeks of nefarious activity that they keep a layer of separation
between themselves and their customers.

O4 vr 9 4 tht 618 4"""

TIMESTAMPED_TWEET_TEXT = """>
a db @
‘ap’ @tier10k

[DB] SEC Probe Into Kraken at an Advanced Stage
and Could Lead to a Settlement in Coming Days:
Bloomberg

3:55 PM - Feb 8, 2023 - 77.3K Views"""


def test_filename(do_kwon_tweet):
    image_file = ImageFile(do_kwon_tweet)
    image_file._ocr_text = WUBLOCKCHAIN_TWEET_TEXT
    image_file.ocr_attempted = True
    assert FilenameExtractor(image_file).filename() == 'do_kwon_debate_the_poor Tweet by @WuBlockchain.jpeg'

    image_file._ocr_text = REPLY_TWEET_TEXT
    assert FilenameExtractor(image_file).filename() == 'do_kwon_debate_the_poor Tweet by @gedaominas replying to @tier10k.jpeg'
