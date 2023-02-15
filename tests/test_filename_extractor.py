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

REDDIT_POST = """© r/binance - Posted by u/TheLostWander_er 13 hours ago

send cash feature is temporarily disable.

I was trying to withdraw cash since last week and I am seeing this message every time I try the send
cash feature. Am I the only one getting this? What else can I do to send cash?

i) 5 Comments Award Vad Share im Save"""


def test_filename(do_kwon_tweet):
    image_file = ImageFile(do_kwon_tweet)
    image_file._ocr_text = WUBLOCKCHAIN_TWEET_TEXT
    image_file.ocr_attempted = True
    assert FilenameExtractor(image_file).filename() == 'do_kwon_debate_the_poor Tweet by @WuBlockchain: "a16z voted 15 million UNI against the final proposal to deploy Uniswap V3 on BNB Chain proposed by OxPlasma Labs. The proposal uses Wormhole as a cross_chain bridge. a16z oppose.jpeg'

    image_file._ocr_text = REPLY_TWEET_TEXT
    assert FilenameExtractor(image_file).filename() == 'do_kwon_debate_the_poor Tweet by @gedaominas replying to @tier10k: "The same thing happened with their SEPA transfers a couple of years ago. Just because Binance isn\'t licensed for money institution activities_ they have to re.jpeg'

    image_file._ocr_text = TIMESTAMPED_TWEET_TEXT
    assert FilenameExtractor(image_file).filename() == 'do_kwon_debate_the_poor Tweet by @tier10k: "_DB_ SEC Probe Into Kraken at an Advanced Stage and Could Lead to a Settlement in Coming Days: Bloomberg 3:55 PM _ Feb 8_ 2023 _ 77.3K Views".jpeg'

    image_file._ocr_text = GABOR_TWEET_TEXT
    assert FilenameExtractor(image_file).filename() == 'do_kwon_debate_the_poor Tweet by @gaborgurbacs: "I think this Coinbase media campaign will have the opposite effect. USDC users will learn about USDT and convert to USDT as they question the motivations and rationale of this c.jpeg'

    image_file._ocr_text = REDDIT_POST
    assert FilenameExtractor(image_file).filename() == 'do_kwon_debate_the_poor Reddit post by TheLostWander_er in binance: "send cash feature is temporarily disable. I was trying to withdraw cash since last week and I am seeing this message every time I try the send cash feature..jpeg'
