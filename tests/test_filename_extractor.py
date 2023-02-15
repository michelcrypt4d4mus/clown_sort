import pytest

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


GABOR_TWEET_TEXT = """fee) Gabor Gurbacs @

@gaborgurbacs

Looking at the facts, Tether (USDT) is the most
trusted stablecoin globally since it continues to be
the #1 stablecoin by market cap and trades 10x the
daily volume of USDC. Sad to see Coinbase behave
like this when an exchange is supposed to remain
impartial.

© Coinbase % @coinbase - Feb 3
Stability = Confidence

Make the switch to the digital dollar, and experience zero fees when you
convert from USDT to USDC.
coinbase.com/blog/switch-to...

6:47 AM - Feb 4, 2023 - 48K Views

20 Retweets 7QuoteTweets 107 Likes

Oo v wv)

o>

Tweet your reply

Replying to @gaborgurbacs

| think this Coinbase media campaign will have the opposite effect. USDC
users will learn about USDT and convert to USDT as they question the
motivations and rationale of this campaign. After-all, if Coinbase and
Coinbase users don’t like USDT why did they list USDT? ;)

fee} Gabor Gurbacs @ @gaborgurbacs - Feb 4

O 5 Td 3 QO 2 tht 2,884 &

Gabor Gurbacs @ @gaborgurbacs - Feb 4 oe
On professionalism: It’s good to see @paoloardoino, @bitcoinlawyer & the
Tether team work and act like professionals. Tether works with both

partners and competitors in a respectful and collaborative manner. Tether
cares about the industry. After all: Rising tides lift all boats."""


BAD_OCR_TWEET = """af

Martin Farber @ASYB111 - tih
Replying to @cz_binance
Any updates on send cash feature? It is temporarily disabled.

1o) td iv) ily 399 a“"""


REDDIT_POST = """© r/binance - Posted by u/TheLostWander_er 13 hours ago

send cash feature is temporarily disable.

I was trying to withdraw cash since last week and I am seeing this message every time I try the send
cash feature. Am I the only one getting this? What else can I do to send cash?

i) 5 Comments Award Vad Share im Save"""


REDDIT_REPLIES = """3 Fluffyhobbit - 5 days ago - edited 5 days ago

Option 4. 80% of us send crypto to cold storage and binance doesn't skip a beat
Edit: forgot to put in doesn't*

> 22 tb ) Reply Give Award Share Report Save Follow

2 LeftAct8968 OP - 5 days ago

I love it. That’s my plan! Haha

> adh i) Reply Give Award Share Report Save Follow

BS Fluffyhobbit - 5 days ago

I feel confident binance can handle our $$ moving out all at once since they just had some
billion dollar transfer days & didn't pause transfers @ @

> 6 ib i) Reply Give Award Share Report Save Follow

a ry DisIsGoodForBitcoin - 5 days ago

& MatrixName - 4 days ago

Exactly!
OP believes that little 1B worth of Voyager assets would impact Binance lol

People withdrew over 6B in days on Binance with zero impact.

> adh ) Reply Give Award Share Report Save Follow"""


REDDIT_R_CRYPTOCURRENCY_REPLY = """Si Roberto9410 i} 17.8k - 13 hr. ago
Platinum | QC: CC 831.
Wow the downfall of BUSD is something to see

<p. 1<4 Giveaward Share Report Save Follow

@ FacundoGabrielGuzman © 0-12hr. ago

Platinum | QC: CC 29, BTC 21
It won't be good. It would send bitcoin to the Mariana Trench
<p.0 <> Giveaward Share Report Save Follow

'S) Bunnywabbit13 i} 1.8k - 9 hr. ago

Platinum | QC: CC 170 | ADA 10 | r/AMD 20

Nothing bad will really happen as long as the peg is secured and everyone gets their
money back.

People will just change from BUSD to other stables.

<p. 1<4 Giveaward Share Report Save Follow
"""

@pytest.fixture(scope='session')
def ocr_image(do_kwon_tweet):
    image_file = ImageFile(do_kwon_tweet)
    image_file.ocr_attempted = True
    return image_file


def test_tweet_filenames(ocr_image):
    ocr_image._ocr_text = WUBLOCKCHAIN_TWEET_TEXT
    assert FilenameExtractor(ocr_image).filename() == 'Tweet by @WuBlockchain: "a16z voted 15 million UNI against the final proposal to deploy Uniswap V3 on BNB Chain proposed by OxPlasma Labs. The proposal uses Wormhole as a cross_chain bridge. a16z o" do_kwon_debate_the_poor.jpeg'
    ocr_image._ocr_text = REPLY_TWEET_TEXT
    assert FilenameExtractor(ocr_image).filename() == 'Tweet by @gedaominas replying to @tier10k: "The same thing happened with their SEPA transfers a couple of years ago. Just because Binance isn\'t licensed for money institution activities_ they have" do_kwon_debate_the_poor.jpeg'
    ocr_image._ocr_text = TIMESTAMPED_TWEET_TEXT
    assert FilenameExtractor(ocr_image).filename() == 'Tweet by @tier10k: "_DB_ SEC Probe Into Kraken at an Advanced Stage and Could Lead to a Settlement in Coming Days: Bloomberg 3:55 PM _ Feb 8_ 2023 _ 77.3K Views" do_kwon_debate_the_poor.jpeg'
    ocr_image._ocr_text = GABOR_TWEET_TEXT
    assert FilenameExtractor(ocr_image).filename() == 'Tweet by @gaborgurbacs: "I think this Coinbase media campaign will have the opposite effect. USDC users will learn about USDT and convert to USDT as they question the motivations and rationale of" do_kwon_debate_the_poor.jpeg'
    ocr_image._ocr_text = BAD_OCR_TWEET
    assert FilenameExtractor(ocr_image).filename() == 'Tweet by @ASYB111: "Replying to @cz_binance Any updates on send cash feature? It is temporarily disabled. 1o_ td iv_ ily 399 a_" do_kwon_debate_the_poor.jpeg'


def test_reddit_filenames(ocr_image):
    ocr_image._ocr_text = REDDIT_POST
    assert FilenameExtractor(ocr_image).filename() == 'Reddit post by TheLostWander_er in binance: "send cash feature is temporarily disable. I was trying to withdraw cash since last week and I am seeing this message every time I try the send cash fe" do_kwon_debate_the_poor.jpeg'
    ocr_image._ocr_text = REDDIT_REPLIES
    assert FilenameExtractor(ocr_image).filename() == 'Reddit post by Fluffyhobbit: "Option 4. 80_ of us send crypto to cold storage and binance doesn\'t skip a beat Edit: forgot to put in doesn\'t_ _ 22 tb _" do_kwon_debate_the_poor.jpeg'
    ocr_image._ocr_text = REDDIT_R_CRYPTOCURRENCY_REPLY
    assert FilenameExtractor(ocr_image).filename() == 'Reddit post by Roberto9410: "Wow the downfall of BUSD is something to see _p. 1_4" do_kwon_debate_the_poor.jpeg'

